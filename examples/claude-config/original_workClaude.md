# Claude 구성 설명서 (스킬 · 에이전트 · hook)

> 이 프로젝트에 붙인 Claude Code 구성을 한곳에 정리한 문서다. 스킬을 쓸 때, 무엇을 썼는지 확인할 때 본다.
> 이 파일과 `.claude/`, `CLAUDE.md`는 **로컬 전용**이다(`.git/info/exclude`). GitHub에 올라가지 않는다.
> Claude 관련 구성을 추가하거나 바꾸면 이 문서의 해당 표와 맨 아래 "변경 이력"을 함께 갱신한다.

---

## 1. 한눈에 보기

| 종류 | 이름 | 실행 방법 | 한 줄 설명 |
|---|---|---|---|
| 스킬 | `/improve` | `/improve v1` 직접 입력 | 미션 + 교안 기준으로 개선안 문서 작성 |
| 스킬 | `/bench` | `/bench after` 직접 입력 | 성능 측정 → Before와 비교표 생성 |
| 에이전트 | `rubric-reviewer` | `/improve`가 자동 호출 | 개선안을 C/K 기준으로 채점 (읽기 전용) |
| hook | `git_guard` | 자동 (Claude의 Bash 실행 전) | Claude 표기 커밋, 로컬 파일 add 차단 |
| hook | `protect_files` | 자동 (Claude의 Bash 실행 전) | 미션·기준표 원본 수정 차단 |
| hook | `auto_pytest` | 자동 (Claude가 파일 수정한 후) | `agent/`·`tests/` 수정 시 단위 테스트 실행 |
| 설정 | `settings.json` | 자동 | 공동 작성자 표기 끔, 원본 Edit 금지, hook 등록 |
| 규칙 | `CLAUDE.md` | 자동 (세션 시작 시 읽음) | 개선안 작업 규칙, 작성자 박기택 고정 |

> 스킬은 `disable-model-invocation: true`라서 **직접 입력할 때만** 실행된다. Claude가 알아서 실행하지 않는다.
> 목록에 안 보이면 `/skills`로 확인하고, 그래도 없으면 Claude Code를 재시작한다.

---

## 2. 스킬

### `/improve` — 개선안 문서 만들기
- **언제**: 발표 전에 "뭘 고쳐야 미션·교안 기준을 채우는지" 정리하고 싶을 때
- **사용법**
  ```
  /improve v1              # 전체 기준으로 개선안 작성
  /improve v1 C3-g K9      # 단위 테스트(C3-g)·Validator(K9) 중심으로 깊게
  /improve                 # 버전 생략 시 오늘 날짜로 저장
  ```
- **결과**: `outputs/improvement-<버전>.md`
  - 기준 충족 표(C/K)
  - 개선안 P1~
  - 로드맵
  - 미해결 질문
- **절차**: 미션·기준표 읽기 → 체크리스트 → 코드 조사로 판정 → 개선안 → `rubric-reviewer` 채점 → FAIL 수정 → 사람이 결정할 질문 출력
- **ID 체계**
  - C = 미션 항목
    - C1 주제 / C2 개선 사항 / C3 기술 요소·캡처 / C4 전후 수치 / C5 한계
    - C3 세부: C3-a Multi-Agent, C3-b MCP, C3-c RAG, C3-d 의존성 주입, C3-e LangSmith, C3-f 모듈화, C3-g 단위 테스트, C3-h 구현 캡처, C3-i 최종 실행 캡처
  - K = 교안 단원 번호: K1 ADR ~ K15 Observability
- **파일**: `.claude/skills/improve/SKILL.md`, `template.md`
- **입력 문서**: `doc/mission_k.md`, `doc/lessonstandard_k.md` (둘 다 수정 금지)

### `/bench` — 측정하고 Before와 비교
- **언제**: 코드를 고친 뒤 "얼마나 좋아졌는지" 숫자로 보고 싶을 때 (발표 ④ 전후 수치)
- **사용법**
  ```
  /bench after                   # After 측정 + baseline과 비교
  /bench after-p1 --vs after     # 직전 측정과 비교
  /bench quick --repeat 1        # 빠른 확인 (Before와 정확한 비교는 아님)
  ```
- **결과**
  - `bench/results/<tag>_raw.jsonl`, `<tag>_summary.csv`
  - `bench/results/compare_<tag>_vs_baseline.md`: 바뀐 값에 ⚠️ 표시
- **안전장치**
  - tag가 `baseline`이거나 이미 있으면 멈추고 묻는다. Before 증거 보호용이다.
  - 서버가 떠 있는지, Before와 같은 모델인지 확인한다.
- **소요 시간**: Ollama 기준 약 25분 (백그라운드 실행, 진행 상황은 물어보면 알려 줌)
- **사전 조건**: `bash sh/run_agent_ollma.sh`로 백엔드(:8100)가 떠 있어야 한다.
- **파일**: `.claude/skills/bench/SKILL.md`, `scripts/compare.py`

---

## 3. 에이전트

### `rubric-reviewer`
- **역할**: `outputs/`의 최신 개선안을 미션(C)·교안(K) 기준으로 채점한다. 문서는 고치지 않는다.
- **도구**: Read, Grep, Glob만 쓴다 (읽기 전용). 모델은 sonnet이다.
- **지적하는 것**
  - 누락된 ID
  - 근거 경로 없는 주장
  - 실제 파일에 없는 수치
  - 교안과 무관한 근거
  - 미션 이탈
  - 5분 발표에 과한 범위
- **출력**: ID별 PASS/FAIL + 이유 + 수정 지시
- **직접 쓰기**: "rubric-reviewer로 outputs/improvement-v1.md 채점해줘"
- **파일**: `.claude/agents/rubric-reviewer.md`

