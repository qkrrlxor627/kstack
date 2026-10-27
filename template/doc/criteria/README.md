# 평가 가이드 넣는 곳

| 파일 | 넣을 것 | 예 |
|---|---|---|
| `mission.md` | **최종 산출물이 갖춰야 할 것** (발표·보고서 목차, 필수/선택 항목, 시간·분량 제한) | 과제 공지, 발표 안내, 제출 요건 |
| `standard.md` | **판정할 때 쓰는 기술·개념 기준** (단원·장별로 번호가 있으면 가장 좋다) | 교안 정리, 코딩 컨벤션, 아키텍처 가이드, 채점표 |
| `ids.md` | (직접 쓰지 않는다) `/kstack-setup`이 위 두 파일로 만드는 C/K ID 표 | — |

- PDF·PPT라면 텍스트로 옮겨 Markdown으로 넣는다. 쪽수를 `(p.N)`로 남겨 두면 판정 근거로 쓸 수 있다.
- 기준이 하나뿐이면 `standard.md`만 넣고 `mission.md`에는 "산출물 요건 없음"이라고 한 줄 쓴다.
- 넣은 뒤에는 원본이다. Claude는 이 두 파일을 고칠 수 없다(`settings.json` deny + `protect_files` hook).
- 파일 이름을 바꾸려면 `.claude/kstack.json`의 `criteria`·`protected`와 `.claude/settings.json`의 `permissions.deny`를 같이 바꾼다(`/kstack-setup`이 맞춰 준다).
