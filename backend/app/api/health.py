from fastapi import APIRouter
from app.services.health_service import check_postgres, check_redis, check_qdrant

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    postgres_status = check_postgres()
    redis_status = check_redis()
    qdrant_status = check_qdrant()

    overall_status = "healthy"
    if not postgres_status["ok"] or not redis_status["ok"] or not qdrant_status["ok"]:
        overall_status = "degraded"

    return {
        "service": "InsuranceAIGents API Gateway",
        "status": overall_status,
        "dependencies": {
            "postgres": postgres_status,
            "redis": redis_status,
            "qdrant": qdrant_status
        }
    }