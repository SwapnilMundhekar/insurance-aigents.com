from fastapi import APIRouter
from app.schemas.system_readiness import SystemReadinessResponse
from app.services.system_readiness_service import check_system_readiness

router = APIRouter(prefix='/system', tags=['system'])

@router.get('/readiness', response_model=SystemReadinessResponse)
def system_readiness():
    return SystemReadinessResponse(**check_system_readiness())
