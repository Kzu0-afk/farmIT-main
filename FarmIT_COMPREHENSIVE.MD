# 🌾 FarmIt_COMPREHENSIVE.MD

## 🧭 Project Overview

**Project Name:** FarmIT
**Project Type:** Small-to-Medium Scale Web Application  
**Core Concept:**  
FarmIt is a **"Farm-to-Market" platform** designed to connect **local farmers** directly with **consumers, restaurants, and small businesses**, enabling transparent and sustainable agricultural trade in the Philippines.

Instead of relying on traditional supply chains that cut into farmer profit margins, FarmIt aims to **digitize the local marketplace**, giving farmers visibility, control, and fairer income opportunities — while providing consumers access to fresh, affordable produce.

---

## 🎯 Vision & Objectives

### 🔹 Primary Goal
To build a functional **web-based marketplace** where:
- Farmers can list their products with photos, pricing, and availability.
- Buyers can browse by **location**, **product type**, and **mode of payment**.
- Both parties can connect and transact efficiently without intermediaries.

### 🔹 Long-Term Vision
- Create a sustainable digital agriculture ecosystem.
- Empower local farmers through direct digital visibility.
- Promote regional traceability — buyers know where their produce comes from.

---

## 💡 Key Features

| Category | Features |
|-----------|-----------|
| **Roles** | Role selection at registration: Customer or Farmer; role-based UX/permissions |
| **Farmer Profile** | Registration, farm page, branding, location tagging, contact details |
| **Product Listings** | Upload photos, set prices, product descriptions, quantity, unit, availability |
| **Customer Access** | Marketplace-first landing, no product CRUD, chat to negotiate |
| **Chat** | Customer-initiated conversations with Farmers on farm page or product view |
| **Marketplace** | Search & filters (location, min/max price), farm highlights, ratings summary |
| **Transaction Details** | Mode of payment, pickup/delivery option, contact and negotiation via chat |
| **Admin Panel** | Manage users, moderate listings, monitor platform activity |
| **Analytics (Future)** | Regional demand insights, trending crops, seasonal supply forecasting |

---

## ⚙️ Technical Stack

| Layer | Framework / Service | Description |
|--------|----------------------|--------------|
| **Backend** | **Django (Python)** | Core logic, CRUD operations, REST API via Django REST Framework |
| **Frontend** | **Tailwind CSS** | Styling and responsive UI |
| **Database** | **Supabase (PostgreSQL)** | Managed DB for product data, farmer profiles, and transactions |
| **Frontend Deployment** | **Vercel** | Lightweight, modern deployment for static/frontend React or template rendering |
| **Backend Deployment** | **Railway** | Fast, simple backend hosting with continuous deployment and PostgreSQL integration |
| **Realtime (Future)** | Django Channels/WebSockets | Upgrade chat to realtime; Phase 4+ |

---

## 🧩 Why Django Over Java (Spring Boot)

### ✅ **Speed & Development Efficiency**
- Django provides **faster setup** and integrated features for rapid prototyping.  
- Spring Boot is better for **large enterprise systems** — overkill for FarmIt’s current scale.

### ✅ **Built-in Features**
Django includes out-of-the-box tools:
- Admin Panel  
- Authentication  
- ORM  
- Form validation  
- CSRF protection  
- REST API (via DRF)

### ✅ **Cost & Deployment**
- Lighter and cheaper to deploy on **Railway** than a JVM-based backend.
- Faster startup, smaller memory footprint, and easier CI/CD configuration.

### ✅ **Maintainability**
- Python is concise and expressive — ideal for small teams.  
- Fewer lines of code = faster debugging, easier iteration.

---

## 🧱 Architecture Overview

**Architecture Type:**  
Monolithic Web Application with RESTful API endpoints.

### 🔹 Backend Flow (Django)
```
User → Django Views/DRF → Role-Based Permissions → Database → JSON/HTML Response
```

### 🔹 Frontend Flow (Tailwind + Django Templates or API Integration)
```
User Interface → Tailwind Styled Components → Django Backend → Supabase Data
```

### 🔹 Chat Flow (MVP)
```
Customer (authenticated) → Start Conversation (product or farm) → Messages (Customer ↔ Farmer)
Permissions: Only Customers can initiate; Farmers can only reply
Transport: HTTP views + AJAX polling (upgrade to Channels in Phase 4+)
```

