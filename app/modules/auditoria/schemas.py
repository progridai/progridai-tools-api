from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

class AuditoriaBase(BaseModel):
    texto_sanitizado: str
    texto_original: Optional[str] = None
    nome_app: Optional[str] = Field("geral", max_length=100)

class AuditoriaCreate(AuditoriaBase):
    pass

class AuditoriaUpdate(BaseModel):
    texto_sanitizado: Optional[str] = None
    texto_original: Optional[str] = None
    nome_app: Optional[str] = Field(None, max_length=100)

class AuditoriaResponse(AuditoriaBase):
    id: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedAuditoriaResponse(BaseModel):
    total: int
    items: List[AuditoriaResponse]
    limit: int
    offset: int
