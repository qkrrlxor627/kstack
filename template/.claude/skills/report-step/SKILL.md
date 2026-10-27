---
name: report-step
description: 개선 1단계(P 하나 또는 묶음)를 끝낸 뒤 ①인식~⑦재발 방지 형식의 단계 문서를 outputs/final-report/에 쓴다
argument-hint: <P ID들> [단계 번호]
disable-model-invocation: true
---

# /report-step — 개선 단계 문서

인자: `$ARGUMENTS`
- 앞의 ID들: 이번 단계에서 고친 개선안(예: `P1`, `P3 P4 P9`). 없으면 묻는다.
- 단계 번호: 없으면 `outputs/final-report/`의 기존 `NN_stepK_*.md`를 보고 다음 번호를 쓴다.

## 입력
- 개선안: `outputs/improvement-*.md` 최신본에서 해당 P의 문제·근거 K ID·대상 C ID
- ID 체계: `doc/criteria/ids.md`
- 코드 변경: `git log`, `git diff <Before 태그 또는 커밋>`, 코드 안의 `[Px BEFORE]` / `[Px AFTER]` 주석 (`grep -rn "\[P1 "`)
- 측정·증거: `bench.results` 폴더, `outputs/before/`, `outputs/after/` (있으면)
- 테스트 결과: `kstack.json`의 `test.cmd`를 실제로 실행한 출력

## 절차
1. 위 입력을 모은다. 코드에 `[Px BEFORE/AFTER]` 주석이 없으면 사용자에게 알리고, 넣을지 묻는다(색인 `00_code_index.md`가 이 주석으로 만들어진다).
2. 테스트를 실행해 통과 수를 기록한다. 실패하면 문서를 쓰지 말고 알린다.
3. 같은 폴더 `step.md` 양식으로 `outputs/final-report/NN_step<K>_<P ID들>.md`를 쓴다.
   - 파일 번호 NN은 03부터 시작한다(00 색인, 01 문제 인식, 02 측정 방법은 `/final-report`가 쓴다).
   - ④ 대안은 최소 2개, 선택하지 않은 이유까지 쓴다. 선택 근거는 K ID로 댄다.
   - ⑥ 검증은 실제로 실행한 것만 쓴다. 아직 안 한 측정은 "N단계에서 측정한다"고 쓴다.
4. `evidence-checker` 서브에이전트로 이 문서를 검사하고 "없음/불일치"를 고친다.
5. 사용자에게 요약과 남은 확인 사항(캡처를 찍어야 하는 장면 등)을 출력한다.

## 규칙
- `outputs/`에만 쓴다. 코드는 고치지 않는다.
- 수치·`파일:줄`은 실제 파일에서만 가져온다. 확인 못 한 판단은 "(추정)".
- 줄 번호는 "이 단계 커밋 기준"임을 문서 머리에 적는다.
- 나빠진 점·포기한 점도 트레이드오프 절에 쓴다.
- 커밋은 하지 않는다. 커밋 메시지를 제안할 때 Claude 공동 작성자 표기를 넣지 않는다.