### 🔹 Deployment Pipeline
```
Frontend (Vercel)
        ↑
        |
API Calls
        ↓
Backend (Django on Railway) ↔ Supabase (Database)
```

---

## 🌐 Database Schema (Refactored for Roles, Chat, Farm Pages)

### User & Profiles
1. **User (existing custom: `users.FarmerUser`)**
   - Keep as the auth model; add `role` field with choices: `CUSTOMER`, `FARMER`
   - Fields (subset): `id` (PK), `email`, `password`, `name`, `location`, `contact_number`, `role`
   - Notes: Do not change `AUTH_USER_MODEL`; we generalize it instead of renaming.

2. **FarmerProfile**
   - `id` (PK), `user` (OneToOne → User), `bio`, `address`, `verification_status`, `avatar_url`

3. **CustomerProfile**
   - `id` (PK), `user` (OneToOne → User), `preferences_json`, `avatar_url`

### Farm & Products
4. **Farm**
   - `id` (PK), `farmer` (OneToOne → User), `name`, `slug`, `description`, `location`, `banner_url`, `branding_color`
   - Index: `slug` unique

5. **Product** (refactor)
   - Add `farm` (FK → Farm, nullable initially for migration), keep legacy `farmer_id` temporarily
   - Fields: `id`, `farm_id`, `product_name`, `price`, `quantity`, `unit`, `description`, `photo_url`, `location`, `mode_of_payment`, `is_approved`, `is_reserved`, `created_at`, `updated_at`
   - Migration plan: populate `farm` from `product.farmer_id` via the farmer’s farm; then make `farm` non-null; then drop `farmer_id`

6. **Review / Rating**
   - `id` (PK), `farm` (FK → Farm), `customer` (FK → User), `rating` (1–5), `comment`, `created_at`
   - Unique constraint: one review per `customer` per `farm`
   - Aggregations: farm average rating, review count

### Chat
7. **Conversation**
   - `id` (PK), `farmer` (FK → User), `customer` (FK → User), `product` (FK → Product, nullable), `created_at`, `last_message_at`
   - Unique constraint: at most one open conversation per (`customer`,`farmer`,`product` nullable)
   - Business rule: Created only by Customers

8. **Message**
   - `id` (PK), `conversation` (FK → Conversation), `sender` (FK → User), `body` (text), `created_at`, `is_read`
   - Permission: only `conversation.customer` or `conversation.farmer` can send

### Future
9. **Transaction (Future Expansion)**
   - `id` (PK), `product_id` (FK), `buyer` (FK → User), `status`, `created_at`


### Migration Strategy (Compatible with Current Progress)
- Add `role` to existing `users.FarmerUser` (default `FARMER` for existing rows)
- Create `FarmerProfile`, `CustomerProfile`, `Farm` tables
- Add `farm` FK to `products.Product` (nullable), backfill via each farmer’s `Farm`
- Enforce `farm` non-null, remove legacy `farmer_id` when safe
- Add `Conversation` and `Message`
- Add `Review`
- Add indexes on common filters: `Product.location`, `Product.price`, `Farm.location`, `Review.farm_id`

---

## 🚀 Development Roadmap (Phase 1–5)

### **Phase 1: Core MVP (Weeks 1–4)**
- [ ] Farmer registration, authentication, and CRUD for product listings
- [ ] Basic frontend with Tailwind CSS integration

### **Phase 2: Usability & Features (Weeks 5–7)**
- [ ] Search & filter by product, price, or location
- [ ] Admin dashboard (moderation and analytics)
- [ ] Simple transaction model (buyer interest, reservation)