---

## 4. hook (하네스가 자동으로 강제)

**동작 원리**
1. Claude가 도구를 쓰기 직전 또는 직후에 하네스가 스크립트를 실행하고, 도구 입력을 JSON으로 넘긴다.
2. 스크립트가 **exit 2**로 끝나면 차단되고, 그 이유가 Claude에게 전달된다.
3. **exit 0**으로 끝나면 통과한다.

| hook | 시점 | 막는 것 / 하는 일 | 통과하는 것 |
|---|---|---|---|
| `git_guard.py` | PreToolUse · Bash | `git add .claude`·`CLAUDE.md`, `git add -f`, 커밋·태그의 `Co-Authored-By`/`Generated with Claude`/`noreply@anthropic.com`, `--author` | 그 외 git 명령 전부 |
| `protect_files.py` | PreToolUse · Bash | 미션·기준표에 `>`, `>>`, `sed -i`, `rm`, `mv`, `cp`(덮어쓰기), `git checkout/restore/rm/mv` | `cat`, `grep`, `sed -n`, 다른 파일로 복사 |
| `auto_pytest.py` | PostToolUse · Edit\|Write | `agent/`·`tests/`의 `.py` 수정 후 `pytest tests -q -x` 실행. 실패하면 결과를 Claude에 전달 | 다른 파일 수정 시 아무것도 안 함 |

- **등록 위치**: `.claude/settings.json`의 `"hooks"`
- **스크립트 위치**: `.claude/hooks/`
- **한계**
  - **Claude가 실행하는 명령만** 검사한다. 터미널에서 직접 치는 git은 검사하지 않는다.
  - `git commit -F 파일`의 내용, `python -c`로 파일 쓰기는 못 잡는다.
- **시험 방법** (스크립트 단독)
  ```bash
  echo '{"tool_input":{"command":"git add CLAUDE.md"}}' | python3 .claude/hooks/git_guard.py; echo $?   # 2면 차단
  ```

---

## 5. 설정·규칙

### `.claude/settings.json`
| 키 | 값 | 의미 |
|---|---|---|
| `attribution` | commit/pr 빈 문자열 | 커밋·PR에 Claude 표기를 넣지 않음 |
| `includeCoAuthoredBy` | `false` | 위와 같음 (이전 버전 호환) |
| `permissions.allow` | `Edit(./outputs/**)` | 개선안 폴더는 승인 없이 수정 |
| `permissions.deny` | `Edit(./doc/mission_k.md)`, `Edit(./doc/lessonstandard_k.md)` | 원본 Edit 금지 |
| `hooks` | 위 4장 | hook 3개 등록 |

### `CLAUDE.md`
- 미션·기준표 경로와 수정 금지
- 산출물은 `outputs/`에만 쓴다
- C/K ID로 매핑한다
- 작성자는 박기택만이고 Claude 표기는 없다
- Claude 구성을 바꾸면 이 문서(`doc/workClaude.md`)를 갱신한다

### git (로컬)
- `.git/info/exclude`: `.claude/`, `CLAUDE.md`, `doc/workClaude.md`를 업로드에서 뺀다
- 저장소 git config: `user.name=박기택`, `user.email=qkrrlxor627@gmail.com`

---

## 6. 만들 때 쓴 내장 스킬·도구

| 내장 스킬 | 언제 썼나 | 무엇에 |
|---|---|---|
| `skill-creator` (anthropic-skills) | `/bench` 제작 | 스킬 구조(SKILL.md + scripts/) 설계. 측정이 25분짜리라 반복 평가 루프는 생략하고, 결과가 매번 같은 비교 스크립트를 실데이터로 시험함 |

**아직 안 썼지만 쓸 수 있는 내장 스킬**
| 스킬 | 쓸 때 |
|---|---|
| `/code-review` | P1 수정 diff 검토 |
| `/simplify` | 수정 코드 정리 |
| `/security-review` | push 전 키 유출 등 점검 |
| Slides 아티팩트 / `pptx` | 발표자료 만들기 |
| `dataviz` | 전후 비교 차트 |

---

## 7. 추천 작업 흐름
```
/improve v1          → 무엇을 고칠지 (outputs/improvement-v1.md)
코드 수정             → auto_pytest hook이 자동 검사 (xfail P1 → XPASS 확인 후 마커 삭제)
/bench after         → 전후 수치 (bench/results/compare_after_vs_baseline.md)
/code-review         → 수정 검토
커밋                  → git_guard가 Claude 표기·로컬 파일을 자동 차단
```

---

## 8. 변경 이력

| 날짜 | 추가/변경 | 파일 |
|---|---|---|
| 2026-10-20 | `/improve` 스킬, `rubric-reviewer`, settings, CLAUDE.md, `doc/mission_k.md` | `.claude/skills/improve/`, `.claude/agents/` |
| 2026-10-20 | `git_guard` hook | `.claude/hooks/git_guard.py` |
| 2026-10-20 | `/bench` 스킬 (skill-creator 사용) | `.claude/skills/bench/` |
| 2026-10-20 | `protect_files`, `auto_pytest` hook + 단위 테스트(15 passed, 1 xfailed) | `.claude/hooks/`, `tests/` |
| 2026-10-20 | 이 설명서 작성 (처음 이름은 `claudeSkillDes.md`) | `doc/workClaude.md` |
| 2026-10-20 | 파일 이름을 `claudeSkillDes.md` → `workClaude.md`로 변경. `CLAUDE.md`, `.git/info/exclude` 참조도 갱신 | `doc/workClaude.md` |
