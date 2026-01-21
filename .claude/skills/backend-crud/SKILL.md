---
name: "backend-crud"
description: "Implement clean and secure CRUD operations in FastAPI with user-based access control."
version: "1.0.0"
---

# Backend CRUD Skill

## When to Use This Skill

- Creating API endpoints
- Updating or deleting user-owned data
- Applying auth-based filtering

## Procedure

1. **Validate request data**
2. **Verify user ownership**
3. **Perform DB operation**
4. **Handle not-found cases**
5. **Return consistent responses**

## Output Format

- CRUD route definitions
- ORM queries
- Error handling patterns

## Quality Criteria

- User can access only own data
- Proper HTTP status codes
- No duplicated logic
- Clean separation of layers

## Example

**Input**: "Create user-specific todo CRUD"

**Output**:
- Secure CRUD endpoints
- Ownership checks
