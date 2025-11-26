# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

# 🧠 Database + Models
from app.core.config import init_db
from app.models.content_corpus import ContentCorpus

# 🔗 API Routers
from app.api.v1.endpoints import generate, content_corpus, stage2
from app.api.v1.endpoints import chatbot
from app.api.v1.endpoints import llm_orchestrator
from app.api.v1 import free_chat
from app.api.v1.endpoints import final_pipeline

app = FastAPI()
app.include_router(chatbot.router, prefix="/api/v1")
app.include_router(llm_orchestrator.router, prefix="/api/v1")
app.include_router(free_chat.router, prefix="/api/v1", tags=["free-chat"])

# 🚨 Custom validation error handler for 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("⚠️ Validation Error:", exc.errors())
    try:
        print("🔎 Request Body:", await request.json())
    except Exception:
        print("🔎 Request Body: [Cannot parse request body as JSON]")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# ⏳ Startup hook
@app.on_event("startup")
async def on_startup():
    await init_db()

# 🔌 Include API routers
app.include_router(generate.router, prefix="/api/v1", tags=["Content Corpus"])
app.include_router(content_corpus.router, prefix="/api/v1", tags=["Content Corpus"])
app.include_router(stage2.router, prefix="/api/v1", tags=["Stage 2"])

# 📁 Static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🌍 CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧾 HTML endpoints (for forms)
@app.get("/generate-corpus", tags=["Content Corpus"])
async def serve_generate_html():
    return FileResponse("static/generate_corpus.html", media_type="text/html")

@app.get("/stage2", tags=["Stage 2"])
async def serve_stage2_html():
    return FileResponse("static/stage2_generate.html", media_type="text/html")

@app.get("/orchestrator-test", tags=["Debug"])
async def serve_orchestrator_test():
    return FileResponse("static/orchestrator_test.html", media_type="text/html")

app.include_router(final_pipeline.router, prefix="/api/v1", tags=["Final Lesson"])
