# Lumen Observatory 144

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


The open-source app everyone uses to manage agents at work.

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/openapi.json
- **PostgreSQL**: localhost:5432

### Manual Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
lumen-observatory-144/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database models & session
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app entry
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features (Roadmap)

- [x] Project skeleton with FastAPI + React
- [ ] Agent Registry CRUD API
- [ ] Agent Execution Engine
- [ ] Workspace & Project Management
- [ ] Dashboard UI

## License

MIT

Maintainer: Ryan Vo <ryandtvo@gmail.com>
