# Simple REST API Template

## Overview
A lightweight REST API template for microservices and backend applications.

## Template Variables
- `{{project_name}}`: Name of the API project
- `{{description}}`: API description
- `{{version}}`: API version
- `{{framework}}`: API framework (fastapi, flask, etc.)

## Project Structure
```
{{project_name}}/
├── main.py               # API entry point
├── api/                  # API modules
│   ├── __init__.py
│   ├── routes/           # Route definitions
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── database/             # Database configuration
│   ├── __init__.py
│   └── connection.py
├── tests/                # Test files
│   ├── test_routes.py
│   └── test_models.py
├── requirements.txt      # Dependencies
├── config.py            # Configuration
└── README.md            # Documentation
```

## Core Features
- RESTful endpoints (GET, POST, PUT, DELETE)
- Request/response validation
- Error handling and status codes
- API documentation
- Database integration
- Authentication middleware

## Implementation Steps
1. Set up project structure
2. Install dependencies
3. Create main application
4. Define data models
5. Implement CRUD operations
6. Add authentication
7. Create API documentation
8. Add comprehensive tests

## Dependencies
```
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
python-jose>=3.3.0
passlib>=1.7.4
```

## API Endpoints
```
GET    /api/v1/health      # Health check
GET    /api/v1/users       # List users
POST   /api/v1/users       # Create user
GET    /api/v1/users/{id}  # Get user
PUT    /api/v1/users/{id}  # Update user
DELETE /api/v1/users/{id}  # Delete user
```

## Best Practices
- Use proper HTTP status codes
- Implement request validation
- Add rate limiting
- Use JWT for authentication
- Include comprehensive logging
- Version your API endpoints

## Security Considerations
- Input validation and sanitization
- Authentication and authorization
- Rate limiting and throttling
- CORS configuration
- SQL injection prevention
- Secure password hashing
