# AI Capstone — 단원별 개발 기준 정리

> 원본: AI캠퍼스_AI_Capstone_20261016.pdf (SK AX, 2026.10, 253p)
> 쪽수 표기는 PDF 페이지 기준 (p.N). 슬라이드 하단 인쇄 번호는 PDF 페이지 − 1.
> 출처 꼬리표: (p.N) = 교안 해당 쪽 / (추론) = 교안 코드·내용에서 끌어낸 판단 / (일반 지식)·(문서 외) = 교안 밖 내용
> 교안 시나리오: 가상의 "장애 진단 Agent" — React(Next.js) ↔ FastAPI ↔ LangGraph(Supervisor), MCP 서버, LangSmith
> 우리 프런트는 Vue라서 5단원은 Vue 기준으로 옮겨 정리함 (React 전용 내용 제외)

## 한눈에 보기

| 단원 | 질문 | 답안 한 줄 |
|---|---|---|
| 1. ADR | 구조를 왜 이렇게 정했는지 어떻게 남길까 | 대안이 있었던 결정만 배경→결정→대안 비교→결과→재검토 조건 틀로 `adr/NNNN-*.md`에 |
| 2. FastAPI 통합 | 비싼 객체는 언제 몇 번 만들고 입출력은 어디서 막을까 | lifespan에서 Agent 1회 생성(싱글턴), Pydantic BaseModel로 422 차단, `--reload`(개발)/`--workers`(운영) 분리 |
| 3. MCP Server | Agent와 도구를 표준으로 어떻게 이을까 | FastMCP로 Tool(동적)/Resource(정적 URI)/Prompt(표준 절차) 분리, subprocess+stdio, 검색도 Tool로 |
| 4. SSE-Backend | 토큰·도구 호출을 생기는 순간 보여줄 수 있을까 | `StreamingResponse` + `astream(stream_mode=["messages","updates"])` → ToolCallStart/End·Token·Done |
| 5. SSE-Frontend (Vue) | Backend 자체 SSE 이벤트를 Frontend가 어떻게 받아 그릴까 | `useChatStream` composable이 fetch로 직접 파싱(buffer→`\n\n` split→미완성 보관→`data:` 파싱), nginx 버퍼링 off, Zod + 공유 상수 |
| 6. Multi-agent | 복잡한 요청을 누가 조율할까 | Supervisor(planning→execute 반복→finalize) + ReAct sub-agent, 단일 `SupervisorState` |
| 7. Query Routing | 단순 질문도 전체 파이프라인을 태워야 할까 | `fast_llm` 라우팅 게이트(simple/complex) + 조건부 Analysis + 권위 게이트 + RoutingDecidedEvent 최우선 |
| 8. Dynamic Planning | research가 부족해도 그대로 진행할까 | `replan_check`(평가)·`replan`(행동) 분리, `MAX_REPLAN_ROUNDS=1`, 상한 넘으면 강제 진행 |
| 9. Validator | 저품질 응답도 그대로 내보낼까 | LLM-as-a-Judge 4기준 → 불합격 시 feedback 재작성(상한), Loop Guard 10회/60초 |
| 10. Error Handling | task 하나 실패하면 전체 실패일까 | 4-Layer + Graceful Degradation, `TimeoutError`만 `with_retry` 0.5s×3 backoff, 나머지 즉시 `ToolError` |
| 11. Cost Optimization | 작업마다 다른 모델을 쓸 수 있을까 | Routing·Planning=gpt-4o-mini, Research·Writing·Validator=gpt-4o (16,250→14,310), Spot+Bin-packing |
| 12. 동시 실행 | 독립 작업을 왜 하나씩 기다릴까 | `asyncio.gather` Fan-out/Fan-in(10.7s→6.4s) + 코루틴별 try/except 격리, 블로킹 금지, Semaphore |
| 13. Stateless Session | 대화 상태를 어디에 저장할까 | `AsyncPostgresSaver` + `create_checkpointer()` 팩토리 + lifespan 주입 |
| 14. Modularization | 수천 줄 파일과 전역 의존성을 어떻게 나눌까 | 역할별 모듈(패키지 하위), 의존성은 호출 인자로 주입, pytest + Mock |
| 15. Observability & Eval | 어디서 느린지·품질이 좋아졌는지 어떻게 알까 | 메트릭→트레이스→로그를 trace_id로 연결, LangSmith Run/Project/Dataset+evaluate()/Hub |

