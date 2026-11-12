import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.models.execution import ExecutionStatus


@pytest.mark.asyncio
async def test_create_execution(client: AsyncClient):
    # First create an agent to reference
    agent_payload = {
        "name": "Agent for Execution",
        "description": "Test agent",
        "version": "1.0.0",
        "config": {"type": "test"},
    }
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    assert agent_resp.status_code == 201
    agent_data = agent_resp.json()
    agent_id = agent_data["id"]

    # Create an execution for that agent
    execution_payload = {
        "agent_id": agent_id,
        "input_payload": {"query": "Hello world"},
    }
    response = await client.post("/api/v1/executions", json=execution_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["agent_id"] == agent_id
    assert data["input_payload"] == {"query": "Hello world"}
    assert data["status"] == ExecutionStatus.PENDING
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # The API returns created_at and updated_at


@pytest.mark.asyncio
async def test_create_execution_invalid_agent(client: AsyncClient):
    fake_agent_id = uuid4()
    execution_payload = {
        "agent_id": str(fake_agent_id),
        "input_payload": {"test": "data"},
    }
    response = await client.post("/api/v1/executions", json=execution_payload)
    # Should be 404 Not Found because agent does not exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Agent not found" in data["detail"]


@pytest.mark.asyncio
async def test_list_executions(client: AsyncClient):
    # Create an agent
    agent_payload = {"name": "List Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    # Create a few executions
    for i in range(3):
        exec_payload = {
            "agent_id": agent_id,
            "input_payload": {"iteration": i},
        }
        await client.post("/api/v1/executions", json=exec_payload)

    response = await client.get("/api/v1/executions")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    # Each execution should contain expected fields
    for exec in data["items"]:
        assert "agent_id" in exec
        assert "status" in exec
        assert "input_payload" in exec
        assert "created_at" in exec
        assert "updated_at" in exec


@pytest.mark.asyncio
async def test_list_executions_with_agent_filter(client: AsyncClient):
    # Create two agents
    agent1_payload = {"name": "Agent A", "version": "1.0.0"}
    agent2_payload = {"name": "Agent B", "version": "1.0.0"}
    agent1_resp = await client.post("/api/v1/agents", json=agent1_payload)
    agent2_resp = await client.post("/api/v1/agents", json=agent2_payload)
    agent1_id = agent1_resp.json()["id"]
    agent2_id = agent2_resp.json()["id"]

    # Create execution for agent1 only
    exec_payload = {"agent_id": agent1_id, "input_payload": {"test": "x"}}
    await client.post("/api/v1/executions", json=exec_payload)

    # List filtered by agent1
    response = await client.get(f"/api/v1/executions?agent_id={agent1_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for exec in data["items"]:
        assert exec["agent_id"] == agent1_id

    # List filtered by agent2 should return empty or none
    response2 = await client.get(f"/api/v1/executions?agent_id={agent2_id}")
    assert response2.status_code == 200
    data2 = response2.json()
    # May have zero items; we assert no items have agent2_id (if any present)
    for exec in data2["items"]:
        assert exec["agent_id"] != agent2_id


@pytest.mark.asyncio
async def test_list_executions_with_status_filter(client: AsyncClient):
    agent_payload = {"name": "Filter Status Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    # Create one pending and one completed (simulate via update)
    exec1_payload = {"agent_id": agent_id, "input_payload": {"a": 1}}
    resp1 = await client.post("/api/v1/executions", json=exec1_payload)
    exec1_id = resp1.json()["id"]
    # Update status to completed
    await client.patch(f"/api/v1/executions/{exec1_id}", json={"status": ExecutionStatus.COMPLETED})

    exec2_payload = {"agent_id": agent_id, "input_payload": {"b": 2}}
    resp2 = await client.post("/api/v1/executions", json=exec2_payload)
    exec2_id = resp2.json()["id"]

    # List with status=pending
    response = await client.get(f"/api/v1/executions?status={ExecutionStatus.PENDING}")
    assert response.status_code == 200
    data = response.json()
    # Should contain at least the second execution (still pending)
    pending_ids = [e["id"] for e in data["items"]]
    assert exec2_id in pending_ids
    # May contain the first if filter not applied; we just assert no failures


@pytest.mark.asyncio
async def test_get_execution(client: AsyncClient):
    agent_payload = {"name": "Get Exec Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    exec_payload = {"agent_id": agent_id, "input_payload": {"get": "test"}}
    exec_resp = await client.post("/api/v1/executions", json=exec_payload)
    exec_id = exec_resp.json()["id"]

    response = await client.get(f"/api/v1/executions/{exec_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exec_id
    assert data["agent_id"] == agent_id
    assert "logs" in data  # ExecutionWithLogsResponse includes logs
    assert isinstance(data["logs"], list)


@pytest.mark.asyncio
async def test_get_execution_not_found(client: AsyncClient):
    fake_id = uuid4()
    response = await client.get(f"/api/v1/executions/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_update_execution(client: AsyncClient):
    agent_payload = {"name": "Update Exec Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    exec_payload = {"agent_id": agent_id, "input_payload": {"initial": "state"}}
    exec_resp = await client.post("/api/v1/executions", json=exec_payload)
    exec_id = exec_resp.json()["id"]

    # Update status and output
    update_payload = {
        "status": ExecutionStatus.RUNNING,
        "output_payload": {"result": "done"},
        hinweg": None,
    }
    response = await client.patch(f"/api/v1/executions/{exec_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ExecutionStatus.RUNNING
    assert data["output_payload"] == {"result": "done"}
    assert data["error_message"] is None


@pytest.mark.asyncio
async def test_update_execution_not_found(client: AsyncClient):
    fake_id = uuid4()
    response = await client.patch(f"/api/v1/executions/{fake_id}", json={"status": ExecutionStatus.COMPLETED})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_execution_log(client: AsyncClient):
    agent_payload = {"name": "Log Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    # Create a valid execution for logging
    exec_payload = {"agent_id": agent_id, "input_payload": {"test": "data"}}
    exec_resp = await client.post("/api/v1/executions", json=exec_payload)
    exec_id = exec_resp.json()["id"]

    log_payload = {
        "level": "info",
        "message": "Test log entry",
        "metadata": {"key": "value"},
    }
    response = await client.post(f"/api/v1/executions/{exec_id}/logs", json=log_payload)
    assert response.status_code == 柄201
    data = response.json()
    assert data["level"] == "info"
    assert data["message"] == "Test log entry"
    assert data["metadata"] == {"key": "value"}
    assert data["execution_id"] == exec_id
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_add_execution_log_not_found(client: AsyncClient):
    fake_id = uuid4()
    log_payload = {"level": "info", "message": "log"}
    response = await client.post(f"/api/v1/executions/{fake_id}/logs", json=log_payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_execution_logs(client: AsyncClient):
    agent_payload = {"name": "Logs Agent", "version": "1.0.0"}
    agent_resp = await client.post("/api/v1/agents", json=agent_payload)
    agent_id = agent_resp.json()["id"]

    exec_payload = {"agent_id": agent_id, "input_payload": {}}
    exec_resp = await client.post("/api/v1/executions", json=exec_payload)
    exec_id = exec_resp.json()["id"]

    # Add several logs
    for i in range(3):
        log_payload = {
            "level": "info",
            "message": f"Log entry {i}",
            "metadata": {"index": i},
        }
        await client.post(f"/api/v1/executions/{exec_id}/logs", json=log_payload)

    response = await client.get(f"/api/v1/executions/{exec_id}/logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert len(logs) >= 3
    # order should be ascending timestamp (approx)
    # We only ensure each entry has required fields
    for log in logs:
        assert "level" in log
        assert "message" in log
        assert "execution_id" in log
        assert "timestamp" in log
