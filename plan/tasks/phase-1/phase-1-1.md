# Phase 1.1: FalkorDB 설치 및 실행

## 📋 Sub-task 개요

Docker를 사용하여 FalkorDB를 설치하고 실행합니다. FalkorDB는 그래프 데이터베이스로, 프로젝트의 핵심 데이터 저장소입니다.

### 파일 경로
**해당 없음** (Docker 명령어 실행)

### Phase 전체 목표 기여
- Phase 7의 Graph DB 저장을 위한 데이터베이스 환경 구축
- Phase 8의 질의 응답 시스템을 위한 그래프 데이터베이스 준비

### 입력 데이터
- **Docker**: Docker가 설치되어 있어야 함
- **포트**: 6379, 3000 포트가 사용 가능해야 함

### 출력 데이터
- **실행 중인 Docker 컨테이너**: `falkordb` 컨테이너
- **FalkorDB 서비스**: 포트 6379에서 접근 가능한 그래프 데이터베이스
- **FalkorDB Browser**: 포트 3000에서 접근 가능한 웹 UI

### Class 구조
**해당 없음** (Docker 명령어 실행)

## 🎯 주요 기능

1. **Docker 이미지 다운로드**
   - `falkordb/falkordb:latest` 이미지 자동 다운로드

2. **컨테이너 실행**
   - 백그라운드 모드로 실행 (`-d`)
   - 포트 매핑 설정

3. **컨테이너 관리**
   - 상태 확인
   - 로그 확인
   - 중지/재시작

## 📊 데이터 구조

### Docker 컨테이너 설정
- **컨테이너 이름**: `falkordb`
- **이미지**: `falkordb/falkordb:latest`
- **포트 매핑**:
  - `6379:6379`: FalkorDB Redis 프로토콜 포트
  - `3000:3000`: FalkorDB Browser 포트

## 💻 코드 예시 및 전체 코드 구현

### Docker 명령어

```bash
# FalkorDB 컨테이너 실행
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  falkordb/falkordb:latest
```

### 컨테이너 관리 명령어

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs falkordb

# 컨테이너 중지
docker stop falkordb

# 컨테이너 재시작
docker start falkordb

# 컨테이너 제거
docker rm falkordb
```

### 포트 설명
- **6379**: FalkorDB Redis 프로토콜 포트 (데이터베이스 연결)
- **3000**: FalkorDB Browser 포트 (웹 UI)

## 🔄 상세 알고리즘/프로세스

### 설치 및 실행 프로세스
1. **Docker 확인**
   - Docker가 설치되어 있는지 확인
   - `docker --version` 명령어로 확인

2. **포트 확인**
   - 포트 6379와 3000이 사용 가능한지 확인
   - `netstat` 또는 `lsof` 명령어로 확인

3. **컨테이너 실행**
   - `docker run` 명령어로 컨테이너 생성 및 실행
   - 백그라운드 모드로 실행 (`-d`)

4. **상태 확인**
   - `docker ps`로 컨테이너 실행 상태 확인
   - `docker logs falkordb`로 로그 확인

### 예외 처리
- 컨테이너 이름 중복: 기존 컨테이너 제거 후 재실행
- 포트 충돌: 다른 포트로 매핑 또는 기존 프로세스 종료

## ⚙️ 설정 및 의존성

### 필요한 환경 변수
- 없음

### 외부 라이브러리 의존성
- **Docker**: Docker Engine 설치 필요

### 설정 파일
- 없음

## 🧪 테스트 케이스

### 단위 테스트 예시
```bash
# 컨테이너 실행 확인
docker ps | grep falkordb

# 포트 확인
netstat -an | grep 6379
netstat -an | grep 3000

# 연결 테스트
redis-cli -h localhost -p 6379 ping
```

### 통합 테스트 시나리오
- 컨테이너 실행 후 FalkorDB 연결 테스트
- 웹 UI 접근 테스트 (http://localhost:3000)
- 컨테이너 재시작 후 데이터 유지 확인

### 검증 방법
- `docker ps`로 컨테이너 실행 상태 확인
- `docker logs falkordb`로 에러 로그 확인
- 웹 브라우저에서 `http://localhost:3000` 접근 확인

## ⚠️ 주의사항

- Docker가 설치되어 있어야 합니다
- 포트 6379와 3000이 사용 가능해야 합니다
- 컨테이너 이름 `falkordb`가 이미 존재하면 오류가 발생할 수 있습니다
- 컨테이너를 제거하면 데이터가 삭제될 수 있습니다 (볼륨 마운트 고려)

## 📝 History

