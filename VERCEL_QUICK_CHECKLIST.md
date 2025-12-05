# ✅ Vercel Deployment Quick Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment
- [ ] Code committed and pushed to GitHub
- [ ] `vercel.json` created in project root
- [ ] `wsgi.py` updated with `app = application`
- [ ] `build.sh` created (optional, for migrations)

## Vercel Setup
- [ ] Signed in to Vercel
- [ ] Created new project
- [ ] Imported GitHub repository
- [ ] Framework preset set to "Other"

## Environment Variables (Set in Vercel Dashboard)
- [ ] `DJANGO_ENV=prod`
- [ ] `DJANGO_SECRET_KEY=<strong-key>`
- [ ] `DATABASE_URL=<supabase-pooler-url>`
- [ ] `DB_CONN_MAX_AGE=600`
- [ ] `DB_SSL_REQUIRE=true`
- [ ] `DJANGO_ALLOWED_HOSTS=<vercel-domain>` (update after first deploy)
- [ ] `CSRF_TRUSTED_ORIGINS=https://<vercel-domain>` (update after first deploy)
- [ ] `SUPABASE_URL=<your-supabase-url>` (if using storage)
- [ ] `SUPABASE_ANON_KEY=<your-anon-key>` (if using storage)
- [ ] `SUPABASE_STORAGE_BUCKET=product-images` (if using storage)

## Deployment
- [ ] Clicked "Deploy"
- [ ] Build completed successfully
- [ ] Got Vercel domain URL

## Post-Deployment
- [ ] `DJANGO_ALLOWED_HOSTS` set (recommend `.vercel.app`)
- [ ] `CSRF_TRUSTED_ORIGINS` set (no wildcard; e.g. https://farm-it-main.vercel.app)
- [ ] Ran migrations (manually or via build script)
- [ ] Redeployed after env var updates

## Testing (Step D)
- [ ] Homepage loads (`/`)
- [ ] Admin panel accessible (`/admin/`)
- [ ] Static files loading (CSS/images)
- [ ] User registration works
- [ ] Login works
- [ ] Marketplace displays products
- [ ] Product creation works (farmers)
- [ ] Image upload works
- [ ] Chat functionality works
- [ ] Reviews work
- [ ] Delivery quotes work
- [ ] HTTPS enforced (no mixed content)
- [ ] Rate limiting works
- [ ] Error pages display correctly (404/500)

## Troubleshooting
- [ ] Checked deployment logs for errors
- [ ] Verified all env vars are set
- [ ] Confirmed database connection
- [ ] Tested static file serving

---

**Status:** ⏳ Ready to deploy | ✅ Deployed | ❌ Issues encountered

**Deployment URL:** `https://________________.vercel.app`

**Notes:**
_________________________________________________
_________________________________________________

