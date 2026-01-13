# KPI & Performance Management System

## Overview

The ConnectFlow Performance Management System provides comprehensive KPI tracking and performance evaluation capabilities for organizations. It enables managers to define metrics, assign them to team members, conduct reviews, and track performance trends over time.

## Key Features

- **Flexible KPI Metrics**: Support for multiple metric types (numeric, percentage, rating, boolean, threshold-based)
- **Role-Based Metrics**: Assign different KPIs based on user roles
- **Automated Scoring**: Calculate scores automatically based on task performance
- **Manual Overrides**: Allow justified manual score adjustments
- **Review Periods**: Support for weekly, monthly, quarterly, and custom periods
- **Historical Tracking**: Preserve all review history and metric versions
- **Audit Trail**: Complete logging of all performance-related actions
- **Role-Based Access**: Strict permissions for managers and members

---

## How KPIs Are Defined

### Creating a KPI Metric

**Who Can Create**: Organization Admins, Department Heads, Team Managers

**Required Fields**:
- **Name**: Descriptive name (e.g., "Task Completion Rate")
- **Description**: Detailed explanation of what the metric measures
- **Metric Type**: 
  - `NUMERIC`: Raw numbers (e.g., tasks completed)
  - `PERCENTAGE`: 0-100% values
  - `RATING`: 1-5 scale
  - `BOOLEAN`: Yes/No
  - `THRESHOLD`: Based on min/target/max values
- **Weight**: Importance factor (0.01-10.00) used in final score calculation
- **Role** (optional): Target role (TEAM_MEMBER, TEAM_MANAGER, etc.)
- **Team** (optional): Specific team this applies to

**Optional Threshold Configuration**:
- **Min Value**: Minimum acceptable performance
- **Target Value**: Expected/goal performance
- **Max Value**: Maximum possible/optimal performance
- **Pass/Fail Enabled**: Whether to enforce minimum threshold

### Example Metrics

1. **Task Completion Rate** (Percentage)
   - Weight: 2.0
   - Target: 90%
   - Applies to: All Team Members

2. **Deadline Adherence** (Percentage)
   - Weight: 1.5
   - Target: 95%
   - Min (Pass/Fail): 80%

3. **Task Volume** (Numeric)
   - Weight: 1.0
   - Target: 20 tasks/month
   - Applies to: Developers

4. **Code Quality Score** (Rating)
   - Weight: 2.5
   - Target: 4.0/5.0
   - Applies to: Senior Developers

---

## How Scores Are Calculated

### Automatic Calculation

The system automatically calculates scores based on user task performance during the review period:

#### 1. Task Completion Rate
```
Score = (Completed Tasks / Total Tasks) × 100
```

#### 2. Deadline Adherence
```
Score = (Tasks Completed On Time / Tasks With Deadlines) × 100
```

#### 3. Task Volume
```
Score = min(100, (Actual Count / Target Count) × 100)
```
Capped at 100% even if exceeding target.

#### 4. Quality Score
```
Score = ((Total Tasks - Reopened Tasks) / Total Tasks) × 100
```
Based on task stability (fewer reopens = higher quality).

### Weighted Final Score

The final review score is calculated as a weighted average:

```
Final Score = Σ(Metric Score × Weight) / Σ(Weights)
```

**Example**:
- Task Completion: 85% × 2.0 = 170
- Deadline Adherence: 92% × 1.5 = 138
- Task Volume: 75% × 1.0 = 75
- Total: 383 / 4.5 weights = **85.11**

### Manual Overrides

Managers can manually override calculated scores when justified:
- **Reason Required**: Must provide explanation
- **Audit Logged**: All overrides are tracked
- **Original Preserved**: Calculated score is kept for reference
- **Effective Score**: Override takes precedence in final calculation

---

## How Reviews Are Finalized

### Review Lifecycle

