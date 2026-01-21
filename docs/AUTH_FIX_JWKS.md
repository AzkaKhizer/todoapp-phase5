# Better Auth Session Validation Fix

## Problem Summary

After successful login, the dashboard would immediately redirect back to login page with the following symptoms:

- Login succeeds and redirect to dashboard happens
- `/api/auth/get-session` returns 500 Internal Server Error
- User is immediately logged out
- ProtectedRoute keeps redirecting to `/login`
- Browser console shows JOSE/JWK/algorithm errors

## Root Cause

Better Auth JWT plugin (v1.4.12) by default uses **JWKS (JSON Web Key Set)** with asymmetric cryptography (RS256/EdDSA), even when you configure `algorithm: "HS256"` in the JWT settings.

The plugin creates:
1. A `jwk` table in the database to store key pairs
2. Asymmetric key pairs (public/private keys)
3. JWKS endpoints for key distribution

This caused a mismatch:
- **Frontend**: Trying to use RS256/EdDSA via JWKS
- **Backend**: Expecting HS256 with shared secret
- **Result**: JWT verification fails → 500 error → logout

## The Fix

### 1. Disable JWKS in Better Auth Server Configuration

**File**: `frontend/src/lib/auth-server.ts`

```typescript
export const auth = betterAuth({
  database: pool,
  secret: SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  emailAndPassword: {
    enabled: true,
  },

  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },

  plugins: [
    jwt({
      jwt: {
        secret: SECRET,
        expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
        algorithm: "HS256", // Use HS256 with shared secret
        issuer: process.env.BETTER_AUTH_URL || "http://localhost:3000",
        audience: process.env.BETTER_AUTH_URL || "http://localhost:3000",
        definePayload: async ({ user, session }) => {
          return {
            sub: user.id,
            email: user.email,
            name: user.name,
            sessionId: session.id,
          };
        },
      },
      // CRITICAL: Disable JWKS to force HS256-only JWT signing
      // Without this, Better Auth creates asymmetric keys and uses RS256/EdDSA
      jwks: false,
    }),
  ],
});
```

**Key change**: Added `jwks: false` to the JWT plugin configuration.

### 2. Environment Variables

Ensure both frontend and backend use the **exact same secret**:

**Frontend** (`.env`):
```bash
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

**Backend** (`.env`):
```bash
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
```

**CRITICAL**: The `BETTER_AUTH_SECRET` must be identical in both files.

### 3. Backend Configuration (Already Correct)

The backend was already correctly configured to verify HS256 tokens:

**File**: `backend/app/services/auth.py`

```python
def verify_token(token: str) -> dict:
    """Verify a Better Auth JWT token and return the payload.

    Uses HS256 with BETTER_AUTH_SECRET for verification.
    """
    payload = jwt.decode(
        token,
        settings.better_auth_secret,  # Shared secret
        algorithms=["HS256"],  # HS256 only
        options={
            "verify_aud": False,
            "verify_iss": False,
            "leeway": 60,
        }
    )
    return payload
```

## What This Fix Does

1. **Disables JWKS**: Prevents Better Auth from creating asymmetric key pairs
2. **Forces HS256**: Ensures all JWTs are signed with HS256 + shared secret
3. **Eliminates Database Dependency**: No `jwk` table needed
4. **Enables Offline Operation**: Works without BetterAuth cloud service
5. **Fixes Session Verification**: `/api/auth/get-session` now returns 200

## Testing the Fix

### 1. Restart Both Servers

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Test Authentication Flow

1. Navigate to `http://localhost:3000/login`
2. Login with test credentials
3. Should redirect to dashboard
4. Dashboard should stay open (no immediate logout)
5. Refresh the page - should remain logged in

### 3. Verify Session Endpoint

```bash
# Login first, then check session
curl http://localhost:3000/api/auth/get-session \
  -H "Cookie: better-auth.session_token=<your-session-cookie>"
```

Should return:
```json
{
  "session": {...},
  "user": {...}
}
```

**Not**: 500 Internal Server Error

### 4. Check Browser Console

Should see NO errors related to:
- JOSE
- JWK
- "Invalid algorithm"
- "Key not found"
- "JWKS"

## Database Cleanup (Optional)

If a `jwk` table was created before this fix, you can remove it:

```sql
-- Connect to your database
DROP TABLE IF EXISTS jwk CASCADE;
```

Or use the provided cleanup script:

```bash
cd frontend
npx tsx src/scripts/cleanup-jwks.ts
```

The table won't be used anymore with `jwks: false`, so cleanup is optional.

## Success Criteria

- `/api/auth/get-session` returns 200 OK
- Dashboard stays open after login
- Page refresh does NOT log user out
- No JOSE / JWK / algorithm errors in console
- Auth works fully offline (no BetterAuth website calls)
- Users can login, logout, and refresh without issues

## Technical Details

### Why JWKS Was Enabled

Better Auth JWT plugin defaults to JWKS for several reasons:
1. **OAuth/OIDC Compliance**: JWKS is standard for OAuth providers
2. **Key Rotation**: Asymmetric keys can be rotated without downtime
3. **Remote Verification**: Third parties can verify tokens without shared secret
4. **Security**: Private keys never leave the auth server

### Why We Disabled It

For this project:
1. **Simplicity**: HS256 with shared secret is simpler
2. **No Remote Services**: Backend is trusted, not third-party
3. **No Key Rotation**: Small project, can restart for secret changes
4. **Backend Integration**: Backend expects HS256 verification
5. **Offline Operation**: No dependency on BetterAuth cloud

### Migration Path (If Needed)

If you later want to use JWKS:

1. Remove `jwks: false` from auth-server.ts
2. Update backend to fetch JWKS from frontend:
   ```python
   from jose import jwk
   # Fetch JWKS from http://localhost:3000/api/auth/jwks
   # Use public key to verify RS256/EdDSA tokens
   ```
3. Update environment variables to include JWKS URL
4. Restart both services

## Related Files

- `frontend/src/lib/auth-server.ts` - Better Auth server config (FIXED)
- `frontend/src/lib/auth-client.ts` - Better Auth client config
- `backend/app/services/auth.py` - JWT verification service
- `backend/app/config.py` - Backend configuration
- `backend/app/dependencies/auth.py` - Auth dependencies

## References

- [Better Auth JWT Plugin Docs](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx)
- [Better Auth JWKS Configuration](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx#jwks)
- [JOSE JWT Library](https://github.com/panva/jose)
