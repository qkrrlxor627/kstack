# kstack

> 평가 가이드를 주면 → 그 기준(C/K ID)으로 코드를 분석하고 → 개선 단계를 기록해 → final-report 형식으로 답하게 만드는 **Claude Code 작업 키트**

`all_total_vue` 과제에서 쓴 `/improve` · `/bench` · `rubric-reviewer` · hook 구성을 다른 코드 프로젝트에도 옮겨 쓸 수 있게 일반화했습니다.

**프로젝트마다 신경 쓸 것은 결국 두 가지입니다: ① 평가 가이드를 넣고 ② `kstack.json` 값을 확인하는 것.** 나머지는 공통입니다.

---

## 목차

1. [새 프로젝트에 적용하기](#1-새-프로젝트에-적용하기) ← 핵심
2. [kstack.json 설정](#2-kstackjson-설정)
3. [프로젝트에서 확인할 파일 / 안 건드려도 되는 파일](#3-프로젝트에서-확인할-파일--안-건드려도-되는-파일)
4. [전체 흐름](#4-전체-흐름)
5. [구성 요소](#5-구성-요소)
6. [폴더 구조](#6-폴더-구조)
7. [kstack 자체를 고칠 때](#7-kstack-자체를-고칠-때)
8. [문제 해결](#8-문제-해결)

---

## 1. 새 프로젝트에 적용하기

### Step 0. 설치 (프로젝트마다 1회)

```bash
bash ~/kstack/install.sh ~/work/new-proj --author "박기택 <qkrrlxor627@gmail.com>"
```

| 항목 | 내용 |
|---|---|
| 전제 | 대상 폴더는 **git 저장소**여야 합니다 |
| 이미 kstack 파일이 있으면 | 설치가 멈춥니다. 덮어쓰려면 `--force` |
| 기본 동작 | `.claude/`, `CLAUDE.md`, `doc/workClaude.md`를 `.git/info/exclude`에 넣어 **원격에 올리지 않습니다** |
| 원격에도 올리려면 | `--commit-config` |

```bash
# 설정 파일까지 커밋 대상으로 두고 설치
bash ~/kstack/install.sh ~/work/new-proj --author "박기택 <qkrrlxor627@gmail.com>" --commit-config

# 이미 설치된 프로젝트에 다시 설치 (kstack.json 먼저 백업)
cp ~/work/new-proj/.claude/kstack.json ~/kstack.json.bak
bash ~/kstack/install.sh ~/work/new-proj --author "박기택 <qkrrlxor627@gmail.com>" --force
```

### Step 1~7. 사용 순서

| # | 할 일 | 결과 |
|---|---|---|
| 1 | 평가 가이드를 `doc/criteria/mission.md`, `standard.md`에 넣는다 | 원본 (Claude 수정 불가) |
| 2 | `/kstack-setup` 실행 → 나온 표를 읽고 고칠 곳을 말한다 | `doc/criteria/ids.md`, `kstack.json` 값 |
| 3 | `/improve v1` | `outputs/improvement-v1.md` (+ 채점표) |
| 4 | (선택) `/bench baseline` | Before 수치 |
| 5 | 코드 수정 (`[P1 BEFORE]` / `[P1 AFTER]` 주석) → `/report-step P1` 반복 | `outputs/final-report/03_step1_P1.md` … |
| 6 | `/bench after` | `compare_after_vs_baseline.md` |
| 7 | `/final-report` | 색인·문제 인식·측정·발표·트레이드오프 |

```text
/kstack-setup
/improve v1
/bench baseline
/report-step P1
/report-step P2
/bench after
/final-report
```

5단계의 코드 주석은 개선안 번호(P1, P2 …)로 Before/After를 표시합니다. 세부 규칙은 `METHOD.md`의 코드 주석 규칙을 따릅니다.

```python
# [P1 BEFORE]
# [P1 AFTER]
```

> 스킬은 **직접 입력해야만 실행**됩니다 (`disable-model-invocation: true`).

### 적용 체크리스트

- [ ] 대상 폴더가 git 저장소인가
- [ ] `install.sh`로 설치했는가 (`--author` 지정)
- [ ] `doc/criteria/mission.md` — 최종 산출물 요건(발표 목차, 필수·선택 항목, 시간 제한)을 넣었는가
- [ ] `doc/criteria/standard.md` — 판정 기준(교안, 채점표, 컨벤션 등)을 넣었는가
- [ ] `/kstack-setup` 후 `doc/criteria/ids.md`의 C/K ID가 맞는지 확인했는가 (틀리면 고치라고 말하거나 직접 수정)
- [ ] `.claude/kstack.json`의 `test` · `bench` · `presentation` 값이 이 프로젝트에 맞는가

---

## 2. kstack.json 설정

`.claude/kstack.json`은 **프로젝트마다 바꾸는 유일한 설정 파일**입니다. `/kstack-setup`이 채워 주지만, 맞는지는 직접 확인해야 합니다.

| 키 | 예 | 쓰는 곳 | 비고 |
|---|---|---|---|
| `criteria.*`, `protected` | `doc/criteria/mission.md` | 모든 스킬, `protect_files` | |
| `test.watch` | `["src/","tests/"]` | `auto_pytest`, `/report-step` | 소스 폴더 |
| `test.cmd` | `python3 -m pytest tests -q -x` | `auto_pytest`, `/report-step` | 비어 있으면 자동 테스트가 꺼짐 |
| `bench.run_cmd` | `python3 bench/run.py --tag {tag} --out {results}` | `/bench` | 측정 명령 |
| `bench.key` | `query_id` | 비교표의 행 키 | |
| `presentation.minutes` | `5` | 발표 시간 배분, 범위 채점 | |

```jsonc
// 일부 예시 (criteria.*, protected는 /kstack-setup이 만든 값 확인)
{
  "test": {
    "watch": ["src/", "tests/"],
    "cmd": "python3 -m pytest tests -q -x"
  },
  "bench": {
    "run_cmd": "python3 bench/run.py --tag {tag} --out {results}",
    "key": "query_id"
  },
  "presentation": {
    "minutes": 5
  }
}
```

> ⚠️ `protected`를 바꾸면 `.claude/settings.json`의 `permissions.deny`도 같이 바꿔야 합니다. (`/kstack-setup`이 맞춰 줍니다.)

---

## 3. 프로젝트에서 확인할 파일 / 안 건드려도 되는 파일

### 매번 확인

| 파일 | 언제 | 무엇을 |
|---|---|---|
| `doc/criteria/mission.md` | 설치 직후 | 평가 가이드 중 최종 산출물 요건 (발표 목차, 필수·선택 항목, 시간 제한) |
| `doc/criteria/standard.md` | 설치 직후 | 판정 기준 (교안, 채점표, 컨벤션 등) |
| `.claude/kstack.json` | `/kstack-setup` 후 | [2. kstack.json 설정](#2-kstackjson-설정) |
| `doc/criteria/ids.md` | `/kstack-setup`이 만든 뒤 | C/K ID가 맞는지 확인 |

### 거의 안 바꿈 (필요할 때만)

| 파일 | 경우 |
|---|---|
| `.claude/settings.json` | 평가 가이드에 맞게 `permissions.deny` 경로를 맞출 때 (`/kstack-setup`이 해 줌) |
| `CLAUDE.md` | 그 프로젝트에만 필요한 규칙을 추가할 때 |
| `doc/workClaude.md` | Claude 구성을 바꾸면 변경 이력 갱신 (보통은 Claude가 갱신) |

### 안 건드려도 됨

- `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` — 모든 프로젝트에 공통이고, 값은 `kstack.json`에서 읽습니다.
- `outputs/` 아래 파일 — 스킬이 만듭니다.

---

## 4. 전체 흐름

```
평가 가이드 (mission.md, standard.md)
        │
        ▼
/kstack-setup ──▶ C/K ID 표(ids.md) + kstack.json + settings.json 맞춤
        │
        ▼
/improve ──▶ ID별 현황 판정 → 개선안 P1~
        │
        ▼
/bench baseline ──▶ Before 수치 (선택)
        │
        ▼
코드 수정 + /report-step Pn ──▶ 단계 문서 ①인식 ~ ⑦재발 방지  (반복)
        │
        ▼
/bench after ──▶ Before/After 비교
        │
        ▼
/final-report ──▶ 최종 보고서 묶음 (outputs/final-report/)
```

---

## 5. 구성 요소

| 종류 | 이름 | 하는 일 |
|---|---|---|
| 스킬 | `/kstack-setup` | 평가 가이드 → C/K ID 표 |
| 스킬 | `/improve` | ID별 현황 판정 → 개선안 P1~ |
| 스킬 | `/bench` | 측정 + 요약 CSV 비교 (`scripts/compare.py`) |
| 스킬 | `/report-step` | 단계 문서 ①인식 ~ ⑦재발 방지 |
| 스킬 | `/final-report` | 최종 보고서 묶음 (`scripts/code_index.py`) |
| 에이전트 | `rubric-reviewer` | C/K 기준 채점 (읽기 전용) |
| 에이전트 | `evidence-checker` | 수치·경로·캡처 실존 검사 (읽기 전용) |
| hook | `git_guard` | 작성자 강제 |
| hook | `protect_files` | 원본(평가 가이드 등 `protected`) 수정 차단 |
| hook | `auto_pytest` | 테스트 자동 실행 (`test.watch`, `test.cmd`) |

---

## 6. 폴더 구조

### kstack 저장소

```
kstack/
├── README.md       이 문서
├── METHOD.md       방법론: ID 체계, 판정·근거 규칙, L1~L3, 코드 주석 규칙, 산출물 흐름, 안전장치
├── install.sh      설치 스크립트
├── template/       대상 프로젝트에 복사되는 것 (CLAUDE.md, .claude/, doc/)
├── examples/       all_total_vue 과제의 실제 산출물 (형식 참고용)
└── tests/
    └── smoke.sh    스모크 테스트
```

### 설치된 프로젝트

```
<project>/
├── CLAUDE.md
├── .claude/
│   ├── kstack.json      ← 프로젝트마다 확인
│   ├── settings.json
│   ├── skills/
│   ├── agents/
│   └── hooks/
├── doc/
│   ├── workClaude.md
│   └── criteria/
│       ├── mission.md   ← 평가 가이드 넣기
│       ├── standard.md  ← 평가 가이드 넣기
│       └── ids.md       ← /kstack-setup 결과 확인
└── outputs/             ← 스킬이 생성
```

---

## 7. kstack 자체를 고칠 때

작업 방식을 바꾸고 싶을 때만 `~/kstack`을 고칩니다.

| 바꿀 것 | 위치 |
|---|---|
| 개선 단계 기록 형식 | `template/.claude/skills/report-step/step.md` |
| 발표 형식 | `final-report/templates/` |

```bash
# 수정 뒤 점검하고 push
bash ~/kstack/tests/smoke.sh
git push
```

> ⚠️ `template/`을 고쳐도 **이미 설치된 프로젝트에는 반영되지 않습니다.** 필요하면 `--force`로 다시 설치하되, 그 프로젝트의 `kstack.json`은 먼저 백업하세요. ([Step 0](#step-0-설치-프로젝트마다-1회) 참고)

---

## 8. 문제 해결

| 증상 | 조치 |
|---|---|
| 스킬이 목록에 안 보임 | Claude Code를 재시작 |
| 스킬이 자동으로 실행되지 않음 | 정상 동작. `disable-model-invocation: true`라 직접 입력해야 실행됨 |
| 설치가 멈춤 | 이미 kstack 파일이 있음 → `kstack.json` 백업 후 `--force` |
| 자동 테스트가 안 돎 | `kstack.json`의 `test.cmd`가 비어 있는지 확인 |
| `.claude/` 등이 원격에 안 올라감 | 기본값(`.git/info/exclude`). 올리려면 `--commit-config`로 설치 |
