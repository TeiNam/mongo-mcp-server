# MongoDB MCP Server

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-green.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-2.3.3-yellow.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4-orange.svg)
![Anthropic](https://img.shields.io/badge/Claude-3.7--Sonnet-purple.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

MongoDB 데이터베이스를 위한 MCP(Method Call Protocol) 서버 애플리케이션입니다. 이 서버는 MongoDB 작업을 도구(Tool)로 노출하고 FastMCP 프레임워크를 통해 AI 에이전트가 MongoDB를 쉽게 조작할 수 있도록 합니다.

## 기능

- MongoDB 컬렉션 목록 조회
- MongoDB 문서 검색 및 필터링
- 외부 AI 에이전트와의 통합을 위한 MCP 인터페이스 제공
- SSE(Server-Sent Events)를 통한 비동기 메시지 스트리밍
- FastAPI 기반의 RESTful 엔드포인트

## 시스템 요구사항

- Python 3.12 이상
- MongoDB 4.4 이상
- 필수 패키지:
  - FastAPI 0.115.12
  - FastMCP 2.3.3
  - Motor
  - Uvicorn
  - python-dotenv

## 설치 및 설정

### 로컬 환경

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/mongo-mcp-server.git
cd mongo-mcp-server
```

2. 가상 환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate.bat  # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 환경 설정:
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
MONGODB_URL=mongodb://username:password@hostname:port/dbname?authSource=admin
```

### Docker 환경

1. Docker 이미지 빌드 및 컨테이너 실행:
```bash
docker-compose up -d
```

2. MongoDB와 앱 서비스가 모두 자동으로 시작됩니다. 기본 MongoDB 접속 정보:
```
호스트: localhost
포트: 27017
사용자: root
비밀번호: example
```

3. 서비스 로그 확인:
```bash
docker-compose logs -f mongo-mcp
```

## 실행 방법

### 로컬 환경

#### 개발 모드

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

#### 프로덕션 모드

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4
```

### Docker 환경

#### 서비스 시작

```bash
docker-compose up -d
```

#### 서비스 중지

```bash
docker-compose down
```

#### 서비스 재시작

```bash
docker-compose restart
```

### UVX 서비스로 등록 (systemd)

1. UVX 서비스 파일 생성:
```bash
sudo nano /etc/systemd/system/mongo-mcp.service
```

2. 서비스 파일에 다음 내용 추가:
```
[Unit]
Description=MongoDB MCP Server
After=network.target

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/mongo-mcp-server
ExecStart=/path/to/mongo-mcp-server/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=mongo-mcp

[Install]
WantedBy=multi-user.target
```

3. 서비스 활성화 및 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mongo-mcp
sudo systemctl start mongo-mcp
```

4. 서비스 상태 확인:
```bash
sudo systemctl status mongo-mcp
```

## API 엔드포인트

- `/health` - 서버 상태 체크
- `/mcp` - FastMCP 엔드포인트 (OpenAPI 문서)
- `/sse` - SSE 연결 엔드포인트
- `/messages` - 메시지 처리 엔드포인트

## 도구(Tools) 추가하기

새로운 MongoDB 작업 도구를 추가하려면:

1. `app/tools/documents/` 또는 `app/tools/collection/` 디렉토리에 새 Python 파일 생성
2. `BaseTool` 클래스를 상속받는 새 도구 클래스 구현
3. `app/tools/registry.py` 파일의 `ToolRegistry` 클래스에 도구 등록

예시:
```python
from .base.tool import BaseTool

class MyNewTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_new_tool"

    @property
    def description(self) -> str:
        return "Description of my new tool"

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

그리고 `ToolRegistry`에 등록:
```python
from .documents.my_new_tool import MyNewTool

# 도구 등록
self.register_tool(MyNewTool())
```

## Docker 구성

이 프로젝트는 Docker 및 Docker Compose를 사용한 컨테이너화를 지원합니다:

### Dockerfile

- Python 3.12 기반 이미지 사용
- 타임존이 Asia/Seoul로 설정됨
- 필요한 모든 의존성이 설치됨
- 헬스체크 엔드포인트 구성 (/health)

### docker-compose.yml

- **mongo-mcp**: MongoDB MCP 서버 컨테이너
  - 빌드: 로컬 Dockerfile 사용
  - 포트: 3000 (호스트) -> 3000 (컨테이너)
  - MongoDB 연결 자동 구성
  - 타임존: Asia/Seoul

- **mongo**: MongoDB 컨테이너
  - 이미지: mongo:4.4
  - 포트: 27017 (호스트) -> 27017 (컨테이너)
  - 루트 계정 자동 생성
  - 데이터 지속성을 위한 볼륨 마운트

## 로그 확인

### 로컬 환경

```bash
sudo journalctl -u mongo-mcp -f
```

### Docker 환경

```bash
docker-compose logs -f mongo-mcp
```

## 문제 해결

- 서버가 시작되지 않는 경우 로그를 확인하여 오류 메시지를 파악하세요.
- MongoDB 연결 문제: 환경 변수 `MONGODB_URL`이 올바른지 확인하세요.
- 도구 등록 오류: 도구 클래스가 `BaseTool`을 올바르게 상속하고 모든 필수 메서드를 구현했는지 확인하세요.
- Docker 문제: `docker-compose ps`로 컨테이너 상태를 확인하고, `docker-compose logs`로 로그를 확인하세요.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.
