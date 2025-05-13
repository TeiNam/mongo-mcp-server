from typing import Dict, Any
from ...mongodb.client import db
from ..base.tool import BaseTool, ToolParams


class DropIndexTool(BaseTool):
    """인덱스 삭제 도구"""

    @property
    def name(self) -> str:
        return "dropIndex"

    @property
    def description(self) -> str:
        return "Drop an index from a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to drop an index from"
                },
                "indexName": {
                    "type": "string",
                    "description": "Name of the index to drop"
                }
            },
            "required": ["collection", "indexName"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            index_name = params.get("indexName")

            if not isinstance(index_name, str):
                raise ValueError("Index name must be a string")

            # 인덱스 삭제
            await db[collection].drop_index(index_name)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Dropped index '{index_name}' from collection '{collection}'"
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)