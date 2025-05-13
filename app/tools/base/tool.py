from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic

# 도구 파라미터 타입
ToolParams = Dict[str, Any]
T = TypeVar('T', bound=ToolParams)


class ToolResponse:
    """도구 응답 형식"""

    def __init__(
            self,
            content: List[Dict[str, str]],
            is_error: bool = False,
            meta: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.is_error = is_error
        self._meta = meta or {}

    def to_dict(self) -> Dict[str, Any]:
        """사전 형태로 변환"""
        return {
            "content": self.content,
            "isError": self.is_error,
            "_meta": self._meta
        }


class BaseTool(Generic[T], ABC):
    """모든 도구의 기본 클래스"""

    @property
    @abstractmethod
    def name(self) -> str:
        """도구 이름"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """도구 설명"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """입력 스키마"""
        pass

    @abstractmethod
    async def execute(self, params: T) -> Dict[str, Any]:
        """도구 실행"""
        pass

    def validate_collection(self, collection: Any) -> str:
        """컬렉션 이름 검증"""
        if not isinstance(collection, str):
            raise ValueError(f"Collection name must be a string, got {type(collection).__name__}")
        return collection

    def validate_object(self, value: Any, name: str) -> Dict[str, Any]:
        """객체 검증"""
        if not value or not isinstance(value, dict):
            raise ValueError(f"{name} must be an object")
        return value

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """오류 처리"""
        return ToolResponse(
            content=[{"type": "text", "text": str(error)}],
            is_error=True
        ).to_dict()