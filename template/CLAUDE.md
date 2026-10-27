## kstack 작업 규칙 — {{PROJECT}}
- 평가 가이드: 미션 `doc/criteria/mission.md` / 기준표 `doc/criteria/standard.md` (둘 다 수정 금지)
- ID 체계: `doc/criteria/ids.md` (C = 미션 항목, K = 기준표 단원). `/kstack-setup`으로 만들고 사람이 확인한다.
- 설정 한 곳: `.claude/kstack.json` (보호 파일, 테스트·측정 명령, 발표 시간)
- 개선안·보고서 산출물은 `outputs/`에만 쓴다. 수치는 측정 결과 폴더 등 실제 파일에서만 인용하고 출처 경로를 붙인다.
- 측정하지 않은 판단은 "(추정)"을 붙인다. 나빠진 지표도 숨기지 않는다.
- 모든 개선안은 C ID와 K ID에 매핑하고, 매핑되지 않는 것은 "기준 외 제안"으로 분리한다.
- 코드를 고칠 때 바뀐 곳에 `[P1 BEFORE]` / `[P1 AFTER]` 주석을 남긴다 (최종 코드 색인의 근거).
- 커밋·PR에 Claude 공동 작성자 표기를 넣지 않는다. 작성자는 항상 {{AUTHOR}}이다.
- Claude 구성(스킬·에이전트·hook·설정)을 추가/변경하면 `doc/workClaude.md`의 표와 변경 이력을 갱신한다.

## 작업 순서
`/kstack-setup` → `/improve v1` → `/bench baseline`(선택) → 코드 수정 → `/report-step P1` … → `/bench after` → `/final-report`
