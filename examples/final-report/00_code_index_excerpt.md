# 최종 코드 위치 색인 (HEAD 기준, 자동 생성)

- 각 단계 문서(03~09)의 `file:줄`은 **그 단계 커밋 당시** 줄 번호다. 뒤 단계에서 코드가 추가되면 줄이 밀린다.
- 지금 코드에서 위치를 찾을 때는 이 표를 쓴다. 표는 코드의 `[Px BEFORE]` / `[Px AFTER]` 주석을 grep해서 만들었다.
- 직접 찾기: `grep -n "\[P1 " agent/*.py server.py web_chat.html`
- 단계 당시 코드 보기: `git show <커밋>:agent/graph.py | sed -n '120,140p'`

| 문제 | 구분 | 위치 | 주석 내용 |
|---|---|---|---|
| P1 | BEFORE | `agent/graph.py:41` | [P1 BEFORE] 여러 시스템이 나와도 '첫 번째 1개'만 MCP Prompt에 넘김 ── |
| P1·#14 | AFTER | `agent/graph.py:46` | [P1·#14 AFTER] 공통 모듈에서 가져온다 (agent/systems.py) ── |
| P1 | AFTER | `agent/graph.py:52` | """[P1 AFTER] MCP Prompt의 system_name에 질문에 나온 시스템 '전부'를 쉼표로 넘긴다. |
| P1 | BEFORE | `agent/ollama_llm.py:246` | [P1 BEFORE] 목록에 없는 target을 '질문의 첫 시스템'으로 바꿔 버림 → 같은 시스템이 중복돼 제거되고 나머지는 사라짐 ── |
| P1 | AFTER | `agent/ollama_llm.py:250` | [P1 AFTER] 모르는 이름은 버린다. 질문에 나온 시스템은 아래 '누락 보충'이 다시 채운다 ── |
| P1 | BEFORE | `agent/ollama_llm.py:264` | [P1 BEFORE] research가 '0개'일 때만 보충 → 모델이 1개만 내면 나머지 시스템은 조사 누락 ── |
| P1 | AFTER | `agent/ollama_llm.py:274` | [P1 AFTER] 모델이 몇 개를 내든, 질문에 나온 시스템 중 빠진 것을 '항상' 보충한다 ── |
| P1 | BEFORE | `agent/openai_llm.py:181` | [P1 BEFORE] 목록에 없는 target을 '질문의 첫 시스템'으로 바꿔 버림 → 같은 시스템이 중복돼 제거되고 나머지는 사라짐 ── |
| P1 | AFTER | `agent/openai_llm.py:185` | [P1 AFTER] 모르는 이름은 버린다. 질문에 나온 시스템은 아래 '누락 보충'이 다시 채운다 ── |
| P1 | BEFORE | `agent/openai_llm.py:199` | [P1 BEFORE] research가 '0개'일 때만 보충 → 모델이 1개만 내면 나머지 시스템은 조사 누락 ── |
| P1 | AFTER | `agent/openai_llm.py:209` | [P1 AFTER] 모델이 몇 개를 내든, 질문에 나온 시스템 중 빠진 것을 '항상' 보충한다 ── |
| P1·#14 | AFTER | `agent/systems.py:1` | """[P1·#14 AFTER] 시스템 이름 추출 공통 모듈. |
| #14 | BEFORE | `agent/graph.py:29` | [#14 BEFORE] ollama_llm.py·openai_llm.py와 똑같은 복사본 ── |
| #14 | BEFORE | `agent/ollama_llm.py:36` | [#14 BEFORE] graph.py·ollama_llm.py·openai_llm.py에 똑같이 복사돼 있던 시스템 추출 로직 ── |
| #14 | AFTER | `agent/ollama_llm.py:70` | [#14 AFTER] 공통 모듈 agent/systems.py 하나로 모았다 (K14 모듈화) ── |
| #14 | BEFORE | `agent/openai_llm.py:32` | [#14 BEFORE] graph.py·ollama_llm.py·openai_llm.py에 똑같이 복사돼 있던 시스템 추출 로직 ── |
| #14 | AFTER | `agent/openai_llm.py:64` | [#14 AFTER] 공통 모듈 agent/systems.py 하나로 모았다 (K14 모듈화) ── |
| P2 | AFTER | `agent/fake_llm.py:123` | notes = [c["data"] for c in collected if c["source"] == "note"]   # [P2 AFTER] 이상 없음/감시 대상 아님 |
| P2 | BEFORE | `agent/graph.py:291` | [P2 BEFORE] 모든 시스템의 알림을 한 문자열로 합친 뒤 규칙을 위에서부터 검사 ── |
| P2 | AFTER | `agent/graph.py:303` | [P2 AFTER] 시스템을 '하나씩', 질문에 나온 순서대로 본다 (K8 근거 기반 분류) ── |
| P2 | AFTER | `agent/graph.py:350` | [P2 AFTER] 분류 근거가 없으면(None) runbook gap task를 만들지 않고 그대로 진행 ── |
| P2 | AFTER | `agent/ollama_llm.py:283` | [P2 AFTER] 감시 대상이 아닌 시스템만 나온 질문(q08 billing-service)은 조사하지 않는다 ── |
| P2 | AFTER | `agent/ollama_llm.py:336` | elif c["source"] == "note":   # [P2 AFTER] runbook을 붙이지 않은 이유 (graph._no_runbook_note) |
| P2 | AFTER | `agent/openai_llm.py:218` | [P2 AFTER] 감시 대상이 아닌 시스템만 나온 질문(q08 billing-service)은 조사하지 않는다 ── |
| P2 | AFTER | `agent/openai_llm.py:281` | elif c["source"] == "note":   # [P2 AFTER] runbook을 붙이지 않은 이유 (graph._no_runbook_note) |
| P3 | BEFORE | `agent/graph.py:176` | [P3 BEFORE] 모델의 needs_analysis 판단만 믿음 → 0.6b 모델은 거의 항상 true (incident 8종 중 7종에서 분석 실행) ── |
| P3 | AFTER | `agent/graph.py:182` | [P3 AFTER] 이중 게이트 (K7 권위 게이트) ── |
| P4 | AFTER | `agent/fake_llm.py:35` | [P4 AFTER] 실모델 백엔드와 인터페이스를 맞추려고 route·plan·analyze를 async def로 바꿨다 |
| P4 | BEFORE | `agent/graph.py:161` | [P4 BEFORE] result, usage = deps.fast_llm.plan(state["query"], procedure) |
| P4 | AFTER | `agent/graph.py:162` | result, usage = await deps.fast_llm.plan(state["query"], procedure)   # [P4 AFTER] |
| P4 | BEFORE | `agent/graph.py:376` | [P4 BEFORE] summary, usage = deps.fast_llm.analyze(state.get("collected", [])) |
