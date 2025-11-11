# Authentication API with Firebase

An Express.js-based authentication system with Firebase integration, providing user registration, login, and token-based authentication.

> **Note:** This project has been migrated from Python (FastAPI) to JavaScript (Express.js). For the legacy Python version, see [pr-reviewer-python-deprecated](https://github.com/your-org/pr-reviewer-python-deprecated).

## Features

- 🔐 Firebase Authentication integration
- 📝 User registration and login
- 🔑 JWT token-based authentication
- 🔄 Token refresh functionality
- 🛡️ Role-based access control
- 🌐 CORS support
- ✅ Input validation with Zod

## Project Structure

```
├── src/
│   ├── index.js                    # Express application entry point
│   ├── __tests__/
│   │   └── auth.test.js           # Test suite
│   └── app/
│       ├── auth/
│       │   ├── models.js          # Zod validation schemas
│       │   ├── firebaseAuth.js    # Firebase authentication service
│       │   ├── middleware.js      # Authentication middleware
│       │   └── routes.js          # API routes
│       └── exampleProtectedRoutes.js
├── package.json                    # Node.js dependencies
├── jest.config.js                 # Jest test configuration
├── env.example                     # Environment variables template
└── README.md                       # This file
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Firebase Configuration

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication in your Firebase project
3. Create a service account:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

### 3. Environment Variables

Copy `env.example` to `.env` and configure the variables:

```bash
cp env.example .env
```

Required environment variables:

```env
# Firebase Configuration (choose one option)
# Option 1: Firebase credentials as JSON string
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"your-project-id",...}

# Option 2: Path to Firebase service account JSON file
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration (comma-separated list)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 4. Run the Application

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

The API will be available at:
- API: http://localhost:8000
- Health Check: http://localhost:8000/health

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user info |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/verify` | Verify token validity |

### Request/Response Examples

#### User Registration

```bash
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "firebase-user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### User Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Token Refresh

```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Protected Endpoint Example

```bash
GET /auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Authentication Middleware

The authentication system provides several middleware functions for protecting routes:

### Basic Authentication

```javascript
import { getCurrentUser } from './app/auth/middleware.js';

router.get('/protected', getCurrentUser, (req, res) => {
  res.json({ message: `Hello ${req.user.email}` });
});
```

### Active User Check

```javascript
import { getCurrentActiveUser } from './app/auth/middleware.js';

router.get('/active-only', getCurrentActiveUser, (req, res) => {
  res.json({ message: 'Active user only' });
});
```

### Role-Based Access

```javascript
import { requireAdmin, requireUser } from './app/auth/middleware.js';

router.get('/admin-only', requireAdmin, (req, res) => {
  res.json({ message: 'Admin only' });
});

router.get('/user-route', requireUser, (req, res) => {
  res.json({ message: 'User or admin' });
});
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server-side errors

## Security Considerations

1. **JWT Secret**: Use a strong, unique secret key in production
2. **Firebase Credentials**: Keep service account credentials secure
3. **CORS**: Configure allowed origins properly for production
4. **Password Policy**: Implement strong password requirements
5. **Rate Limiting**: Consider adding rate limiting for auth endpoints
6. **HTTPS**: Always use HTTPS in production

## Development

### Running in Development Mode

```bash
npm run dev
```

The server will run with auto-reload enabled using nodemon.

### Testing

Run the test suite:

```bash
npm test
```

### Environment Variables for Development

For development, you can use the default values in `env.example`. Make sure to:

1. Set up a Firebase project
2. Configure the Firebase credentials
3. Generate a secure JWT secret

## Production Deployment

1. Set `ENVIRONMENT=production`
2. Configure proper CORS origins
3. Use environment-specific Firebase credentials
4. Set up proper logging
5. Use a process manager like PM2
6. Configure reverse proxy (nginx)
7. Set up SSL/TLS certificates

## Migration from Python

This project was migrated from Python (FastAPI) to JavaScript (Express.js). See [MIGRATION.md](./MIGRATION.md) for detailed migration information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
