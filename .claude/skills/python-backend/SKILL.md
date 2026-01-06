---
name: "python-backend"
description: "Implement the Phase I Todo app backend in Python 3.13+ for console execution. Use when generating Python code for in-memory storage and task management."
version: "1.0.0"
---

# Python Backend Skill

## When to Use This Skill
- User asks to "implement Python backend"
- User wants in-memory task management logic
- User needs CLI interaction with Python modules

## Procedure
1. **Read spec**: Reference feature specifications from `spec-driven`
2. **Create data models**: Task entity with ID, title, description, status
3. **Implement core features**:
   - Add Task
   - View Tasks
   - Update Task
   - Delete Task
   - Mark Complete/Incomplete
4. **Ensure in-memory storage only**
5. **Implement CLI interaction** for each feature
6. **Add input validation and error handling**

## Output Format
- Modular Python code under `/src`
- Entry point `main.py` for running the CLI
- Function-based or class-based architecture

## Quality Criteria
- Correct behavior for all features
- No persistence beyond memory
- Clean, readable, modular Python code
- Deterministic and testable

## Example
**Input**: "Generate Add Task module"
**Output**:
- `task.py` with Task class
- `task_manager.py` with add_task function
- CLI prompts for title/description
- Returns new task with unique ID and status incomplete
