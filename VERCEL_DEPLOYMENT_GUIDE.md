# 🚀 Vercel Frontend Deployment Guide for FarmIT

This guide provides step-by-step instructions to deploy your Django application to Vercel.

---

## 📋 Prerequisites

- ✅ GitHub account
- ✅ Vercel account (free tier is sufficient)
- ✅ Your Django project is working locally
- ✅ Supabase database connection verified (already completed)

---

## 🔧 Step 1: Prepare Your Project

### 1.1 Ensure Your Code is Committed

Make sure all your changes are committed to Git:

```bash
git add .
git commit -m "Prepare for Vercel deployment"
```

### 1.2 Push to GitHub

If you haven't already, push your code to GitHub:

```bash
git push origin feature/develop
```

**Note:** If you don't have a GitHub repository yet:
1. Go to [GitHub](https://github.com) and create a new repository
2. Follow GitHub's instructions to connect your local repo

---

## 🌐 Step 2: Create Vercel Project

### 2.1 Sign In to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account (recommended for easy integration)

### 2.2 Import Your Repository

1. Click **"Add New..."** → **"Project"**
2. Find and select your `farmIT-main` repository
3. Click **"Import"**

---

## ⚙️ Step 3: Configure Vercel Project Settings

### 3.1 Framework Preset

- **Framework Preset:** Select **"Other"** (Django is not in the list, but that's fine)

### 3.2 Root Directory

- **Root Directory:** Leave as **`.`** (root of repository)

### 3.3 Build Settings

- **Build Command:** Leave **empty** (Vercel will auto-detect from `vercel.json`)
- **Output Directory:** Leave **empty** (Django doesn't need this)

### 3.4 Install Command (Optional)

- Leave as default or set to: `pip install -r requirements.txt`

---

## 🔐 Step 4: Set Environment Variables

Click **"Environment Variables"** and add the following:

### Required Variables:

```
DJANGO_ENV=prod
```

```
DJANGO_SECRET_KEY=<your-strong-production-secret-key>
```
**Generate a strong key:** Use Django's `get_random_secret_key()` or an online generator.

```
DATABASE_URL=<your-supabase-session-pooler-url>
```
**Format:** `postgresql://postgres:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`

```
DB_CONN_MAX_AGE=600
```

```
DB_SSL_REQUIRE=true
```

```
DJANGO_ALLOWED_HOSTS=<your-vercel-domain>.vercel.app
```
**Note:** You'll get the domain after first deployment. You can update this later.

```
CSRF_TRUSTED_ORIGINS=https://<your-vercel-domain>.vercel.app
```
**Note:** Update this after you get your Vercel domain.

### Supabase Storage Variables (if using image uploads):

```
SUPABASE_URL=https://<your-project-ref>.supabase.co
```

```
SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

```
SUPABASE_STORAGE_BUCKET=product-images
```

### Optional Variables:

```
SECURE_HSTS_SECONDS=31536000
```

```
DJANGO_LOG_LEVEL=WARNING
```

---

## 🚀 Step 5: Deploy

1. Click **"Deploy"** button
2. Wait for the build to complete (usually 2-5 minutes)
3. Vercel will show you the deployment URL (e.g., `farmit-main-xyz123.vercel.app`)

---

## ✅ Step 6: Post-Deployment Configuration

### 6.1 Update Environment Variables

After your first deployment, you'll get a Vercel domain. Update these variables:

1. Go to **Project Settings** → **Environment Variables**
2. Update `DJANGO_ALLOWED_HOSTS` to include your Vercel domain:
   ```
   DJANGO_ALLOWED_HOSTS=<your-vercel-domain>.vercel.app
   ```
3. Update `CSRF_TRUSTED_ORIGINS`:
   ```
   CSRF_TRUSTED_ORIGINS=https://<your-vercel-domain>.vercel.app
   ```

### 6.2 Run Migrations

Vercel doesn't automatically run migrations. You have two options:

**Option A: Run migrations manually via Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link to your project
vercel link

# Run migrations
vercel env pull .env.local
python farmIT/manage.py migrate --settings=farmIT.settings.prod
```

**Option B: Add migration to build process (Recommended)**

We'll add a build script that runs migrations automatically. See Step 7.

### 6.3 Redeploy

After updating environment variables, trigger a new deployment:
- Go to **Deployments** tab
- Click **"Redeploy"** on the latest deployment
- Or push a new commit to trigger auto-deployment

---

## 🔧 Step 7: Add Automatic Migrations (Optional but Recommended)

Create a build script that runs migrations automatically:

### 7.1 Create `build.sh`

Create a file `build.sh` in your project root:

```bash
#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python farmIT/manage.py migrate --noinput

# Collect static files
python farmIT/manage.py collectstatic --noinput
```

### 7.2 Update `vercel.json`

Add build command to `vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "bash build.sh",
  "builds": [
    {
      "src": "farmIT/farmIT/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "farmIT/farmIT/wsgi.py"
    }
  ]
}
```

**Note:** Vercel's Python runtime may have limitations with build scripts. If this doesn't work, stick with manual migrations (Option A in Step 6.2).

---

## 🧪 Step 8: Test Your Deployment

### 8.1 Basic Checks

1. **Homepage:** Visit `https://<your-domain>.vercel.app/`
   - Should load without errors

2. **Admin Panel:** Visit `https://<your-domain>.vercel.app/admin/`
   - Should show login page

3. **Static Files:** Check if CSS/images load correctly
   - Look for any broken images or unstyled pages

### 8.2 Core Functionality Tests

Test these key flows:

- ✅ **User Registration:** `/accounts/register/`
- ✅ **Login:** `/accounts/login/`
- ✅ **Marketplace:** `/` (for customers) or `/products/` (for farmers)
- ✅ **Product Creation:** `/products/create/` (farmers only)
- ✅ **Chat:** `/chat/` (after login)
- ✅ **Farm Pages:** `/farm/<slug>/`

---

## 🔍 Troubleshooting

### Issue: 500 Internal Server Error

**Solutions:**
1. Check Vercel deployment logs (click on deployment → "Logs")
2. Verify all environment variables are set correctly
3. Ensure `DJANGO_SECRET_KEY` is strong and unique
4. Check database connection (`DATABASE_URL` format)

### Issue: Static Files Not Loading

**Solutions:**
1. Ensure `collectstatic` runs during build
2. Check `STATIC_ROOT` and `STATIC_URL` in settings
3. Verify WhiteNoise middleware is enabled (already in your `base.py`)

### Issue: CSRF Token Errors

**Solutions:**
1. Verify `CSRF_TRUSTED_ORIGINS` includes your Vercel domain with `https://`
2. Ensure `CSRF_COOKIE_SECURE = True` in production settings (already set)
3. Check that cookies are being set correctly

### Issue: Database Connection Errors

**Solutions:**
1. Verify `DATABASE_URL` uses Supabase Session Pooler (port 6543)
2. Check `DB_SSL_REQUIRE=true` is set
3. Ensure Supabase allows connections from Vercel's IPs (should be automatic)

---

## 📝 Important Notes

### Vercel Limitations

- **Serverless Functions:** Vercel runs Django as serverless functions, which means:
  - Cold starts may occur (first request after inactivity can be slow)
  - Long-running requests may timeout (Vercel has a 10-second timeout for free tier)
  - File uploads work, but large files may have issues

### Static Files

- Static files are served via WhiteNoise (already configured)
- Ensure `collectstatic` runs during build
- Static files are included in the deployment bundle

### Database Migrations

- Migrations don't run automatically
- Run them manually via Vercel CLI or add to build script
- Consider using Django management commands via Vercel's CLI

---

## 🎯 Next Steps (Step D - Post-Deploy Checks)

After successful deployment, proceed with **Step D** from your checklist:

1. ✅ Test farmer & customer login/registration
2. ✅ Test marketplace listing & product detail
3. ✅ Test product create/edit/delete with image upload
4. ✅ Test chat, reviews, delivery quote
5. ✅ Verify HTTPS is enforced
6. ✅ Check rate limiting works
7. ✅ Test error pages (404/500)

---

## 📚 Additional Resources

- [Vercel Django Documentation](https://vercel.com/docs/frameworks/django)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

**Ready to deploy?** Follow Steps 1-8 above, and you'll have your FarmIT application live on Vercel! 🚀

