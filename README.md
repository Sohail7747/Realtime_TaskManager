# Real-Time Task Manager

Starter Django project for the internship machine test.

## Stack
- Django
- Django REST Framework
- Django Channels / WebSockets
- PostgreSQL
- Redis
- HTML, CSS, JavaScript, Bootstrap (frontend to be added)

## 1. Create and activate a virtual environment (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure environment

Copy `.env.example` to `.env` and update `DB_PASSWORD` and `DJANGO_SECRET_KEY`.

Create a PostgreSQL database named `realtime_task_manager` (or change `DB_NAME` in `.env`).

In development (`DJANGO_DEBUG=True`), Channels uses its in-memory layer by default, so
connected users on the same development server receive live updates without installing Redis.
For multiple application processes or production, run Redis and set
`USE_REDIS_CHANNEL_LAYER=True` and `REDIS_URL` in `.env`; the in-memory layer does not share
events between processes.

## 4. Create database tables

The project uses a custom user model (`accounts.User`). It is important to keep this model
in place before the first migration.

```powershell
python manage.py makemigrations accounts tasks
python manage.py migrate
```

## 5. Create an admin account

```powershell
python manage.py createsuperuser
```

## 6. Run the development ASGI server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/

## Current scaffold status

This ZIP contains the configured project foundation, custom user and task models, Django admin
registrations, PostgreSQL settings, DRF defaults, and the Channels ASGI/WebSocket entry point.
Registration/login APIs, task CRUD APIs, permissions, WebSocket event broadcasting, and the
Bootstrap pages are intentionally the next implementation steps.
