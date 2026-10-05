# jobtrack

Full-stack job application tracker: browse vacancies collected by
[az-job-radar](https://github.com/saidmuradkhan/az-job-radar), save the ones you like,
and track every application from "applied" to "offer". Salaries are converted with
[cbar-rates](https://github.com/saidmuradkhan/cbar-rates).

**Live demo:** jobs.saidmuradkhan.dev *(coming soon)*

> Part of a 3-service system: az-job-radar (Python) · cbar-rates (Go) · **jobtrack** (Django + React)

## Tech stack

- **Backend:** Django · Django REST Framework · JWT auth · PostgreSQL
- **Frontend:** React (Vite)
- **Infra:** Docker Compose · GitHub Actions

## Backend API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/api/auth/register/` | Create an account (`username`, `email`, `password`) |
| POST | `/api/auth/token/` | Log in, returns `access` + `refresh` JWT |
| POST | `/api/auth/token/refresh/` | Get a new access token |
| GET | `/api/auth/me/` | Current user |
| GET, POST | `/api/applications/` | List / create your applications |
| GET, PATCH, PUT, DELETE | `/api/applications/{id}/` | One application |

List filters: `?status=interview`, `?search=python` (company, position, notes),
`?ordering=-applied_on` (`applied_on`, `company`, `salary`, `created_at`).
Every request except register/login needs `Authorization: Bearer <access>`,
and each user only ever sees their own applications.

## Run the backend locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
pytest
```

## Structure

```
jobtrack/
├── backend/    # Django + DRF API
└── frontend/   # React app
```

## Roadmap

- [x] Django project + `applications` app, run dev server
- [x] `Application` model (company, position, status, applied_on, salary, currency, url, notes) + Django admin
- [x] DRF serializers + CRUD API for applications
- [x] User registration & JWT login (`djangorestframework-simplejwt`)
- [x] Each user sees only their own applications (permissions)
- [x] Filtering & search (status, company)
- [x] API tests (pytest-django) + CI
- [ ] React frontend: login, applications list, add/edit form
- [ ] Kanban board view by status
- [ ] Import vacancies from az-job-radar API
- [ ] Salary conversion via cbar-rates
- [ ] PostgreSQL + Docker Compose
- [ ] Deploy

## License

MIT
