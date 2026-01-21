---
name: "frontend-auth"
description: "Implement frontend authentication using Next.js App Router, Better Auth, and JWT handling."
version: "1.0.0"
---

# Frontend Authentication Skill

## When to Use This Skill

- Setting up login or signup flows
- Managing user sessions
- Calling protected backend APIs
- Protecting frontend routes

## Procedure

1. **Configure Better Auth**
2. **Enable JWT plugin**
3. **Store and retrieve tokens securely**
4. **Attach token to API requests**
5. **Handle unauthenticated states**

## Output Format

- Better Auth config
- Auth-aware API client
- Protected route examples
- Environment variable list

## Quality Criteria

- No token leakage to UI
- Use environment variables correctly
- Clear auth flow
- Minimal boilerplate
- Works with App Router

## Example

**Input**: "Protect dashboard route"

**Output**:
- Middleware or layout-based protection
- Redirect unauthenticated users
