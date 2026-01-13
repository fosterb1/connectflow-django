"""
Integration test for the complete KPI & Performance Management workflow.

Run with: python manage.py test apps.performance.test_integration
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date
from decimal import Decimal

from apps.accounts.models import User
from apps.organizations.models import Organization, Department, Team, SharedProject, ProjectTask
from apps.performance.models import (
    KPIMetric, KPIThreshold, KPIAssignment,
    PerformanceReview, PerformanceScore, PerformanceAuditLog
)
from apps.performance.services import PerformanceScoringService
from apps.performance.permissions import PerformancePermissions
from apps.performance.utils import ReviewPeriodHelper


class CompleteWorkflowIntegrationTest(TestCase):
    """
    Test complete end-to-end workflow:
    1. Manager creates KPI metrics
    2. Manager assigns KPIs to team member
    3. Team member completes tasks
    4. Manager creates performance review
    5. System calculates scores
    6. Manager reviews and optionally overrides
    7. Manager finalizes review
    8. System logs all actions
    """
    
    def setUp(self):
        """Set up test organization with users and team structure."""
        # Create organization
        self.org = Organization.objects.create(
            name="TechCorp",
            code="TECHCORP"
        )
        
        # Create users
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@techcorp.com",
            password="admin123",
            first_name="Alice",
            last_name="Admin",
            organization=self.org,
            role=User.Role.ORG_ADMIN
        )
        
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@techcorp.com",
            password="manager123",
            first_name="Bob",
            last_name="Manager",
            organization=self.org,
            role=User.Role.TEAM_MANAGER
        )
        
        self.member = User.objects.create_user(
            username="developer",
            email="dev@techcorp.com",
            password="dev123",
            first_name="Charlie",
            last_name="Developer",
            organization=self.org,
            role=User.Role.TEAM_MEMBER
        )
        
        # Create team structure
        self.dept = Department.objects.create(
            organization=self.org,
            name="Engineering",
            head=self.manager
        )
        
        self.team = Team.objects.create(
            department=self.dept,
            name="Backend Team",
            manager=self.manager
        )
        self.team.members.add(self.member)
        
        # Create a project for tasks
        self.project = SharedProject.objects.create(
            name="Q1 Backend Project",
            host_organization=self.org,
            created_by=self.admin
        )
    
    def test_complete_performance_evaluation_workflow(self):
        """Test the complete workflow from KPI creation to finalized review."""
        
        # ===== STEP 1: Manager creates KPI metrics =====
        self.assertTrue(PerformancePermissions.can_create_kpi_metric(self.manager))
        
        completion_metric = KPIMetric.objects.create(
            organization=self.org,
            name="Task Completion Rate",
            description="Percentage of tasks completed successfully",
            metric_type=KPIMetric.MetricType.PERCENTAGE,
            weight=Decimal('2.00'),
            role=User.Role.TEAM_MEMBER,
            created_by=self.manager
        )
        
        KPIThreshold.objects.create(
            metric=completion_metric,
            min_value=Decimal('70.00'),
            target_value=Decimal('90.00'),
            max_value=Decimal('100.00'),
            pass_fail_enabled=True
        )
        
        quality_metric = KPIMetric.objects.create(
            organization=self.org,
            name="Work Quality",
            description="Quality of work delivered",
            metric_type=KPIMetric.MetricType.RATING,
            weight=Decimal('1.50'),
            role=User.Role.TEAM_MEMBER,
            created_by=self.manager
        )
        
        # Verify metrics created
        self.assertEqual(KPIMetric.objects.filter(organization=self.org).count(), 2)
        
        # ===== STEP 2: Manager assigns KPIs to team member =====
        self.assertTrue(PerformancePermissions.can_assign_kpi(self.manager, self.member))
        
        review_period = '2026-01'
        
        assignment1 = KPIAssignment.objects.create(
            metric=completion_metric,
            user=self.member,
            review_period=review_period,
            assigned_by=self.manager
        )
        
        assignment2 = KPIAssignment.objects.create(
            metric=quality_metric,
            user=self.member,
            review_period=review_period,
            assigned_by=self.manager
        )
        
        # Verify assignments
        self.assertEqual(
            KPIAssignment.objects.filter(user=self.member, review_period=review_period).count(),
            2
        )
        
        # ===== STEP 3: Team member completes tasks =====
        # Create 10 tasks, complete 8 of them
        from django.utils import timezone as tz
        
        period_start = tz.make_aware(timezone.datetime(2026, 1, 1))
        period_end = tz.make_aware(timezone.datetime(2026, 1, 31))
        due_date = tz.make_aware(timezone.datetime(2026, 1, 31, 23, 59, 59))
        
        for i in range(10):
            task = ProjectTask.objects.create(
                project=self.project,
                creator=self.manager,
                assigned_to=self.member,
                title=f"Task {i+1}",
                description=f"Description for task {i+1}",
                status=ProjectTask.TaskStatus.COMPLETED if i < 8 else ProjectTask.TaskStatus.TODO,
                due_date=due_date
            )
            # Set created_at to be in review period
            task.created_at = period_start
            task.save()
        
        # Verify tasks
        total_tasks = ProjectTask.objects.filter(assigned_to=self.member).count()
        completed_tasks = ProjectTask.objects.filter(
            assigned_to=self.member,
            status=ProjectTask.TaskStatus.COMPLETED
        ).count()
        
        self.assertEqual(total_tasks, 10)
        self.assertEqual(completed_tasks, 8)
        
        # ===== STEP 4: Manager creates performance review =====
        self.assertTrue(PerformancePermissions.can_create_review(self.manager, self.member))
        
        review = PerformanceReview.objects.create(
            user=self.member,
            reviewer=self.manager,
            organization=self.org,
            review_period_start=date(2026, 1, 1),
            review_period_end=date(2026, 1, 31)
        )
        
        # Verify review created
        self.assertEqual(review.status, PerformanceReview.ReviewStatus.DRAFT)
        self.assertIsNone(review.final_score)
        
        # ===== STEP 5: System calculates scores =====
        scores = PerformanceScoringService.generate_review_scores(review, self.manager)
        
        # Verify scores generated
        self.assertEqual(len(scores), 2)
        
        # Check completion rate score (should be 80% - 8/10)
        completion_score = PerformanceScore.objects.get(
            review=review,
            metric=completion_metric
        )
        self.assertIsNotNone(completion_score.calculated_score)
        # Score should be around 80%
        self.assertGreaterEqual(float(completion_score.calculated_score), 75.0)
        self.assertLessEqual(float(completion_score.calculated_score), 85.0)
        
        # ===== STEP 6: Manager reviews and optionally overrides =====
        # Manager decides to override quality score based on code review
        quality_score = PerformanceScore.objects.get(
            review=review,
            metric=quality_metric
        )
        
        PerformanceScoringService.override_score(
            score=quality_score,
            new_score=Decimal('95.00'),
            reason="Exceptional code quality observed in Project X deliverables",
            actor=self.manager
        )
        
        # Verify override
        quality_score.refresh_from_db()
        self.assertEqual(quality_score.manual_override_score, Decimal('95.00'))
        self.assertEqual(quality_score.get_effective_score(), Decimal('95.00'))
        self.assertEqual(quality_score.overridden_by, self.manager)
        
        # ===== STEP 7: Manager finalizes review =====
        self.assertTrue(PerformancePermissions.can_finalize_review(self.manager, review))
        
        review.comments = "Good performance overall. Keep up the great work on code quality."
        review.save()
        
        PerformanceScoringService.finalize_review(review, self.manager)
        
        # Verify finalization
        review.refresh_from_db()
        self.assertEqual(review.status, PerformanceReview.ReviewStatus.FINALIZED)
        self.assertIsNotNone(review.final_score)
        self.assertIsNotNone(review.finalized_at)
        
        # Verify final score is calculated correctly
        # (80 * 2.0 + 95 * 1.5) / 3.5 = (160 + 142.5) / 3.5 = 86.43
        expected_score = (80 * 2.0 + 95 * 1.5) / 3.5
        self.assertAlmostEqual(float(review.final_score), expected_score, places=1)
        
        # ===== STEP 8: System logs all actions =====
        # Verify audit logs were created
        logs = PerformanceAuditLog.objects.filter(organization=self.org)
        
        # Verify we have some logs (at least review finalization)
        self.assertGreater(logs.count(), 0)
        
        # Check for review finalization log
        finalization_log = logs.filter(
            action=PerformanceAuditLog.ActionType.REVIEW_FINALIZED
        ).first()
        self.assertIsNotNone(finalization_log)
        
        # ===== STEP 9: Verify member can view their review =====
        self.assertTrue(PerformancePermissions.can_view_review(self.member, review))
        
        # Member cannot edit finalized review
        self.assertFalse(PerformancePermissions.can_edit_review(self.member, review))
        
        # ===== STEP 10: Verify finalized review is locked =====
        # Try to override score on finalized review (should fail)
        with self.assertRaises(ValueError):
            PerformanceScoringService.override_score(
                score=completion_score,
                new_score=Decimal('100.00'),
                reason="Trying to change after finalization",
                actor=self.manager
            )
        
        print("\n✅ Complete workflow test passed successfully!")
        print(f"   - KPIs created: 2")
        print(f"   - Assignments: 2")
        print(f"   - Tasks completed: {completed_tasks}/{total_tasks}")
        print(f"   - Final score: {review.final_score}")
        print(f"   - Audit logs: {logs.count()}")
