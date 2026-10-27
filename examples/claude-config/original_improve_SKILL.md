---
name: improve
description: 미션(doc/mission_k.md)과 수업 기준표(doc/lessonstandard_k.md)를 근거로 개선안 문서를 설계한다
argument-hint: [버전] [집중할 기준ID(선택)]
disable-model-invocation: true
---

# /improve — 미션 + 교안 기준 → 개선안 문서

인자: `$ARGUMENTS`
- 첫 단어: 버전. 없으면 오늘 날짜(YYYY-MM-DD)를 쓴다.
- 두 번째 이후: 집중할 C/K ID.

## 입력 문서 (읽기 전용, 절대 수정 금지)
- 미션: `doc/mission_k.md`
- 기준표: `doc/lessonstandard_k.md` (2,000줄 이상이므로 나눠서 끝까지 읽는다)
- 참고:
  - `bench/results/before.md`: Before 측정. 수치는 여기서만 인용한다
  - `doc/presentation_k.md`
  - `doc/guide.md`
  - `doc/workLog.md`
  - `doc/README.md`

## 절차
1. 미션과 기준표를 끝까지 읽는다.
2. 체크리스트를 만든다(ID / 기준 / 충족 판단 방법).
   - C ID = 미션 항목
     - C1 주제, C2 개선 사항, C3 기술 요소·캡처, C4 전후 수치(선택), C5 한계·트레이드오프
     - C3 세부 기술: C3-a Multi-Agent, C3-b MCP, C3-c RAG, C3-d 의존성 주입, C3-e LangSmith, C3-f 모듈화, C3-g 단위 테스트
     - 캡처: C3-h 구현 기능 캡처, C3-i 최종 실행 캡처
   - K ID = 교안 단원 번호 그대로
     - K1 ADR, K2 FastAPI, K3 MCP, K4 SSE-Backend, K5 SSE-Frontend(Vue)
     - K6 Multi-agent, K7 Routing, K8 Dynamic Planning, K9 Validator, K10 Error Handling
     - K11 Cost, K12 동시 실행, K13 Session, K14 Modularization, K15 Observability & Eval
3. 코드(`server.py`, `agent/`, `mcp_server*.py`, `web_chat.html`, `sh/`)와 참고 자료를 조사해 ID별 현황을 판정한다.
   - 판정은 충족 / 부분 / 미충족 중 하나이고, 근거 파일 경로(가능하면 함수명)를 붙인다.
   - 확인하지 못한 항목은 "미확인"으로 쓴다.
   - 없다고 알려진 것도 실제로 다시 확인한다:
     - 벡터 RAG: runbook은 코드 규칙으로 고른 뒤 MCP Resource로 넣는다
     - 단위 테스트: `tests/`
     - ADR: `adr/`
     - After 수치
     - 최신 캡처: `doc/image_usecase/`는 qwen2.5 시절 캡처다
4. 부분·미충족 항목마다 개선안을 쓴다.
   - 순서: 문제 → 근거 K ID → 변경 내용(파일/함수) → 기대 효과 → 우선순위(영향×난이도)
   - 발표가 5분이라는 점과 마감 전에 할 수 있는지를 우선순위에 반영한다.
   - `bench/results/before.md`의 3-1~3-6을 후보로 반드시 검토한다.
     - 3-1: 여러 시스템 중 1개만 조사
     - 3-3: analysis 남발
     - 3-6: validate가 형식만 검사
5. 같은 폴더의 `template.md` 양식으로 `outputs/improvement-<버전>.md`를 작성한다. 집중 ID가 있으면 그 항목을 깊게 쓴다.
6. `rubric-reviewer` 서브에이전트로 검토받고, FAIL 항목을 고쳐 최종본을 저장한다.
7. 끝에 "사람이 결정해야 할 질문" 목록을 출력한다.

## 규칙
- 산출물은 `outputs/`에만 쓴다. 다른 파일은 수정하지 않는다.
- 미션과 기준표가 충돌하면 임의로 정하지 말고 질문한다. 예: 미션은 RAG를 요구하지만 교안 단원에는 RAG가 없다.
- 근거 없는 수치나 사실을 만들지 않는다. 수치에는 출처 파일 경로를 붙인다.
- 커밋은 하지 않는다. 커밋을 안내할 때 Claude 공동 작성자 표기를 넣지 않는다.
