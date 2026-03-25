<!-- Context: project-intelligence/decisions | Priority: high | Version: 1.1 | Updated: 2026-03-25 -->

# Decisions Log

**Purpose**: 왜 지금의 구조와 규칙을 유지하는지 빠르게 이해하기 위한 의사결정 기록.
**Last Updated**: 2026-03-25

## Quick Reference
- **Most Important**: 헥사고날 아키텍처 + 유스케이스 중심 구조 유지
- **Auth Direction**: 학교 연동 + 쿠키 기반 인증 + refresh token 저장소 분리
- **Domain Rule**: 도메인 의미가 있는 규칙은 `core/`가 아니라 각 도메인에 둔다
- **Update When**: 구조 변경, 인증 방식 변경, 도메인 경계 재설정

## Decision: 헥사고날 아키텍처와 유스케이스 중심 구조 유지
**Date**: 2026-03-25
**Status**: Decided
**Priority**: Highest

**Context**: 이 프로젝트는 향후 AI 평가, 리포트, 시험 응시, 강의실 운영이 함께 커질 가능성이 높다. 기능이 늘어나도 인증, 조직, 강의실, 자료, 평가 규칙이 한곳에 뒤섞이지 않도록 구조적 기준이 필요했다.

**Decision**: `app/<domain>/domain`, `application`, `adapter` 경계를 유지하고, 서비스는 유스케이스 단위로 작게 나눈다. 라우터는 입력/응답 변환에 집중하고 비즈니스 규칙은 유스케이스와 도메인 계층이 맡는다.

**Rationale**:
- 운영 기반과 AI 평가 확장을 분리할 수 있다.
- 테스트 단위를 유스케이스 기준으로 명확하게 유지할 수 있다.
- 라우터, ORM, 외부 연동이 바뀌어도 핵심 규칙의 영향 범위를 줄일 수 있다.

**Trade-off**: 초기엔 파일 수와 계층 수가 늘어나 단순 CRUD보다 무겁게 느껴질 수 있다. 대신 장기적으로 변경 비용과 규칙 누수를 줄인다.

## Decision: 라우터는 얇게 유지하고 규칙은 서비스/도메인에 둔다
**Date**: 2026-03-25
**Status**: Decided

**Context**: 권한, 조직 스코프, 강의실 소유권 같은 규칙이 라우터에 흩어지면 재사용이 어렵고 누락 위험이 커진다.

**Decision**: 라우터는 `Request -> Command -> UseCase -> Response` 흐름만 담당한다. helper 함수는 최소화하고, 자원/역할/조직 규칙은 서비스와 도메인 계층에서 재검증한다.

**Rationale**:
- 같은 규칙을 API, 배치, 다른 입력 채널에서 재사용할 수 있다.
- 테스트가 HTTP 레이어에 묶이지 않는다.
- 인증 이후에도 리소스 단위 접근 제어를 안전하게 다시 확인할 수 있다.

**Trade-off**: 서비스 코드가 더 중요해지고 설계 품질 요구가 높아진다. 대신 라우터 비대화와 규칙 중복을 막는다.

## Decision: 학교 연동 인증 + 쿠키 기반 인증을 채택한다
**Date**: 2026-03-25
**Status**: Decided

**Context**: 이 플랫폼은 대학 운영 맥락 안에서 학생과 교수/관리자를 구분해야 하며, 실제 학교 시스템과 연결되는 인증 흐름이 필요하다.

**Decision**: 조직 단위 로그인 흐름을 유지하고, access token은 쿠키로 전달한다. refresh token은 별도 저장소에 보관해 회전과 무효화를 관리한다.

**Rationale**:
- 학교 소속과 역할을 로그인 시점에 확정할 수 있다.
- 웹 기반 서비스에서 일관된 인증 UX를 제공한다.
- 로그아웃, 재발급, 토큰 무효화 흐름을 통제할 수 있다.

**Trade-off**: 외부 학교 시스템 의존성과 쿠키 보안 설정 관리가 필요하다. 대신 실제 교육 운영 시나리오와 잘 맞는다.

## Decision: 도메인 의미가 있는 공통 로직은 `core/`에 두지 않는다
**Date**: 2026-03-25
**Status**: Decided

**Context**: 강의실 접근, 자료 공개 범위, 조직 스코프 같은 규칙은 여러 곳에서 재사용될 수 있지만, 단순 기술 유틸은 아니다.

**Decision**: 재사용되더라도 교육 도메인 의미가 있으면 해당 도메인 서비스/모델에 남긴다. `core/`는 프레임워크, 세션, 공통 예외, 인증 인프라 같은 기술 기반에만 사용한다.

**Rationale**:
- 정책 변경이 생겼을 때 영향 지점을 쉽게 추적할 수 있다.
- 도메인 규칙이 기술 유틸처럼 추상화되어 의미를 잃는 것을 막는다.
- 프로젝트가 템플릿으로 재사용될 때도 비즈니스 규칙이 `core/`에 섞이지 않는다.

**Trade-off**: 비슷해 보이는 로직이 각 도메인에 나뉠 수 있다. 대신 규칙의 소유권이 분명해진다.

## Current Watch Items
- AI 심층 평가 엔진이 추가될 때도 현재 도메인 경계를 유지할 수 있는지 검토 필요
- 한성대 연동 외 다른 학교 시스템 확장 시 인증 추상화 수준 재검토 필요
- 시험/리포트 도메인 추가 시 유스케이스 수 증가에 따른 탐색성 유지 필요

## 📂 Codebase References
- `main.py` - 앱 조립과 현재 아키텍처 진입점
- `app/container.py` - 도메인별 컨테이너와 유스케이스 wiring
- `app/user/adapter/input/api/v1/user.py` - 얇은 라우터 + 응답 매핑 패턴
- `app/user/application/service/user.py` - 유스케이스 중심 서비스 구조
- `app/classroom/application/service/classroom.py` - 서비스 계층의 조직/권한/소유권 규칙
- `app/classroom_material/application/service/classroom_material.py` - 도메인 의미가 있는 접근 규칙 배치 예시
- `app/auth/application/service/auth.py` - 학교 연동 로그인과 refresh token 관리
- `app/organization/adapter/output/integration/hansung.py` - 외부 학교 시스템 연동 근거
- `core/fastapi/dependencies/permission.py` - 공통 인증/인가 인프라와 도메인 규칙의 경계

## Related Files
- `technical-domain.md` - 현재 구현 패턴과 보안/테스트 규칙
- `business-domain.md` - 제품 목표와 사용자 맥락
- `business-tech-bridge.md` - 제품 요구가 왜 현재 구조로 연결되는지 설명
