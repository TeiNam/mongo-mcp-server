import asyncio
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


async def seed_database():
    """테스트 데이터베이스에 샘플 데이터 생성"""
    client = AsyncIOMotorClient("mongodb://root:example@localhost:27017/admin")
    db = client.test

    # 기존 컬렉션 삭제
    try:
        await db.users.drop()
        await db.products.drop()
        await db.orders.drop()
    except Exception:
        pass

    # 컬렉션 생성
    await db.create_collection("users")
    await db.users.create_index([("email", 1)], unique=True)
    await db.users.create_index([("address.city", 1)])

    await db.create_collection("products")
    await db.products.create_index([("sku", 1)], unique=True)
    await db.products.create_index([("category", 1)])

    await db.create_collection("orders")
    await db.orders.create_index([("userId", 1)])
    await db.orders.create_index([("orderDate", 1)])

    # 사용자 데이터
    user_ids = {
        "john": ObjectId(),
        "jane": ObjectId()
    }

    users = [
        {
            "_id": user_ids["john"],
            "email": "john@example.com",
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA",
                "coordinates": {
                    "lat": 40.7128,
                    "lng": -74.006,
                }
            },
            "interests": ["sports", "technology"],
            "memberSince": datetime.datetime(2023, 1, 1),
            "isActive": True
        },
        {
            "_id": user_ids["jane"],
            "email": "jane@example.com",
            "name": "Jane Smith",
            "age": 25,
            "address": {
                "street": "456 Market St",
                "city": "San Francisco",
                "country": "USA",
                "coordinates": {
                    "lat": 37.7749,
                    "lng": -122.4194,
                }
            },
            "interests": ["art", "music", "travel"],
            "memberSince": datetime.datetime(2023, 2, 15),
            "isActive": True
        }
    ]

    await db.users.insert_many(users)

    # 제품 데이터
    products = [
        {
            "_id": ObjectId(),
            "sku": "LAPTOP001",
            "name": "Pro Laptop",
            "category": "Electronics",
            "price": 1299.99,
            "specs": {
                "cpu": "Intel i7",
                "ram": "16GB",
                "storage": "512GB SSD",
            },
            "inStock": True,
            "tags": ["laptop", "computer", "work"],
            "ratings": [4.5, 4.8, 4.2],
            "lastUpdated": datetime.datetime.now()
        },
        {
            "_id": ObjectId(),
            "sku": "PHONE001",
            "name": "SmartPhone X",
            "category": "Electronics",
            "price": 699.99,
            "specs": {
                "screen": "6.1 inch",
                "camera": "12MP",
                "storage": "256GB",
            },
            "inStock": True,
            "tags": ["phone", "mobile", "smart device"],
            "ratings": [4.7, 4.6],
            "lastUpdated": datetime.datetime.now()
        },
        {
            "_id": ObjectId(),
            "sku": "BOOK001",
            "name": "Database Design",
            "category": "Books",
            "price": 49.99,
            "specs": {
                "format": "Hardcover",
                "pages": 500,
                "language": "English",
            },
            "inStock": False,
            "tags": ["education", "technology", "programming"],
            "ratings": [4.9],
            "lastUpdated": datetime.datetime.now()
        }
    ]

    await db.products.insert_many(products)

    # 주문 데이터
    orders = [
        {
            "_id": ObjectId(),
            "userId": user_ids["john"],
            "orderDate": datetime.datetime(2024, 1, 15),
            "status": "completed",
            "items": [
                {
                    "productSku": "LAPTOP001",
                    "quantity": 1,
                    "priceAtTime": 1299.99,
                },
                {
                    "productSku": "BOOK001",
                    "quantity": 2,
                    "priceAtTime": 49.99,
                }
            ],
            "totalAmount": 1399.97,
            "shippingAddress": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA",
            },
            "paymentMethod": {
                "type": "credit_card",
                "last4": "4242",
            }
        },
        {
            "_id": ObjectId(),
            "userId": user_ids["jane"],
            "orderDate": datetime.datetime(2024, 2, 1),
            "status": "processing",
            "items": [
                {
                    "productSku": "PHONE001",
                    "quantity": 1,
                    "priceAtTime": 699.99,
                }
            ],
            "totalAmount": 699.99,
            "shippingAddress": {
                "street": "456 Market St",
                "city": "San Francisco",
                "country": "USA",
            },
            "paymentMethod": {
                "type": "paypal",
                "email": "jane@example.com",
            }
        }
    ]

    await db.orders.insert_many(orders)

    print("Seed completed successfully!")
    await client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())