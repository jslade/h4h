# Copilot Instructions for h4h (hash-for-heat)

## Project Overview

This is a Python/React application for remotely monitoring and controlling ASIC miners that generate heat in residential applications. The project consists of:

- **Backend**: Flask REST API with PostgreSQL database
- **Frontend**: React application with Material-UI
- **Infrastructure**: Docker Compose for local development

## Technology Stack

### Backend (Python)
- **Framework**: Flask 3.0.2
- **Database**: PostgreSQL with SQLAlchemy 2.0.28
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Migrations**: Flask-Migrate with Alembic
- **Task Scheduling**: Flask-APScheduler
- **ASIC Control**: pyasic 0.39.3
- **Logging**: structlog
- **Data Validation**: Pydantic

### Frontend (JavaScript/React)
- **Framework**: React 18.2.0
- **UI Library**: Material-UI (@mui/material) 5.15.13
- **State Management**: TanStack React Query 5.29.2
- **Routing**: React Router DOM 6.22.3
- **Build Tool**: Create React App (react-scripts 5.0.1)

### Development Environment
- **Containerization**: Docker & Docker Compose
- **Database Admin**: pgAdmin 4

## Code Style & Standards

### Python (Backend)
- **Linter/Formatter**: Ruff
- **Type Checker**: mypy (strict mode enabled)
- **Python Version**: 3.12+
- **Line Length**: 90 characters
- **Import Style**: Sorted imports with combine-as-imports
- **Max Complexity**: 17 (McCabe)

Key style rules:
- Use type hints for all functions and variables
- Follow strict mypy checking
- Import sorting is enforced
- Test files in `hfh/test/` directory ignore type checking

### JavaScript (Frontend)
- **ESLint Config**: react-app
- Follow React best practices
- Use functional components with hooks
- Proxy backend API through `http://backend:5000`

## Project Structure

```
/
├── backend/              # Flask backend application
│   ├── hfh/             # Main application package
│   │   ├── app.py       # Flask app initialization
│   │   ├── controllers/ # API route controllers
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── services/    # Business logic layer
│   │   ├── dtos/        # Data transfer objects
│   │   ├── migrations/  # Alembic database migrations
│   │   ├── scheduled_tasks.py  # Background tasks
│   │   └── test/        # Test files
│   ├── alembic/         # Alembic configuration
│   ├── pyproject.toml   # Python project configuration
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container definition
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── api.js       # API client
│   │   ├── components/  # React components
│   │   └── utils/       # Utility functions
│   ├── public/          # Static assets
│   ├── package.json     # Node.js dependencies
│   └── Dockerfile       # Frontend container definition
└── docker-compose.yml   # Multi-container orchestration
```

## Development Workflow

### Running the Application

Start all services with Docker Compose:
```bash
docker-compose up
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001
- PostgreSQL: localhost:5432
- pgAdmin: http://localhost:3002

### Backend Development

```bash
cd backend

# Install dependencies (if not using Docker)
pip install -r requirements.txt

# Run linter
ruff check hfh/

# Run type checker
mypy hfh/

# Run tests
pytest

# Database migrations
flask db upgrade
flask db migrate -m "migration message"
```

### Frontend Development

```bash
cd frontend

# Install dependencies (if not using Docker)
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Database

- **Engine**: PostgreSQL
- **Development Database**: hfh_dev
- **Connection**: Managed via SQLAlchemy
- **Migrations**: Alembic via Flask-Migrate

Default credentials (development only - DO NOT use in production):
- Username: postgres
- Password: password
- Database: hfh_dev

⚠️ **Security Note**: These credentials are for local development only. Never use default credentials in production environments.

## Testing

### Backend Tests
- Located in `backend/hfh/test/`
- Run with: `pytest`
- Model tests in `backend/hfh/test/model_tests/`

### Frontend Tests
- Located alongside components
- Run with: `npm test`
- Uses Jest and React Testing Library

## Key Guidelines for Copilot

1. **Type Safety**: Always use type hints in Python code (mypy strict mode)
2. **Code Quality**: Run ruff checks before committing Python code
3. **Line Length**: Keep Python lines under 90 characters
4. **Imports**: Use combined imports where possible (e.g., `from x import a, b`)
5. **API Structure**: Backend controllers should be RESTful and return JSON
6. **React Components**: Use functional components with hooks, not class components
7. **State Management**: Use React Query for server state, local state for UI
8. **Database Changes**: Always create migrations for schema changes
9. **Error Handling**: Use proper error handling with structured logging (structlog)
10. **Security**: Never commit database credentials or secrets

## Special Considerations

- **ASIC Integration**: Uses pyasic 0.39.3 (newer versions have issues with privileged commands)
- **Backend Port**: Flask runs on port 5000 inside container, mapped to 3001 on host
- **Frontend Proxy**: Frontend proxies API requests to backend service
- **Test Files**: Type checking is disabled for files in `hfh/test/` directory

## Common Tasks

### Adding a New API Endpoint
1. Create/update controller in `backend/hfh/controllers/`
2. Add route registration in appropriate controller file
3. Create/update service in `backend/hfh/services/`
4. Add/update models in `backend/hfh/models/` if needed
5. Create migration if schema changed
6. Update frontend API client in `frontend/src/api.js`

### Adding a Database Model
1. Create model in `backend/hfh/models/`
2. Run migration: `flask db migrate -m "add model_name"`
3. Review and edit migration if needed
4. Apply migration: `flask db upgrade`

### Adding a React Component
1. Create component in `frontend/src/components/`
2. Use Material-UI components for UI consistency
3. Use React Query hooks for data fetching
4. Add routing in appropriate place if needed