### **Phase 3 (CRUCIAL FEATS): Roles, Chat MVP, Farm Pages, Marketplace Highlights, Maps (Weeks 8–10)** ✅ **COMPLETED**
- NOTE: Supabase database integration and hosting are paused during this phase and moved to Phase 4.
- [x] Role selection at registration (Customer/Farmer) and role-based redirects ✅ **COMPLETED**
- [x] Customer: marketplace-first landing, no product CRUD; chat entry points ✅ **COMPLETED**
- [x] Farmer: virtual farm page creation and management; product management under farm ✅ **COMPLETED**
- [x] Chat MVP: customer-initiated conversations, farmer replies; message center ✅ **COMPLETED**
- [x] Marketplace highlights: farm cards with top products and rating snapshots ✅ **COMPLETED**
- [x] Security: permission gates by role, rate-limit chat creation, content sanitization ✅ **COMPLETED**
- [x] Maps & Delivery Planning: addresses/locations, distance/ETA, delivery quoting, map display ✅ **COMPLETED**
- [x] Review/Rating system: farm reviews by customers ✅ **COMPLETED**
- [x] Enhanced UI/UX: creative farmer-themed design with carousel, pagination, and professional aesthetics ✅ **COMPLETED**
- **📋 NEXT: Testing Phase** - Comprehensive testing of all Phase 3 features before moving to Phase 4

### **Phase 4: Cloud Database & Hosting (Shifted) (Weeks 11–12)**
- [x] Django backend setup with Supabase PostgreSQL connection *(Nov 19, 2025 — env-driven config, SQLite fallback preserved, Supabase Session Pooler required for IPv4-only Windows/Railway clients)*
- [x] Product image upload to Supabase Storage *(bucket-backed, URL-only in DB)*
- [ ] Deployment setup (Railway backend, Vercel frontend)

#### Phase 4 progress notes (Nov 19, 2025)
- **Environment-driven settings:** `farmIT/settings/__init__.py` now reads `DJANGO_ENV` (`dev` default, `prod` for hardened mode) so we can run `python manage.py runserver` locally without touching `DJANGO_SETTINGS_MODULE`.  
- **.env layout:** `farmIT/.env` holds `DJANGO_ENV`, `DJANGO_SECRET_KEY`, and Supabase credentials (`DATABASE_URL`, `DB_CONN_MAX_AGE`, `DB_SSL_REQUIRE`). Local dev can point to SQLite by omitting `DATABASE_URL`; production simply sets the variable.  
- **Supabase connectivity:** Windows and Railway networks lacked IPv6, so the direct Supabase host (`db.<hash>.supabase.co`) failed with `getaddrinfo`. Switching the `DATABASE_URL` to the **Session Pooler** endpoint (`aws-*.pooler.supabase.com:6543`) solved the IPv4 compatibility issue and gives automatic connection pooling.  
- **Procfile + release flow:** Added `Procfile` with `release: python manage.py migrate --noinput` and `web: gunicorn farmIT.wsgi`, so Railway/Vercel deployments will reuse the same env vars.  
- **Status:** Migrations executed successfully against Supabase; dashboard shows new REST activity. Next focus is wiring Supabase Storage and provisioning Railway/Vercel apps.

##### Phase 4 environment profiles (inner `farmIT/.env`)
- **Outer `.env` (project root):** remains as a commented template and is **never modified**; all active settings come from the inner `farmIT/.env`.
- **Local dev (SQLite, HTTP, Brave/other browser):**
  - `DJANGO_ENV=dev`
  - `DJANGO_SECRET_KEY=...strong-random...`
  - `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`
  - `CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000`
  - `DATABASE_URL=` *(empty → use SQLite fallback)*
  - `DB_CONN_MAX_AGE=600`, `DB_SSL_REQUIRE=true`
- **Local dev using Supabase DB (still dev profile):**
  - Same as above, but set `DATABASE_URL` to the Supabase **Session Pooler** URL.
  - Keep `DJANGO_ENV=dev` so the server stays on HTTP for easy local testing.
- **Production (Railway/Vercel):**
  - Environment variables configured in the host (not from `.env` files).
  - `DJANGO_ENV=prod`, strong `DJANGO_SECRET_KEY`, `DATABASE_URL` pointing to Supabase pooler, HTTPS origins in `CSRF_TRUSTED_ORIGINS`.

##### Dev HTTPS gotcha (Edge vs local HTTP)
- During Phase 3 wrap-up, Microsoft Edge cached an HTTPS rule for `127.0.0.1:8000`, which caused repeated `400` errors and “connection is not secure” messages when talking to the Django dev server (which only serves HTTP).
- The stack itself was healthy (verified via `curl http://127.0.0.1:8000` returning `200 OK`); the fix was to either:
  - Clear Edge’s HTTPS-only / HSTS state for `127.0.0.1` and force HTTP, **or**
  - Use a different browser (e.g., Brave) that respects plain `http://127.0.0.1:8000` during local development.

