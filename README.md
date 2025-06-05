# URL Shortener API

A modern, secure, and feature-rich URL shortening service built with FastAPI and SQLAlchemy.

## Features

- 🔐 Secure authentication with JWT tokens
- 🔗 URL shortening with custom keys
- 📊 Click tracking and analytics
- 👤 User management and URL ownership
- 🔒 Secret keys for URL management
- 🚫 URL deactivation capability
- 🗑️ URL deletion functionality
- 📝 Comprehensive API documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **PostgreSQL**: Database (with UUID support)
- **JWT**: Authentication
- **Alembic**: Database migrations
- **Python 3.8+**: Programming language

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd urlshortner
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Run database migrations:

```bash
alembic upgrade head
```

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /register` - Register a new user
- `POST /token` - Get JWT access token
- `GET /users/me` - Get current user profile

### URL Management

- `POST /url` - Create a new short URL
- `GET /urls` - Get all URLs for authenticated user
- `GET /s/{short_key}` - Redirect to target URL
- `GET /info/{secret_key}` - Get URL information
- `DELETE /admin/{secret_key}` - Deactivate a URL
- `DELETE /delete/{secret_key}` - Permanently delete a URL

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- CORS middleware configuration
- Rate limiting (configurable)
- Secure password reset functionality

## Database Schema

### Users Table

- UUID primary key
- Username (unique)
- Email (unique)
- Hashed password
- Active status
- Creation timestamp

### URLs Table

- UUID primary key
- Short key (unique)
- Secret key (unique)
- Target URL
- Click count
- Active status
- Owner reference
- Creation timestamp

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request



## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- FastAPI documentation
- SQLAlchemy documentation
- Pydantic documentation
