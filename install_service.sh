#!/bin/bash

# 스크립트가 루트 권한으로 실행되었는지 확인
if [[ $EUID -ne 0 ]]; then
   echo "이 스크립트는 루트 권한으로 실행해야 합니다" 
   exit 1
fi

# 현재 디렉토리 경로
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_NAME="mongo-mcp"
SERVICE_FILE="${SCRIPT_DIR}/${SERVICE_NAME}.service"

echo "MongoDB MCP 서비스 설치 시작..."

# 환경 변수 설정
echo "MongoDB 접속 정보 설정"
read -p "MongoDB 사용자명: " DB_USER
read -sp "MongoDB 비밀번호: " DB_PASS
echo ""
read -p "MongoDB 호스트 (기본값: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}
read -p "MongoDB 포트 (기본값: 27017): " DB_PORT
DB_PORT=${DB_PORT:-27017}
read -p "MongoDB 데이터베이스 이름: " DB_NAME
read -p "사용자 인증 소스 (기본값: admin): " AUTH_SOURCE
AUTH_SOURCE=${AUTH_SOURCE:-admin}

# 서비스 파일에서 환경 변수 업데이트
MONGODB_URL="mongodb://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}?authSource=${AUTH_SOURCE}"
sed -i "s|Environment=\"MONGODB_URL=.*\"|Environment=\"MONGODB_URL=${MONGODB_URL}\"|g" "$SERVICE_FILE"

# 현재 사용자 정보 업데이트
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)
sed -i "s|User=.*|User=${CURRENT_USER}|g" "$SERVICE_FILE"
sed -i "s|Group=.*|Group=${CURRENT_GROUP}|g" "$SERVICE_FILE"

# 작업 디렉토리 업데이트
sed -i "s|WorkingDirectory=.*|WorkingDirectory=${SCRIPT_DIR}|g" "$SERVICE_FILE"

# 가상 환경 경로 업데이트
VENV_PATH="${SCRIPT_DIR}/venv"
sed -i "s|Environment=\"PATH=.*\"|Environment=\"PATH=${VENV_PATH}/bin\"|g" "$SERVICE_FILE"
sed -i "s|Environment=\"PYTHONPATH=.*\"|Environment=\"PYTHONPATH=${SCRIPT_DIR}\"|g" "$SERVICE_FILE"
sed -i "s|ExecStart=.*|ExecStart=${VENV_PATH}/bin/uvicorn app.main:app --host 0.0.0.0 --port 3000|g" "$SERVICE_FILE"

# systemd 서비스 디렉토리로 서비스 파일 복사
echo "서비스 파일을 /etc/systemd/system/ 디렉토리로 복사 중..."
cp "$SERVICE_FILE" "/etc/systemd/system/"

# systemd 재로드 및 서비스 활성화
echo "systemd 데몬 재로드 중..."
systemctl daemon-reload

echo "서비스 활성화 중..."
systemctl enable $SERVICE_NAME

echo "서비스 시작 중..."
systemctl start $SERVICE_NAME

# 서비스 상태 확인
echo "서비스 상태 확인 중..."
systemctl status $SERVICE_NAME

echo "MongoDB MCP 서비스 설치 완료!"
echo "다음 명령으로 서비스를 관리할 수 있습니다:"
echo "  - 서비스 시작: sudo systemctl start $SERVICE_NAME"
echo "  - 서비스 중지: sudo systemctl stop $SERVICE_NAME"
echo "  - 서비스 재시작: sudo systemctl restart $SERVICE_NAME"
echo "  - 상태 확인: sudo systemctl status $SERVICE_NAME"
echo "  - 로그 확인: sudo journalctl -u $SERVICE_NAME -f"
