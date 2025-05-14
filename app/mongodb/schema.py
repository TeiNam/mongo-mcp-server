from typing import Dict, List, Any, Set, Optional

from motor.motor_asyncio import AsyncIOMotorCollection


class MongoFieldSchema:
    """MongoDB 필드 스키마 정의"""

    def __init__(self, field: str, field_type: str, is_required: bool,
                 sub_fields: Optional[List['MongoFieldSchema']] = None):
        self.field = field
        self.type = field_type
        self.is_required = is_required
        self.sub_fields = sub_fields

    def to_dict(self) -> Dict[str, Any]:
        """사전 형태로 변환"""
        result = {
            "field": self.field,
            "type": self.type,
            "isRequired": self.is_required
        }
        if self.sub_fields:
            result["subFields"] = [sf.to_dict() for sf in self.sub_fields]
        return result


class MongoCollectionSchema:
    """MongoDB 컬렉션 스키마 정의"""

    def __init__(self, collection: str, fields: List[MongoFieldSchema], count: int,
                 indexes: Optional[List[Any]] = None):
        self.collection = collection
        self.fields = fields
        self.count = count
        self.indexes = indexes

    def to_dict(self) -> Dict[str, Any]:
        """사전 형태로 변환"""
        return {
            "collection": self.collection,
            "fields": [field.to_dict() for field in self.fields],
            "count": self.count,
            "indexes": self.indexes
        }


def infer_schema_from_value(value: Any) -> str:
    """값의 타입 추론"""
    if value is None:
        return "null"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (bytes, bytearray)):
        return "binary"
    return str(type(value).__name__)


def infer_schema_from_document(doc: Dict[str, Any], parent_path: str = "") -> List[MongoFieldSchema]:
    """문서로부터 스키마 추론"""
    schema = []

    for key, value in doc.items():
        field_path = f"{parent_path}.{key}" if parent_path else key
        field_type = infer_schema_from_value(value)

        field = MongoFieldSchema(
            field=field_path,
            field_type=field_type,
            is_required=True
        )

        # 객체나 배열에 대한 하위 필드 처리
        if field_type == "object" and value is not None:
            field.sub_fields = infer_schema_from_document(value, field_path)
        elif field_type == "array" and isinstance(value, list) and value:
            array_type = infer_schema_from_value(value[0])
            if array_type == "object":
                field.sub_fields = infer_schema_from_document(value[0], f"{field_path}[]")

        schema.append(field)

    return schema


async def build_collection_schema(collection: AsyncIOMotorCollection, sample_size: int = 100) -> MongoCollectionSchema:
    """컬렉션 스키마 구축"""
    # 샘플 문서 가져오기
    docs = await collection.find().limit(sample_size).to_list(length=sample_size)
    count = await collection.count_documents({})
    indexes = await collection.index_information()

    field_schemas: Dict[str, Set[str]] = {}
    required_fields: Set[str] = set()

    # 모든 필드 수집
    for doc in docs:
        doc_schema = infer_schema_from_document(doc)
        for field in doc_schema:
            if field.field not in field_schemas:
                field_schemas[field.field] = set()
            field_schemas[field.field].add(field.type)
            required_fields.add(field.field)

    # 필수 필드 결정
    for doc in docs:
        doc_fields = set(doc.keys())
        for field in list(required_fields):
            if field.split(".")[0] not in doc_fields:
                required_fields.remove(field)

    # 필드 스키마 생성
    fields: List[MongoFieldSchema] = []
    for field, types in field_schemas.items():
        fields.append(MongoFieldSchema(
            field=field,
            field_type="|".join(types) if len(types) > 1 else next(iter(types)),
            is_required=field in required_fields
        ))

    # 하위 필드 정보 추가
    for doc in docs:
        doc_schema = infer_schema_from_document(doc)
        for field_schema in doc_schema:
            if field_schema.sub_fields:
                existing_field = next((f for f in fields if f.field == field_schema.field), None)
                if existing_field and not existing_field.sub_fields:
                    existing_field.sub_fields = field_schema.sub_fields

    return MongoCollectionSchema(
        collection=collection.name,
        fields=fields,
        count=count,
        indexes=list(indexes.values())
    )
