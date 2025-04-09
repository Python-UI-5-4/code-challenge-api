# 🚀 Devolt 코드 채점 API 서버

**Devolt 채점 시스템의 MSA 기반 API 서버입니다.**  
Spring Boot 백엔드와 채점 워커를 중개하며, 코드 채점 요청을 Redis 태스크 큐에 등록하고 결과를 반환합니다.

<br /><br />




## 🧱 채점 요청/응답 처리 구조
### 채점 등록/실행/중단 요청
```
End User -> Spring Boot Backend -> Flask API Server -> Redis -> Celery Worker
```
- 채점 실행/중단 요청은 WebHook 방식을 통해 비동기적으로 처리됩니다.
<br />

### 채점 실행 결과 응답
```
Celery Worker -> Spring Boot Backend -> End User
```
- 채점 실행 결과는 다음과 같은 순서로 전달되며, WebHook 콜백 방식을 사용합니다.
- 엔드 유저는 구독 중인 SSE 세션을 통해 결과를 전달 받습니다.

<br /><br />




## ✨ 주요 기능

- REST API 엔드포인트 제공
- 코드 채점 요청 처리 및 검증
- Redis 태스크 큐에 작업 등록
- 채점 결과 웹훅 콜백 처리
- HMAC 기반 API 키 인증
