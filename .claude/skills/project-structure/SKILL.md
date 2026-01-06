---
name: "project-structure"
description: "Define and enforce Phase I Python project structure and folder layout. Use when generating source code directories and entry points."
version: "1.0.0"
---

# Project Structure Skill

## When to Use This Skill
- User asks "how to organize project"
- User wants clear /src directory, modules, and entry points

## Procedure
1. **Create root folders**:
   - /src
   - /specs/history
2. **Module separation**:
   - `task.py` → Task entity
   - `task_manager.py` → Feature functions
   - `cli.py` → CLI menu & interaction
3. **Entry point**:
   - `main.py` calls CLI loop
4. **README.md & CLAUDE.md placeholders**
5. **No global state abuse**
6. **Prepare for QA verification**

## Output Format
- Folder structure diagram
- File names with purpose
- README.md placeholders

## Quality Criteria
- Clear separation of concerns
- Traceable to spec and plan
- Ready for Claude Code execution

## Example
**Input**: "Generate Phase I folder layout"
**Output**:
/src
  task.py
  task_manager.py
  cli.py
  main.py
/specs/history
README.md
CLAUDE.md
