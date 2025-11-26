from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
#the name od the database
DB_NAME = "mongo_project_amit"
# MongoDB connection URI
MONGO_URI = "mongodb://localhost:27017/"


client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
print("✅ Motor client created — database reference ready!")


async def check_connection():
    try:
        await db.command("ping")
        print("✅ Connection to MongoDB successful via motor.")
    except Exception as e:
        print(f"❌ Ping failed: {e}")


if __name__ == "__main__":
    asyncio.run(check_connection())