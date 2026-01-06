# The Evolution of Todo: Spec-Driven, Agentic AI Development

A hackathon project demonstrating the evolution from a simple console application to a full-stack web application using Spec-Driven Development (SDD).

## Phases

### Phase I: Todo Console Application
A Python console-based todo application with in-memory storage.

```bash
cd todo
uv run python -m todo
```

### Phase II: Todo Full-Stack Web Application
A modern, full-stack todo application with FastAPI backend and Next.js frontend.

## Phase II Features

- User registration and authentication with JWT tokens
- Create, read, update, and delete tasks
- Toggle task completion status
- Multi-user isolation (users can only see their own tasks)
- Responsive design with dark mode support
- Type-safe API with Pydantic schemas

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** (Neon) - Cloud database
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form handling

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (or Neon account)
- UV (Python package manager)
- pnpm (Node.js package manager)

## Setup

### Backend Setup

```bash
cd backend

# Copy environment variables
cp .env.example .env

# Edit .env with your database credentials:
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# JWT_SECRET=your-secret-key
# JWT_EXPIRY_HOURS=24
# CORS_ORIGINS=http://localhost:3000

# Install dependencies with UV
uv sync

# Run the backend
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### Frontend Setup

```bash
cd frontend

# Copy environment variables
cp .env.example .env

# Edit .env:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Install dependencies with pnpm
pnpm install

# Run the development server
pnpm dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks` - List all tasks (paginated)
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Full update task
- `PATCH /api/tasks/{id}` - Partial update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Database connection
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── main.py            # FastAPI application
│   │   ├── dependencies/      # FastAPI dependencies
│   │   ├── models/            # SQLModel models
│   │   ├── routers/           # API routes
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   └── tests/                 # Backend tests
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   └── lib/               # Utilities
│   └── __tests__/             # Frontend tests
├── specs/                     # Design specifications
└── todo/                      # Phase I console app
```

## Running Tests

### Phase I Tests
```bash
uv run pytest
```

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## License

MIT License
