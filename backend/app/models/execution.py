import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Optional
from sqlalchemy import Column, String, Text, DateTime, JSON, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExecutionStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Execution(Base):
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False, index=True)
    input_payload = Column(JSON, nullable=False, default=dict)
    output_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_executions_agent_id_status", "agent_id", "status"),
        Index("ix_executions_created_at", "created_at"),
    )

    agent = relationship("Agent", backref="executions")

    def __repr__(self) -> str:
        return f"<Execution(id={self.id}, agent_id={self.agent_id}, status={self.status})>"


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(20), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_execution_logs_execution_id_timestamp", "execution_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<ExecutionLog(id={self.id}, execution_id={self.execution_id}, level={self.level})>"
