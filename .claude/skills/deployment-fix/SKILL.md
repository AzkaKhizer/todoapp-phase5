---
name: "deployment-fix"
description: "Debug and fix deployment issues for FastAPI and Next.js on Railway, Vercel, or similar platforms."
version: "1.0.0"
---

# Deployment Debugging Skill

## When to Use This Skill

- Backend fails to deploy
- Database connection errors
- Missing environment variables
- psycopg or build errors

## Procedure

1. **Check build logs**
2. **Verify env variables**
3. **Confirm correct DB driver**
4. **Validate startup command**
5. **Test health endpoint**

## Output Format

- Root cause explanation
- Fix steps
- Correct deployment config

## Quality Criteria

- Clear actionable fixes
- Platform-specific advice
- No guessing

## Example

**Input**: "Railway backend not starting"

**Output**:
- Error diagnosis
- Exact fix steps
