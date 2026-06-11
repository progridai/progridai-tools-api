from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class AuditoriaTextoSanitizado(Base):
    __tablename__ = "auditoria_texto_sanitizado"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    nome_app = Column(String(100), server_default='geral', nullable=False)
    texto_original = Column(Text, nullable=True)
    texto_sanitizado = Column(Text, nullable=False)
