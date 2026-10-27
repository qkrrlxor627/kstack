# Claude 구성 설명서 (kstack) — {{PROJECT}}

> 이 프로젝트에 붙인 Claude Code 구성을 한곳에 정리한 문서다.
> 이 파일과 `.claude/`, `CLAUDE.md`는 기본적으로 **로컬 전용**이다(`.git/info/exclude`).
> Claude 관련 구성을 추가하거나 바꾸면 이 문서의 해당 표와 맨 아래 "변경 이력"을 함께 갱신한다.

## 1. 한눈에 보기

| 종류 | 이름 | 실행 방법 | 한 줄 설명 |
|---|---|---|---|
| 스킬 | `/kstack-setup` | 직접 입력 (설치 직후 1회) | 평가 가이드 → `doc/criteria/ids.md` C/K ID 표 + 설정 제안 |
| 스킬 | `/improve` | `/improve v1 [ID…]` | ID별 현황 판정 → `outputs/improvement-<버전>.md` |
| 스킬 | `/bench` | `/bench baseline`, `/bench after` | 측정 → Before와 비교표 (`kstack.json`의 `bench`) |
| 스킬 | `/report-step` | `/report-step P1` | 단계 문서 ①~⑦ → `outputs/final-report/NN_step*.md` |
| 스킬 | `/final-report` | `/final-report [all]` | 코드 색인·문제 인식·측정·발표·트레이드오프 |
| 에이전트 | `rubric-reviewer` | `/improve`, `/final-report`가 호출 | C/K ID 기준 PASS/FAIL 채점 (읽기 전용) |
| 에이전트 | `evidence-checker` | `/report-step`, `/final-report`가 호출 | 수치·경로·캡처가 실제로 있는지 검사 (읽기 전용) |
| hook | `git_guard` | 자동 (Bash 전) | Claude 표기 커밋, `--author`, 로컬 전용 파일 add 차단 |
| hook | `protect_files` | 자동 (Bash 전) | 평가 가이드 원본 수정 차단 |
| hook | `auto_pytest` | 자동 (Edit/Write 후) | `test.watch` 폴더 수정 시 `test.cmd` 실행 |
| 설정 | `kstack.json` | hook·스킬이 읽음 | 경로·명령·발표 시간 |
| 설정 | `settings.json` | 자동 | 공동 작성자 표기 끔, 원본 Edit 금지, hook 등록 |
| 규칙 | `CLAUDE.md` | 세션 시작 시 | 작업 규칙, 작성자 고정 |

> 스킬은 `disable-model-invocation: true`라서 직접 입력할 때만 실행된다.

## 2. kstack.json 현재 값
| 키 | 값 | 의미 |
|---|---|---|
| `test.watch` / `test.cmd` | | 비어 있으면 auto_pytest는 아무것도 안 함 |
| `bench.run_cmd` | | 비어 있으면 /bench는 멈추고 안내 |
| `presentation.minutes` | | 발표 시간 |

## 3. 변경 이력

| 날짜 | 추가/변경 | 파일 |
|---|---|---|
| {{DATE}} | kstack 설치 | `.claude/`, `CLAUDE.md`, `doc/criteria/`, `doc/workClaude.md` |
