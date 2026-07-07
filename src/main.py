from fastapi import FastAPI
from src.api.routes import router
from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservice for asynchronously processing receipts and extracting structured data.",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
