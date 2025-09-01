# Bloom

A minimal self‑analysis survey app (Django REST Framework + Next.js). Answer curated questions one by one, get live progress, and see aggregated traits.

## Stack
- **Backend:** Django, DRF, JWT (SimpleJWT), drf-yasg, CORS, WhiteNoise
- **AI (optional):** OpenAI via Agno agents (validator + analysis)
- **Frontend:** Next.js (App Router), Tailwind, Framer Motion, React Icons

## Layout
```
Bloom_Project/
├─ Bloom_Backend/        # Django API
│  ├─ accounts/          # Register/Login (JWT)
│  └─ self_analysis/     # Questions, Answers, Traits, Agents
├─ bloom-web/            # Next.js frontend
└─ Notebooks/            # (optional) notebooks / experiments
```

## Quickstart

### 1) Backend (Django)
```bash
cd Bloom_Backend
python -m venv venv && source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt                   # or install manually: django, djangorestframework, drf-yasg, djangorestframework-simplejwt, python-dotenv, django-cors-headers, whitenoise
cp .env.example .env                              # then edit:
# SECRET_KEY=...
# DEBUG=True
# OPENAI_API_KEY=...    # optional, enables agents
python manage.py migrate
python manage.py seed_self_analysis --reset       # seed a few questions, options, traits
python manage.py runserver
```
- API docs: **http://localhost:8000/api/docs/**
- Auth:
  - `POST /accounts/register/` → `{username, password}`
  - `POST /accounts/login/` → `{username, password}` ⇒ returns `{access, refresh}`

Key endpoints (prefixes already mounted in project urls):
- `GET /self-analysis/answers/next/`
- `POST /self-analysis/answers/answer-and-next/`
- `GET /self-analysis/self-analysis/overview/`
- `POST /self-analysis/self-analysis/recalc/`

### 2) Frontend (Next.js)
```bash
cd bloom-web
npm i
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```
Open **http://localhost:3000**

- Pages:
  - `/` Landing
  - `/login` and `/register`
  - `/home` Survey (protected; requires `access_token` cookie)

## Notes
- Without `OPENAI_API_KEY`, text validation/analysis gracefully degrades (validator is permissive and analysis returns empty traits).
- Seed command gives a tiny, realistic set of questions & options for quick testing.

## License
MIT (or your preference)