1. **Draft State** (Initial)
   - Manager creates review for a user
   - Specifies review period (start/end dates)
   - System auto-generates scores based on KPI assignments
   - Scores can be viewed and overridden
   - Comments can be added

2. **Finalization**
   - Manager reviews all scores
   - Adds overall feedback comments
   - Clicks "Finalize Review"
   - System calculates weighted final score
   - Status changes to FINALIZED
   - Timestamp recorded

3. **Locked State** (After Finalization)
   - **Cannot** edit scores
   - **Cannot** change comments
   - **Cannot** delete review
   - Preserves snapshot integrity
   - Member can view their finalized review

### What Happens on Finalization

```python
1. Validate all scores are present
2. Calculate weighted final score
3. Set status = FINALIZED
4. Record finalized_at timestamp
5. Log action to audit trail
6. Lock review from further edits
```

---

## Review Periods

### Supported Formats

- **Monthly**: `2026-01`, `2026-02`, etc.
- **Quarterly**: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`
- **Weekly**: `2026-W01`, `2026-W02`, etc.
- **Custom**: Any start/end date range

### Period Matching

KPI assignments use the same period identifier:
- Review period: `2026-01`
- Assigned KPIs: `review_period="2026-01"`
- System automatically matches and calculates

---

## Permissions & Access Control

### Organization Admin
- ✅ Create/edit all KPI metrics
- ✅ Assign KPIs to any user
- ✅ Create reviews for any user
- ✅ View all reviews
- ✅ Override any score
- ✅ Finalize any review
- ✅ View audit logs

### Department Head
- ✅ Create/edit KPI metrics
- ✅ Assign KPIs to department members
- ✅ Create reviews for department members
- ✅ View department reviews
- ✅ Override scores in own reviews
- ✅ Finalize own reviews

### Team Manager
- ✅ Create/edit KPI metrics
- ✅ Assign KPIs to team members only
- ✅ Create reviews for team members only
- ✅ View own team reviews
- ✅ Override scores in own reviews
- ✅ Finalize own reviews

### Team Member
- ✅ View own KPI assignments
- ✅ View own performance dashboard
- ✅ View own review history
- ❌ Cannot create metrics
- ❌ Cannot assign KPIs
- ❌ Cannot create reviews
- ❌ Cannot override scores
- ❌ Cannot view others' reviews

---

## Audit Trail

All actions are logged with:
- **Actor**: Who performed the action
- **Action Type**: What was done
- **Target User**: Who was affected
- **Timestamp**: When it occurred
- **Reason**: Justification (for overrides)
- **Details**: Additional context (JSON)

### Logged Actions

- `METRIC_CREATED`: New KPI metric created
- `METRIC_UPDATED`: KPI metric modified
- `METRIC_DEACTIVATED`: KPI metric set inactive
- `ASSIGNMENT_CREATED`: KPI assigned to user
- `REVIEW_CREATED`: Performance review initiated
- `SCORE_CALCULATED`: Automatic score generated
- `SCORE_OVERRIDDEN`: Manual override applied
- `REVIEW_FINALIZED`: Review locked and completed

### Accessing Audit Logs

**Admin Panel**: `/admin/performance/performanceauditlog/`

**Programmatic**:
```python
from apps.performance.models import PerformanceAuditLog

# Get recent actions
logs = PerformanceAuditLog.objects.filter(
    organization=org
).order_by('-timestamp')[:50]
```

---

## Usage Examples

### 1. Create a KPI Metric (Manager)

```python
from apps.performance.models import KPIMetric, KPIThreshold
from decimal import Decimal

# Create metric
metric = KPIMetric.objects.create(
    organization=org,
    name="Task Completion Rate",
    description="Percentage of tasks completed successfully",
    metric_type=KPIMetric.MetricType.PERCENTAGE,
    weight=Decimal('2.00'),
    role='TEAM_MEMBER',
    created_by=manager_user
)

