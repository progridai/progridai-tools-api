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
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista registros de auditoria com paginação e filtros opcionais.
    Se nenhuma data for informada, busca automaticamente os registros de hoje.
    """
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if end_date is None:
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    try:
        total, items = await service.list_auditorias(
            db=db,
            skip=skip,
            limit=limit,
            nome_app=nome_app,
            start_date=start_date,
            end_date=end_date
        )
        return {
            "total": total,
            "items": items,
            "limit": limit,
            "offset": skip
        }
    except Exception as e:
        # Retorna erro 503 em vez de 500 para deixar claro que é o banco
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"Não foi possível conectar ao banco de dados. Verifique a configuração DATABASE_URL. Erro: {str(e)}"
        )

@router.get("/{id}", response_model=schemas.AuditoriaResponse)
async def get_auditoria(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera um registro de auditoria pelo ID.
    """
    try:
        auditoria = await service.get_auditoria(db=db, id=id)
        if not auditoria:
            raise HTTPException(status_code=404, detail="Auditoria não encontrada")
        return auditoria
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"Não foi possível conectar ao banco de dados. Erro: {str(e)}"
        )
