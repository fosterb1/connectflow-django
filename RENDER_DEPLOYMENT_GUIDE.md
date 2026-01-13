# RENDER.COM DEPLOYMENT - PERFORMANCE FEATURE

## ✅ What to Check on Render.com

### 1. Trigger New Deployment
Since we just pushed the code, you need to deploy it:

**Go to**: https://dashboard.render.com
1. Click on your **connectflow-django** service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Wait for the build to complete (usually 5-10 minutes)

### 2. Check Build Logs
While deploying, watch the logs:

**Look for these messages:**
```
Installing dependencies...
Collecting static files...
Running database migrations...
  Applying performance.0001_initial... OK
Build complete!
```

**If you see errors:**
- Check if `apps.performance` is in `INSTALLED_APPS`
- Verify migrations folder exists
- Check for database connection issues

### 3. Verify Migration Applied
After deployment completes, you can verify via Render shell:

**In Render Dashboard:**
1. Go to your service
2. Click **"Shell"** tab
3. Run:
```bash
python manage.py showmigrations performance
```

**Expected output:**
```
performance
 [X] 0001_initial
```

### 4. Access the Feature
After successful deployment:

**Admin Panel:**
- URL: `https://your-app.onrender.com/admin/performance/`
- Should see 6 models: KPI Metrics, KPI Thresholds, etc.

**Manager Dashboard:**
- URL: `https://your-app.onrender.com/performance/kpi/metrics/`

**Member Dashboard:**
- URL: `https://your-app.onrender.com/performance/my/dashboard/`

---

## 🔧 If Performance Still Doesn't Show

### Check Environment Variables
Make sure these are set on Render:
- `DJANGO_SETTINGS_MODULE` = `connectflow.settings`
- `DEBUG` = `False` (for production)
- Database credentials are correct

### Force Rebuild
If auto-deploy didn't work:
1. Go to Render dashboard
2. Settings → Build Command
3. Should be: `./build.sh`
4. Click "Save"
5. Manually deploy again

### Check Settings
Verify in your deployed code that `settings.py` has:
```python
INSTALLED_APPS = [
    ...
    'apps.performance',
]
```

---

## 🆘 Quick Fixes

### If migrations fail:
```bash
# In Render Shell
python manage.py migrate performance --fake-initial
```

### If admin doesn't show performance:
```bash
# In Render Shell
python manage.py collectstatic --noinput
```

### Force database sync:
```bash
# In Render Shell
python manage.py migrate --run-syncdb
```

---

## ✅ Success Indicators

You'll know it worked when:
1. ✅ Build logs show "Applying performance.0001_initial... OK"
2. ✅ Admin panel shows "Performance" section
3. ✅ No 404 errors on `/performance/` URLs
4. ✅ You can create KPI metrics in admin

---

## 📞 Still Having Issues?

**Check these:**
1. Is the latest commit deployed? (Check commit hash in Render)
2. Did the build complete successfully? (No red errors)
3. Is the database PostgreSQL/production ready?
4. Are there any error messages in logs?

**Common Error Messages:**
- "No such table: kpi_metrics" → Migrations not run
- "404 Not Found" → URLs not configured
- "Permission denied" → Check user role/permissions

---

**Last Deployed**: Check Render dashboard  
**Latest Commit**: ed36635 - "feat: Add KPI & Performance Management System"
