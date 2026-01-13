"""
Tests for Performance Management System.

Run with: python manage.py test apps.performance
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.models import User
from apps.organizations.models import Organization, Department, Team, ProjectTask
from apps.performance.models import (
    KPIMetric, KPIThreshold, KPIAssignment,
    PerformanceReview, PerformanceScore, PerformanceAuditLog
)
from apps.performance.services import PerformanceScoringService
from apps.performance.permissions import PerformancePermissions


class KPIMetricTestCase(TestCase):
    """Test KPI Metric creation and management."""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Corp",
            code="TESTCORP"
        )
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.ORG_ADMIN
        )
    
    def test_create_kpi_metric(self):
        """Test creating a KPI metric."""
        metric = KPIMetric.objects.create(
            organization=self.org,
            name="Task Completion Rate",
            metric_type=KPIMetric.MetricType.PERCENTAGE,
            weight=Decimal('2.00'),
            created_by=self.admin
        )
        
        self.assertEqual(metric.name, "Task Completion Rate")
        self.assertTrue(metric.is_active)
        self.assertEqual(metric.version, 1)
    
    def test_create_threshold(self):
        """Test creating a KPI threshold."""
        metric = KPIMetric.objects.create(
            organization=self.org,
            name="Deadline Adherence",
            metric_type=KPIMetric.MetricType.PERCENTAGE,
            weight=Decimal('1.50'),
            created_by=self.admin
        )
        
        threshold = KPIThreshold.objects.create(
            metric=metric,
            min_value=Decimal('70.00'),
            target_value=Decimal('90.00'),
            max_value=Decimal('100.00'),
            pass_fail_enabled=True
        )
        
        self.assertEqual(threshold.target_value, Decimal('90.00'))
        self.assertTrue(threshold.pass_fail_enabled)


class PerformanceReviewTestCase(TestCase):
    """Test performance review creation and scoring."""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Corp",
            code="TESTCORP"
        )
        
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.TEAM_MANAGER
        )
        
        self.member = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.TEAM_MEMBER
        )
        
        self.metric = KPIMetric.objects.create(
            organization=self.org,
            name="Task Completion",
            metric_type=KPIMetric.MetricType.PERCENTAGE,
            weight=Decimal('1.00'),
            created_by=self.manager
        )
    
    def test_create_review(self):
        """Test creating a performance review."""
        review = PerformanceReview.objects.create(
            user=self.member,
            reviewer=self.manager,
            organization=self.org,
            review_period_start=date(2026, 1, 1),
            review_period_end=date(2026, 1, 31)
        )
        
        self.assertEqual(review.status, PerformanceReview.ReviewStatus.DRAFT)
        self.assertIsNone(review.final_score)
        self.assertIsNone(review.finalized_at)
    
    def test_calculate_final_score(self):
        """Test weighted final score calculation."""
        review = PerformanceReview.objects.create(
            user=self.member,
            reviewer=self.manager,
            organization=self.org,
            review_period_start=date(2026, 1, 1),
            review_period_end=date(2026, 1, 31)
        )
        
        # Create scores
        PerformanceScore.objects.create(
            review=review,
            metric=self.metric,
            calculated_score=Decimal('85.00')
        )
        
        metric2 = KPIMetric.objects.create(
            organization=self.org,
            name="Quality",
            metric_type=KPIMetric.MetricType.PERCENTAGE,
            weight=Decimal('2.00'),
            created_by=self.manager
        )
        
        PerformanceScore.objects.create(
            review=review,
            metric=metric2,
            calculated_score=Decimal('90.00')
        )
        
        # Calculate final score: (85*1 + 90*2) / 3 = 88.33
        final_score = PerformanceScoringService.calculate_final_score(review)
        
        self.assertAlmostEqual(float(final_score), 88.33, places=2)
    
    def test_override_score(self):
        """Test manual score override."""
        review = PerformanceReview.objects.create(
            user=self.member,
            reviewer=self.manager,
            organization=self.org,
            review_period_start=date(2026, 1, 1),
            review_period_end=date(2026, 1, 31)
        )
        
        score = PerformanceScore.objects.create(
            review=review,
            metric=self.metric,
            calculated_score=Decimal('75.00')
        )
        
        PerformanceScoringService.override_score(
            score=score,
            new_score=Decimal('90.00'),
            reason="Exceptional circumstances",
            actor=self.manager
        )
        
        score.refresh_from_db()
        self.assertEqual(score.manual_override_score, Decimal('90.00'))
        self.assertEqual(score.get_effective_score(), Decimal('90.00'))
        self.assertEqual(score.overridden_by, self.manager)
    
    def test_finalize_review(self):
        """Test review finalization."""
        review = PerformanceReview.objects.create(
            user=self.member,
            reviewer=self.manager,
            organization=self.org,
            review_period_start=date(2026, 1, 1),
            review_period_end=date(2026, 1, 31)
        )
        
        PerformanceScore.objects.create(
            review=review,
            metric=self.metric,
            calculated_score=Decimal('85.00')
        )
        
        PerformanceScoringService.finalize_review(review, self.manager)
        
        review.refresh_from_db()
        self.assertEqual(review.status, PerformanceReview.ReviewStatus.FINALIZED)
        self.assertIsNotNone(review.finalized_at)
        self.assertIsNotNone(review.final_score)


class PermissionsTestCase(TestCase):
    """Test permission checks."""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Corp",
            code="TESTCORP"
        )
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.ORG_ADMIN
        )
        
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.TEAM_MANAGER
        )
        
        self.member = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.TEAM_MEMBER
        )
    
    def test_admin_can_create_kpi(self):
        """Test admin can create KPI metrics."""
        self.assertTrue(PerformancePermissions.can_create_kpi_metric(self.admin))
    
    def test_manager_can_create_kpi(self):
        """Test manager can create KPI metrics."""
        self.assertTrue(PerformancePermissions.can_create_kpi_metric(self.manager))
    
    def test_member_cannot_create_kpi(self):
        """Test member cannot create KPI metrics."""
        self.assertFalse(PerformancePermissions.can_create_kpi_metric(self.member))
    
    def test_member_cannot_view_team_performance(self):
        """Test member cannot view team performance."""
        self.assertFalse(PerformancePermissions.can_view_team_performance(self.member))


class AuditLogTestCase(TestCase):
    """Test audit logging."""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Corp",
            code="TESTCORP"
        )
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="test123",
            organization=self.org,
            role=User.Role.ORG_ADMIN
        )
    
    def test_log_action(self):
        """Test audit log creation."""
        log = PerformanceAuditLog.log_action(
            organization=self.org,
            actor=self.admin,
            action=PerformanceAuditLog.ActionType.METRIC_CREATED,
            reason="Creating new metric"
        )
        
        self.assertEqual(log.organization, self.org)
        self.assertEqual(log.actor, self.admin)
        self.assertEqual(log.action, PerformanceAuditLog.ActionType.METRIC_CREATED)
        self.assertIsNotNone(log.timestamp)

