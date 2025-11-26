# tests/conftest.py
import pytest
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
async def test_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_db"]
    yield db
    client.drop_database("test_db")  # מנקה אחרי הטסט