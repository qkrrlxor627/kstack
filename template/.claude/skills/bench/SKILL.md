---
name: bench
description: kstack.json의 측정 명령으로 같은 입력 세트를 돌려 수치를 남기고 Before(baseline)와 비교표를 만든다. 개선 전 baseline, 개선 후 After 측정, 발표용 전후 수치 확보에 쓴다
argument-hint: <tag> [--vs baseline]
disable-model-invocation: true
---

# /bench — 측정하고 Before와 비교

인자: `$ARGUMENTS`
- 첫 단어 `<tag>`: 이번 측정의 이름(예: `baseline`, `after`, `after-p1`). 없으면 측정하지 말고 무슨 이름으로 할지 묻는다.
- `--vs <tag>`: 비교 기준(기본 `baseline`). `<tag>`가 `baseline`이면 비교는 하지 않는다.

설정은 `.claude/kstack.json`의 `bench`에서 읽는다.
- `run_cmd`: 측정 명령. `{tag}`, `{results}` 자리표시자를 쓸 수 있다. 예: `python3 bench/run.py --tag {tag} --out {results}`
- `health_cmd`: 측정 전 대상이 떠 있는지 확인하는 명령(선택)
- `results`: 결과 폴더 / `summary`: 요약 CSV 경로 패턴 / `key`: CSV의 키 열 / `ignore_cols`: 비교에서 뺄 열
- `minutes`: 1회 예상 소요 시간(분, 알면)

`run_cmd`가 비어 있으면 멈추고 알린다: 이 프로젝트에 측정 스크립트가 없다. 같은 입력 세트를 정해 결과를 `<key>`열이 있는 CSV로 남기는 스크립트를 먼저 만들어야 한다(만들지는 사용자에게 묻는다).

## 왜 이 순서인가
측정이 오래 걸리면 잘못된 조건으로 돌린 시간이 통째로 버려진다. 그리고 Before 결과는 다시 만들 수 없는 증거다. 1~2단계는 그 둘을 막는 확인이다.

## 절차
1. **덮어쓰기 방지**
   - `<tag>`의 요약 CSV가 이미 있으면 멈추고 덮어쓸지 묻는다. 특히 `baseline`은 Before 증거라 기본값은 "덮어쓰지 않음"이다.
2. **조건 확인**
   - `health_cmd`가 있으면 실행한다. 실패하면 멈추고 대상을 띄우는 방법을 안내한다.
   - 기준(`--vs`) 측정과 조건(모델, 환경 변수, 입력 세트 파일, 반복 횟수)이 같은지 확인한다. 기준 CSV나 로그에 조건이 남아 있으면 비교한다.
   - 다르면 그대로 진행하지 말고 알린다. 조건이 다르면 전후 차이가 코드 때문인지 구분할 수 없다.
3. **측정 실행**
   - 오래 걸리면 백그라운드로 실행하고 로그를 `<results>/<tag>_run.log`에 남긴다.
   - 시작했다는 것과 예상 시간을 알린다.
4. **비교** (`<tag>`가 baseline이 아닐 때)
   ```bash
   python3 .claude/skills/bench/scripts/compare.py <vs 요약 CSV> <tag 요약 CSV> \
     --key <key> --ignore <ignore_cols 쉼표> --labels <vs>,<tag> --out <results>/compare_<tag>_vs_<vs>.md
   ```
5. **보고**
   - 전체 지표 변화와 ⚠️가 붙은 행을 짧게 요약한다.
   - 나빠진 항목도 숨기지 않는다. 최종 보고서의 "한계·트레이드오프"에 쓸 재료다.
   - 원인은 결과 파일·로그에서 확인된 것만 말한다. 추정이면 "(추정)"을 붙인다.

## 하지 않는 것
- 대상 코드는 고치지 않는다. 측정만 한다.
- 측정 스크립트와 입력 세트를 Before 이후에 바꾸지 않는다. 바뀌면 Before와 비교할 수 없다(바꿔야 하면 baseline을 다시 재고 그 사실을 기록한다).
- 커밋하지 않는다.
