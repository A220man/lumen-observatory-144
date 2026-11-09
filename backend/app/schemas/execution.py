from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class ExecutionBase(BaseModel):
    agent_id: UUID
    input_payload: Dict[str, Any] = Field(default_factory=dict)


class ExecutionCreate(ExecutionBase):
    pass


class ExecutionUpdate(BaseModel):
    status: Optional[str] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ExecutionLogBase(BaseModel):
    level: str = Field(..., pattern="^(info|warning|error|debug)$")
    message: str
    metadata: Optional[Dict[str, Any]] = None


class ExecutionLogCreate(ExecutionLogBase):
    pass


class ExecutionLogResponse(ExecutionLogBase):
    id: UUID
    execution_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionResponse(ExecutionBase):
    id: UUID
    status: str
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionListResponse(BaseModel):
    items: List[ExecutionResponse]
    total: int
    page: int
    page_size: int


class ExecutionWithLogsResponse(ExecutionResponse):
    logs: List[ExecutionLogResponse] = Field(default_factory=list)
