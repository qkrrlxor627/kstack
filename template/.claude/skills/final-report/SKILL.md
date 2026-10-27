---
name: final-report
description: 단계 문서·측정 결과를 모아 outputs/final-report/의 코드 색인·문제 인식·측정 방법·최종 발표·트레이드오프 문서를 만든다. 미션(C ID) 순서를 그대로 따른다
argument-hint: [index|problem|measure|present|tradeoffs|all]
disable-model-invocation: true
---

# /final-report — 최종 보고서 묶음

인자: `$ARGUMENTS` — 만들 문서. 없으면 `all`.

| 인자 | 파일 | 양식 |
|---|---|---|
| `index` | `00_code_index.md` | 스크립트로 생성 (아래) |
| `problem` | `01_problem_recognition.md` | `templates/01_problem_recognition.md` |
| `measure` | `02_measurement.md` | `templates/02_measurement.md` |
| `present` | `<마지막 번호+1>_final_presentation.md` | `templates/final_presentation.md` |
| `tradeoffs` | `<그다음 번호>_tradeoffs_summary.md` | `templates/tradeoffs_summary.md` |

단계 문서(03~)는 `/report-step`이 이미 썼다고 가정한다. 없으면 멈추고 알린다.

## 입력
- `doc/criteria/ids.md`: C ID 순서 = 발표 순서. 발표 시간(`kstack.json`의 `presentation.minutes`)
- `outputs/improvement-*.md` 최신본, `outputs/final-report/NN_step*.md` 전부
- 측정: `bench.results`의 요약 CSV와 `compare_*.md`
- 캡처: `outputs/before/captures/`, `outputs/after/captures/` (같은 파일명 = 같은 장면)

## 절차
1. **index**: 코드 색인을 만든다.
   ```bash
   python3 .claude/skills/final-report/scripts/code_index.py --out outputs/final-report/00_code_index.md <소스 폴더들>
   ```
   소스 폴더는 `kstack.json`의 `test.watch`를 기본으로 쓴다.
2. **problem**: Before만 다룬다. "측정 방법을 바꾸니 문제가 보였다" → 문제 지도(고치는 순서·수준·영향 지표) → 문제별 슬라이드(증거 캡처 + 대본 1~2문장).
3. **measure**: 무엇을, 어떤 입력 세트로, 몇 번, 어떤 조건으로 쟀는지. 지표 정의. 재현 명령.
4. **present**: 미션의 C ID 순서대로 절을 만든다. 각 절 제목에 시간 배분을 붙이고 합이 발표 시간을 넘지 않게 한다. 절마다 표 + 캡처 경로 + `> 대본:` 한 단락.
   - 개선 사항 표: # / 문제 / 고친 방법 / 결과(수치) / 단계 문서
   - 기술 요소 표: C ID 하위 기술마다 어디에 / 이번에 바꾼 것 / 캡처
   - 수치 절: Before → After 표, 출처는 `compare_*.md`
   - 한계 절: tradeoffs 문서의 핵심 3줄
5. **tradeoffs**: 환경별 순효과 표 → 개선별 얻은 것/내준 것/되돌리는 방법 → 남은 한계.
   - ✅ 측정으로 확인한 이득 / ⚠️ 측정으로 확인한 비용 / (추정) 측정하지 않은 판단
6. `evidence-checker`로 이번에 쓴 문서를 검사하고 "없음/불일치"를 고친다. `rubric-reviewer`로 발표 문서가 C ID를 모두 덮는지 채점받는다.
7. 사용자에게: 만든 파일, 검사 결과, 아직 없는 캡처 목록, 발표 시간 합계를 출력한다.

## 규칙
- `outputs/`에만 쓴다.
- 수치는 측정 파일에서만. 단계 문서의 수치를 옮길 때도 원 출처 경로를 같이 옮긴다.
- 나빠진 지표를 빼지 않는다. 발표의 "한계"는 미션 항목이다.
- 기준 외 작업은 "(기준 외)"로 표시한다.
