import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    payload = {
        "name": "Test Agent",
        "description": "A test agent",
        "version": "1.0.0",
        "config": {"model": "gpt-4", "temperature": 0.7},
    }
    response = await client.post("/api/v1/agents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["description"] == "A test agent"
    assert data["version"] == "1.0.0"
    assert data["config"] == {"model": "gpt-4", "temperature": 0.7}
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_agent_invalid_version(client: AsyncClient):
    payload = {
        "name": "Test Agent",
        "version": "invalid-version",
    }
    response = await client.post("/api/v1/agents", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    # Create a few agents first
    for i in range(3):
        await client.post("/api/v1/agents", json={"name": f"Agent {i}", "version": "1.0.0"})

    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_agents_with_pagination(client: AsyncClient):
    response = await client.get("/api/v1/agents?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_list_agents_with_name_filter(client: AsyncClient):
    await client.post("/api/v1/agents", json={"name": "Special Agent", "version": "1.0.0"})
    await client.post("/api/v1/agents", json={"name": "Other Agent", "version": "1.0.0"})

    response = await client.get("/api/v1/agents?name=Special")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for agent in data["items"]:
        assert "Special" in agent["name"]


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient):
    create_response = await client.post("/api/v1/agents", json={"name": "Get Test Agent", "version": "1.0.0"})
    agent_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "Get Test Agent"


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    fake_id = uuid4()
    response = await client.get(f"/api/v1/agents/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient):
    create_response = await client.post("/api/v1/agents", json={"name": "Update Test", "version": "1.0.0"})
    agent_id = create_response.json()["id"]

    update_payload = {"name": "Updated Name", "description": "New description"}
    response = await client.patch(f"/api/v1/agents/{agent_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New description"
    assert data["version"] == "1.0.0"  # unchanged


@pytest.mark.asyncio
async def test_update_agent_not_found(client: AsyncClient):
    fake_id = uuid4()
    response = await client.patch(f"/api/v1/agents/{fake_id}", json={"name": "New Name"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    create_response = await client.post("/api/v1/agents", json={"name": "Delete Test", "version": "1.0.0"})
    agent_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/agents/{agent_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent_not_found(client: AsyncClient):
    fake_id = uuid4()
    response = await client.delete(f"/api/v1/agents/{fake_id}")
    assert response.status_code == 404
