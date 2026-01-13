# 📊 KPI & Performance Management - Complete Workflow Guide

## 🎯 How It Works: Step-by-Step Guide

---

## **STEP 1: Manager Creates KPI Metrics**

### What is a KPI Metric?
A KPI (Key Performance Indicator) is a measurable value that shows how well an employee is performing.

### How to Create:

1. **Login as Manager/Admin**
2. **Click "Performance"** in the sidebar
3. **Click "Manage KPIs"** button
4. **Click "Create KPI"** button

### Fill in the Form:

**Basic Information:**
- **Name**: e.g., "Task Completion Rate"
- **Description**: e.g., "Percentage of assigned tasks completed on time"
- **Metric Type**: Choose one:
  - `Percentage` - e.g., 85% completion rate
  - `Numeric` - e.g., 50 tasks completed
  - `Rating` - e.g., 4 out of 5 stars
  - `Boolean` - e.g., Yes/No (passed/failed)
  - `Threshold` - e.g., Meet minimum target
- **Weight**: How important this metric is (1.0 = normal, 2.0 = twice as important)

**Assignment Criteria (Optional):**
- **Target Role**: e.g., Only for "Team Members"
- **Target Team**: e.g., Only for "Sales Team"

**Performance Thresholds (Optional):**
- **Minimum Value**: e.g., 60 (below this is poor)
- **Target Value**: e.g., 90 (this is the goal)
- **Maximum Value**: e.g., 100 (perfect score)

### Example KPI Metrics:

```
1. Task Completion Rate
   - Type: Percentage
   - Target: 90%
   - Weight: 2.0 (very important)
   - Auto-calculated from completed tasks

2. Deadline Adherence
   - Type: Percentage
   - Target: 85%
   - Weight: 1.5
   - Auto-calculated from on-time task completion

3. Quality of Work
   - Type: Rating
   - Target: 4.0/5.0
   - Weight: 1.0
   - Manually rated by manager

4. Team Collaboration
   - Type: Rating
   - Target: 4.5/5.0
   - Weight: 1.0
   - Manually rated by manager
```

---

## **STEP 2: Manager Assigns KPIs to Team Members**

### How to Assign:

1. **Click "Performance"** in sidebar
2. **Click "Manage KPIs"**
3. **Click "Assign to Users"** on a KPI card (or use main "Assign KPIs" page)

### Fill in Assignment Form:

- **Select KPI Metric**: Choose from dropdown (e.g., "Task Completion Rate")
- **Select Team Member**: Choose the person (e.g., "John Doe")
- **Review Period**: Choose when to evaluate:
  - `2026-01` - January 2026 (monthly)
  - `2026-Q1` - Quarter 1 2026 (quarterly)
  - `2026-W05` - Week 5 2026 (weekly)

### Example Assignment:

```
Assign to John Doe (Team Member):
- Task Completion Rate (for Jan 2026)
- Deadline Adherence (for Jan 2026)
- Quality of Work (for Jan 2026)
- Team Collaboration (for Jan 2026)
```

**What Happens:**
- John can now see these KPIs in his "My Performance" dashboard
- System will track his performance automatically
- Manager can review and appraise at end of period

---

## **STEP 3: Team Member Views Their KPIs**

### What They See:

1. **Login as Team Member**
2. **Click "My Performance"** in sidebar
3. **View Dashboard** showing:
   - Current assigned KPIs
   - Target values
   - Who assigned them
   - Review period

### Dashboard Shows:

```
Current KPIs (2026-01)

┌─────────────────────────────────────┐
│ Task Completion Rate                │
│ Percentage | Target: 90%            │
│ Assigned by: Manager Smith          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Deadline Adherence                  │
│ Percentage | Target: 85%            │
│ Assigned by: Manager Smith          │
└─────────────────────────────────────┘
```

**What They Can Do:**
- View their assigned KPIs
- See performance targets
- View past performance reviews
- Track their progress (read-only, cannot edit)

---

## **STEP 4: System Auto-Calculates Scores (During Period)**

### Automatic Scoring:

The system automatically tracks:

1. **Task Completion Rate**
   - Counts completed tasks vs. total assigned
   - Example: 45 completed / 50 assigned = 90%

2. **Deadline Adherence**
   - Counts on-time tasks vs. late tasks
   - Example: 40 on-time / 50 total = 80%

3. **Task Volume**
   - Total number of tasks handled
   - Example: 50 tasks completed

4. **Task Quality**
   - Based on reopened/rejected tasks
   - Example: 0 reopened = 100% quality

