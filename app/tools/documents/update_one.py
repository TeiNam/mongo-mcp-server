import json
from typing import Dict, Any

from ..base.tool import BaseTool
from ...mongodb.client import db


class UpdateOneTool(BaseTool):
    """문서 수정 도구"""

    @property
    def name(self) -> str:
        return "updateOne"

    @property
    def description(self) -> str:
        return "Update a single document in a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to update in"
                },
                "filter": {
                    "type": "object",
                    "description": "Filter to select the document to update"
                },
                "update": {
                    "type": "object",
                    "description": "Update operations to apply to the document (MongoDB update operators)"
                },
                "upsert": {
                    "type": "boolean",
                    "description": "Create a new document if no document matches the filter",
                    "default": False
                }
            },
            "required": ["collection", "filter", "update"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            filter_query = self.validate_object(params.get("filter"), "Filter")
            update = self.validate_object(params.get("update"), "Update")
            upsert = params.get("upsert", False)

            # 문서 수정
            result = await db[collection].update_one(
                filter_query,
                update,
                upsert=upsert
            )

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "matchedCount": result.matched_count,
                            "modifiedCount": result.modified_count,
                            "upsertedId": str(result.upserted_id) if result.upserted_id else None,
                            "acknowledged": result.acknowledged
                        }, indent=2)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)
