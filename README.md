# FastAPI Todo API

A REST API for managing todos with user authentication, JWT access/refresh tokens, and MySQL persistence.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy 2.0** — ORM
- **MySQL** — database (via PyMySQL)
- **JWT** — authentication (python-jose)
- **Passlib + bcrypt** — password hashing
- **uv** — dependency and project management

## Project Structure

```
fastapi-project/
├── app/
│   ├── auth/           # JWT, password hashing, token blacklist
│   ├── core/           # App configuration
│   ├── database/       # DB engine, session, get_db
│   ├── models/         # SQLAlchemy models (User, Todo)
│   ├── routes/         # API endpoints (users, todos)
│   ├── schemas/        # Pydantic request/response models
│   └── main.py         # FastAPI app entry point
├── .env                # Environment variables (not committed)
└── pyproject.toml
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- MySQL server running locally

## Setup

1. **Clone and enter the project**

   ```bash
   cd fastapi-project
   ```

2. **Create the MySQL database**

   ```sql
   CREATE DATABASE todo_db;
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/todo_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

4. **Install dependencies**

   ```bash
   uv sync
   ```

5. **Run the server**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

   API: http://127.0.0.1:8000  
   Swagger docs: http://127.0.0.1:8000/docs

> **Important:** Run uvicorn from the `fastapi-project` folder, not the parent directory.

## Authentication Flow

1. **Register** — `POST /users/register` (admin only)
2. **Login** — `POST /users/login` → returns `access_token` and `refresh_token`
3. **Authorize** — use the access token as `Bearer <token>` on protected routes
4. **Refresh** — `POST /users/refresh` when the access token expires
5. **Logout** — `POST /users/logout` to revoke tokens

| Token | Lifetime | Used for |
|---|---|---|
| Access token | 30 minutes (configurable) | API requests |
| Refresh token | 7 days (configurable) | Getting a new access token |

## API Endpoints

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/users/register` | Admin | Register a new user |
| POST | `/users/login` | No | Login and get tokens |
| POST | `/users/refresh` | No | Get a new access token |
| POST | `/users/logout` | Yes | Revoke access (and optional refresh) token |
| GET | `/users/` | Yes | List users (admin: all, user: self) |

### Todos

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/todos/` | Yes | Create a todo for the current user |
| GET | `/todos/` | Yes | List current user's todos (paginated) |
| GET | `/todos/{id}` | Yes | Get a single todo |
| PUT | `/todos/{id}` | Yes | Update a todo |
| PATCH | `/todos/{id}/complete` | Yes | Mark todo as complete |
| DELETE | `/todos/{id}` | Yes | Delete a todo |

## Testing with Swagger

1. Open http://127.0.0.1:8000/docs
2. Call `POST /users/login` with username and password
3. Copy the `access_token` from the response
4. Click **Authorize** and paste: `Bearer <access_token>`
5. Call protected endpoints (`/todos/`, `/users/`, etc.)

To refresh an expired access token:

```json
POST /users/refresh
{
  "refresh_token": "<your_refresh_token>"
}
```

To logout and revoke tokens:

```json
POST /users/logout
{
  "refresh_token": "<your_refresh_token>"
}
```

## Database Notes

- Tables are created automatically on startup via `Base.metadata.create_all()`.
- If you change a model (e.g. add a column), `create_all` will **not** update existing tables. Use `ALTER TABLE` in MySQL or Alembic migrations.
- For production, replace `create_all` with **Alembic** for schema migrations.

## Roles

- **admin** — can register users and list all users
- **user** — can manage their own todos and view their own profile