### Example During January:

```
John Doe's Progress (Jan 1-31):
- Completed 45/50 tasks = 90% ✓
- 40 tasks on time = 80% ⚠️
- 0 tasks reopened = 100% quality ✓
```

---

## **STEP 5: Manager Creates Performance Review**

### How to Create Review:

**Option A: Via Admin Panel (Easiest)**
1. Go to `/admin/performance/performancereview/`
2. Click "Add Performance Review"
3. Fill in:
   - **User**: Select team member
   - **Reviewer**: You (auto-filled)
   - **Organization**: Your org (auto-filled)
   - **Review Period Start**: 2026-01-01
   - **Review Period End**: 2026-01-31
   - **Status**: Draft
4. Click "Save"

**Option B: Via Management Command**
```bash
python manage.py generate_reviews --period 2026-01 --organization 1
```

### What Happens:
- Review is created in "Draft" status
- All assigned KPIs for that period are included
- Scores are empty (ready to be calculated)

---

## **STEP 6: Manager Generates Scores**

### Auto-Generate Scores:

**In Admin Panel:**
1. Open the review you created
2. You'll see it has no scores yet
3. Use the scoring service to generate them

**Via Django Shell (Recommended for now):**
```python
python manage.py shell

from apps.performance.models import PerformanceReview
from apps.performance.services import PerformanceScoringService
from apps.accounts.models import User

# Get the review
review = PerformanceReview.objects.get(id='<review-uuid>')

# Get the manager
manager = User.objects.get(email='manager@example.com')

# Generate scores automatically
PerformanceScoringService.generate_review_scores(review, manager)

# Check the scores
for score in review.scores.all():
    print(f"{score.metric.name}: {score.calculated_score}")
```

### What This Does:
- Analyzes all tasks from the review period
- Calculates score for each KPI metric
- Applies weights to each metric
- Creates PerformanceScore records

### Example Output:
```
Task Completion Rate: 90.0 (weight: 2.0 → 180.0 weighted)
Deadline Adherence: 80.0 (weight: 1.5 → 120.0 weighted)
Quality of Work: 100.0 (weight: 1.0 → 100.0 weighted)
Team Collaboration: null (manual rating needed)
```

---

## **STEP 7: Manager Manually Rates Subjective Metrics**

### For Metrics That Can't Be Auto-Calculated:

Some metrics like "Team Collaboration" need manual rating.

**Via Admin Panel:**
1. Go to `/admin/performance/performancescore/`
2. Find the score for "Team Collaboration"
3. Edit it:
   - **Manual Override Score**: 85.0
   - **Override Reason**: "Great team player, helped 3 colleagues with complex tasks"
4. Save

**What Happens:**
- The manual score overrides the calculated score
- Manager's reason is logged for audit trail
- System records who made the override and when

---

## **STEP 8: Manager Reviews and Finalizes**

### Review the Complete Assessment:

**In Admin Panel:**
1. Open the Performance Review
2. Check all scores are present
3. Add overall comments
4. Change status from "Draft" to "Finalized"
5. Save

**Via Django Shell (Alternative):**
```python
from apps.performance.services import PerformanceScoringService

# Finalize the review
PerformanceScoringService.finalize_review(review, manager)
```

### What Finalization Does:
- Calculates weighted final score (0-100)
- Locks the review (no more edits)
- Records finalization timestamp
- Logs action to audit trail
- Makes review visible to team member

### Final Score Calculation:
```
Formula: (Sum of weighted scores) / (Sum of weights) = Final Score

Example:
- Task Completion: 90 × 2.0 = 180
- Deadline Adherence: 80 × 1.5 = 120
- Quality: 100 × 1.0 = 100
- Collaboration: 85 × 1.0 = 85

Total: 485
Total Weight: 5.5
Final Score: 485 / 5.5 = 88.18/100

Grade: Good (75-90 range)
```

---

## **STEP 9: Team Member Views Their Review**

### What They See:

1. **Login as Team Member**
2. **Click "My Performance"** in sidebar
3. **See "Recent Performance Reviews"**
4. **Click on the review** to see details

### Review Detail Shows:

