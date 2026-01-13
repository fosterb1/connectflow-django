# Deployment Checklist - KPI & Performance Management System

## ✅ Pre-Deployment Verification

### System Checks
- [x] Django system check passes without errors
- [x] All migrations applied successfully
- [x] All tests passing (12/12 tests)
- [x] No breaking changes to existing functionality
- [x] Verification script passes all checks

### Code Quality
- [x] No hard-coded values
- [x] Service layer pattern implemented
- [x] Permissions enforced at all levels
- [x] Transaction-safe database operations
- [x] Proper error handling
- [x] Comprehensive docstrings

### Database
- [x] Models properly defined with indexes
- [x] Foreign key relationships correct
- [x] Cascade behavior appropriate
- [x] Unique constraints in place
- [x] Tenant isolation enforced
- [x] Migration file tested

### Security
- [x] Role-based permissions implemented
- [x] Tenant isolation verified
- [x] Audit trail complete
- [x] No SQL injection vulnerabilities
- [x] Review locking enforced
- [x] Override justification required

---

## 📋 Deployment Steps

### Step 1: Backup
```bash
# Backup current database
python manage.py dumpdata > backup_pre_performance.json

# Or if using PostgreSQL
pg_dump connectflow_db > backup_pre_performance.sql
```

### Step 2: Code Deployment
```bash
# Pull latest code (if using version control)
git pull origin main

# Or verify files are in place
python verify_performance_system.py
```

### Step 3: Install Dependencies
```bash
# No new dependencies required
# System uses only existing Django packages
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
# Apply performance migrations
python manage.py migrate performance

# Verify migration applied
python manage.py showmigrations performance
```

### Step 5: Collect Static Files (Production)
```bash
# If in production
python manage.py collectstatic --noinput
```

### Step 6: Run Tests
```bash
# Run full test suite
python manage.py test apps.performance

# Run system check
python manage.py check --deploy
```

### Step 7: Verify Admin Access
```bash
# Start server
python manage.py runserver

# Navigate to: http://localhost:8000/admin/performance/
# Verify all 6 models are accessible
```

### Step 8: Create Initial Data (Optional)
```bash
# Access Django shell
python manage.py shell

# Create sample KPI metrics for testing
from apps.performance.models import KPIMetric
from apps.accounts.models import User
from apps.organizations.models import Organization
from decimal import Decimal

# Get first org and admin
org = Organization.objects.first()
admin = User.objects.filter(role='ORG_ADMIN').first()

# Create sample metric
KPIMetric.objects.create(
    organization=org,
    name="Task Completion Rate",
    metric_type=KPIMetric.MetricType.PERCENTAGE,
    weight=Decimal('2.00'),
    created_by=admin
)
```

### Step 9: Verify URLs
```bash
# Test URL resolution
python manage.py shell

from django.urls import reverse

# Test URLs
print(reverse('performance:my_dashboard'))
print(reverse('performance:kpi_metric_list'))
print(reverse('performance:team_overview'))
```

### Step 10: Production Restart
```bash
# Restart application server
# For Gunicorn:
sudo systemctl restart gunicorn

# For uwsgi:
sudo systemctl restart uwsgi

# For development:
python manage.py runserver
```

---

## 🧪 Post-Deployment Testing

### Functional Tests

#### 1. Admin Panel
- [ ] Login to `/admin/`
- [ ] Navigate to Performance section
- [ ] Verify all 6 models are visible
- [ ] Create a test KPI metric
- [ ] View audit logs

#### 2. Manager Functionality
- [ ] Login as manager
- [ ] Navigate to `/performance/kpi/metrics/`
- [ ] Create a new KPI metric
- [ ] Assign KPI to team member
- [ ] Create performance review
- [ ] View team performance overview

#### 3. Member Functionality
- [ ] Login as team member
- [ ] Navigate to `/performance/my/dashboard/`
- [ ] View assigned KPIs
- [ ] View performance history

#### 4. API Endpoints
```bash
# Test with curl or Postman

# Get metrics
curl -H "Authorization: Token <token>" \
  http://localhost:8000/performance/api/metrics/

# Get personal performance
curl -H "Authorization: Token <token>" \
  http://localhost:8000/performance/api/my-performance/
```

#### 5. Permissions
- [ ] Verify member cannot access manager views
- [ ] Verify manager can only manage their team
- [ ] Verify admin has full access
- [ ] Test finalized review locking

---

## 📊 Monitoring

### Performance Metrics to Monitor

1. **Database Performance**
   - Query execution times for review generation
   - Index usage on filtered queries
   - Number of records in audit log

2. **User Activity**
   - Number of active KPI metrics
   - Number of reviews created per period
   - Number of score overrides

3. **System Health**
   - Error rates in scoring calculations
   - API response times
   - Failed review finalizations

### Logging
```python
# Check logs for any errors
# In settings.py, ensure logging is configured:

LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/connectflow/performance.log',
        },
    },
    'loggers': {
        'apps.performance': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## 🔄 Rollback Plan

### If Issues Occur

1. **Rollback Migration**
   ```bash
   python manage.py migrate performance zero
   ```

2. **Remove from URLs**
   ```python
   # In connectflow/urls.py, comment out:
   # path('performance/', include('apps.performance.urls')),
   ```

3. **Remove from INSTALLED_APPS**
   ```python
   # In settings.py, comment out:
   # 'apps.performance',
   ```

4. **Restart Server**
   ```bash
   sudo systemctl restart gunicorn
   ```

5. **Restore Database (if needed)**
   ```bash
   python manage.py loaddata backup_pre_performance.json
   ```

---

## 📞 Support Resources

### Documentation
- User Guide: `KPI_PERFORMANCE_DOCUMENTATION.md`
- Quick Reference: `PERFORMANCE_QUICK_REFERENCE.md`
- API Docs: See `API_DOCUMENTATION.md`

### Troubleshooting
- Check logs: `/var/log/connectflow/performance.log`
- Run verification: `python verify_performance_system.py`
- Run tests: `python manage.py test apps.performance`

### Common Issues

**Issue**: Migrations fail
**Solution**: Check database permissions, ensure previous migrations are applied

**Issue**: 404 on performance URLs
**Solution**: Verify URL configuration in `connectflow/urls.py`

**Issue**: Permission denied errors
**Solution**: Check user roles, verify organization membership

**Issue**: Scores not calculating
**Solution**: Ensure KPIs are assigned for the review period, verify user has tasks

---

## ✅ Sign-Off

### Pre-Deployment
- [ ] All checks completed
- [ ] Tests passing
- [ ] Documentation reviewed
- [ ] Backup created
- [ ] Stakeholders notified

### Deployment
- [ ] Code deployed
- [ ] Migrations applied
- [ ] Static files collected
- [ ] Server restarted
- [ ] Post-deployment tests passed

### Post-Deployment
- [ ] Functionality verified
- [ ] Performance acceptable
- [ ] No errors in logs
- [ ] Users can access features
- [ ] Monitoring in place

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Approved By**: _____________  

---

**Status**: Ready for Deployment ✅
