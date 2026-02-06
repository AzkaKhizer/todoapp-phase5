# Quick Start Guide

This guide will help you get the Todo application running locally in under 10 minutes.

## Prerequisites

Ensure you have the following installed:

- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **uv** - Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **PostgreSQL** - Local or [Neon](https://neon.tech) (free tier)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo/todoapp-phase3.git
cd todoapp-phase3
```

## Step 2: Set Up the Backend

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/todoapp
BETTER_AUTH_SECRET=your-super-secret-key-change-in-production
BETTER_AUTH_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
EOF
```

If using Neon, replace `DATABASE_URL` with your Neon connection string.

### Start the Backend

```bash
uv run uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Verify at: http://localhost:8000/api/health

## Step 3: Set Up the Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
```

### Start the Frontend

```bash
npm run dev
```

You should see:
```
▲ Next.js 15.x
- Local: http://localhost:3000
```

## Step 4: Use the Application

1. Open http://localhost:3000 in your browser
2. Click "Register" to create an account
3. Start creating tasks!

## Features to Try

### Basic Tasks
- Create a task with title and description
- Mark tasks as complete
- Delete tasks

### Enhanced Features
- **Due Dates**: Set a due date when creating a task
- **Priorities**: Set priority (low, medium, high, urgent)
- **Tags**: Add tags to organize tasks
- **Filters**: Filter tasks by status, priority, or tags
- **Search**: Search tasks by title

### Real-Time Features
- Open the app in two browser tabs
- Create a task in one tab
- See it appear in the other tab instantly!

### Activity Log
- Navigate to the Activity page
- View your task history
- Check productivity metrics

## Troubleshooting

### Backend won't start

**Database connection error:**
```
Ensure PostgreSQL is running and DATABASE_URL is correct.
For Neon: Check your connection string includes ?sslmode=require
```

**Port already in use:**
```bash
# Use a different port
uv run uvicorn app.main:app --reload --port 8001
# Update frontend .env: NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

### Frontend won't start

**Port 3000 in use:**
```bash
npm run dev -- --port 3001
```

**API connection error:**
```
Ensure backend is running and NEXT_PUBLIC_API_URL is correct.
Check browser console for CORS errors.
```

### Authentication issues

**"Invalid token" errors:**
```
1. Clear browser cookies/localStorage
2. Register a new account
3. Check BETTER_AUTH_SECRET matches in backend .env
```

## Next Steps

### Run Tests

```bash
# Backend tests
cd backend
uv run pytest tests/unit -v

# Frontend build
cd frontend
npm run build
```

### Local Kubernetes Deployment

See [Kubernetes Guide](./KUBERNETES.md) for deploying with Dapr and Kafka.

### Cloud Deployment

See [Azure Deployment Guide](./AZURE.md) for deploying to Azure AKS.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │
│   (Next.js)     │     │    (FastAPI)    │
│   Port 3000     │◀────│    Port 8000    │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   PostgreSQL    │
                        │   (Database)    │
                        └─────────────────┘
```

For event-driven features (reminders, real-time sync), the full architecture includes:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│     Kafka       │
│   (Next.js)     │◀────│    (FastAPI)    │◀────│   (Events)      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
        │                        │
        │ WebSocket              │
        └────────────────────────┘
```
