import urllib.parse
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# 전역 변수로 클라이언트와 데이터베이스 객체 유지
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


def get_safe_connection_string(url: str) -> str:
    """민감한 정보가 제거된 안전한 연결 문자열 반환"""
    try:
        parsed = urllib.parse.urlparse(url)

        # 사용자 정보가 있는 경우 마스킹 처리
        if parsed.username:
            safe_url = f"{parsed.scheme}://"
            if parsed.username:
                safe_url += "****"  # 사용자명 마스킹
                if parsed.password:
                    safe_url += ":****"  # 비밀번호 마스킹
                safe_url += "@"

            # 호스트 정보 및 나머지 부분 추가
            safe_url += f"{parsed.hostname}"
            if parsed.port:
                safe_url += f":{parsed.port}"
            if parsed.path:
                safe_url += f"{parsed.path}"
            if parsed.query:
                safe_url += f"?{parsed.query}"

            return safe_url
        else:
            # 사용자 정보가 없는 경우 URL 그대로 반환
            return url
    except Exception:
        # 파싱 오류 시 더 안전하게 처리
        return "mongodb://*****:*****@*****:*****/****"


async def connect_to_mongodb(database_url: str):
    """MongoDB에 비동기로 연결"""
    global client, db

    try:
        # 안전한 연결 문자열로 로그 출력
        safe_url = get_safe_connection_string(database_url)
        print(f"MongoDB 연결 시도 중: {safe_url}")

        # 클라이언트 생성
        client = AsyncIOMotorClient(database_url)

        # 데이터베이스 이름 파싱
        parsed_url = urllib.parse.urlparse(database_url)
        db_name = parsed_url.path.split("/")[1] if parsed_url.path and len(parsed_url.path.split("/")) > 1 else "admin"
        print(f"데이터베이스 선택: {db_name}")

        # 데이터베이스 객체 가져오기
        db = client[db_name]

        # 연결 확인을 위해 admin 명령 실행
        server_info = await client.admin.command('serverStatus')
        version = server_info['version']
        uptime = server_info['uptime']
        connections = server_info['connections']

        # 연결 성공 상세 정보 출력
        print(f"MongoDB 연결 성공!")
        print(f"  - 서버 버전: {version}")
        print(f"  - 가동 시간: {uptime}초")
        print(f"  - 활성 연결: {connections['current']}/{connections['available']}")
        print(f"  - 데이터베이스: {db_name}")

        # 사용 가능한 컬렉션 출력
        collections = await db.list_collection_names()
        if collections:
            print(f"  - 사용 가능한 컬렉션: {', '.join(collections)}")
        else:
            print(f"  - 데이터베이스에 컬렉션이 없습니다.")

        return db

    except Exception as error:
        print(f"MongoDB 연결 오류: {str(error).replace(database_url, safe_url)}")
        raise error


async def close_mongodb():
    """MongoDB 연결 종료"""
    global client
    if client:
        try:
            client.close()
            print("MongoDB 연결이 안전하게 종료되었습니다.")
        except Exception as e:
            print(f"MongoDB 연결 종료 중 오류: {e}")
