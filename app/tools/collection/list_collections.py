from typing import Dict, Any

from ..base.tool import BaseTool, ToolParams
from ...mongodb.client import db


class ListCollectionsTool(BaseTool):
    """컬렉션 목록 조회 도구"""

    @property
    def name(self) -> str:
        return "listCollections"

    @property
    def description(self) -> str:
        return "List all available collections in the database"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, _params: ToolParams) -> Dict[str, Any]:
        try:
            collections = await db.list_collections().to_list(length=100)
            collections_data = [{"name": c["name"], "type": c["type"]} for c in collections]

            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(collections_data)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)
