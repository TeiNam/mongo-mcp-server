#!/bin/bash

# 색상 설정
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}MongoDB MCP 서버 개발 환경 설정${NC}"
echo "========================================"

# 현재 디렉토리
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 가상 환경 생성 (존재하지 않는 경우)
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}가상 환경 생성 중...${NC}"
    python3 -m venv venv
fi

# 가상 환경 활성화
echo -e "${YELLOW}가상 환경 활성화 중...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# 의존성 설치
echo -e "${YELLOW}의존성 설치 중...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 실행 권한 부여
echo -e "${YELLOW}스크립트에 실행 권한 부여 중...${NC}"
chmod +x uvx-register.sh

# 성공 메시지
echo -e "\n${GREEN}개발 환경 설정이 완료되었습니다!${NC}"
echo -e "다음 명령어로 서버를 시작할 수 있습니다:"
echo -e "  ${BLUE}mongo-mcp-server${NC}"
echo -e "또는"
echo -e "  ${BLUE}mongo-mcp-server --transport=sse${NC}"
echo -e "\nUVX로 실행:"
echo -e "  ${BLUE}uvx mongo-mcp-server${NC}"
echo -e "  ${BLUE}uvx mongo-mcp-server --transport=sse${NC}"
echo -e "\n명령어 도움말을 보려면:"
echo -e "  ${BLUE}mongo-mcp-server --help${NC}"
echo -e "\n패키지 업로드 준비:"
echo -e "  ${BLUE}python setup.py sdist bdist_wheel${NC}"
