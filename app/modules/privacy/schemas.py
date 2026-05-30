from typing import List, Optional
from pydantic import BaseModel, Field

class EntityOut(BaseModel):
    type: str
    token: Optional[str] = None
    value: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    score: Optional[float] = None

class SanitizeRequest(BaseModel):
    text: str = Field(..., description="The free text to be sanitized")
    restoreEnabled: bool = Field(False, description="If true, generates a token map for future restoration")

class SanitizeResponse(BaseModel):
    sanitizedText: str
    mapId: Optional[str] = None
    blocked: bool = False
    entities: List[EntityOut]

class RestoreRequest(BaseModel):
    mapId: str
    text: str

class RestoreResponse(BaseModel):
    restoredText: str

class DetectRequest(BaseModel):
    text: str
    includeValues: bool = False

class DetectResponse(BaseModel):
    hasSensitiveData: bool
    entities: List[EntityOut]

class ValidateRequest(BaseModel):
    text: str

class ValidateResponse(BaseModel):
    valid: bool
    blocked: bool
    message: str
    entities: Optional[List[EntityOut]] = None

class DeleteMapResponse(BaseModel):
    deleted: bool
    mapId: str
