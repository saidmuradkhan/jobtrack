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

## Structure

```
jobtrack/
├── backend/    # Django + DRF API
└── frontend/   # React app
```

## Roadmap

- [ ] Django project + `applications` app, run dev server
- [ ] `Application` model (company, position, status, applied_on, notes) + Django admin
- [ ] DRF serializers + CRUD API for applications
- [ ] User registration & JWT login (`djangorestframework-simplejwt`)
- [ ] Each user sees only their own applications (permissions)
- [ ] Filtering & search (status, company)
- [ ] API tests (pytest-django)
- [ ] React frontend: login, applications list, add/edit form
- [ ] Kanban board view by status
- [ ] Import vacancies from az-job-radar API
- [ ] Salary conversion via cbar-rates
- [ ] PostgreSQL + Docker Compose
- [ ] Deploy

## License

MIT
