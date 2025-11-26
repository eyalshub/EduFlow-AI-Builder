import asyncio
from app.models.content_corpus import init_content_corpus

async def init_all_collections():
    await init_content_corpus()

if __name__ == "__main__":
    asyncio.run(init_all_collections())