##### Supabase Storage for product images (Phase 4)
- **Storage model:** the `Product.photo_url` field stores a **public URL only**; the actual binary file is uploaded to a Supabase Storage bucket.
- **Bucket:** `product-images` *(public bucket)*.
- **Upload flow (backend):**
  - Django form `ProductForm` now exposes an optional `image_file` field (`Product Image Upload`).
  - On create/update, views call `upload_product_image(image_file)` in `products/storage.py`.
  - The helper initializes a Supabase client from env (`SUPABASE_URL`, `SUPABASE_ANON_KEY`), uploads bytes to `product-images/products/<uuid>-<filename>`, and stores the returned public URL in `photo_url`.
- **Env vars required (inner `farmIT/.env`):**
  - `SUPABASE_URL=https://<project-ref>.supabase.co`
  - `SUPABASE_ANON_KEY=<anon public key>`
  - `SUPABASE_STORAGE_BUCKET=product-images`
- **Row Level Security (RLS) policies on `storage.objects`:**
  - Public uploads for the `product-images` bucket:
    \[
    \texttt{create policy "public uploads for product-images" on storage.objects for insert to anon with check (bucket_id = 'product-images');}
    \]
  - Public read access for the same bucket:
    \[
    \texttt{create policy "public read for product-images" on storage.objects for select to anon using (bucket_id = 'product-images');}
    \]
- **Frontend usage:** templates always read `product.photo_url`; if empty, they render the existing placeholder illustration. The product detail hero image uses Tailwind `object-cover` with responsive heights to maintain the original design while staying visually balanced across screen sizes.

##### Next steps for hosting rollout (Railway + Vercel)
- **Railway backend app (to be done):**
  - Create a new Railway project for the Django backend and connect the GitHub repo.
  - Configure env vars in Railway:
    - `DJANGO_ENV=prod`
    - `DJANGO_SECRET_KEY=<strong-production-secret>`
    - `DATABASE_URL=<Supabase Session Pooler URL>`
    - `DB_CONN_MAX_AGE`, `DB_SSL_REQUIRE=true`
    - `DJANGO_ALLOWED_HOSTS=<railway-domain>`
    - `CSRF_TRUSTED_ORIGINS=https://<railway-domain>,https://<vercel-domain>` *(Vercel URL added once available)*.
  - Rely on the existing `Procfile` for `release` and `web` processes (`migrate` + `gunicorn farmIT.wsgi`).
- **Vercel frontend/domain (optional split frontend, future step):**
  - If the frontend is split out, deploy templates/static frontend to Vercel and point it to the Railway API.
  - Add the Vercel HTTPS URL to Railway’s `CSRF_TRUSTED_ORIGINS` and, if needed, `DJANGO_ALLOWED_HOSTS`.
  - Verify CORS/CSRF behaviour between Vercel (frontend) and Railway (backend) before launch.

### **Phase 5: Polishing & Launch (Weeks 13–15)**
- [ ] Responsive UI/UX improvements
- [ ] Performance optimization
- [ ] Security enhancements (CSRF, JWT auth)
- [ ] Final testing & deployment to production

---

## 🧠 Strategic Context

### **Why This Project Matters in the Philippines**
- Local farmers often lack access to **digital marketplaces**.
- Middlemen reduce their profit margins by 30–50%.
- Consumers pay high retail prices while farmers earn low farmgate prices.
- Digitization bridges this gap — allowing transparent, fair, and traceable trade.

### **Why Django + Supabase + Railway/Vercel is Ideal**
- Perfect for **rapid deployment and testing** in regional markets.
- Minimal cost overhead during pilot phase.
- Scales to medium complexity without heavy DevOps burden.

---

## 📈 Long-Term Potential
If validated regionally, FarmIt can evolve into:
- **Mobile-ready PWA** for offline rural access.
- **Analytics dashboard** for government/local agencies.
- **Smart logistics integration** (with 3rd-party delivery APIs).
- **Microfinancing or insurance partnerships** for verified farmers.

