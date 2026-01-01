# Phase 1.1: FalkorDB 설치 및 실행

## 📋 개요

Docker를 사용하여 FalkorDB를 설치하고 실행합니다. FalkorDB는 그래프 데이터베이스로, 프로젝트의 핵심 데이터 저장소입니다.

## 🎯 목표

- FalkorDB Docker 이미지 다운로드
- Docker 컨테이너 실행
- 포트 매핑 설정 (6379, 3000)
- 컨테이너 상태 확인

## 📝 상세 구현

### Docker 명령어

```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  falkordb/falkordb:latest
```

### 포트 설명

- **6379**: FalkorDB Redis 프로토콜 포트 (데이터베이스 연결)
- **3000**: FalkorDB Browser 포트 (웹 UI)

### 컨테이너 확인

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs falkordb

# 컨테이너 중지
docker stop falkordb

# 컨테이너 재시작
docker start falkordb
```

## ⚠️ 주의사항

- Docker가 설치되어 있어야 합니다
- 포트 6379와 3000이 사용 가능해야 합니다
- 컨테이너 이름 `falkordb`가 이미 존재하면 오류가 발생할 수 있습니다

## 📝 History

