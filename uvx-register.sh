#!/bin/bash

# 색상 설정
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}MongoDB MCP 서버 UVX 등록 유틸리티${NC}"
echo "========================================"

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo -e "${YELLOW}현재 디렉토리:${NC} $SCRIPT_DIR"

# uvx 명령어 확인
if ! command -v uvx &> /dev/null; then
    echo -e "${RED}uvx 명령어를 찾을 수 없습니다.${NC}"
    echo "uvx를 먼저 설치해주세요."
    exit 1
fi

echo -e "${YELLOW}UVX 버전:${NC} $(uvx --version)"

# 서비스 이름 설정
SERVICE_NAME="mongo-mcp"
echo -e "${YELLOW}서비스 이름:${NC} $SERVICE_NAME"

# MongoDB URL 입력 받기
read -p "MongoDB URL을 입력하세요 (기본값: mongodb://localhost:27017/admin): " MONGODB_URL
MONGODB_URL=${MONGODB_URL:-mongodb://localhost:27017/admin}

# 포트 입력 받기
read -p "서비스 포트를 입력하세요 (기본값: 3000): " PORT
PORT=${PORT:-3000}

# 서비스 등록
echo -e "\n${GREEN}uvx에 서비스 등록 중...${NC}"

# 서비스 파일 생성
TEMP_SERVICE_FILE=$(mktemp)
cat > "$TEMP_SERVICE_FILE" << EOF
name: $SERVICE_NAME
description: MongoDB MCP Server for AI Agents
command: uvicorn
args:
  - app.main:app
  - --host
  - 0.0.0.0
  - --port
  - $PORT
cwd: $SCRIPT_DIR
env:
  MONGODB_URL: $MONGODB_URL
  PORT: $PORT
  PYTHONPATH: $SCRIPT_DIR
  TZ: Asia/Seoul
tags:
  - mongodb
  - mcp
  - database
  - ai
EOF

# uvx 서비스 등록
uvx register --file "$TEMP_SERVICE_FILE"
RESULT=$?

# 임시 파일 삭제
rm "$TEMP_SERVICE_FILE"

# 등록 결과 확인
if [ $RESULT -eq 0 ]; then
    echo -e "\n${GREEN}서비스 등록이 완료되었습니다!${NC}"
    echo -e "다음 명령어로 서비스를 관리할 수 있습니다:"
    echo -e "  ${BLUE}서비스 시작:${NC} uvx start $SERVICE_NAME"
    echo -e "  ${BLUE}서비스 중지:${NC} uvx stop $SERVICE_NAME"
    echo -e "  ${BLUE}서비스 상태:${NC} uvx status $SERVICE_NAME"
    echo -e "  ${BLUE}서비스 로그:${NC} uvx logs $SERVICE_NAME"
    
    # 서비스 시작 여부 확인
    read -p "서비스를 지금 시작하시겠습니까? (y/n): " START_SERVICE
    if [[ "$START_SERVICE" =~ ^[Yy]$ ]]; then
        echo -e "\n${GREEN}서비스 시작 중...${NC}"
        uvx start $SERVICE_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "\n${GREEN}서비스가 성공적으로 시작되었습니다!${NC}"
            echo -e "서비스 URL: http://localhost:$PORT"
            echo -e "MCP 엔드포인트: http://localhost:$PORT/mcp"
            echo -e "헬스 체크: http://localhost:$PORT/health"
        else
            echo -e "\n${RED}서비스 시작 중 오류가 발생했습니다.${NC}"
            echo "로그를 확인하세요: uvx logs $SERVICE_NAME"
        fi
    else
        echo -e "\n서비스를 나중에 시작하려면 다음 명령어를 사용하세요:"
        echo -e "  ${BLUE}uvx start $SERVICE_NAME${NC}"
    fi
else
    echo -e "\n${RED}서비스 등록 중 오류가 발생했습니다.${NC}"
fi
