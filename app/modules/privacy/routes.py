from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.modules.privacy.schemas import (
    SanitizeRequest, SanitizeResponse,
    RestoreRequest, RestoreResponse,
    DetectRequest, DetectResponse,
    ValidateRequest, ValidateResponse,
    DeleteMapResponse
)
from app.modules.privacy.service import PrivacyService
from app.modules.privacy.token_store import delete_map

router = APIRouter(prefix="/privacy", tags=["Privacy"], dependencies=[Depends(get_api_key)])

@router.post("/sanitize", response_model=SanitizeResponse)
def sanitize_text(request: SanitizeRequest):
    return PrivacyService.sanitize(request)

@router.post("/restore", response_model=RestoreResponse)
def restore_text(request: RestoreRequest):
    return PrivacyService.restore(request)

@router.post("/detect", response_model=DetectResponse)
def detect_data(request: DetectRequest):
    return PrivacyService.detect(request)

@router.post("/validate", response_model=ValidateResponse)
def validate_text(request: ValidateRequest):
    return PrivacyService.validate(request)

@router.delete("/maps/{mapId}", response_model=DeleteMapResponse)
def delete_token_map(mapId: str):
    deleted = delete_map(mapId)
    return DeleteMapResponse(deleted=deleted, mapId=mapId)
