# app/logger.py
import logging
import sys
from pathlib import Path

# 로그 디렉토리 생성
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)


# 로거 설정
def setup_logger(name: str, log_file: str, level=logging.INFO):
    """로거 설정 함수"""
    # 파일 핸들러
    file_handler = logging.FileHandler(log_dir / log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    ))

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    ))

    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 메인 로거 생성
main_logger = setup_logger('mongo-mcp', 'server.log')
mongodb_logger = setup_logger('mongodb', 'mongodb.log')
tools_logger = setup_logger('tools', 'tools.log')