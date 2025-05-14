from typing import Dict, List, Optional, Any

from .base.tool import BaseTool
from .collection.list_collections import ListCollectionsTool
from .documents.delete_one import DeleteOneTool
from .documents.find import FindTool
from .documents.insert_one import InsertOneTool
from .documents.update_one import UpdateOneTool
from .indexes.create_index import CreateIndexTool
from .indexes.drop_index import DropIndexTool
from .indexes.list_indexes import ListIndexesTool


class ToolRegistry:
    """도구 레지스트리"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

        # 도구 등록
        self.register_tool(ListCollectionsTool())
        self.register_tool(FindTool())
        self.register_tool(InsertOneTool())
        self.register_tool(UpdateOneTool())
        self.register_tool(DeleteOneTool())
        self.register_tool(CreateIndexTool())
        self.register_tool(DropIndexTool())
        self.register_tool(ListIndexesTool())

    def register_tool(self, tool: BaseTool):
        """도구 등록"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """이름으로 도구 조회"""
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return tool

    def get_all_tools(self) -> List[BaseTool]:
        """모든 도구 목록 반환"""
        return list(self.tools.values())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """도구 스키마 목록 반환"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {
                    "type": "object",
                    "properties": tool.input_schema.get("properties", {}),
                    "required": tool.input_schema.get("required", [])
                }
            }
            for tool in self.get_all_tools()
        ]
