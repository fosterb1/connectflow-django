# 🎯 KPI System - Visual Quick Start

## 📊 The Complete Flow in 3 Minutes

```
┌─────────────────────────────────────────────────────────────────┐
│                     KPI PERFORMANCE SYSTEM                       │
│                    Complete Monthly Cycle                        │
└─────────────────────────────────────────────────────────────────┘

STEP 1: MANAGER CREATES KPI METRICS
════════════════════════════════════════════════════════════════════
┌────────────────┐
│ Manager Login  │
└───────┬────────┘
        │
        ├──> Click "Performance" in sidebar
        │
        ├──> Click "Manage KPIs"
        │
        ├──> Click "Create KPI"
        │
        └──> Fill form:
             ┌─────────────────────────────────────────┐
             │ Name: Task Completion Rate             │
             │ Type: Percentage                       │
             │ Target: 90%                            │
             │ Weight: 2.0                            │
             │ Role: Team Member                      │
             └─────────────────────────────────────────┘
             ✅ CREATED


STEP 2: MANAGER ASSIGNS KPIs TO TEAM MEMBERS
════════════════════════════════════════════════════════════════════
        │
        ├──> Click "Assign KPIs"
        │
        └──> Fill form:
             ┌─────────────────────────────────────────┐
             │ KPI: Task Completion Rate              │
             │ Team Member: John Doe                  │
             │ Period: 2026-01 (January)              │
             └─────────────────────────────────────────┘
             ✅ ASSIGNED

             John can now see this in his dashboard!


STEP 3: TEAM MEMBER SEES THEIR KPIS
════════════════════════════════════════════════════════════════════
┌────────────────┐
│ Member Login   │ (John Doe)
└───────┬────────┘
        │
        ├──> Click "My Performance"
        │
        └──> Dashboard shows:
             ┌─────────────────────────────────────────┐
             │ CURRENT KPIS (2026-01)                 │
             │                                        │
             │ ┌─────────────────────────────────┐   │
             │ │ Task Completion Rate            │   │
             │ │ Target: 90%                     │   │
             │ │ Assigned by: Manager Smith      │   │
             │ └─────────────────────────────────┘   │
             │                                        │
             │ ┌─────────────────────────────────┐   │
             │ │ Deadline Adherence              │   │
             │ │ Target: 85%                     │   │
             │ │ Assigned by: Manager Smith      │   │
             │ └─────────────────────────────────┘   │
             └─────────────────────────────────────────┘


STEP 4: DURING THE MONTH - SYSTEM AUTO-TRACKS
════════════════════════════════════════════════════════════════════

John works on tasks...
├──> Task 1: ✅ Completed on time
├──> Task 2: ✅ Completed on time  
├──> Task 3: ✅ Completed on time
├──> Task 4: ⏰ Completed late
└──> Task 5: ✅ Completed on time

System automatically calculates:
┌─────────────────────────────────────────┐
│ Task Completion: 5/5 = 100%    ✓      │
│ Deadline Adherence: 4/5 = 80%  ⚠️      │
│ Quality: 0 reopened = 100%     ✓      │
└─────────────────────────────────────────┘


STEP 5: END OF MONTH - MANAGER CREATES REVIEW
════════════════════════════════════════════════════════════════════
┌────────────────┐
│ Manager Login  │
└───────┬────────┘
        │
        ├──> Go to Admin Panel
        │
        ├──> Performance → Performance Reviews
        │
        ├──> Add Performance Review
        │
        └──> Fill:
             ┌─────────────────────────────────────────┐
             │ User: John Doe                         │
             │ Period Start: 2026-01-01               │
             │ Period End: 2026-01-31                 │
             │ Status: Draft                          │
             └─────────────────────────────────────────┘
             ✅ REVIEW CREATED (empty, no scores yet)


STEP 6: MANAGER GENERATES AUTO-SCORES
════════════════════════════════════════════════════════════════════

Option A: Via Django Shell
───────────────────────────
python manage.py shell

>>> from apps.performance.models import PerformanceReview
>>> from apps.performance.services import PerformanceScoringService
>>> from apps.accounts.models import User
>>> 
>>> review = PerformanceReview.objects.get(id='xxx')
>>> manager = User.objects.get(email='manager@example.com')
>>> 
>>> # Generate scores
>>> PerformanceScoringService.generate_review_scores(review, manager)

Output:
┌─────────────────────────────────────────┐
│ ✅ Task Completion Rate: 100.0         │
│ ✅ Deadline Adherence: 80.0            │
│ ✅ Quality of Work: 100.0              │
│ ⏸️  Team Collaboration: null           │
│    (needs manual rating)               │
└─────────────────────────────────────────┘


STEP 7: MANAGER ADDS MANUAL RATINGS
════════════════════════════════════════════════════════════════════
        │
        ├──> Admin Panel → Performance Scores
        │
        ├──> Find "Team Collaboration" score
        │
        ├──> Edit:
        │    ┌─────────────────────────────────────────┐
        │    │ Manual Override Score: 90              │
        │    │ Override Reason: "Excellent team       │
        │    │ player, mentored 2 junior members"     │
        │    └─────────────────────────────────────────┘
        │
        └──> Save ✅


STEP 8: MANAGER FINALIZES REVIEW
════════════════════════════════════════════════════════════════════
        │
        ├──> Open the Performance Review
        │
        ├──> Add overall comments:
        │    "Great performance this month!"
        │
        ├──> Change Status: Draft → Finalized
        │
        └──> Save ✅

System calculates final score:
┌─────────────────────────────────────────┐
│ FINAL SCORE CALCULATION                │
│                                        │
│ Task Completion:  100 × 2.0 = 200     │
│ Deadline:          80 × 1.5 = 120     │
│ Quality:          100 × 1.0 = 100     │
│ Collaboration:     90 × 1.0 =  90     │
│                         ─────────      │
│ Total:                        510     │
│ Total Weight:                 5.5     │
│                                        │
│ FINAL SCORE: 510 ÷ 5.5 = 92.73/100   │
│ GRADE: EXCELLENT ⭐⭐⭐⭐⭐                │
└─────────────────────────────────────────┘

Review is now LOCKED (no more edits allowed)


STEP 9: TEAM MEMBER VIEWS FINALIZED REVIEW
════════════════════════════════════════════════════════════════════
┌────────────────┐
│ Member Login   │ (John Doe)
└───────┬────────┘
        │
        ├──> Click "My Performance"
        │
        ├──> See "Recent Performance Reviews"
        │
        ├──> Click on review
        │
        └──> View detailed scores:
             ┌─────────────────────────────────────────┐
             │ PERFORMANCE REVIEW                     │
             │ Jan 1 - Jan 31, 2026                   │
             │ Reviewer: Manager Smith                │
             │                                        │
             │ FINAL SCORE: 92.73/100                 │
             │ GRADE: EXCELLENT ⭐⭐⭐⭐⭐                 │
             │                                        │
             │ ──────────────────────────────────────│
             │ Individual Scores:                     │
             │                                        │
             │ Task Completion Rate                   │
             │ Score: 100/100 (Weight: 2.0)          │
             │                                        │
             │ Deadline Adherence                     │
             │ Score: 80/100 (Weight: 1.5)           │
             │                                        │
             │ Quality of Work                        │
             │ Score: 100/100 (Weight: 1.0)          │
             │                                        │
             │ Team Collaboration                     │
             │ Score: 90/100 (Weight: 1.0)           │
             │ Note: Excellent team player,           │
             │ mentored 2 junior members              │
             │ ──────────────────────────────────────│
             │                                        │
             │ Manager Comments:                      │
             │ "Great performance this month!"        │
             └─────────────────────────────────────────┘
```

