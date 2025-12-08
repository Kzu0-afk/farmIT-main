# FarmIT

FarmIT is a farm-to-market web platform for the Philippines that connects local farmers directly with consumers, restaurants, and small businesses. It focuses on transparent, fair trade by digitizing listings, chat, delivery planning, and reviews.

## Current Goal
- Keep the core marketplace, chat, product media uploads, and delivery quoting stable in production on Vercel.
- Continue Supabase-backed data and storage; postpone separate Railway backend until needed.
- Iterate on mapping UX (Leaflet/OSM) while preparing for a future routing provider.

## Core Features
- Farmer and customer roles with tailored navigation.
- Marketplace listings with photos, price, quantity, payment modes, and farm info.
- Product image uploads to Supabase Storage (public bucket).
- Chat between customers and farmers (polling-based auto-refresh).
- Reviews and ratings on farms (avg rating + count in marketplace highlights).
- Delivery quote flow using farm/address coordinates (Haversine distance, ETA, fee).
- Address book for customers; delivery request creation.
- Role-based permissions and rate limiting for protection.

## Stack
- Backend: Django (Python)
- Frontend: Django templates + Tailwind CSS
- Database: Supabase PostgreSQL (Session Pooler; SQLite fallback for local dev)
- Storage: Supabase Storage (`product-images` bucket, public URLs)
- Deployment: Vercel (serverless, Python 3.12)
- Mapping (current): Leaflet + OpenStreetMap tiles (no API key required)

## Deployment Notes
- Environment-driven settings (`DJANGO_ENV=dev|prod`); `prod` hardens security (HSTS, secure cookies, SSL redirect).
- Vercel: `vercel.json` uses `@vercel/python`, bundles Django app, and maps `application` as `app` in `wsgi.py`.
- Hosts/CSRF: `ALLOWED_HOSTS=.vercel.app`; `CSRF_TRUSTED_ORIGINS` set to the prod Vercel domain.
- Migrations: run locally against Supabase via Session Pooler or via CLI before deploy.

## Security & Reliability
- CSRF protection, session auth, and role-based access on all views.
- Rate limiting middleware applied (including chat endpoints) to mitigate abuse.
- No mock data is shipped; all content is real user-generated records.

## Where to Learn More
- See `FarmIT_COMPREHENSIVE.MD` for deep design, architecture, deployment steps, and phase progress.
- See `MAPPING_INTEGRATION_PLAN.md` for mapping/routing roadmap and UI plans.


