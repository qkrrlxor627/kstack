# kstack 방법론 — 평가 가이드로 분석하고 final-report로 답한다

all_total_vue 과제(2026-10)에서 실제로 쓴 방식을 정리했다. 실물은 `examples/`에 있다.

## 1. 핵심 생각
1. **기준을 먼저 고정한다.** 평가 가이드(미션·기준표)를 원본 그대로 두고, 거기서 ID를 뽑는다. 이후 모든 판단·개선·보고는 그 ID로 말한다. "좋아 보이는 개선"이 아니라 "어느 기준을 채우는 개선"만 한다.
2. **판정에는 경로를, 수치에는 출처를.** 모든 현황 주장에 `파일:줄`, 모든 숫자에 결과 파일 경로를 붙인다. 확인 못 한 것은 "(추정)".
3. **Before는 증거다.** 고치기 전에 같은 입력 세트로 재고, 그 결과는 덮어쓰지 않는다. After는 같은 조건으로만 비교한다.
4. **채점은 따로 한다.** 쓴 사람(메인 세션)과 채점하는 사람(읽기 전용 서브에이전트)을 나눈다.
5. **나빠진 것도 보고서에 넣는다.** 트레이드오프는 미션 항목이고, 다음 개선의 출발점이다.

## 2. ID 체계
| 접두 | 출처 | 의미 | 예 |
|---|---|---|---|
| C | 미션 (`doc/criteria/mission.md`) | 최종 산출물이 갖춰야 할 것. **발표·보고서 목차 순서** | C1 주제, C3-a Multi-Agent, C4 전후 수치 |
| K | 기준표 (`doc/criteria/standard.md`) | 판정·설계 근거가 되는 개념. **원문 단원 번호 그대로** | K6 Multi-agent, K14 Modularization |
| P | 개선안 (`/improve`) | 고칠 문제. 우선순위 순 번호 | P1 여러 시스템 중 1개만 조사 |
| N | 측정·검증 중 새로 발견한 문제 | 개선 뒤에 드러난 회귀·누락 | N4 route 보정 회귀 |
| #n | 사용자가 따로 준 문제 목록 번호 (있으면) | P와 함께 표기 | P1(#1, #14) |

- 판정 4단계: **충족 / 부분 / 미충족 / 미확인**
- C나 K에 매핑되지 않는 개선은 **기준 외 제안**으로 분리한다(해도 되지만 점수 근거로 쓰지 않는다).

## 3. 수준 (L1~L3)
| 수준 | 기록 범위 | 언제 |
|---|---|---|
| L3 | ①인식 ②정의 ③원인 ④가설·대안 ⑤실행 ⑥검증 ⑦재발 방지 **전부 + 기록** | 핵심 문제, 발표에서 깊게 말할 것 |
| L2 (초안) | ②정의 ③원인 ⑤실행 ⑥검증 | 원인은 분명하지만 대안 비교가 크지 않은 것 |
| L1 (초안) | ⑤실행 ⑥검증 | 단순 수정 |

> L3은 과제 final-report에 쓰인 정의다. L1·L2는 kstack을 만들며 정리한 초안이니 프로젝트에 맞게 고쳐 쓴다.

## 4. 코드 주석 규칙
고친 곳에 Before를 주석으로 남기고 After에 표시한다. `00_code_index.md`가 이 주석을 grep해서 만들어진다.
```python
# [P1 BEFORE] 첫 시스템 1개만 넘김 ── (원래 코드 주석으로 보존)
# [P1 AFTER] 질문에 나온 시스템 '전부'를 넘긴다 (K6 권위 정규화)
# [P1·#14 AFTER] 여러 ID면 ·로 연결
```

## 5. 산출물 흐름
```
doc/criteria/mission.md + standard.md        (원본, 수정 금지)
        │ /kstack-setup
        ▼
doc/criteria/ids.md                            (C/K ID 표 — 사람 확인)
        │ /improve v1  ──▶ rubric-reviewer 채점
        ▼
outputs/improvement-v1.md                      (현황 판정 + P1~ + 로드맵)
        │ /bench baseline                      (Before 증거, 덮어쓰기 금지)
        │ 코드 수정 + [Px BEFORE/AFTER] 주석 + 테스트 (auto_pytest hook)
        │ /report-step P1 ──▶ evidence-checker
        ▼
outputs/final-report/03_step1_P1.md …          (단계마다 ①~⑦)
        │ /bench after → compare_after_vs_baseline.md
        │ /final-report ──▶ evidence-checker + rubric-reviewer
        ▼
outputs/final-report/
  00_code_index.md          코드 위치 색인 (자동)
  01_problem_recognition.md Before 문제 지도 + 슬라이드
  02_measurement.md         무엇을 어떻게 쟀나
  03~NN_step*.md            단계 문서
  NN_final_presentation.md  미션 C 순서, 시간 배분, 대본
  NN_tradeoffs_summary.md   ✅/⚠️/(추정)
```

## 6. 안전장치 (사람이 실수해도 지켜지는 것)
| 무엇을 | 어떻게 |
|---|---|
| 평가 가이드 원본 | `settings.json` deny Edit + `protect_files` hook (Bash 쓰기 차단) |
| 커밋 작성자 | `attribution` 빈 값 + `git_guard` hook (Co-Authored-By, `--author` 차단) |
| Claude 설정 유출 | `.git/info/exclude` + `git_guard` (로컬 전용 경로 add 차단) |
| 코드 회귀 | `auto_pytest` hook (감시 폴더 수정 직후 테스트) |
| Before 증거 | `/bench`가 기존 결과 덮어쓰기 전에 멈추고 묻는다 |
| 지어낸 수치 | `rubric-reviewer`, `evidence-checker`가 실제 파일에서 다시 찾는다 |

hook은 **Claude가 실행하는 명령만** 검사한다. 터미널에서 직접 치는 명령은 막지 않는다.
