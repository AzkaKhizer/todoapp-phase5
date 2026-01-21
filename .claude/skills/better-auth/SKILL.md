---
name: "backend-auth"
description: "Implement secure authentication and authorization in FastAPI using JWT. Use when building or protecting backend APIs."
version: "1.0.0"
---

# Backend Authentication Skill

## When to Use This Skill

- User asks to protect FastAPI routes
- User mentions JWT, auth middleware, or token validation
- Backend requires user-based access control
- Debugging authentication or authorization issues

## Procedure

1. **Load secrets** from environment variables
2. **Validate JWT** signature and expiration
3. **Extract user identity** from token payload
4. **Provide FastAPI dependency** for route protection
5. **Enforce user-level data isolation**

## Output Format

- JWT utility functions
- FastAPI `Depends()` auth dependency
- Protected route examples
- Environment variable requirements

## Quality Criteria

- Tokens must be verified cryptographically
- Expired or invalid tokens must raise HTTP 401
- No secrets hardcoded
- Follow FastAPI best practices
- Minimal and secure implementation

## Example

**Input**: "Protect this FastAPI route with JWT"

**Output**:
- JWT decode function
- `get_current_user` dependency
- Example protected endpoint
