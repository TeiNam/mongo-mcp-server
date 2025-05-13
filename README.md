# MongoDB MCP 서버

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-green.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.3.3-yellow.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4-orange.svg)
![Anthropic](https://img.shields.io/badge/Claude-3.7--Sonnet-purple.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

MongoDB 데이터베이스와의 원활한 상호작용을 표준화된 프로토콜로 제공하는 강력한 Model Context Protocol(MCP) 서버 구현체입니다.

## 작성자
**Rastalion**

## 개요
이 MCP 서버 구현체는 Model Context Protocol을 통해 MongoDB 데이터베이스와 상호작용할 수 있는 강력한 인터페이스를 제공합니다. 데이터베이스, 컬렉션 및 문서에 대한 작업을 async/await 패턴과 오류 처리를 통해 안정적으로 지원합니다.

## 특징
* MongoDB CRUD 작업 완벽 지원
* MongoDB와의 안전한 연결 처리
* 최적의 성능을 위한 비동기(async/await) 패턴
* 포괄적인 오류 처리
* 쉬운 배포를 위한 Docker 지원
* 타입 힌트를 갖춘 쿼리 실행
* 실시간 업데이트를 위한 SSE(Server-Sent Events) 지원

## Quick Start

### Python 사용

```bash
# 저장소 복제
git clone https://github.com/yourusername/mongo-mcp-server.git
cd mongo-mcp-server

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export MONGODB_URL="mongodb://username:password@hostname:port/dbname?authSource=admin"

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

### Docker 사용

```bash
# 저장소 복제
git clone https://github.com/yourusername/mongo-mcp-server.git
cd mongo-mcp-server

# Docker Compose로 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f mongo-mcp
```

### UVX 사용

UVX는 다양한 환경에서 서비스를 쉽게 관리할 수 있는 도구입니다.

```bash
# 등록 스크립트에 실행 권한 부여
chmod +x uvx-register.sh

# UVX에 서비스 등록
./uvx-register.sh

# 서비스 시작
uvx start mongo-mcp

# 상태 확인
uvx status mongo-mcp

# 로그 확인
uvx logs mongo-mcp
```

더 자세한 내용은 [UVX 가이드](./UVX_GUIDE.md)를 참조하세요.

## 환경 변수

서버 실행 전에 다음 환경 변수를 설정하세요:

```bash
# 필수
MONGODB_URL="mongodb://username:password@hostname:port/dbname?authSource=admin"

# 선택 - 기본값 표시
PORT=3000
```

## API 엔드포인트

- **상태 확인**: `GET /health`
- **MCP API**: `GET /mcp` - FastMCP 엔드포인트 (OpenAPI 문서)
- **SSE 연결**: `GET /sse` - Server-Sent Events 엔드포인트
- **메시지 처리**: `POST /messages` - 메시지 처리 엔드포인트

## IDE 통합

### VS Code 설정

VS Code settings.json에 다음을 추가하세요:

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "mongodbUri",
        "description": "MongoDB 연결 URI"
      }
    ],
    "servers": {
      "mongodb": {
        "command": "uvicorn",
        "args": ["app.main:app", "--host", "0.0.0.0", "--port", "3000"],
        "env": {
          "MONGODB_URL": "$(mongodbUri)"
        }
      }
    }
  }
}
```

### Claude 또는 다른 AI 어시스턴트

Claude 또는 다른 AI 어시스턴트를 위해 MCP 서버를 다음과 같이 구성하세요:

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

## 사용 가능한 도구

| 도구 이름 | 설명 |
|-----------|-------------|
| `listCollections` | 데이터베이스의 모든 사용 가능한 컬렉션 목록 조회 |
| `find` | MongoDB 쿼리 구문을 사용하여 컬렉션의 문서 조회 |
| `insertOne` | 컬렉션에 단일 문서 삽입 |
| `updateOne` | 컬렉션에서 단일 문서 업데이트 |
| `deleteOne` | 컬렉션에서 단일 문서 삭제 |
| `indexes` | 컬렉션의 모든 인덱스 목록 조회 |
| `createIndex` | 컬렉션에 새로운 인덱스 생성 |
| `dropIndex` | 컬렉션에서 기존 인덱스 삭제 |

## 고급 사용법

### 사용자 정의 도구 추가

1. `app/tools/documents/` 또는 `app/tools/collection/`에 새 도구 생성:

```python
from ..base.tool import BaseTool

class MyNewTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_new_tool"

    @property
    def description(self) -> str:
        return "새 도구에 대한 설명"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                # 도구 입력 스키마 정의
            }
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # 도구 실행 로직 구현
        pass
```

2. `app/tools/registry.py`에 도구 등록:

```python
from .documents.my_new_tool import MyNewTool

# ToolRegistry.__init__ 메서드 내에서
self.register_tool(MyNewTool())
```

## 문제 해결

- **서버가 시작되지 않는 경우**: `docker-compose logs mongo-mcp` 또는 `sudo journalctl -u mongo-mcp -f`로 로그 확인
- **MongoDB 연결 문제**: `MONGODB_URL`이 올바르고 접근 가능한지 확인
- **도구 실행 오류**: 도구 구현과 입력 매개변수 확인

## Docker 구성

Docker 설정에는 다음이 포함됩니다:

- Python 3.12 기본 이미지
- Asia/Seoul 타임존
- MongoDB 4.4 인스턴스
- 데이터베이스 스토리지를 위한 영구 볼륨
- 양쪽 서비스에 대한 헬스 체크
- 자동화된 네트워크 구성

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