---

## 1. ADR (p.5–22)

**단원 질문** — 구조를 왜 이렇게 정했냐는 질문에 어떻게 답할 수 있게 남겨 둘까? (p.7)

### 답안

아키텍처 결정은 **ADR(Architecture Decision Record)** 로 남기면 된다. 대상은 **실제 대안이 있었고 트레이드오프를 저울질한 결정만**이다. 형식은 모든 ADR이 같다.

1. 배경
2. 결정
3. 대안 비교(장점·단점)
4. 결과/트레이드오프
5. 재검토 조건

이렇게 쓴 문서를 `adr/NNNN-제목.md` 파일 하나에 하나씩, 상태(Accepted)와 관련 모듈을 달아 둔다. 단순 버그 수정처럼 대안이 없는 결정은 남기지 않는다. (p.7, p.8)

```markdown
# ADR-0002: MCP Server를 독립 subprocess로 실행
- 상태: Accepted / 관련 모듈: M01, M02
## 배경 (Context) / ## 결정 (Decision)
## 대체 가능한 요소 (Alternatives Considered)   ← A/B/C 표, 채택안 ★
## 결과/트레이드오프 (Consequences) / ## 재검토 조건
```

### 답안을 위한 과정

1. **결정의 이유는 기록하지 않으면 사라진다.** 아키텍처 결정이 코드나 채팅에만 암묵적으로 남으면, 시간이 지나 "왜 이렇게 만들었는지" 아무도 설명하지 못한다. (p.7)
2. **이유가 사라지면 같은 논쟁이 되풀이된다.** 어떤 대안을 검토했고 왜 포기했는지가 남지 않으면, 같은 논쟁을 반복하거나 과거에 기각한 대안으로 되돌아간다. (p.7)
3. **그래서 "무엇을 골랐나"뿐 아니라 "무엇을 버렸나"까지 남겨야 한다.** 그래서 틀에 "대안 비교"가 반드시 들어간다. ADR-0002는 A 인프로세스 / B subprocess(채택) / C 원격 HTTP를 장점·단점과 함께 표로 남겼다. (p.7, p.8)
4. **모든 결정을 남기면 기록이 묻힌다.** 기준은 "실제 대안이 있었고 트레이드오프를 저울질했는가"다. MCP Server 프로세스 경계 선택(0002)은 작성하고, 단순 버그 수정(M15)은 제외한다. (p.7)
5. **틀이 같아야 나중에 찾아 쓸 수 있다.** 모든 결정을 "배경 → 결정 → 대안 비교 → 결과" 한 틀로 쓰면, 온보딩하거나 재검토할 때 근거를 바로 찾는다. (p.7)
6. **결정에는 유통기한을 적어 둔다.** "재검토 조건"이 있어야 언제 다시 열어볼지 알 수 있다. ADR-0002는 "여러 Backend가 하나의 MCP Server를 공유해야 할 때 C(원격)로 전환 검토"라고 적었다. "결과/트레이드오프"에는 감수한 비용을 적는다. 여기서는 "MCP 계층 수평 확장은 범위 밖"이다. (p.7, p.8)
7. **이 교안 전체가 그 틀로 쓰였다.** p.9–22의 14개 결정이 모두 같은 형식이다. 각 결정마다 A/B/C(/D) 대안, 예시 로그 2개, ✓/✗/△ 평가, "그래서 B로 간다"는 결론이 붙어 있다. 2~15단원의 트레이드오프 표가 이 비교에서 나온다. (p.9–22)

### 주요 코드