---

## 🧩 Summary Table

| Component | Decision | Rationale |
|------------|-----------|------------|
| **Backend** | Django | Fast prototyping, built-in CRUD, scalable; easy role-based permissions |
| **Frontend** | Tailwind | Lightweight, modern, responsive |
| **Database** | Supabase (Phase 4) | Paused in Phase 3; enable in Phase 4 |
| **Frontend Hosting** | Vercel | Simple deployment for small-medium web apps |
| **Backend Hosting** | Railway | Free-tier support, smooth Django integration |
| **Scope** | Small-to-Midscale MVP | Focus on local validation first |
| **Next Step** | **Phase 4 hosting rollout** | Supabase connection landed; next session connects Railway (backend) + Vercel (frontend) and adds Supabase Storage |

---

**Author:** MJ Villahermosa  
**Date:** November 2025  
**Last Updated:** November 19, 2025 (Supabase connection + env switcher)  
**Purpose:** Strategic and technical documentation for *FarmIt* — to guide initial development and align coding agents or contributors.


---

## 🔧 Phase 3 (CRUCIAL FEATS) — Implementation Plan (Tied to Current Code)

### Current Status (as of today - Phase 3 Complete)
- ✅ Custom user model `users.FarmerUser` in use (`AUTH_USER_MODEL` set)
- ✅ Product CRUD, templates (`products` app), admin, search & filters exist
- ✅ Rate limiting middleware present (`farmIT.middleware.RateLimitMiddleware`)
- ✅ Local dev on SQLite; env-ready to switch to Postgres (optional)
- ✅ **Role-based system implemented**: Customer/Farmer roles with profiles
- ✅ **Farm pages implemented**: Virtual farm creation and management for farmers
- ✅ **Chat MVP implemented**: Customer-initiated conversations, farmer replies, message center
- ✅ **Marketplace highlights implemented**: Horizontal carousel with featured farms, ratings, and top products
- ✅ **Review/Rating system implemented**: Farm reviews by customers with star ratings
- ✅ **Maps & Delivery Planning implemented**: Address management, distance/ETA calculation, delivery quoting
- ✅ **Enhanced UI/UX implemented**: Creative farmer-themed design with gradient backgrounds, carousel, pagination
- 📋 **Testing Phase**: Ready to begin comprehensive testing of all Phase 3 features

### Backend Changes
- User Roles ✅ **COMPLETED**
  - ✅ Add `role` to `users.FarmerUser` with choices: `CUSTOMER`/`FARMER`; default `FARMER` for existing
  - ✅ Add `FarmerProfile` and `CustomerProfile` (OneToOne to User)
  - ✅ Registration: require role selection and create respective profile
- Farm Pages ✅ **COMPLETED**
  - ✅ Create `Farm` (OneToOne to farmer user) with slug and branding fields
  - ✅ Refactor `Product` to reference `Farm`; add migration path and data backfill
  - ✅ Permissions: only farmer owners of a farm can manage products
- Chat ✅ **COMPLETED**
  - ✅ `Conversation` and `Message` models (customer starts; farmer replies)
  - ✅ Views: create/start on product or farm page, list conversations, list/send messages
  - ✅ Throttling: per-user rate limit on conversation creation and message sending
  - ✅ Sanitization: escape message HTML; enforce max length
- Marketplace & Reviews ✅ **COMPLETED**
  - ✅ Add `Review` on `Farm` by customers; compute average rating and counts
  - ✅ Marketplace queries: highlight farms (avg rating, review count, popular products)
  - ✅ Horizontal carousel banner for featured farms with auto-rotation
  - ✅ Pagination system (12 products per page) for optimal performance
