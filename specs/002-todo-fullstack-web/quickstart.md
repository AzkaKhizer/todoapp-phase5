# Quickstart Guide: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05
**Spec**: @specs/002-todo-fullstack-web/spec.md

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| pnpm | 9+ | Frontend package manager |
| UV | Latest | Python package manager |
| Git | 2.40+ | Version control |

### External Services

| Service | Purpose | Setup |
|---------|---------|-------|
| Neon PostgreSQL | Database | Create free account at neon.tech |

---

## Project Structure

```
Hackathon2/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLModel models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── task.py
│   │   ├── routers/           # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── tasks.py
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── task.py
│   │   └── dependencies/      # FastAPI dependencies
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── tests/
│   ├── pyproject.toml
│   └── .env
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx       # Landing
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── dashboard/
│   │   ├── components/        # React components
│   │   │   ├── ui/
│   │   │   ├── forms/
│   │   │   └── layout/
│   │   ├── lib/               # Utilities
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   └── hooks/             # Custom hooks
│   │       ├── useAuth.ts
│   │       └── useTasks.ts
│   ├── package.json
│   └── .env.local
└── specs/                      # Specifications
    └── 002-todo-fullstack-web/
```

---

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
cd Hackathon2
git checkout 002-todo-fullstack-web
```

### 2. Setup Backend

```bash
# Create backend directory
mkdir -p backend/app

# Initialize Python project
cd backend
uv init
uv add fastapi uvicorn sqlmodel asyncpg python-jose bcrypt python-dotenv

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET=your-256-bit-secret-key-here
JWT_EXPIRY_HOURS=24
CORS_ORIGINS=http://localhost:3000
EOF
```

### 3. Setup Frontend

```bash
# Create frontend directory
cd ../frontend

# Initialize Next.js project
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Install additional dependencies
pnpm add react-hook-form

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

### 4. Configure Neon Database

1. Create account at [neon.tech](https://neon.tech)
2. Create new project "todo-fullstack"
3. Copy connection string
4. Update `backend/.env` with connection string

### 5. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pnpm dev
```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection | `postgresql+asyncpg://user:pass@host/db` |
| JWT_SECRET | Secret for signing tokens | 64-character random string |
| JWT_EXPIRY_HOURS | Token validity period | `24` |
| CORS_ORIGINS | Allowed frontend origins | `http://localhost:3000` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API base URL | `http://localhost:8000/api` |

---

## Development URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## Common Commands

### Backend

```bash
# Run development server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Frontend

```bash
# Run development server
pnpm dev

# Build for production
pnpm build

# Run production build
pnpm start

# Run tests
pnpm test

# Lint code
pnpm lint

# Type check
pnpm type-check
```

---

## Database Operations

### Create Tables (First Run)

Tables are auto-created on first startup via SQLModel's `create_all()`.

### Reset Database

```bash
# In Neon dashboard: delete and recreate database
# Or run SQL:
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

---

## Testing Credentials

For development/testing, use these credentials:

| Email | Password | Purpose |
|-------|----------|---------|
| test@example.com | password123 | Primary test user |
| user2@example.com | password456 | Secondary test user |

---

## Troubleshooting

### Backend won't start

1. Check DATABASE_URL is correct
2. Verify Neon database is accessible
3. Check port 8000 is not in use

### Frontend can't connect to backend

1. Verify backend is running on port 8000
2. Check CORS_ORIGINS includes frontend URL
3. Verify NEXT_PUBLIC_API_URL is correct

### Database connection errors

1. Check Neon project is active (not sleeping)
2. Verify connection string format
3. Check network connectivity

---

## Next Steps

1. **Verify Setup**: Access http://localhost:3000 and http://localhost:8000/docs
2. **Start Coding**: Begin with Phase 1 tasks in tasks.md
3. **Run Tests**: Execute test suite after each phase
4. **Deploy**: Follow deployment guide when ready

---

## Related Documents

- @specs/002-todo-fullstack-web/spec.md - Feature specification
- @specs/002-todo-fullstack-web/plan.md - Implementation plan
- @specs/002-todo-fullstack-web/tasks.md - Task breakdown
- @specs/002-todo-fullstack-web/research.md - Technology decisions
