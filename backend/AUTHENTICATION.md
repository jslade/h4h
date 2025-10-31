# Authentication

This application now supports username/password authentication with per-device persistent sessions.

## Features

- User authentication with bcrypt password hashing
- Long-lived sessions (~10 years) with session tracking
- HttpOnly cookies for security (Secure flag in production)
- Support for both cookie and Bearer token authentication
- Session metadata (user agent, IP address, timestamps)

## API Endpoints

### POST /api/login

Authenticates a user and creates a session.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "string"
}
```

Sets an HttpOnly cookie named `h4h_session` with the session ID.

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials

**Example:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}' \
  -c cookies.txt
```

### POST /api/logout

Logs out the current user by deleting their session.

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated

**Example:**
```bash
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

## Authentication Methods

The `get_current_user()` dependency checks for authentication in two ways:

1. **Cookie**: Reads the `h4h_session` cookie
2. **Bearer Token**: Reads the `Authorization: Bearer <session_id>` header

Example using Bearer token:
```bash
curl http://localhost:5000/api/some-endpoint \
  -H 'Authorization: Bearer <session-id>'
```

## Creating Users

Users must be created directly in the database. Use the Python shell or a migration:

```python
from hfh.models.user import User
from hfh.db import DB

with APP.app_context():
    user = User(name="admin")
    user.set_password("secure_password_here")
    DB.session.add(user)
    DB.session.commit()
```

## Database Schema

### Users Table
- `id`: Integer, primary key
- `name`: String(60), unique, indexed (username)
- `password_hash`: String(255), bcrypt hash

### Sessions Table
- `id`: String(36), UUID primary key
- `user_id`: Integer, foreign key to users
- `user_agent`: String(255), optional
- `ip_address`: String(45), optional
- `created_at`: DateTime
- `last_used_at`: DateTime

## Security Considerations

- Passwords are hashed using bcrypt via passlib
- Session cookies are HttpOnly to prevent XSS attacks
- Session cookies use the Secure flag in production
- Sessions have a long expiration (~10 years) but can be manually invalidated
- Session last_used_at is updated on each request for tracking