- Maps & Delivery (MVP, FoodPanda-style planning) ✅ **COMPLETED**
  - ✅ Models:
    - ✅ `Address`: `user` (FK), `label`, `line1`, `barangay`, `city`, `province`, `postal_code`, `country`, `latitude`, `longitude`, `is_default`
    - ✅ `DeliveryRequest`: `id`, `customer` (FK), `farm` (FK), `pickup_address` (farm-derived), `dropoff_address` (FK → Address), `distance_km`, `eta_minutes`, `quoted_fee`, `status`, `created_at`
  - ✅ APIs/Endpoints (Django views):
    - ✅ GET `/deliveries/quote/<product_id>/` → input: product_id + address_id; output: `distance`, `eta`, `fee`
    - ✅ POST `/deliveries/create/<product_id>/` → creates delivery request (status = `QUOTED`)
    - ✅ GET `/deliveries/` → list of delivery requests for user
    - ✅ GET `/addresses/` → customer address book management
  - ✅ Pricing (configurable): base fee (₱50) + per-km rate (₱10/km), calculated via Haversine formula
  - ✅ MVP Strategy (implemented):
    - ✅ Local coordinate-based distance calculation (Haversine formula)
    - ✅ No external API dependencies for MVP (can integrate Mapbox/Google Maps later)
    - ✅ Farm and Address models include latitude/longitude fields
  - ✅ Security & Privacy:
    - ✅ Secure address storage; role-based access (customers only)
    - ✅ Rate-limit delivery quote requests
    - ✅ Customer-only address management
- Security ✅ **COMPLETED**
  - ✅ Role-based decorators/permissions on views
  - ✅ CSRF protection (existing), session management (existing)
  - ✅ Anti-DDOS (existing rate-limit), extended to chat endpoints
  - ✅ Rate limiting on conversation creation (20 per minute)
  - ✅ Message sanitization (HTML escaping, max length enforcement)
  - ✅ Role-based access control for all views (product CRUD, address management, delivery requests)

### Recent Infrastructure Updates (Nov 17, 2025)
- ✅ **Settings Modularization:** Single `settings.py` replaced with `farmIT/settings/base.py`, `dev.py`, and `prod.py` for clear environment separation.
- ✅ **Production Security Hardening:** Prod profile enforces `SECURE_SSL_REDIRECT`, HSTS (`SECURE_HSTS_SECONDS=31536000`, preload, include subdomains), secure session/CSRF cookies, trusted proxy header, and manifest-compressed static files.
- ✅ **Procfile Update:** Release and web processes now set `DJANGO_SETTINGS_MODULE=farmIT.settings.prod`, guaranteeing prod-safe defaults during deploys.
- ✅ **Deploy Checks:** `manage.py check --deploy` passes under prod configuration when a strong `DJANGO_SECRET_KEY` is provided via environment variable.
- 🔜 **Phase 4 Preparation:** With infrastructure locked down, the next working session will focus on Phase 4 (cloud database + hosting + Supabase integration) right after concluding Phase 3 testing.

### UI/UX Changes
- Registration ✅ **COMPLETED & ENHANCED**
  - ✅ Role selection with enhanced card-style UI (Customer/Farmer) with icons and descriptions
  - ✅ Professional form design with improved visual hierarchy
- Navigation ✅ **COMPLETED**
  - ✅ If `role=CUSTOMER`: marketplace as home; hide product create/edit/delete
  - ✅ If `role=FARMER`: show `My Farm` page, `Manage Products`
- Pages ✅ **COMPLETED & ENHANCED**
  - ✅ Farm Page: banner, branding, description, location, product grid, "Chat with Farmer" button, reviews section
  - ✅ Product Detail: "Chat with Farmer" button for customers, "View Farm Page" link, "Get Delivery Quote" link
  - ✅ Chat: professional inbox and conversation view with enhanced UI (polling), upgrade to realtime later
  - ✅ Marketplace: filters (existing) + horizontal carousel banner for featured farms with ratings and top products
  - ✅ Maps/Delivery:
    - ✅ Customer address book with create/list/set default functionality
    - ✅ "Get Delivery Quote" on product detail → distance, ETA, fee calculation
    - ✅ Delivery request creation and management
    - ✅ Delivery list view for both customers and farmers
  - ✅ UI/UX Enhancements:
    - ✅ Creative farmer-themed gradient background (amber to green sunrise effect)
    - ✅ Horizontal carousel for featured farms (auto-rotate every 7 seconds)
    - ✅ Pagination system (12 products per page)
    - ✅ Enhanced product cards with hover effects
    - ✅ Professional review cards and forms
    - ✅ Frosted glass effects and backdrop blur throughout

