# AXIMO 아키텍처 v0 (Single Source of Truth)

## 1) 고객 문제 정의 (Non-negotiable)
- 직원 문제로 지친 중소기업 대표가 핵심 고객이다.
- 사용자는 '설정/학습' 자체를 원하지 않는다: "이거 좀 해 봐", "왜 안돼?" 수준의 요청만 하길 원한다.
- Notion/Monday 실패 이유는 사용자가 '시스템 설계자' 역할을 떠안아야 하기 때문이다.

## 2) AXIMO의 한 문장 정의
- AXIMO는 "AI SaaS"가 아니라 "AI 직원 임대(Workforce Infrastructure)"다.

## 3) 포지셔닝
- Notion/Monday/OpenClaw/Workgroup은 사용자가 구조를 구성해야 하는 툴에 가깝다.
- AXIMO는 사용자가 말하면 업무 구조가 생성되고 실행되는 '직원형 인터페이스'를 제공한다.

## 4) 시스템 철학 (3-layer Interface)
- Create: Web UI 중심, 텍스트 + 선택형 UI + 다이어그램(ComfyUI 스타일) 옵션 제공.
- Operate: 메신저(텍스트) 우선, 이후 Voice(전화/미팅)로 점진 확장.
- Presence: Vivido Avatar는 Phase3의 '마지막 1인치' 인터페이스로 적용.

## 5) 아키텍처 원칙 (Guardrails)
- 모든 외부 발송/예약/인보이스는 승인 기반으로만 실행한다.
- 감사 로그(Audit Log)는 필수이며 모든 주요 의사결정/실행을 추적 가능해야 한다.
- 회사별 메모리는 강하게 격리한다.
- 글로벌 인사이트는 익명 집계/정책 기반으로만 활용하며, 명시적 동의를 전제로 한다.

## 6) Core Components (Brain)
- Control Plane API
- Role Builder: 전자상거래 옵션을 내부 스킬 번들+설정으로 컴파일한다.
- Skill Registry: OpenClaw skills + AXIMO-native skill format을 수용한다.
- Deterministic Router + Approval Gate
- Memory Store
- Audit Log
- Channel Adapters: Web / Messenger / Voice / Avatar

## 7) Multi-Agent 운영 (내부는 조직, 외부는 1명 Persona)
- Core Trio(고정): Planner / Executor / Critic-Risk
- Dynamic Specialist(조건부 최대 1): 전략/분석/보고에만 참여, 실행 금지, 옵션+근거+리스크만 반환.
- Execution은 Deterministic, Strategy는 Deliberative 원칙을 적용한다.

## 8) 대표 시나리오: Deal Execution Role (1~8 단계 매핑)
- 1) 이메일 인입: 고객 커뮤니케이션이 유입되면 업무 트리거를 생성한다.
- 2) 고객 구조화(DB/KB): 고객 정보/히스토리/제약조건을 구조화해 메모리에 저장한다.
- 3) 발주서 초안: 역할 기반 템플릿으로 초안을 작성한다.
- 4) 네고/수정: 변경 요청을 반영해 버전 관리하며 리스크를 표기한다.
- 5) 전략 리포트: 대안, 근거, 리스크를 요약한 의사결정 자료를 생성한다.
- 6) 승인: 외부 실행 전 대표 승인 게이트를 통과해야 한다.
- 7) 고객 커뮤니케이션/미팅/인보이스: 승인된 액션만 외부 채널로 실행한다.
- 8) 사후 기록: 실행 결과를 감사 로그/메모리에 동기화한다.

## 9) MVP-0 (이번 주 구현 대상: 최소 기능)
- Web에서 텍스트 명령 입력 → Intent 파악 → Admin Employee 결과 생성.
- 승인 게이트: 발송/예약은 승인 없이는 불가.
- Linear Daily Brief 자동 게시/상태 업데이트는 운영 기능으로 유지.

## 10) Phase Roadmap
- Phase1: Web Create + Messenger Operate(텍스트)
- Phase2: Voice Operate(콜/미팅)
- Phase3: Vivido Presence(Avatar)
