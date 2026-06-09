from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime
from typing import Optional, Tuple, List

from .models import AuditoriaTextoSanitizado
from .schemas import AuditoriaCreate, AuditoriaUpdate

async def create_auditoria(db: AsyncSession, obj_in: AuditoriaCreate) -> AuditoriaTextoSanitizado:
    db_obj = AuditoriaTextoSanitizado(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_auditoria(db: AsyncSession, id: int) -> Optional[AuditoriaTextoSanitizado]:
    result = await db.execute(select(AuditoriaTextoSanitizado).where(AuditoriaTextoSanitizado.id == id))
    return result.scalars().first()

async def list_auditorias(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    nome_app: Optional[str] = None,
    id_requisicao: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Tuple[int, List[AuditoriaTextoSanitizado]]:
    query = select(AuditoriaTextoSanitizado)
    
    if nome_app:
        query = query.where(AuditoriaTextoSanitizado.nome_app == nome_app)
    if id_requisicao:
        query = query.where(AuditoriaTextoSanitizado.id_requisicao == id_requisicao)
    if start_date:
        query = query.where(AuditoriaTextoSanitizado.data_criacao >= start_date)
    if end_date:
        query = query.where(AuditoriaTextoSanitizado.data_criacao <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get items
    query = query.order_by(AuditoriaTextoSanitizado.id.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return total, items
