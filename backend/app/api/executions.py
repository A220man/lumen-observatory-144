from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Agent
from app.models.execution import Execution, ExecutionLog, ExecutionStatus
from app.schemas.execution import (
    ExecutionCreate,
    ExecutionUpdate,
    ExecutionResponse,
    ExecutionListResponse,
    ExecutionLogCreate,
    ExecutionLogResponse,
    ExecutionWithLogsResponse,
)

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    payload: ExecutionCreate,
    db: AsyncSession = Depends(get_db),
) -> Execution:
    """Create a new execution for an agent."""
    # Verify agent exists
    agent_query = select(Agent).where(Agent.id == payload.agent_id)
    agent_result = await db.execute(agent_query)
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    execution = Execution(
        agent_id=payload.agent_id,
        input_payload=payload.input_payload,
        status=ExecutionStatus.PENDING,
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    return execution


@router.get("", response_model=ExecutionListResponse)
async def list_executions(
    agent_id: Optional[UUID] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by execution status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
) -> ExecutionListResponse:
    """List executions with pagination and optional filtering."""
    query = select(Execution)
    count_query = select(func.count(Execution.id))

    if agent_id:
        query = query.where(Execution.agent_id == agent_id)
        count_query = count_query.where(Execution.agent_id == agent_id)
    if status:
        query = query.where(Execution.status == status)
        count_query = count_query.where(Execution.status == status)

    query = query.order_by(Execution.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    executions = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return ExecutionListResponse(
        items=[ExecutionResponse.model_validate(exec) for exec in executions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{execution_id}", response_model=ExecutionWithLogsResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ExecutionWithLogsResponse:
    """Get an execution by ID with its logs."""
    query = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(query)
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    logs_query = select(ExecutionLog).where(ExecutionLog.execution_id == execution_id).order_by(ExecutionLog.timestamp.asc())
    logs_result = await db.execute(logs_query)
    logs = logs_result.scalars().all()

    response = ExecutionWithLogsResponse.model_validate(execution)
    response.logs = [ExecutionLogResponse.model_validate(log) for log in logs]
    return response


@router.patch("/{execution_id}", response_model=ExecutionResponse)
async def update_execution(
    execution_id: UUID,
    payload: ExecutionUpdate,
    db: AsyncSession = Depends(get_db),
) -> Execution:
    """Update an execution (status, output, error)."""
    query = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(query)
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(execution, field, value)

    await db.commit()
    await db.refresh(execution)
    return execution


@router.post("/{execution_id}/logs", response_model=ExecutionLogResponse, status_code=status.HTTP_201_CREATED)
async def add_execution_log(
    execution_id: UUID,
    payload: ExecutionLogCreate,
    db: AsyncSession = Depends(get_db),
) -> ExecutionLog:
    """Add a log entry to an execution."""
    query = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(query)
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    log = ExecutionLog(
        execution_id=execution_id,
        level=payload.level,
        message=payload.message,
        metadata=payload.metadata,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/{execution_id}/logs", response_model=list[ExecutionLogResponse])
async def get_execution_logs(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ExecutionLogResponse]:
    """Get all logs for an execution."""
    query = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(query)
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    logs_query = select(ExecutionLog).where(ExecutionLog.execution_id == execution_id).order_by(ExecutionLog.timestamp.asc())
    logs_result = await db.execute(logs_query)
    logs = logs_result.scalars().all()
    return [ExecutionLogResponse.model_validate(log) for log in logs]
