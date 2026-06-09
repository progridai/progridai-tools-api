from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from . import schemas, service

router = APIRouter()

@router.get("/", response_model=schemas.PaginatedAuditoriaResponse)
async def list_auditorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    nome_app: Optional[str] = None,
    id_requisicao: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista registros de auditoria com paginação e filtros opcionais.
    """
    total, items = await service.list_auditorias(
        db=db,
        skip=skip,
        limit=limit,
        nome_app=nome_app,
        id_requisicao=id_requisicao,
        start_date=start_date,
        end_date=end_date
    )
    return {
        "total": total,
        "items": items,
        "limit": limit,
        "offset": skip
    }

@router.get("/{id}", response_model=schemas.AuditoriaResponse)
async def get_auditoria(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera um registro de auditoria pelo ID.
    """
    auditoria = await service.get_auditoria(db=db, id=id)
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    return auditoria
