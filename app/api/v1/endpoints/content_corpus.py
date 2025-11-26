from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.crud.crud_content_corpus import get_document_by_id
from bson import ObjectId

router = APIRouter()

@router.get("/content-corpus/{corpus_id}")
async def get_content_corpus(corpus_id: str):
    try:
        doc = await get_document_by_id(corpus_id)
        if not doc:
            return JSONResponse(status_code=404, content={"status": "error", "detail": "Corpus not found"})

        doc["_id"] = str(doc["_id"])  
        return JSONResponse(content=doc)

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})
