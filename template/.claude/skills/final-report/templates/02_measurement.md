# 측정 방법 — 무엇을, 어떻게 쟀나

## 1. 입력 세트
| 항목 | 값 |
|---|---|
| 파일 | `<입력 세트 경로>` (Before 이후 변경 없음) |
| 개수 / 반복 | N개 × R회 |
| 구성 | <유형별 개수> |

## 2. 조건 (Before와 After가 같아야 하는 것)
| 조건 | Before | After |
|---|---|---|
| 모델/환경 | | |
| 측정 명령 | `<bench.run_cmd>` | 같음 |

## 3. 지표 정의
| 지표 | 정의 | 계산 위치 | 왜 이 지표인가 (C ID) |
|---|---|---|---|
| | | `파일:함수` | |

## 4. 결과 파일
| tag | 요약 | 비교 |
|---|---|---|
| baseline | `<results>/baseline_summary.csv` | — |
| after | `<results>/after_summary.csv` | `<results>/compare_after_vs_baseline.md` |

## 5. 재현
```bash
<health_cmd>
<run_cmd with tag>
python3 .claude/skills/bench/scripts/compare.py <before.csv> <after.csv> --key <key>
```

## 6. 측정의 한계
- <표본 수, 비결정성, 환경 차이 등>