---

## 🔄 Monthly Cycle Timeline

```
JANUARY 2026
════════════════════════════════════════════════════════════════════

Week 1 (Jan 1-7)
┌────────────────────────────────────────────────────────────────┐
│ ✅ Manager assigns KPIs to all team members                    │
│ ✅ Members see KPIs in their dashboards                        │
│ ✅ Everyone starts working                                     │
└────────────────────────────────────────────────────────────────┘

Weeks 2-4 (Jan 8-31)
┌────────────────────────────────────────────────────────────────┐
│ 🔄 Members work on tasks                                       │
│ 🔄 System auto-tracks performance                              │
│ 📊 Manager can monitor progress in Team Overview               │
└────────────────────────────────────────────────────────────────┘

End of Month (Jan 31 - Feb 5)
┌────────────────────────────────────────────────────────────────┐
│ ✅ Manager creates reviews                                     │
│ ✅ Manager generates auto-scores                               │
│ ✅ Manager adds manual ratings                                 │
│ ✅ Manager finalizes reviews                                   │
│ ✅ Members view their reviews                                  │
│ 💬 1-on-1 meetings to discuss results                          │
└────────────────────────────────────────────────────────────────┘

FEBRUARY 2026
┌────────────────────────────────────────────────────────────────┐
│ 🔄 Repeat cycle for February                                   │
│ 📈 Track trends over time                                      │
│ 🔧 Adjust KPIs as needed                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Access URLs

### For Managers:
```
📋 KPI Metrics List:     /performance/kpi/metrics/
➕ Create KPI:           /performance/kpi/metrics/create/
👥 Assign KPIs:          /performance/kpi/assign/
📊 Team Overview:        /performance/team/overview/
⚙️  Admin Panel:          /admin/performance/
```

### For Members:
```
📊 My Dashboard:         /performance/my/dashboard/
📜 Performance History:  /performance/my/history/
🔍 Review Detail:        /performance/my/review/<id>/
```

---

## 📊 Example Real-World Scenario

### Scenario: Sales Team Performance

**KPIs Created by Manager:**
1. Sales Target Achievement (Percentage, Weight: 3.0)
2. Customer Satisfaction (Rating, Weight: 2.0)
3. Response Time (Numeric, Weight: 1.5)
4. Team Collaboration (Rating, Weight: 1.0)

**Assigned to:** Sarah Johnson (Sales Rep)  
**Period:** January 2026

**During January:**
- Sarah closes 25 deals (target: 20) = 125% ✓
- Customer ratings average 4.8/5.0 = 96% ✓
- Average response time: 2 hours (target: 3) = Better than target ✓
- Manager rates collaboration: 4.5/5.0 = 90% ✓

**Final Review:**
```
Sales Target:      125 × 3.0 = 375
Satisfaction:       96 × 2.0 = 192
Response Time:     100 × 1.5 = 150
Collaboration:      90 × 1.0 =  90
                          ─────
Total:                        807
Total Weight:                 7.5

Final Score: 807 ÷ 7.5 = 107.6/100 (capped at 100)

RESULT: EXCEPTIONAL PERFORMANCE ⭐⭐⭐⭐⭐
BONUS: Recommended for bonus/promotion
```

---

## 🎓 Training Resources

- **Full Documentation**: `KPI_PERFORMANCE_DOCUMENTATION.md`
- **Quick Reference**: `PERFORMANCE_QUICK_REFERENCE.md`
- **Implementation Details**: `PERFORMANCE_IMPLEMENTATION_SUMMARY.md`
- **This Guide**: `HOW_KPI_WORKS.md`

---

**Need Help?** Contact your system administrator or check the admin panel at `/admin/performance/`
