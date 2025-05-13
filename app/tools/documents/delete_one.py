from typing import Dict, Any
import json
from ...mongodb.client import db
from ..base.tool import BaseTool, ToolParams


class DeleteOneTool(BaseTool):
    """문서 삭제 도구"""

    @property
    def name(self) -> str:
        return "deleteOne"

    @property
    def description(self) -> str:
        return "Delete a single document from a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to delete from"
                },
                "filter": {
                    "type": "object",
                    "description": "Filter to select the document to delete"
                }
            },
            "required": ["collection", "filter"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            filter_query = self.validate_object(params.get("filter"), "Filter")

            # 문서 삭제
            result = await db[collection].delete_one(filter_query)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "deletedCount": result.deleted_count,
                            "acknowledged": result.acknowledged
                        }, indent=2)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)