### Data Migration Steps
1) ✅ Add `role` to `users.FarmerUser` (default `FARMER`) + create profiles - **COMPLETED**
2) ✅ Create `Farm` for each existing farmer - **COMPLETED**
3) ✅ Add `farm` FK to `Product` (nullable) and backfill via farmer's farm - **COMPLETED**
4) ✅ Backfill empty farm slugs via data migration - **COMPLETED**
5) ✅ Create `Conversation`, `Message` tables - **COMPLETED**
6) ✅ Create `Review`, `Address`, `DeliveryRequest` tables - **COMPLETED**
7) ✅ Add `latitude` and `longitude` fields to `Farm` model - **COMPLETED**
8) ⏳ Make `farm` non-null; plan to drop legacy `farmer_id` later - **DEFERRED** (farm FK is nullable for backward compatibility)
9) ⏳ Add indexes for filters and highlights; spatial-friendly indexes on `(latitude, longitude)` - **OPTIONAL** (can be added during Phase 4 optimization)

### Performance & Future Work
- Add queryset prefetch/select_related in marketplace and farm pages
- Cache rating aggregates per farm (denormalized fields or cached properties)
- Upgrade chat to Django Channels (WebSockets) in Phase 4+
- Cache distance/ETA quotes by `(farm_id, lat, lng)` with short TTL; dedupe calls

### Compliance with Rules
- Infrastructure: aligns to project goals and existing Django stack
- Design: professional, Tailwind-based, role-aware navigation and pages
- Security: rate limiting, permissions, sanitization, no mock data introduced

### Phase 3 Completion Status (Updated)

**✅ COMPLETED FEATURES:**
1. **Role Selection & Management**
   - ✅ Role field added to `FarmerUser` model (CUSTOMER/FARMER)
   - ✅ `FarmerProfile` and `CustomerProfile` models created
   - ✅ Enhanced registration form with card-style role selection UI
   - ✅ Role-based redirects: Customers → Marketplace, Farmers → My Farm
   - ✅ Role-based permissions on all views (product CRUD restricted to farmers)

2. **Farm Pages**
   - ✅ `Farm` model with slug, branding, and description fields
   - ✅ My Farm page for farmers to manage their virtual farm
   - ✅ Public farm detail pages with product listings
   - ✅ Product model updated with `farm` foreign key (nullable for migration compatibility)

3. **Chat MVP**
   - ✅ `Conversation` and `Message` models implemented
   - ✅ Customer-initiated conversations from product/farm pages
   - ✅ Message center (inbox) for both roles
   - ✅ Conversation detail view with message threading
   - ✅ Rate limiting on conversation creation
   - ✅ Enhanced UI for messaging interface

4. **Security & Permissions**
   - ✅ Role-based view decorators and permission checks
   - ✅ Chat throttling (20 conversations per minute per user)
   - ✅ Message sanitization
   - ✅ CSRF protection (existing)
   - ✅ Rate limiting middleware (existing, extended to chat)

**✅ ALL PHASE 3 ITEMS COMPLETED:**
- ✅ Marketplace highlights: horizontal carousel banner with featured farms, ratings, and top products
- ✅ Maps & Delivery Planning: address management, distance/ETA calculation (Haversine), delivery quoting, delivery request system
- ✅ Review/Rating system: farm reviews by customers with star ratings and comments
- ✅ Enhanced UI/UX: creative farmer-themed design with gradient backgrounds, carousel animations, pagination

**📋 TESTING PHASE (DEFERRED):**
- **Status**: Comprehensive Phase 3 testing is planned but intentionally deferred so we can proceed with Phase 4 (Cloud Database & Hosting) setup first.
- **Planned Focus Areas** (to be executed later):
  - Role-based user flows (Customer vs Farmer)
  - Chat functionality (conversation creation, messaging, permissions)
  - Farm management (creation, editing, product association)
  - Marketplace features (search, filters, pagination, carousel)
  - Review/Rating system (submission, display, permissions)
  - Delivery system (address management, quote calculation, request creation)
  - Security (permissions, rate limiting, CSRF protection)
  - UI/UX responsiveness across devices
  - Edge cases and error handling
- **Planned Testing Approach**: Manual testing + automated tests for critical paths, to be run after initial Phase 4 infrastructure work is in place.
