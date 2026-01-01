# Security Update Deployment Guide

## Quick Start - Deploying Security Fixes

This guide helps you deploy the January 2026 security updates to production safely.

---

## 🚦 Pre-Deployment Checklist

### 1. Review Changes
```bash
git status
git diff connectflow/settings.py
git diff apps/organizations/billing_views.py
```

### 2. Backup Current Production
```bash
# Backup database (adjust for your hosting)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Backup environment variables
# Copy current .env or environment config to safe location
```

### 3. Test Locally First
```bash
# Set DEBUG=False locally
export DEBUG=False
export SECRET_KEY="test-key-minimum-50-characters-long-random-string"
export ALLOWED_HOSTS="localhost,127.0.0.1"

# Run checks
python manage.py check --deploy
python manage.py migrate --plan

# Start server and test
python manage.py runserver
```

---

## 📋 Deployment Steps

### Step 1: Update Environment Variables

**CRITICAL**: Set these on your hosting platform (Render/Heroku/Railway):

```bash
# Required Updates
SECRET_KEY=<generate-new-50-char-random-string>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,*.onrender.com

# Verify These Exist
PAYSTACK_SECRET_KEY=sk_live_...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
```

**Generate Secret Key** (run locally):
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### Step 2: Deploy Code Changes

#### For Render.com:
```bash
git add .
git commit -m "security: implement critical security hardening updates"
git push origin main
# Render auto-deploys from main branch
```

#### For Railway:
```bash
git push railway main
```

#### For Heroku:
```bash
git push heroku main
```

---

### Step 3: Run Migrations

The deployment should auto-run migrations, but verify:

**Render**: Check deploy logs for:
```
Running migrations:
  Applying accounts.0012_add_database_indexes... OK
```

**Manual Migration** (if needed via Render Shell):
```bash
python manage.py migrate
```

---

### Step 4: Verify Deployment

#### A. Check Security Headers
```bash
curl -I https://your-app.onrender.com

# Should see:
# Strict-Transport-Security: max-age=31536000
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Referrer-Policy: strict-origin-when-cross-origin
```

#### B. Test Paystack Webhook
```bash
# In Render logs, webhook requests should show:
[INFO] Subscription created for org <uuid>

# Or security warnings for invalid signatures:
[WARNING] Invalid Paystack webhook signature
```

#### C. Check Application Works
1. Visit login page: `https://your-app.onrender.com/accounts/login/`
2. Test Google Sign-In
3. Upload a file (test Cloudinary)
4. Send a message (test WebSockets)

---

## 🔍 Post-Deployment Verification

### 1. Check Logs
```bash
# Render: View logs in dashboard
# Look for errors like:
# - "CRITICAL: SQLite detected in production!"
# - Any 500 errors
```

### 2. Test Paystack Webhook (Important!)

**Set Webhook URL in Paystack Dashboard**:
```
https://your-app.onrender.com/organizations/billing/webhook/paystack/
```

**Send Test Event**:
- Go to Paystack Dashboard > Settings > Webhooks
- Send test event for `subscription.create`
- Check Render logs for signature verification success

### 3. Verify HTTPS Redirect
```bash
curl -I http://your-app.onrender.com
# Should see 301 redirect to https://
```

### 4. Test Error Pages
- Visit `/admin/` without login
- Should NOT see debug information
- Should see clean error page

---

## ⚠️ Troubleshooting

### Issue: "SECRET_KEY environment variable must be set"
**Solution**: 
```bash
# In Render dashboard:
# Environment > Add Variable
SECRET_KEY=<paste-50-char-random-key>
# Save and redeploy
```

### Issue: "CRITICAL: SQLite detected in production!"
**Solution**:
```bash
# Ensure DATABASE_URL is set:
DATABASE_URL=postgresql://user:password@host:port/dbname
# Render sets this automatically, verify it exists
```

### Issue: Paystack webhook returns 401
**Possible Causes**:
1. Signature mismatch (Paystack signature changed?)
2. PAYSTACK_SECRET_KEY incorrect
3. Request body modified in transit

**Debug**:
```bash
# Add to billing_views.py temporarily:
logger.info(f"Received signature: {paystack_signature}")
logger.info(f"Request body: {request.body}")
```

### Issue: WebSocket connections fail
**Check**:
1. REDIS_URL is set correctly
2. Channel layers configuration in settings
3. CORS settings allow WebSocket origins

---

## 🔄 Rollback Plan

If critical issues arise:

### Quick Rollback (Render)
1. Go to Render Dashboard
2. Select your service
3. Click "Rollback" to previous deployment
4. Verify application works

### Manual Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard <previous-commit-hash>
git push --force origin main
```

**Restore Environment Variables**:
- Restore from backup taken in pre-deployment

---

## 📊 Success Metrics

After deployment, you should see:

✅ **No critical errors** in logs  
✅ **HTTPS working** with valid certificate  
✅ **Webhooks processing** successfully  
✅ **Users can login** via Google/Email  
✅ **Files upload** to Cloudinary  
✅ **Messages send** in real-time  
✅ **Security headers** present in responses  

---

## 🎯 Next Steps (Optional)

### Recommended Enhancements:
1. **Set up rate limiting**:
   ```bash
   pip install django-ratelimit
   # Add to requirements.txt
   ```

2. **Enable monitoring**:
   - Add Sentry for error tracking
   - Set up uptime monitoring (UptimeRobot, Better Uptime)

3. **Automated backups**:
   - Configure Render PostgreSQL backups
   - Or use external service like Cron-based pg_dump

4. **Load testing**:
   ```bash
   pip install locust
   # Run load tests to verify performance
   ```

---

## 📞 Emergency Contacts

**If deployment fails critically**:
1. Immediately rollback using Render dashboard
2. Check error logs for specific issues
3. Verify all environment variables are set
4. Test locally with production settings

**For security incidents**:
- Review SECURITY.md
- Check SECURITY_FIXES.md for what was changed
- Contact project maintainer

---

## ✅ Deployment Complete!

Once all checks pass:
1. ✅ Mark deployment as successful in your tracking system
2. ✅ Update team on new security features
3. ✅ Monitor logs for 24 hours post-deployment
4. ✅ Schedule review of optional enhancements

**Congratulations!** Your ConnectFlow Pro instance is now significantly more secure. 🔒

---

**Last Updated**: January 1, 2026  
**Author**: Foster Boadi  
**Version**: v1.0.0 Security Hardening
