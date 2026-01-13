# Performance App Deployment Checklist

## Issue: 500 Errors After Deployment

The performance app has been pushed to Git, but Render needs to:

### 1. Run Migrations
```bash
# On Render console or via deploy script
python manage.py migrate performance
```

### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 3. Restart the Service
After migrations, restart the Render service.

### 4. Check Logs
If errors persist, check Render logs:
- Settings > Logs
- Look for migration errors or template errors

### Common Issues:

**Missing migrations**: Run `python manage.py migrate` on Render
**Static files**: Run `python manage.py collectstatic`
**Environment variables**: Ensure all required vars are set on Render

### Quick Fix:
1. Go to Render dashboard
2. Shell tab for your service
3. Run: `python manage.py migrate`
4. Restart service

The existing apps (organization, channels, projects) should work fine once migrations are applied.
