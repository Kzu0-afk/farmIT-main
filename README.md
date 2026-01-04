## FarmIT

FarmIT is a farm-to-market web platform for the Philippines that connects local farmers directly with consumers, restaurants, and small businesses. It supports marketplace listings, chat, delivery quoting, and farm reviews with a focus on fair trade and transparency.

## Current focus

- **Stability**: keep the core marketplace, chat, media uploads, and delivery quoting stable on Vercel.
- **Data & storage**: use PostgreSQL in production (commonly via Supabase), with SQLite as the local dev fallback.
- **Mapping UX**: iterate on Leaflet + OpenStreetMap now while keeping room for a future routing provider.

## Core features

- **Roles & permissions**: farmer and customer roles with role-aware UI and access control.
- **Marketplace**: listings with photos/URLs, price, quantity, payment modes, and farm information.
- **Product media**: optional upload to Supabase Storage (public bucket) or paste an image URL.
- **Chat**: farmer ↔ customer chat (polling-based auto-refresh).
- **Reviews**: farm ratings and review counts (used in marketplace highlights).
- **Delivery quoting**: distance-based quoting using farm/address coordinates (Haversine distance, ETA/fee).
- **Address book & delivery requests**: customer-managed addresses and delivery request creation.
- **Abuse protection**: per-IP rate limiting middleware and standard Django security controls.

## Tech stack

- **Backend**: Django (Python)
- **Frontend**: Django templates + Tailwind CSS
- **Database**: SQLite by default; PostgreSQL via `DATABASE_URL` for production (e.g., Supabase Session Pooler)
- **Storage**: Supabase Storage for product images (optional; public URLs)
- **Deployment**: Vercel Serverless (`python3.12`)
- **Mapping**: Leaflet + OpenStreetMap tiles (no API key required)

## Repository layout (high level)

- `farmIT/manage.py`: Django entrypoint
- `farmIT/farmIT/settings/`: environment-driven settings (`base.py`, `dev.py`, `prod.py`)
- `farmIT/products/`, `farmIT/chat/`, `farmIT/users/`: core apps
- `templates/`, `farmIT/static/`: UI templates and static assets
- `vercel.json`: Vercel build + routing configuration
- `env.example`: environment variable template

## Local development

### Prerequisites

- Python 3.12+ (recommended to match production)

### Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

2. Configure environment variables:

- Copy `env.example` to `.env` at the repo root and adjust values as needed.
- By default, the app runs on **SQLite**. To use Postgres, set `DATABASE_URL`.

3. Run migrations and start the server:

```bash
python farmIT/manage.py migrate
python farmIT/manage.py runserver
```

### Optional: Supabase Storage for product image uploads

If you want image uploads (instead of pasting an image URL), set:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_STORAGE_BUCKET` (defaults to `product-images`)

If these are not set, the app will **skip uploads** and you can still provide an image URL in the product form.

## Deployment (Vercel)

- **Runtime**: configured in `vercel.json` (Python 3.12)
- **Settings**: use `DJANGO_ENV=prod` for hardened production settings (HSTS, secure cookies, SSL redirect).
- **Migrations/static**: `build.sh` can run migrations and `collectstatic` during deployment.

See:
- `VERCEL_DEPLOYMENT_GUIDE.md`
- `VERCEL_QUICK_CHECKLIST.md`

## Security & reliability notes

- **Django defaults**: CSRF protection, session auth, and password validators.
- **Production hardening**: HSTS, HTTPS redirect, secure cookies, and security headers in `prod` settings.
- **Rate limiting**: simple per-IP fixed-window rate limiting middleware to mitigate abuse.
- **Logging**: production defaults avoid verbose request/SQL logs.

## Documentation

- `FarmIT_COMPREHENSIVE.MD`: architecture, design notes, deployment steps, and project progress.
- `MAPPING_INTEGRATION_PLAN.md`: mapping/routing roadmap and UI plans.
- `UI_ENHANCEMENTS_SUMMARY.md`: UI/UX iteration notes.


