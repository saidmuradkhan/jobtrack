# jobtrack

Full-stack job application tracker: browse vacancies collected by
[az-job-radar](https://github.com/saidmuradkhan/az-job-radar), save the ones you like,
and track every application from "applied" to "offer". Salaries are converted with
[cbar-rates](https://github.com/saidmuradkhan/cbar-rates).

**Live demo:** jobs.saidmuradkhan.dev *(coming soon)*

> Part of a 3-service system: az-job-radar (Python) · cbar-rates (Go) · **jobtrack** (Django + React)

## Tech stack

- **Backend:** Django · Django REST Framework · JWT auth · PostgreSQL
- **Frontend:** React (Vite) · Vitest · Testing Library
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
| GET | `/api/vacancies/?q=&category=&page=` | Vacancies from az-job-radar, 20 per page, with `saved` for the ones you already track |
| GET | `/api/rates/` | Official CBAR rates from cbar-rates (`per_unit` in AZN), cached for an hour |

List filters: `?status=interview`, `?search=python` (company, position, notes),
`?ordering=-applied_on` (`applied_on`, `company`, `salary`, `created_at`).
Every request except register/login needs `Authorization: Bearer <access>`,
and each user only ever sees their own applications.

Saving a vacancy creates a `wishlist` application with its `vacancy_uid`; the same
vacancy can't be saved twice by one user.

## How the three services talk

```
browser ──► jobtrack frontend ──► jobtrack API ──► az-job-radar  /vacancies
                                              └──► cbar-rates    /rates
```

The browser only talks to the jobtrack API. The API calls the other two services
server-side and sends `X-Preview-Token`, so the shared secret never reaches the browser.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `RADAR_API_URL` | `https://radar.saidmuradkhan.dev` | az-job-radar base URL |
| `RATES_API_URL` | `https://rates.saidmuradkhan.dev` | cbar-rates base URL |
| `PREVIEW_USER`, `PREVIEW_PASSWORD` | — | Preview login. If either is missing, the site is public. |
| `PREVIEW_SECRET` | — | Signs the preview cookie and is sent as `X-Preview-Token` to the other services (same value everywhere) |
| `FRONTEND_URL` | — | Where the preview login may send people back to, e.g. `https://jobs.saidmuradkhan.dev` |
| `PREVIEW_COOKIE_DOMAIN` | — | e.g. `.saidmuradkhan.dev`, so the frontend's requests carry the preview cookie |

While the preview login is on, `/health` stays open, the API answers `401` with a
`preview_login` link and the frontend sends the browser there.

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

## Run the frontend locally

With the backend running on `127.0.0.1:8000`:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, /api is proxied to the backend
npm test           # Vitest + Testing Library
npm run lint
npm run build
```

Sign up, then add applications from the list view or drag cards between
columns on the board view to change their status.
For a deployed build, set `VITE_API_URL` to the backend URL.

The Vacancies tab needs az-job-radar: either set `PREVIEW_SECRET` for the backend
(the live sites are behind the preview login) or point `RADAR_API_URL` and
`RATES_API_URL` at locally running copies.

## Structure

```
jobtrack/
├── backend/    # Django + DRF API
└── frontend/   # React (Vite) app
```

## Roadmap

- [x] Django project + `applications` app, run dev server
- [x] `Application` model (company, position, status, applied_on, salary, currency, url, notes) + Django admin
- [x] DRF serializers + CRUD API for applications
- [x] User registration & JWT login (`djangorestframework-simplejwt`)
- [x] Each user sees only their own applications (permissions)
- [x] Filtering & search (status, company)
- [x] API tests (pytest-django) + CI
- [x] React frontend: login, applications list, add/edit form
- [x] Kanban board view by status, filter and search
- [x] Frontend tests (Vitest + Testing Library) in CI
- [x] Browse az-job-radar vacancies and save one as an application in a click
- [x] Salaries shown in AZN and USD with official rates from cbar-rates
- [x] Preview login (signed cookie) until review
- [ ] PostgreSQL + Docker Compose
- [ ] Deploy

## License

MIT
