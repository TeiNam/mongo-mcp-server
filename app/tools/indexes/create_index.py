from typing import Dict, Any, List, Union
import json
from ...mongodb.client import db
from ..base.tool import BaseTool, ToolParams


class CreateIndexTool(BaseTool):
    """인덱스 생성 도구"""

    @property
    def name(self) -> str:
        return "createIndex"

    @property
    def description(self) -> str:
        return "Create a new index on a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to create an index on"
                },
                "field": {
                    "type": "string",
                    "description": "Field name to index"
                },
                "order": {
                    "type": "number",
                    "enum": [1, -1],
                    "description": "Index order (1 for ascending, -1 for descending)",
                    "default": 1
                },
                "unique": {
                    "type": "boolean",
                    "description": "Whether the index should be unique",
                    "default": False
                },
                "name": {
                    "type": "string",
                    "description": "Optional name for the index"
                }
            },
            "required": ["collection", "field"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            field = params.get("field")
            order = params.get("order", 1)
            unique = params.get("unique", False)
            name = params.get("name")

            if not isinstance(field, str):
                raise ValueError("Field must be a string")

            # 인덱스 옵션 생성
            options: Dict[str, Any] = {"unique": unique}
            if name:
                options["name"] = name

            # 인덱스 생성
            result = await db[collection].create_index([(field, order)], **options)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Created index '{result}' on collection '{collection}'"
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)