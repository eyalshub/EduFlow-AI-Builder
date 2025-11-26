# tests/core/test_config.py
# This file contains tests for the core configuration of the MongoDB connection and Beanie ORM initialization.
import pytest
import asyncio
from app.core import config


@pytest.mark.asyncio
async def test_mongo_connection():
    """Test that MongoDB is alive via ping."""
    try:
        await config.check_connection()
    except Exception as e:
        pytest.fail(f"MongoDB ping failed: {e}")


@pytest.mark.asyncio
async def test_beanie_initialization():
    """Test Beanie initialization without errors."""
    try:
        await config.init_db()
    except Exception as e:
        pytest.fail(f"Beanie initialization failed: {e}")
