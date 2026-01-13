# ⚡ KPI System - Quick Cheat Sheet

## For Managers: 5-Step Process

```
1. CREATE KPI METRICS
   Performance → Manage KPIs → Create KPI
   Example: "Task Completion Rate" (Percentage, Target: 90%)

2. ASSIGN TO TEAM MEMBERS
   Performance → Assign KPIs
   Select: Metric + Member + Period (e.g., 2026-01)

3. CREATE REVIEW (End of Month)
   Admin → Performance Reviews → Add
   Select: Member + Start/End dates

4. GENERATE SCORES
   Django Shell:
   PerformanceScoringService.generate_review_scores(review, manager)

5. FINALIZE
   Admin → Open Review → Change Status to "Finalized" → Save
```

## For Team Members: 2-Step Process

```
1. VIEW YOUR KPIS
   My Performance → See current assigned KPIs

2. VIEW YOUR REVIEWS
   My Performance → Recent Reviews → Click to view details
```

## Key URLs

| Action | URL |
|--------|-----|
| Manager KPI List | `/performance/kpi/metrics/` |
| Create KPI | `/performance/kpi/metrics/create/` |
| Assign KPIs | `/performance/kpi/assign/` |
| Team Overview | `/performance/team/overview/` |
| Member Dashboard | `/performance/my/dashboard/` |
| Admin Panel | `/admin/performance/` |

## Django Shell Commands

```python
# Generate scores for a review
from apps.performance.models import PerformanceReview
from apps.performance.services import PerformanceScoringService
from apps.accounts.models import User

review = PerformanceReview.objects.get(id='<uuid>')
manager = User.objects.get(email='manager@example.com')

PerformanceScoringService.generate_review_scores(review, manager)

# Finalize a review
PerformanceScoringService.finalize_review(review, manager)

# Check scores
for score in review.scores.all():
    print(f"{score.metric.name}: {score.calculated_score}")
```

## Auto-Calculated Metrics

- **Task Completion Rate**: Completed tasks / Total tasks
- **Deadline Adherence**: On-time tasks / Total tasks  
- **Task Volume**: Number of tasks completed
- **Quality Score**: 100% - (Reopened tasks / Total tasks)

## Manual Metrics

- **Team Collaboration**: Manager's subjective rating
- **Communication Skills**: Manager's assessment
- **Innovation**: Manager's evaluation
- **Leadership**: Manager's rating

## Score Calculation

```
Final Score = (Sum of weighted scores) / (Sum of weights)

Example:
- Metric A: 90 × 2.0 = 180
- Metric B: 80 × 1.5 = 120
- Metric C: 95 × 1.0 = 95
Total: 395 / 4.5 = 87.78/100
```

## Grading Scale

| Score | Grade |
|-------|-------|
| 90-100 | Excellent ⭐⭐⭐⭐⭐ |
| 75-89 | Good ⭐⭐⭐⭐ |
| 60-74 | Satisfactory ⭐⭐⭐ |
| 50-59 | Needs Improvement ⚠️ |
| 0-49 | Poor ❌ |

## Permissions

| Action | Admin | Manager | Member |
|--------|-------|---------|--------|
| Create KPIs | ✅ | ✅ | ❌ |
| Assign KPIs | ✅ | ✅ (own team) | ❌ |
| Create Reviews | ✅ | ✅ (own team) | ❌ |
| Finalize Reviews | ✅ | ✅ (own reviews) | ❌ |
| View Own KPIs | ✅ | ✅ | ✅ |
| View Own Reviews | ✅ | ✅ | ✅ |
| View Team Performance | ✅ | ✅ | ❌ |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No Performance in sidebar | Redeploy from Render.com |
| Can't create KPI | Check you're Admin/Manager |
| Scores are null | Run generate_review_scores() |
| Can't finalize | All scores must be present |
| Member can't see review | Review must be finalized |

## Support

- Full Guide: `HOW_KPI_WORKS.md`
- Visual Guide: `KPI_VISUAL_GUIDE.md`
- Documentation: `KPI_PERFORMANCE_DOCUMENTATION.md`
- Admin Panel: `/admin/performance/`

---

**Last Updated**: January 13, 2026
