# UVX 서비스 등록 가이드

이 문서는 MongoDB MCP 서버를 UVX 서비스 관리자에 등록하고 관리하는 방법을 설명합니다.

## 사전 요구사항

- UVX 설치됨 (`npm install -g uvx` 또는 관련 패키지 매니저 사용)
- Python 3.12 이상 설치됨
- 필요한 Python 패키지 설치됨 (`pip install -r requirements.txt`)

## UVX 서비스 등록하기

### 자동 등록 (권장)

프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다:

```bash
# 스크립트에 실행 권한 부여
chmod +x uvx-register.sh

# 스크립트 실행
./uvx-register.sh
```

스크립트는 다음을 수행합니다:
1. UVX가 설치되어 있는지 확인
2. MongoDB URL 입력 요청 (기본값: mongodb://localhost:27017/admin)
3. 서비스 포트 입력 요청 (기본값: 3000)
4. UVX 서비스 구성파일 생성 및 등록
5. 서비스 등록 후 시작 여부 확인

### 수동 등록

1. UVX 서비스 구성 파일 생성:

```yaml
name: mongo-mcp
description: MongoDB MCP Server for AI Agents
command: uvicorn
args:
  - app.main:app
  - --host
  - 0.0.0.0
  - --port
  - 3000
cwd: /path/to/mongo-mcp-server
env:
  MONGODB_URL: mongodb://username:password@hostname:port/dbname?authSource=admin
  PORT: 3000
  PYTHONPATH: /path/to/mongo-mcp-server
  TZ: Asia/Seoul
tags:
  - mongodb
  - mcp
  - database
  - ai
```

2. UVX에 서비스 등록:

```bash
uvx register --file your-service-file.yml
```

## UVX 서비스 관리

### 기본 명령어

- **서비스 시작**: `uvx start mongo-mcp`
- **서비스 중지**: `uvx stop mongo-mcp`
- **서비스 재시작**: `uvx restart mongo-mcp`
- **서비스 상태 확인**: `uvx status mongo-mcp`
- **서비스 로그 보기**: `uvx logs mongo-mcp`
- **등록된 모든 서비스 보기**: `uvx list`

### 직접 실행 명령어

- **기본 실행**: `uvx mongo-mcp-server`
- **SSE 모드 실행**: `uvx mongo-mcp-server --transport=sse`
- **MongoDB URL 지정**: `uvx mongo-mcp-server --mongodb-url="mongodb://user:pass@host:port/db"`

### 서비스 자동 시작 설정

UVX 서비스를 시스템 부팅 시 자동으로 시작하도록 설정:

```bash
uvx enable mongo-mcp
```

자동 시작 비활성화:

```bash
uvx disable mongo-mcp
```

## 문제 해결

### 서비스가 시작되지 않는 경우

로그를 확인합니다:

```bash
uvx logs mongo-mcp
```

### 서비스가 충돌하는 경우

다른 포트를 사용하도록 서비스를 수정합니다:

1. 서비스 중지: `uvx stop mongo-mcp`
2. 서비스 삭제: `uvx unregister mongo-mcp`
3. 다른 포트로 재등록: `./uvx-register.sh` (다른 포트 입력)

### UVX 서비스 완전 제거

```bash
uvx unregister mongo-mcp
```

## AI 어시스턴트 연동

UVX를 통해 MongoDB MCP 서버를 AI 어시스턴트와 연동하려면:

1. 서비스가 실행 중인지 확인: `uvx status mongo-mcp`
2. AI 구성 파일에 MCP 엔드포인트 추가:

```json
{
  "mcp": {
    "servers": {
      "mongodb": {
        "url": "http://localhost:3000/mcp"
      }
    }
  }
}
```

3. AI 어시스턴트에서 다음과 같이 접근:
   - listCollections: 컬렉션 목록 조회
   - find: 문서 검색 및 필터링

## 관련 문서

- [UVX 공식 문서](https://github.com/uvx-js)
- [MongoDB MCP 서버 README](./README.md)
