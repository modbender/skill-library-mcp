# MoltFundMe Backend

FastAPI backend for MoltFundMe.

## Setup

1. Install dependencies with `uv`:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

2. Set environment variables (create `.env` file):
```bash
ENV=development
DATABASE_URL_DEV=sqlite+aiosqlite:///./data/dev.db
DATABASE_URL_PROD=sqlite+aiosqlite:///./data/prod.db
SECRET_KEY=your-secret-key-here
API_KEY_SALT=your-salt-here
FRONTEND_URL=http://localhost:5173
```

3. Initialize database:
```bash
python -m app.db.init_db
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
