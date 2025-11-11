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

### **Phase 3 (CRUCIAL FEATS): Roles, Chat MVP, Farm Pages, Marketplace Highlights, Maps (Weeks 8–10)**
- NOTE: Supabase database integration and hosting are paused during this phase and moved to Phase 4.
- [ ] Role selection at registration (Customer/Farmer) and role-based redirects
- [ ] Customer: marketplace-first landing, no product CRUD; chat entry points
- [ ] Farmer: virtual farm page creation and management; product management under farm
- [ ] Chat MVP: customer-initiated conversations, farmer replies; message center
- [ ] Marketplace highlights: farm cards with top products and rating snapshots
- [ ] Security: permission gates by role, rate-limit chat creation, content sanitization
- [ ] Maps & Delivery Planning: addresses/locations, distance/ETA, delivery quoting, map display

### **Phase 4: Cloud Database & Hosting (Shifted) (Weeks 11–12)**
- [ ] Django backend setup with Supabase PostgreSQL connection
- [ ] Product image upload to Supabase storage
- [ ] Deployment setup (Railway backend, Vercel frontend)

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
| **Next Step** | Implement Phase 3 CRUCIAL FEATS | Roles, chat MVP, farm pages, marketplace highlights, maps |

---

**Author:** MJ Villahermosa  
**Date:** November 2025  
**Purpose:** Strategic and technical documentation for *FarmIt* — to guide initial development and align coding agents or contributors.


---

## 🔧 Phase 3 (CRUCIAL FEATS) — Implementation Plan (Tied to Current Code)

### Current Status (as of today)
- Custom user model `users.FarmerUser` in use (`AUTH_USER_MODEL` set)
- Product CRUD, templates (`products` app), admin, search & filters exist
- Rate limiting middleware present (`farmIT.middleware.RateLimitMiddleware`)
- Local dev on SQLite; env-ready to switch to Postgres (optional)

### Backend Changes
- User Roles
  - Add `role` to `users.FarmerUser` with choices: `CUSTOMER`/`FARMER`; default `FARMER` for existing
  - Add `FarmerProfile` and `CustomerProfile` (OneToOne to User)
  - Registration: require role selection and create respective profile
- Farm Pages
  - Create `Farm` (OneToOne to farmer user) with slug and branding fields
  - Refactor `Product` to reference `Farm`; add migration path and data backfill
  - Permissions: only farmer owners of a farm can manage products
- Chat
  - `Conversation` and `Message` models (customer starts; farmer replies)
  - Views: create/start on product or farm page, list conversations, list/send messages
  - Throttling: per-user rate limit on conversation creation and message sending
  - Sanitization: escape message HTML; enforce max length
- Marketplace & Reviews
  - Add `Review` on `Farm` by customers; compute average rating and counts
  - Marketplace queries: highlight farms (avg rating, review count, popular products)
- Maps & Delivery (MVP, FoodPanda-style planning)
  - Models:
    - `Address`: `user` (FK), `label`, `line1`, `barangay`, `city`, `province`, `postal_code`, `country`, `latitude`, `longitude`, `is_default`
    - `DeliveryRequest`: `id`, `customer` (FK), `farm` (FK), `pickup_address` (farm-derived), `dropoff_address` (FK → Address), `distance_km`, `eta_minutes`, `quoted_fee`, `status`, `created_at`
    - `RouteSnapshot` (optional): `delivery_request` (FK), `polyline`, `provider`, `raw_response_json`
  - APIs/Endpoints (Django views/DRF):
    - POST `/deliveries/quote/` → input: farm_id + address_id or freeform address; output: `distance`, `eta`, `fee`
    - POST `/deliveries/create/` → locks quote to a request (status = `PENDING`)
    - GET `/deliveries/:id/` → details incl. route polyline for map display
  - Pricing (configurable): base fee + per-km rate, surge multiplier (future)
  - Providers/Options:
    - Google Maps Platform: Geocoding, Distance Matrix, Directions, Maps JS
    - Mapbox: Geocoding, Directions Matrix, GL JS (good free tier)
    - OpenStreetMap + OSRM/OpenRouteService: open data; hosted/self-host options
  - MVP Strategy (recommended):
    - Use Mapbox for tiles + routes; abstract provider to allow switching later
  - Security & Privacy:
    - Secure address storage; PH bounds validation; rate-limit quoting
    - Keep provider keys server-side; issue minimal client tokens for map SDKs
- Security
  - Role-based decorators/permissions on views
  - CSRF protection (existing), session management (existing)
  - Anti-DDOS (existing rate-limit), extend to chat endpoints

### UI/UX Changes
- Registration
  - Role selection radio buttons (Customer/Farmer) with brief description
- Navigation
  - If `role=CUSTOMER`: marketplace as home; hide product create/edit/delete
  - If `role=FARMER`: show `My Farm` page, `Manage Products`
- Pages
  - Farm Page: banner, branding, description, location, product grid, rating summary, “Chat with Farmer”
  - Product Detail: “Chat with Farmer” button for customers
  - Chat: simple inbox and thread view (polling), upgrade to realtime later
  - Marketplace: filters (existing) + top farms section (rating and top products)
  - Maps/Delivery:
    - Customer address book with geocoding autocomplete
    - “Get Delivery Quote” on product/farm → distance, ETA, fee
    - Map preview with route polyline (farm → customer)

### Data Migration Steps
1) Add `role` to `users.FarmerUser` (default `FARMER`) + create profiles
2) Create `Farm` for each existing farmer
3) Add `farm` FK to `Product` (nullable) and backfill via farmer’s farm
4) Make `farm` non-null; plan to drop legacy `farmer_id` later
5) Create `Conversation`, `Message`, `Review`, `Address`, `DeliveryRequest` tables
6) Add indexes for filters and highlights; spatial-friendly indexes on `(latitude, longitude)`

### Performance & Future Work
- Add queryset prefetch/select_related in marketplace and farm pages
- Cache rating aggregates per farm (denormalized fields or cached properties)
- Upgrade chat to Django Channels (WebSockets) in Phase 4+
- Cache distance/ETA quotes by `(farm_id, lat, lng)` with short TTL; dedupe calls

### Compliance with Rules
- Infrastructure: aligns to project goals and existing Django stack
- Design: professional, Tailwind-based, role-aware navigation and pages
- Security: rate limiting, permissions, sanitization, no mock data introduced
