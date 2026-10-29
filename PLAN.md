# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-setup

## Roadmap

### project-setup — Project Setup & Skeleton

Status: done

Acceptance:
- FastAPI backend runs with health endpoint
- React frontend builds and serves
- Docker compose works for local development
- Basic project structure with backend/frontend separation

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/db/session.py`, `backend/app/db/base.py`, `backend/app/api/__init__.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/Layout.tsx`, `frontend/src/pages/Dashboard.tsx`, `docker-compose.yml`

Tests: `backend: health endpoint returns 200`, `frontend: npm run build succeeds`

### agent-registry — Agent Registry API

Status: planned

Acceptance:
- CRUD endpoints for agents
- Agent metadata storage (name, description, version, config)
- List/filter agents

### agent-execution — Agent Execution Engine

Status: planned

Acceptance:
- Run agent with input payload
- Stream execution logs
- Track execution status/history

### workspace-management — Workspace & Project Management

Status: planned

Acceptance:
- Create/list workspaces
- Projects within workspaces
- Agent assignments to projects

### ui-dashboard — Dashboard UI

Status: planned

Acceptance:
- Agent list view
- Execution history view
- Workspace/project navigation

