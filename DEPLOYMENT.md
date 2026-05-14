# Deployment Guide

This guide explains how to deploy the Study Helper Web Application locally and in a lightweight production setup.

## Prerequisites

- Python 3.10+ installed
- Git (optional)
- PowerShell or terminal access on Windows

## Local Deployment

1. Clone or copy the repository.
2. Create and activate a Python virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

4. Start the application.

```powershell
python app.py
```

5. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Environment Configuration

The application supports configuration via environment variables.

- `PORT` — server port (default: `5000`)
- `STORAGE_PATH` — custom storage file path for JSON persistence
- `FLASK_ENV` — set to `development` for development mode
- `FLASK_DEBUG` — set to `1` to enable Flask debug mode

Example:

```powershell
$env:PORT = 8080
$env:STORAGE_PATH = "D:\data\study_app.json"
$env:FLASK_ENV = "development"
python app.py
```

## Production Deployment

For a more production-oriented server, install `gunicorn` and run:

```powershell
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

If deploying behind a reverse proxy or load balancer, bind to `0.0.0.0` and configure the proxy to forward requests to the app.

## Testing

Run unit and integration tests with:

```powershell
python -m pytest tests/ -v
```

A successful run should show all tests passing.

## Notes

- Storage is saved locally in `data/storage.json` by default.
- The JSON schema is initialized automatically on first run.
- Static frontend files are served from `static/` and the main user interface is in `templates/index.html`.
