import json
from typing import Dict, Any

from ..base.tool import BaseTool
from ...mongodb.client import db


class InsertOneTool(BaseTool):
    """문서 삽입 도구"""

    @property
    def name(self) -> str:
        return "insertOne"

    @property
    def description(self) -> str:
        return "Insert a single document into a collection"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to insert into"
                },
                "document": {
                    "type": "object",
                    "description": "Document to insert"
                }
            },
            "required": ["collection", "document"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            document = self.validate_object(params.get("document"), "Document")

            # 문서 삽입
            result = await db[collection].insert_one(document)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "insertedId": str(result.inserted_id),
                            "acknowledged": result.acknowledged
                        }, indent=2)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)
