import os
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# 올바른 fastmcp 임포트
from fastmcp.server import FastMCP
# 서버용 SSE 트랜스포트 임포트
from fastmcp.low_level.sse_server_transport import SseServerTransport

from app.mongodb.client import connect_to_mongodb, close_mongodb
from app.tools.registry import ToolRegistry

# 환경 변수 로드
load_dotenv()
database_url = os.getenv("MONGODB_URL", "mongodb://root:example@localhost:27017/admin")

# 수명 주기 관리자
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 수명 주기 관리"""
    # 시작 시 실행
    await connect_to_mongodb(database_url)
    print("MongoDB MCP server running")
    yield
    # 종료 시 실행
    await close_mongodb()

# FastAPI 앱 생성
app = FastAPI(title="MongoDB MCP Server", lifespan=lifespan)

# FastMCP 인스턴스 생성
mcp = FastMCP(
    name="mongo-mcp",
    version="0.1.0"
)

# 도구 레지스트리 초기화
tool_registry = ToolRegistry()

@app.get("/health")
async def health_check():
    """상태 체크 엔드포인트"""
    return {"status": "ok"}

# 도구 등록
for tool in tool_registry.get_all_tools():
    try:
        # 시그니처에 맞게 수정: (fn, name=None, description=None, tags=None, annotations=None)
        if hasattr(mcp, 'add_tool'):
            # 첫 번째 인자로 함수를 전달하고, 나머지는 키워드 인자로 전달
            if callable(tool.execute):
                mcp.add_tool(
                    tool.execute,  # fn 인자 - 첫 번째 위치
                    name=tool.name,
                    description=tool.description
                )
                print(f"도구 등록 성공: {tool.name}")
            else:
                print(f"도구 실행 함수가 호출 가능한 객체가 아닙니다: {tool.name}, 타입: {type(tool.execute)}")
                # 디버깅 정보 출력
                print(f"도구 속성: {dir(tool)}")
                print(f"execute 타입: {type(tool.execute)}")
        elif hasattr(mcp, 'register_tool'):
            if callable(tool.execute):
                mcp.register_tool(
                    tool.execute,
                    name=tool.name,
                    description=tool.description
                )
                print(f"도구 등록 성공: {tool.name}")
            else:
                print(f"도구 실행 함수가 호출 가능한 객체가 아닙니다: {tool.name}")
        else:
            print(f"도구 등록 메서드를 찾을 수 없습니다: {tool.name}")
    except Exception as e:
        print(f"도구 등록 중 오류: {e}")
        # 오류 발생 시 메서드 시그니처 확인
        if hasattr(mcp, 'add_tool'):
            import inspect
            print(f"add_tool 메서드 시그니처: {inspect.signature(mcp.add_tool)}")
            
        # 도구 디버깅 정보 출력
        try:
            print(f"도구 정보: {tool.name}, 타입: {type(tool)}")
            if hasattr(tool, 'execute'):
                print(f"execute 타입: {type(tool.execute)}")
        except:
            pass

# FastMCP 앱 연결 - FastMCP API 변경사항 적용
try:
    print("FastMCP 앱 연결 시도")
    
    # from_fastapi 메서드 사용 시도 (권장 방식)
    if hasattr(mcp, 'from_fastapi') and callable(mcp.from_fastapi):
        # FastMCP 앱을 FastAPI 앱에 연결
        mcp.from_fastapi(app, prefix="/mcp")
        print("성공: from_fastapi 메서드로 FastMCP 앱 통합")
        
    # 대체 방식: 필요한 앱 마운트
    else:
        # 앱 마운트 상태 추적
        apps_mounted = 0
        
        # HTTP 앱 마운트
        if hasattr(mcp, 'http_app'):
            try:
                app.mount("/mcp", mcp.http_app)
                print("성공: HTTP 앱을 /mcp 경로에 마운트")
                apps_mounted += 1
            except Exception as e:
                print(f"HTTP 앱 마운트 실패: {e}")
        
        # SSE 앱 마운트
        if hasattr(mcp, 'sse_app'):
            try:
                app.mount("/mcp/sse", mcp.sse_app)
                print("성공: SSE 앱을 /mcp/sse 경로에 마운트")
                apps_mounted += 1
            except Exception as e:
                print(f"SSE 앱 마운트 실패: {e}")
                
        # 스트리밍 HTTP 앱 마운트
        if hasattr(mcp, 'streamable_http_app'):
            try:
                app.mount("/mcp/stream", mcp.streamable_http_app)
                print("성공: 스트리밍 HTTP 앱을 /mcp/stream 경로에 마운트")
                apps_mounted += 1
            except Exception as e:
                print(f"스트리밍 HTTP 앱 마운트 실패: {e}")
        
        # 앱 마운트 결과 요약
        if apps_mounted > 0:
            print(f"성공: {apps_mounted}개 FastMCP 앱 통합 완료")
        else:
            print("주의: FastMCP 앱을 마운트할 수 없습니다.")
            print("커스텀 엔드포인트(/sse, /messages)를 통해 기능이 제공됩니다.")
            
        # 마운트 상태와 관계없이 커스텀 엔드포인트 사용 안내
        print("참고: 커스텀 엔드포인트도 사용 가능 (/sse, /messages)")
except Exception as e:
    print(f"FastMCP 앱 연결 중 오류: {e}")
    import traceback
    traceback.print_exc()

# SSE 엔드포인트
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE 엔드포인트"""
    try:
        # SseServerTransport 생성
        transport = SseServerTransport(request)

        # FastMCP에 트랜스포트 연결
        if hasattr(mcp, 'handle_connection'):
            await mcp.handle_connection(transport)
        elif hasattr(mcp, 'connect'):
            await mcp.connect(transport)
        else:
            print("트랜스포트 연결 메서드를 찾을 수 없습니다.")
            return JSONResponse(
                status_code=500,
                content={"error": "Transport connection method not found"}
            )

        # 응답 반환
        return transport.response
    except Exception as e:
        print(f"SSE 연결 처리 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"SSE connection error: {str(e)}"}
        )

# 메시지 엔드포인트
@app.post("/messages")
async def messages_endpoint(request: Request):
    """메시지 처리 엔드포인트"""
    try:
        data = await request.json()
        session_id = request.query_params.get("sessionId")

        # FastMCP로 메시지 처리
        if hasattr(mcp, 'handle_message'):
            response = await mcp.handle_message(session_id, data)
        elif hasattr(mcp, 'process_message'):
            response = await mcp.process_message(session_id, data)
        else:
            print("메시지 처리 메서드를 찾을 수 없습니다.")
            return JSONResponse(
                status_code=500,
                content={"error": "Message processing method not found"}
            )

        return JSONResponse(content=response)
    except Exception as e:
        print(f"메시지 처리 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Message processing error: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)