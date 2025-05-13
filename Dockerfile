FROM python:3.12-slim

# 타임존 설정 (Asia/Seoul)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치를 위한 requirements.txt 추가
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 추가
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# 포트 노출
EXPOSE 3000