# Add threshold
KPIThreshold.objects.create(
    metric=metric,
    min_value=Decimal('70.00'),
    target_value=Decimal('90.00'),
    max_value=Decimal('100.00'),
    pass_fail_enabled=True
)
```

### 2. Assign KPIs to User

```python
from apps.performance.models import KPIAssignment

assignment = KPIAssignment.objects.create(
    metric=metric,
    user=team_member,
    review_period='2026-01',
    assigned_by=manager
)
```

### 3. Create and Conduct Review

```python
from apps.performance.models import PerformanceReview
from apps.performance.services import PerformanceScoringService
from datetime import date

# Create review
review = PerformanceReview.objects.create(
    user=team_member,
    reviewer=manager,
    organization=org,
    review_period_start=date(2026, 1, 1),
    review_period_end=date(2026, 1, 31)
)

# Auto-generate scores
PerformanceScoringService.generate_review_scores(review, manager)

# Optional: Override a score
score = review.scores.first()
PerformanceScoringService.override_score(
    score=score,
    new_score=Decimal('95.00'),
    reason="Exceptional performance on critical project",
    actor=manager
)

# Finalize review
PerformanceScoringService.finalize_review(review, manager)
```

### 4. View Performance (Member)

```python
# Get current KPI assignments
from django.utils import timezone

current_period = timezone.now().strftime('%Y-%m')
assignments = KPIAssignment.objects.filter(
    user=member,
    review_period=current_period
)

# Get performance history
reviews = PerformanceReview.objects.filter(
    user=member,
    status=PerformanceReview.ReviewStatus.FINALIZED
).order_by('-review_period_end')
```

---

## API Endpoints

### GET `/performance/api/metrics/`
Returns active KPI metrics for organization (JSON)

### GET `/performance/api/my-performance/`
Returns user's performance review history (JSON)

### GET `/performance/api/team-performance/`
Returns team performance data (Manager only, JSON)

### POST `/performance/review/create/`
Create new performance review

### POST `/performance/score/<score_id>/override/`
Override a calculated score

### POST `/performance/review/<review_id>/finalize/`
Finalize and lock a review

---

## Database Schema

### Tables

- `kpi_metrics`: KPI metric definitions
- `kpi_thresholds`: Performance thresholds for metrics
- `kpi_assignments`: User-metric assignments per period
- `performance_reviews`: Review records
- `performance_scores`: Individual metric scores
- `performance_audit_logs`: Complete audit trail

### Key Indexes

- `organization + is_active` on metrics
- `role + is_active` on metrics
- `user + review_period` on assignments
- `user + status` on reviews
- `organization + timestamp` on audit logs

---

## Best Practices

1. **Define Clear Metrics**: Ensure KPIs are measurable and relevant to roles
2. **Set Realistic Targets**: Base thresholds on historical data
3. **Regular Reviews**: Conduct reviews consistently (monthly/quarterly)
4. **Justify Overrides**: Always provide detailed reasons for manual adjustments
5. **Preserve History**: Never hard-delete metrics; use `is_active=False`
6. **Version Control**: Increment `version` when updating existing metrics
7. **Lock Reviews**: Always finalize reviews to maintain data integrity
8. **Monitor Trends**: Use historical data to adjust targets over time

---

## Troubleshooting

### Issue: Scores not calculating
- **Check**: Ensure KPIs are assigned for the review period
- **Check**: Verify user has tasks in the date range
- **Check**: Confirm metric type matches calculation logic

### Issue: Cannot finalize review
- **Check**: User has permission (reviewer or admin)
- **Check**: Review is in DRAFT status
- **Check**: All assigned KPIs have scores

### Issue: Override not working
- **Check**: Review is not finalized
- **Check**: Reason field is not empty
- **Check**: User has edit permission

---

## Support

For technical issues or questions:
- Check Admin Panel: `/admin/performance/`
- View Audit Logs: `/admin/performance/performanceauditlog/`
- Contact: System Administrator

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Module**: `apps.performance`
