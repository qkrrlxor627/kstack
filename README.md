# kstack

평가 가이드를 주면 → 그 기준(C/K ID)으로 코드를 분석하고 → 개선 단계를 기록해 → `final-report` 형식으로 답하게 만드는 Claude Code 작업 키트.
all_total_vue 과제에서 쓴 `/improve`·`/bench`·`rubric-reviewer`·hook 구성을 다른 코드 프로젝트에 옮길 수 있게 일반화했다.

## 설치 (프로젝트마다 1회)
```bash
bash ~/kstack/install.sh ~/work/new-proj --author "박기택 <qkrrlxor627@gmail.com>"
```
- 대상은 git 저장소여야 한다. 이미 kstack 파일이 있으면 멈춘다(`--force`로 덮기).
- 기본으로 `.claude/`, `CLAUDE.md`, `doc/workClaude.md`를 `.git/info/exclude`에 넣는다(원격에 안 올림). 올리려면 `--commit-config`.

## 사용 순서
| # | 할 일 | 결과 |
|---|---|---|
| 1 | 평가 가이드를 `doc/criteria/mission.md`, `standard.md`에 넣는다 | 원본 (Claude 수정 불가) |
| 2 | `/kstack-setup` → 표를 읽고 고칠 곳을 말한다 | `doc/criteria/ids.md`, `kstack.json` 값 |
| 3 | `/improve v1` | `outputs/improvement-v1.md` (+ 채점표) |
| 4 | (선택) `/bench baseline` | Before 수치 |
| 5 | 코드 수정 (`[P1 BEFORE]`/`[P1 AFTER]` 주석) → `/report-step P1` 반복 | `outputs/final-report/03_step1_P1.md` … |
| 6 | `/bench after` | `compare_after_vs_baseline.md` |
| 7 | `/final-report` | 색인·문제 인식·측정·발표·트레이드오프 |

스킬은 직접 입력해야만 실행된다(`disable-model-invocation: true`). 목록에 안 보이면 Claude Code를 재시작한다.

## 프로젝트마다 바꾸는 것: `.claude/kstack.json`
| 키 | 예 | 쓰는 곳 |
|---|---|---|
| `criteria.*`, `protected` | `doc/criteria/mission.md` | 모든 스킬, `protect_files` |
| `test.watch`, `test.cmd` | `["src/","tests/"]`, `python3 -m pytest tests -q -x` | `auto_pytest`, `/report-step` |
| `bench.run_cmd` | `python3 bench/run.py --tag {tag} --out {results}` | `/bench` |
| `bench.key` | `query_id` | 비교표의 행 키 |
| `presentation.minutes` | `5` | 발표 시간 배분, 범위 채점 |

`protected`를 바꾸면 `settings.json`의 `permissions.deny`도 같이 바꾼다(`/kstack-setup`이 맞춘다).

## 폴더
```
kstack/
├── README.md          이 문서
├── METHOD.md          방법론: ID 체계, 판정·근거 규칙, L1~L3, 코드 주석 규칙, 산출물 흐름, 안전장치
├── install.sh         설치 스크립트
├── template/          대상 프로젝트에 복사되는 것 (CLAUDE.md, .claude/, doc/)
└── examples/          all_total_vue 과제의 실제 산출물 (형식 참고용)
```

## 구성 요소
| 종류 | 이름 | 하는 일 |
|---|---|---|
| 스킬 | `/kstack-setup` | 평가 가이드 → C/K ID 표 |
| 스킬 | `/improve` | ID별 현황 판정 → 개선안 P1~ |
| 스킬 | `/bench` | 측정 + 요약 CSV 비교 (`scripts/compare.py`) |
| 스킬 | `/report-step` | 단계 문서 ①인식~⑦재발 방지 |
| 스킬 | `/final-report` | 최종 보고서 묶음 (`scripts/code_index.py`) |
| 에이전트 | `rubric-reviewer` | C/K 기준 채점 (읽기 전용) |
| 에이전트 | `evidence-checker` | 수치·경로·캡처 실존 검사 (읽기 전용) |
| hook | `git_guard`, `protect_files`, `auto_pytest` | 작성자·원본·테스트 자동 강제 |

## 이 키트를 고칠 때
- `template/`을 고치면 이미 설치된 프로젝트에는 반영되지 않는다. 필요하면 `--force`로 다시 설치하되, 그 프로젝트의 `kstack.json`은 먼저 백업한다.
- 수정 뒤 확인: `bash ~/kstack/tests/smoke.sh`