```
Performance Review: Jan 1 - Jan 31, 2026
Reviewer: Manager Smith
Status: Finalized
Final Score: 88.18/100 (Good)

Individual Scores:
┌──────────────────────────────────────┐
│ Task Completion Rate                 │
│ Score: 90/100 (Weight: 2.0)         │
│ Status: Auto-calculated             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Deadline Adherence                   │
│ Score: 80/100 (Weight: 1.5)         │
│ Status: Auto-calculated             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Quality of Work                      │
│ Score: 100/100 (Weight: 1.0)        │
│ Status: Auto-calculated             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Team Collaboration                   │
│ Score: 85/100 (Weight: 1.0)         │
│ Status: Manually rated by Manager   │
│ Reason: Great team player, helped   │
│ 3 colleagues with complex tasks     │
└──────────────────────────────────────┘

Manager Comments:
"Excellent performance overall. Keep up the 
good work on task completion. Focus on 
meeting more deadlines next month."
```

---

## 🔄 **Complete Monthly Cycle**

### Timeline Example (January 2026):

**Week 1 (Jan 1-7):**
- ✅ Manager assigns KPIs to all team members for January
- ✅ Team members see their KPIs in dashboard
- ✅ Everyone starts working on tasks

**Weeks 2-4 (Jan 8-31):**
- ✅ Team members complete tasks
- ✅ System auto-tracks performance
- ✅ Manager can monitor progress in real-time

**End of Month (Jan 31):**
- ✅ Manager creates performance reviews
- ✅ Manager generates auto-scores
- ✅ Manager adds manual ratings for subjective metrics
- ✅ Manager reviews and finalizes

**Early February:**
- ✅ Team members view their finalized reviews
- ✅ Managers discuss results in 1-on-1 meetings
- ✅ System logs everything for compliance

**Next Cycle:**
- ✅ Repeat for February 2026
- ✅ Track trends over time
- ✅ Adjust KPIs as needed

---

## 🎨 **UI Navigation Quick Reference**

### Manager Journey:
```
Login → Performance → Manage KPIs → Create KPI
                    → Assign KPIs → Select user/period
                    → Team Overview → See all reviews
                    → Admin Panel → Create/finalize reviews
```

### Member Journey:
```
Login → My Performance → View Current KPIs
                      → View Performance History
                      → View Review Details
```

---

## 📊 **Performance Grading Scale**

```
90-100: Excellent ⭐⭐⭐⭐⭐
75-89:  Good ⭐⭐⭐⭐
60-74:  Satisfactory ⭐⭐⭐
50-59:  Needs Improvement ⚠️
0-49:   Poor ❌
```

---

## 🔒 **Security & Permissions**

### What Each Role Can Do:

**Admin:**
- ✅ Everything (full access)

**Manager:**
- ✅ Create KPI metrics
- ✅ Assign KPIs to their team members
- ✅ Create reviews for their team
- ✅ View team performance
- ✅ Override scores
- ✅ Finalize reviews
- ❌ Cannot view other managers' teams

**Team Member:**
- ✅ View own assigned KPIs
- ✅ View own performance reviews
- ✅ View own history
- ❌ Cannot create/edit anything
- ❌ Cannot view other members' data

---

## 📝 **Best Practices**

### For Managers:

1. **Set Clear KPIs**: Make metrics specific and measurable
2. **Assign Early**: Assign KPIs at the start of the period
3. **Mix Auto & Manual**: Use auto-calculated + manual metrics
4. **Be Fair**: Use consistent criteria for all team members
5. **Add Comments**: Always explain manual overrides
6. **Finalize Promptly**: Complete reviews within 7 days of period end
7. **Discuss Results**: Have 1-on-1 meetings to review scores

### For Team Members:

1. **Check KPIs**: Review your assigned KPIs early
2. **Track Progress**: Monitor your dashboard regularly
3. **Ask Questions**: Clarify unclear metrics with your manager
4. **Stay Focused**: Work towards meeting targets
5. **Review Feedback**: Read finalized reviews carefully

---

## 🆘 **Troubleshooting**

### "I don't see Performance in sidebar"
- **Check**: You must be logged in
- **Check**: You must have an organization
- **Solution**: Redeploy on Render.com if just updated

### "No KPIs assigned"
- **Cause**: Manager hasn't assigned KPIs yet
- **Solution**: Contact your manager

### "Scores are 0 or null"
- **Cause**: No tasks completed in review period
- **Solution**: Complete tasks or wait for manager's manual rating

### "Cannot finalize review"
- **Cause**: Some scores might be missing
- **Solution**: Generate all scores first, then finalize

---

## 📞 **Need Help?**

- **Admin Panel**: `/admin/performance/`
- **Documentation**: See `KPI_PERFORMANCE_DOCUMENTATION.md`
- **Quick Ref**: See `PERFORMANCE_QUICK_REFERENCE.md`
- **Support**: Contact your system administrator

---

**Created**: January 13, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
