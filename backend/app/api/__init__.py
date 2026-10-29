from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok", "service": "lumen-observatory-api"}

@api_router.get("/")
async def root():
    return {"message": "Lumen Observatory API", "version": "0.1.0"}
