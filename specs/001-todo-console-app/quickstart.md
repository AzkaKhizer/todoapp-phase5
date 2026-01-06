# Quickstart: Todo Console Application

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04

---

## Prerequisites

- Python 3.13 or higher
- UV (Astral's Python package manager)

### Verify Prerequisites

```bash
# Check Python version
python --version
# Expected: Python 3.13.x or higher

# Check UV installation
uv --version
# Expected: uv x.x.x
```

### Install UV (if needed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Project Setup

### 1. Navigate to Project Root

```bash
cd /path/to/Hackathon2
```

### 2. Initialize UV Environment

```bash
# UV automatically creates virtual environment on first run
uv sync
```

### 3. Verify Installation

```bash
uv run python -m todo
# Should display the main menu
```

---

## Running the Application

### Standard Execution

```bash
uv run python -m todo
```

### Alternative (after UV sync)

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Then run directly
python -m todo
```

---

## Running Tests

### All Tests

```bash
uv run pytest
```

### Specific Test Categories

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# With verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src/todo
```

---

## Development Workflow

### 1. Make Changes

Edit files in `src/todo/`:
- `models.py` - Task data structure
- `services.py` - TaskStore logic
- `cli.py` - Console interface

### 2. Run Tests

```bash
uv run pytest
```

### 3. Run Application

```bash
uv run python -m todo
```

### 4. Iterate

Repeat steps 1-3 until all acceptance criteria pass.

---

## Project Structure

```
Hackathon2/
├── pyproject.toml           # Project configuration
├── src/
│   └── todo/
│       ├── __init__.py      # Package marker
│       ├── __main__.py      # Entry point
│       ├── models.py        # Task dataclass
│       ├── services.py      # TaskStore service
│       └── cli.py           # Console interface
└── tests/
    ├── unit/
    │   ├── test_models.py   # Task model tests
    │   └── test_services.py # TaskStore tests
    └── integration/
        └── test_cli.py      # End-to-end tests
```

---

## Common Issues

### Python Version Too Old

```
Error: requires Python >=3.13
```

**Solution**: Install Python 3.13+ from https://python.org or use pyenv:
```bash
pyenv install 3.13.0
pyenv local 3.13.0
```

### UV Not Found

```
command not found: uv
```

**Solution**: Install UV per the instructions above, then restart your terminal.

### Module Not Found

```
ModuleNotFoundError: No module named 'todo'
```

**Solution**: Ensure you're running from the project root and using `uv run`:
```bash
cd /path/to/Hackathon2
uv run python -m todo
```

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `uv run python -m todo` | Run the application |
| `uv run pytest` | Run all tests |
| `uv run pytest -v` | Run tests with verbose output |
| `uv run pytest --tb=short` | Run tests with short traceback |
| `uv sync` | Sync dependencies |
| `uv add --dev <package>` | Add dev dependency |

---

## Spec References

- [spec.md](./spec.md) - Feature specification
- [plan.md](./plan.md) - Implementation plan
- [data-model.md](./data-model.md) - Entity definitions
- [contracts/](./contracts/) - API contracts
