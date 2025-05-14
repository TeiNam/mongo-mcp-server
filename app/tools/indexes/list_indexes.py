import json
from typing import Dict, Any

from ..base.tool import BaseTool
from ...mongodb.client import db


class ListIndexesTool(BaseTool):
    """인덱스 목록 조회 도구"""

    @property
    def name(self) -> str:
        return "indexes"

    @property
    def description(self) -> str:
        return "List all indexes for a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to get indexes for"
                }
            },
            "required": ["collection"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            indexes = await db[collection].index_information()

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(indexes, default=str, indent=2)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)
