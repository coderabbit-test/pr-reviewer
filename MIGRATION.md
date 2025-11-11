# Migration Guide: Python to JavaScript

This document describes the migration of the Authentication API from Python (FastAPI) to JavaScript (Express.js).

## Overview

The project has been migrated from:
- **Python 3.x + FastAPI** → **Node.js 18+ + Express.js**
- **Pydantic** → **Zod** (for validation)
- **firebase-admin (Python)** → **firebase-admin (Node.js)**
- **PyJWT** → **jsonwebtoken**
- **uvicorn** → **Node.js native server**

## Dependency Mapping

| Python Package | JavaScript Package | Purpose |
|---------------|-------------------|---------|
| fastapi | express | Web framework |
| firebase-admin | firebase-admin | Firebase Admin SDK |
| PyJWT | jsonwebtoken | JWT token handling |
| pydantic | zod | Data validation |
| python-dotenv | dotenv | Environment variables |
| uvicorn | node (native) | Server runtime |
| - | cors | CORS middleware |
| - | jest | Testing framework |
| - | supertest | HTTP testing |

## Project Structure Changes

### Before (Python)
```
app/
├── __init__.py
├── main.py
└── auth/
    ├── __init__.py
    ├── models.py
    ├── firebase_auth.py
    ├── dependencies.py
    └── routes.py
```

### After (JavaScript)
```
src/
├── index.js
└── app/
    ├── auth/
    │   ├── models.js
    │   ├── firebaseAuth.js
    │   ├── middleware.js
    │   └── routes.js
    └── exampleProtectedRoutes.js
```

## Key Changes

### 1. Models (Pydantic → Zod)

**Before:**
```python
from pydantic import BaseModel, EmailStr

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
```

**After:**
```javascript
import { z } from 'zod';

export const UserSignupRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
});
```

### 2. Dependencies → Middleware

**Before:**
```python
from fastapi import Depends
from .dependencies import get_current_user

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user['email']}"}
```

**After:**
```javascript
import { getCurrentUser } from './auth/middleware.js';

router.get('/protected', getCurrentUser, (req, res) => {
  res.json({ message: `Hello ${req.user.email}` });
});
```

### 3. Routes

**Before:**
```python
@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignupRequest):
    # ...
```

**After:**
```javascript
router.post('/signup', validate(UserSignupRequestSchema), async (req, res) => {
  // ...
});
```

### 4. Firebase Auth Service

The Firebase Admin SDK API is similar, but with JavaScript async/await patterns:
- `auth.create_user()` → `admin.auth().createUser()`
- `auth.get_user_by_email()` → `admin.auth().getUserByEmail()`
- `auth.verify_id_token()` → `admin.auth().verifyIdToken()`

### 5. Error Handling

**Before:**
```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials"
)
```

**After:**
```javascript
res.status(401).json({
  detail: 'Invalid credentials'
});
```

## Environment Variables

The environment variables remain the same:

```env
FIREBASE_CREDENTIALS={...}
# OR
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

JWT_SECRET=your-secret-key
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Running the Application

### Before (Python)
```bash
pip install -r requirements.txt
python run.py
```

### After (JavaScript)
```bash
npm install
npm start
# or for development
npm run dev
```

## Testing

### Before (Python)
```bash
python test_auth.py
```

### After (JavaScript)
```bash
npm test
```

## API Compatibility

All API endpoints remain the same:
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /auth/verify`
- `GET /protected/*`

Request/response formats are identical, ensuring backward compatibility.

## Breaking Changes

1. **Server Runtime**: Requires Node.js 18+ instead of Python 3.x
2. **Module System**: Uses ES modules (`import/export`) instead of Python imports
3. **Async Patterns**: Uses JavaScript Promises/async-await (similar to Python but different syntax)

## Migration Checklist

- [x] Map Python dependencies to JavaScript equivalents
- [x] Create package.json with dependencies
- [x] Rewrite models using Zod
- [x] Rewrite Firebase auth service
- [x] Rewrite dependencies as Express middleware
- [x] Rewrite all routes
- [x] Rewrite main application file
- [x] Create test suite
- [x] Update documentation

## Next Steps

1. Test all endpoints with your Firebase project
2. Update CI/CD pipelines to use Node.js
3. Update deployment configurations
4. Consider adding TypeScript for better type safety
5. Add API documentation (Swagger/OpenAPI) if needed

## Notes

- The Firebase Admin SDK initialization handles both JSON string and file path credentials
- JWT token generation and verification logic is preserved
- All authentication flows remain the same
- CORS configuration is now explicit via the `cors` package

