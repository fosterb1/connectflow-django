from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class KPIMetric(models.Model):
    """
    Defines Key Performance Indicators for performance evaluation.
    Metrics can be assigned to roles, teams, or specific users.
    """
    
    class MetricType(models.TextChoices):
        NUMERIC = 'NUMERIC', _('Numeric Value')
        PERCENTAGE = 'PERCENTAGE', _('Percentage')
        RATING = 'RATING', _('Rating (1-5)')
        BOOLEAN = 'BOOLEAN', _('Yes/No')
        THRESHOLD = 'THRESHOLD', _('Threshold-based')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='kpi_metrics',
        db_index=True,
        help_text=_("Organization this metric belongs to")
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Metric name (e.g., Task Completion Rate)")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of this metric")
    )
    
    metric_type = models.CharField(
        max_length=20,
        choices=MetricType.choices,
        default=MetricType.NUMERIC,
        help_text=_("Type of metric")
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.01), MaxValueValidator(10.00)],
        help_text=_("Weight/importance of this metric in final score (0.01-10.00)")
    )
    
    role = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("Target role for this metric (from User.Role choices)")
    )
    
    team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpi_metrics',
        help_text=_("Specific team this metric applies to (optional)")
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Is this metric currently active?")
    )
    
    version = models.IntegerField(
        default=1,
        help_text=_("Metric version for change tracking")
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_metrics',
        help_text=_("User who created this metric")
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kpi_metrics'
        verbose_name = _('KPI Metric')
        verbose_name_plural = _('KPI Metrics')
        ordering = ['organization', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class KPIThreshold(models.Model):
    """
    Defines performance thresholds for a KPI metric.
    Used to determine pass/fail and performance bands.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    metric = models.OneToOneField(
        KPIMetric,
        on_delete=models.CASCADE,
        related_name='threshold',
        help_text=_("KPI metric this threshold applies to")
    )
    
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Minimum acceptable value")
    )
    
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Target/expected value")
    )
    
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Maximum possible/optimal value")
    )
    
    pass_fail_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable pass/fail evaluation based on min_value")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kpi_thresholds'
        verbose_name = _('KPI Threshold')
        verbose_name_plural = _('KPI Thresholds')
    
    def __str__(self):
        return f"Threshold for {self.metric.name}"


class KPIAssignment(models.Model):
    """
    Assigns KPI metrics to specific users for a review period.
    Allows tracking who is evaluated on which metrics.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text=_("KPI metric being assigned")
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='kpi_assignments',
        db_index=True,
        help_text=_("User this metric is assigned to")
    )
    
    review_period = models.CharField(
        max_length=50,
        help_text=_("Review period identifier (e.g., '2026-Q1', '2026-01')")
    )
    
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_kpis',
        help_text=_("Manager who assigned this metric")
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kpi_assignments'
        verbose_name = _('KPI Assignment')
        verbose_name_plural = _('KPI Assignments')
        ordering = ['-assigned_at']
        unique_together = [['metric', 'user', 'review_period']]
        indexes = [
            models.Index(fields=['user', 'review_period']),
        ]
    
    def __str__(self):
        return f"{self.metric.name} → {self.user.get_full_name()} ({self.review_period})"


class PerformanceReview(models.Model):
    """
    Represents a performance review for a user during a specific period.
    Contains aggregated scores and overall evaluation.
    """
    
    class ReviewStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        FINALIZED = 'FINALIZED', _('Finalized')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        db_index=True,
        help_text=_("User being reviewed")
    )
    
    reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_reviews',
        help_text=_("Manager conducting the review")
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        db_index=True,
        help_text=_("Organization context")
    )
    
    review_period_start = models.DateField(
        db_index=True,
        help_text=_("Start date of review period")
    )
    
    review_period_end = models.DateField(
        db_index=True,
        help_text=_("End date of review period")
    )
    
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Aggregated weighted score (0-100)")
    )
    
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
        db_index=True,
        help_text=_("Review status")
    )
    
    comments = models.TextField(
        blank=True,
        help_text=_("Reviewer's overall comments and feedback")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this review was finalized")
    )
    
    class Meta:
        db_table = 'performance_reviews'
        verbose_name = _('Performance Review')
        verbose_name_plural = _('Performance Reviews')
        ordering = ['-review_period_end', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['organization', 'review_period_end']),
        ]
    
    def __str__(self):
        return f"Review: {self.user.get_full_name()} ({self.review_period_start} to {self.review_period_end})"