**① ADR 파일 — `adr/0002-mcp-server-as-subprocess.md`** (p.8, 교안 예시를 마크다운으로 옮김)
```markdown
# ADR-0002: MCP Server를 독립 subprocess로 실행
- 상태: Accepted                                  <!-- ← 결정의 현재 상태 -->
- 관련 모듈: M01 (Backend Integration Core), M02 (MCP Capability Server)   <!-- ← 영향받는 모듈 -->

## 배경 (Context)
MCP Server를 Backend와 어떤 프로세스/배포 경계로 연결할지 결정해야 했다.

## 결정 (Decision)
Backend가 MCP Server를 자식 subprocess로 직접 기동하고 stdio transport로 통신한다.

## 대체 가능한 요소 (Alternatives Considered)   <!-- ← ADR의 핵심: 버린 대안까지 남김 -->
| 대안 | 설명 | 장점 | 단점 |
|---|---|---|---|
| A. In-process 라이브러리 통합 | 별도 프로세스 없이 코드베이스에 직접 import | 오버헤드 없음 | MCP 표준 준수 목적 자체가 무의미해짐 |
| ★ B. Subprocess + stdio (채택) | 자식 프로세스로 실행, stdio로 통신 | 표준 client 재사용, 프로세스 격리 | 로컬 단일 머신 배포 전제 |
| C. 원격 HTTP/SSE MCP 서비스 | 별도 컨테이너/서버로 배포 | 독립 스케일링 | 이 규모엔 과설계 |

## 결과/트레이드오프 (Consequences)               <!-- ← 채택하면서 감수한 것 -->
서버 재시작 시 MCP subprocess도 함께 재시작되므로, MCP 계층 자체의 수평 확장은 범위 밖이다.

## 재검토 조건                                    <!-- ← 이 결정을 다시 열 시점 -->
여러 Backend 인스턴스가 하나의 MCP Server를 공유해야 하는 시점에는 C로 전환을 검토한다.
```

> 교안의 ADR 단원에는 프로그래밍 코드가 없습니다. 위는 교안이 보여 준 ADR 파일 형식(p.8)입니다.

### 주의사항 (교안)

> 이 단원에는 "필드 주의점" 슬라이드가 없어서, 본문에서 경고한 내용을 모았습니다.

- **대안이 없던 결정은 ADR로 쓰지 않는다.** 단순 버그 수정(M15)은 제외한다. 대안·트레이드오프가 있는 결정만 남긴다. (p.7)
- **결정만 쓰고 대안을 빼면 ADR의 목적이 사라진다.** "어떤 대안을 검토하고 왜 포기했는지"가 남지 않는 것이 ADR이 없을 때의 문제 그 자체다. (p.7)
- **재검토 조건을 비워 두지 않는다.** 교안 예시는 "언제 C로 전환할지"를 명시했다. (p.7, p.8)

### 대안별 트레이드오프

| 대안 | 장점 | 단점 | 이럴 때 | 판정 |
|---|---|---|---|---|
| 기록 없음 (코드·채팅에 암묵적으로) | 작성 비용 없음 (추론) | 시간이 지나면 이유를 아무도 설명 못함. 같은 논쟁 반복, 기각된 대안으로 회귀 (p.7) | — | ✗ |
| 모든 결정을 ADR로 | 빠짐없이 남음 (추론) | 대안이 없는 결정까지 쌓여 중요한 결정이 묻힘 (추론, p.7 판단 기준의 반대) | — | ✗ (p.7 기준상 제외 대상) |
| **대안이 있던 결정만, 고정 틀로 ADR (채택)** | 온보딩·재검토 때 근거를 바로 찾음. 버린 대안과 재검토 조건까지 남음 (p.7) | 결정마다 대안 비교를 정리하는 수고 (추론) | 프로세스 경계, 전송 방식, 저장소 선택처럼 되돌리기 비싼 결정 (p.8–22) | ✓ |
| 위키·Confluence 페이지로 관리 (문서 외) | 비개발자도 검색·열람 쉬움 (일반 지식) | 코드와 떨어져 있어 버전이 어긋나기 쉬움 (일반 지식) | 기획·운영 인원이 함께 보는 조직 (일반 지식) | — |
| 이슈·PR 본문에 결정 기록 (문서 외) | 변경과 결정이 한곳에 묶임 (일반 지식) | 여러 PR에 흩어져 결정 단위로 다시 찾기 어려움 (일반 지식) | 결정 하나가 PR 하나로 끝나는 작은 팀 (일반 지식) | — |

---

## 2. FastAPI 통합 (p.23–36)

**단원 질문** — Agent를 FastAPI 서버에 붙일 때, 비싼 객체는 언제 몇 번 만들고 입출력은 어디서 막을까? (p.25, p.26, p.31)

### 답안

