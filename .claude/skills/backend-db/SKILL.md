---
name: "backend-db"
description: "Design and integrate PostgreSQL database using SQLAlchemy and Neon in FastAPI projects."
version: "1.0.0"
---

# Backend Database Skill

## When to Use This Skill

- Setting up PostgreSQL
- Designing database models
- Integrating SQLAlchemy
- Fixing DB connection errors

## Procedure

1. **Load database URL from env**
2. **Create SQLAlchemy engine**
3. **Define ORM models**
4. **Create DB session dependency**
5. **Handle migrations-ready structure**

## Output Format

- SQLAlchemy engine setup
- Base model definition
- Session dependency
- Example CRUD query

## Quality Criteria

- psycopg driver supported
- No credentials in code
- Clean session handling
- Scalable project structure

## Example

**Input**: "Connect FastAPI to Neon"

**Output**:
- Database config
- Session dependency
- Health check query
