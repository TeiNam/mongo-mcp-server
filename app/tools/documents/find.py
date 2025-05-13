import json
from typing import Dict, Any, List, Optional
from ...mongodb.client import db
from ..base.tool import BaseTool, ToolParams


class FindParams(ToolParams):
    """Find 도구 파라미터"""
    collection: str
    filter: Optional[Dict[str, Any]] = {}
    limit: Optional[int] = 10
    projection: Optional[Dict[str, Any]] = {}


class FindTool(BaseTool[FindParams]):
    """문서 조회 도구"""

    @property
    def name(self) -> str:
        return "find"

    @property
    def description(self) -> str:
        return "Query documents in a collection using MongoDB query syntax"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Name of the collection to query"
                },
                "filter": {
                    "type": "object",
                    "description": "MongoDB query filter",
                    "default": {}
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum documents to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 1000
                },
                "projection": {
                    "type": "object",
                    "description": "Fields to include/exclude",
                    "default": {}
                }
            },
            "required": ["collection"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            collection = self.validate_collection(params.get("collection"))
            filter_query = params.get("filter", {})
            projection = params.get("projection", {})
            limit = min(params.get("limit", 10), 1000)

            cursor = db[collection].find(filter_query, projection).limit(limit)
            results = await cursor.to_list(length=limit)

            # ObjectId를 문자열로 변환
            for doc in results:
                if "_id" in doc and hasattr(doc["_id"], "__str__"):
                    doc["_id"] = str(doc["_id"])

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(results, default=str, indent=2)
                    }
                ],
                "isError": False
            }
        except Exception as error:
            return self.handle_error(error)