class PerformanceScore(models.Model):
    """
    Individual metric scores within a performance review.
    Supports both calculated and manually overridden scores.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name='scores',
        help_text=_("Parent performance review")
    )
    
    metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.CASCADE,
        related_name='performance_scores',
        help_text=_("KPI metric being scored")
    )
    
    calculated_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Auto-calculated score (0-100)")
    )
    
    manual_override_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Manually overridden score (0-100)")
    )
    
    override_reason = models.TextField(
        blank=True,
        help_text=_("Required justification if score is manually overridden")
    )
    
    overridden_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='score_overrides',
        help_text=_("User who overrode the score")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'performance_scores'
        verbose_name = _('Performance Score')
        verbose_name_plural = _('Performance Scores')
        ordering = ['review', 'metric']
        unique_together = [['review', 'metric']]
    
    def __str__(self):
        return f"{self.metric.name}: {self.get_effective_score()}"
    
    def get_effective_score(self):
        """Returns the score that should be used (override takes precedence)."""
        if self.manual_override_score is not None:
            return self.manual_override_score
        return self.calculated_score or 0


class PerformanceAuditLog(models.Model):
    """
    Audit trail for all performance-related actions.
    Tracks changes, overrides, and review finalization.
    """
    
    class ActionType(models.TextChoices):
        METRIC_CREATED = 'METRIC_CREATED', _('Metric Created')
        METRIC_UPDATED = 'METRIC_UPDATED', _('Metric Updated')
        METRIC_DEACTIVATED = 'METRIC_DEACTIVATED', _('Metric Deactivated')
        ASSIGNMENT_CREATED = 'ASSIGNMENT_CREATED', _('KPI Assigned')
        REVIEW_CREATED = 'REVIEW_CREATED', _('Review Created')
        SCORE_CALCULATED = 'SCORE_CALCULATED', _('Score Calculated')
        SCORE_OVERRIDDEN = 'SCORE_OVERRIDDEN', _('Score Overridden')
        REVIEW_FINALIZED = 'REVIEW_FINALIZED', _('Review Finalized')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='performance_audit_logs',
        db_index=True,
        help_text=_("Organization context")
    )
    
    actor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='performance_actions',
        help_text=_("User who performed the action")
    )
    
    action = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        db_index=True,
        help_text=_("Type of action performed")
    )
    
    target_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_audit_targets',
        help_text=_("User affected by this action (if applicable)")
    )
    
    metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Related metric (if applicable)")
    )
    
    review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Related review (if applicable)")
    )
    
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional details about the action")
    )
    
    reason = models.TextField(
        blank=True,
        help_text=_("Reason or justification for the action")
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'performance_audit_logs'
        verbose_name = _('Performance Audit Log')
        verbose_name_plural = _('Performance Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, organization, actor, action, **kwargs):
        """
        Convenience method to create audit log entries.
        
        Usage:
            PerformanceAuditLog.log_action(
                organization=org,
                actor=user,
                action=PerformanceAuditLog.ActionType.SCORE_OVERRIDDEN,
                target_user=reviewed_user,
                metric=kpi_metric,
                reason="Exceptional circumstances"
            )
        """
        return cls.objects.create(
            organization=organization,
            actor=actor,
            action=action,
            **kwargs
        )


class Responsibility(models.Model):
    """
    Specific duties or role-based tasks assigned to a member.
    Members or managers can check these off as they are performed.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        OVERDUE = 'OVERDUE', _('Overdue')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='responsibilities'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='responsibilities',
        db_index=True
    )
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_responsibilities'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(db_index=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_responsibilities'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'responsibilities'
        verbose_name = _('Responsibility')
        verbose_name_plural = _('Responsibilities')
        ordering = ['deadline', 'status']

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        # Auto-update status to overdue if deadline passed and still pending
        if self.status == self.Status.PENDING and self.deadline < timezone.now():
            self.status = self.Status.OVERDUE
        super().save(*args, **kwargs)
