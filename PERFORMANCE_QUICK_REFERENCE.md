# Performance Management - Quick Reference

## 🚀 Quick Start

### For Managers

**Create a KPI Metric:**
```python
from apps.performance.models import KPIMetric
from decimal import Decimal

KPIMetric.objects.create(
    organization=request.user.organization,
    name="Task Completion Rate",
    metric_type=KPIMetric.MetricType.PERCENTAGE,
    weight=Decimal('2.00'),
    role='TEAM_MEMBER',
    created_by=request.user
)
```

**Assign KPI to User:**
```python
from apps.performance.models import KPIAssignment

KPIAssignment.objects.create(
    metric=kpi_metric,
    user=team_member,
    review_period='2026-01',  # YYYY-MM format
    assigned_by=request.user
)
```

**Generate Review:**
```python
from apps.performance.models import PerformanceReview
from apps.performance.services import PerformanceScoringService
from datetime import date

review = PerformanceReview.objects.create(
    user=team_member,
    reviewer=request.user,
    organization=request.user.organization,
    review_period_start=date(2026, 1, 1),
    review_period_end=date(2026, 1, 31)
)

# Auto-calculate scores
PerformanceScoringService.generate_review_scores(review, request.user)

# Finalize when ready
PerformanceScoringService.finalize_review(review, request.user)
```

**Override a Score:**
```python
from decimal import Decimal

PerformanceScoringService.override_score(
    score=performance_score,
    new_score=Decimal('95.00'),
    reason="Exceptional performance on Project X",
    actor=request.user
)
```

---

### For Members

**View My KPIs:**
```python
from apps.performance.models import KPIAssignment

my_kpis = KPIAssignment.objects.filter(
    user=request.user,
    review_period='2026-01'
).select_related('metric')
```

**View My Reviews:**
```python
from apps.performance.models import PerformanceReview

my_reviews = PerformanceReview.objects.filter(
    user=request.user,
    status=PerformanceReview.ReviewStatus.FINALIZED
).order_by('-review_period_end')
```

---

## 📊 Common Queries

**Get Team Performance:**
```python
reviews = PerformanceReview.objects.filter(
    organization=org,
    status=PerformanceReview.ReviewStatus.FINALIZED
).select_related('user').order_by('-final_score')[:10]
```

**Check Current Period:**
```python
from apps.performance.utils import ReviewPeriodHelper

current_period = ReviewPeriodHelper.get_current_period('monthly')  # '2026-01'
```

**Get Period Dates:**
```python
start, end = ReviewPeriodHelper.get_period_dates('2026-Q1')
```

**View Audit Logs:**
```python
from apps.performance.models import PerformanceAuditLog

logs = PerformanceAuditLog.objects.filter(
    organization=org,
    action=PerformanceAuditLog.ActionType.SCORE_OVERRIDDEN
).order_by('-timestamp')[:20]
```

---

## 🔑 Permission Checks

```python
from apps.performance.permissions import PerformancePermissions

# Can create KPI?
PerformancePermissions.can_create_kpi_metric(user)

# Can assign KPI to target user?
PerformancePermissions.can_assign_kpi(user, target_user)

# Can finalize review?
PerformancePermissions.can_finalize_review(user, review)

# Can view team performance?
PerformancePermissions.can_view_team_performance(user)
```

---

## 🌐 URLs

**Manager Views:**
- `/performance/kpi/metrics/` - List KPI metrics
- `/performance/kpi/metrics/create/` - Create new metric
- `/performance/kpi/assign/` - Assign KPIs
- `/performance/team/overview/` - Team performance
- `/performance/review/<id>/` - Review details

**Member Views:**
- `/performance/my/dashboard/` - Personal dashboard
- `/performance/my/history/` - Performance history

**API:**
- `/performance/api/metrics/` - KPI metrics (JSON)
- `/performance/api/my-performance/` - My data (JSON)
- `/performance/api/team-performance/` - Team data (JSON)

---

## 📝 Metric Types

| Type | Use Case | Example |
|------|----------|---------|
| NUMERIC | Count-based | Tasks completed (15) |
| PERCENTAGE | 0-100 values | Completion rate (85%) |
| RATING | 1-5 scale | Code quality (4.5) |
| BOOLEAN | Yes/No | Certified (Yes) |
| THRESHOLD | Target-based | Revenue ($50k vs $60k target) |

---

## 📅 Review Periods

| Format | Example | Description |
|--------|---------|-------------|
| Monthly | `2026-01` | January 2026 |
| Quarterly | `2026-Q1` | Q1 2026 (Jan-Mar) |
| Weekly | `2026-W01` | Week 1 of 2026 |
| Custom | Start/End dates | Any date range |

---

## ⚡ Management Commands

**Bulk Generate Reviews:**
```bash
python manage.py generate_reviews --period 2026-01 --org <org_uuid>
python manage.py generate_reviews --period 2026-Q1 --org <org_uuid> --auto-finalize
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test apps.performance

# Run specific test
python manage.py test apps.performance.tests.PerformanceReviewTestCase

# Check system
python manage.py check
```

---

## 📊 Score Calculation

**Task Completion Rate:**
```
Score = (Completed Tasks / Total Tasks) × 100
```

**Deadline Adherence:**
```
Score = (On-Time Tasks / Tasks With Deadlines) × 100
```

**Final Weighted Score:**
```
Final = Σ(Score × Weight) / Σ(Weights)
```

Example:
- Completion: 85% × 2.0 = 170
- Quality: 90% × 1.5 = 135
- Final: 305 / 3.5 = **87.14**

---

## 🎯 Best Practices

1. **Set Realistic Targets**: Base on historical data
2. **Document Overrides**: Always provide detailed reasons
3. **Regular Reviews**: Monthly or quarterly
4. **Version Metrics**: Increment version on changes
5. **Lock Reviews**: Finalize to preserve integrity
6. **Monitor Trends**: Use historical data to adjust

---

## 🆘 Troubleshooting

**Issue**: Scores not calculating  
**Fix**: Ensure KPIs assigned for the period and user has tasks

**Issue**: Cannot finalize review  
**Fix**: Check review status is DRAFT and user has permission

**Issue**: Override fails  
**Fix**: Ensure reason is provided and review not finalized

---

## 📞 Support

- **Admin Panel**: `/admin/performance/`
- **Audit Logs**: `/admin/performance/performanceauditlog/`
- **Documentation**: `KPI_PERFORMANCE_DOCUMENTATION.md`

---

**Quick Ref v1.0** | ConnectFlow Performance Management
