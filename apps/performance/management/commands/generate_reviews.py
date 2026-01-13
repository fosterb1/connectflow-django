"""
Management command to generate monthly performance reviews.

Usage:
    python manage.py generate_reviews --period 2026-01 --org <org_id>
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.performance.models import KPIAssignment, PerformanceReview
from apps.performance.services import PerformanceScoringService
from apps.performance.utils import ReviewPeriodHelper
from apps.organizations.models import Organization
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Generate performance reviews for a period'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            help='Review period (e.g., 2026-01, 2026-Q1)',
            required=True
        )
        parser.add_argument(
            '--org',
            type=str,
            help='Organization UUID',
            required=True
        )
        parser.add_argument(
            '--auto-finalize',
            action='store_true',
            help='Automatically finalize reviews after creation'
        )

    def handle(self, *args, **options):
        period = options['period']
        org_id = options['org']
        auto_finalize = options.get('auto_finalize', False)
        
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Organization {org_id} not found'))
            return
        
        # Get period dates
        start_date, end_date = ReviewPeriodHelper.get_period_dates(period)
        
        self.stdout.write(f'Generating reviews for {org.name}')
        self.stdout.write(f'Period: {start_date} to {end_date}')
        
        # Get all users with KPI assignments for this period
        assignments = KPIAssignment.objects.filter(
            metric__organization=org,
            review_period=period
        ).values_list('user_id', flat=True).distinct()
        
        created_count = 0
        skipped_count = 0
        
        for user_id in assignments:
            user = User.objects.get(id=user_id)
            
            # Check if review already exists
            existing = PerformanceReview.objects.filter(
                user=user,
                organization=org,
                review_period_start=start_date,
                review_period_end=end_date
            ).exists()
            
            if existing:
                self.stdout.write(f'  - Skipped {user.get_full_name()} (review exists)')
                skipped_count += 1
                continue
            
            # Find appropriate reviewer
            reviewer = self._find_reviewer(user)
            
            if not reviewer:
                self.stdout.write(
                    self.style.WARNING(f'  - Skipped {user.get_full_name()} (no reviewer found)')
                )
                skipped_count += 1
                continue
            
            # Create review
            review = PerformanceReview.objects.create(
                user=user,
                reviewer=reviewer,
                organization=org,
                review_period_start=start_date,
                review_period_end=end_date
            )
            
            # Generate scores
            PerformanceScoringService.generate_review_scores(review, reviewer)
            
            # Auto-finalize if requested
            if auto_finalize:
                PerformanceScoringService.finalize_review(review, reviewer)
                status = 'created and finalized'
            else:
                status = 'created (draft)'
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ {user.get_full_name()} - {status}')
            )
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCompleted: {created_count} reviews created, {skipped_count} skipped'
        ))
    
    def _find_reviewer(self, user):
        """Find appropriate reviewer for a user."""
        # Check if user is in a team with a manager
        team = user.teams.filter(manager__isnull=False).first()
        if team:
            return team.manager
        
        # Check if user's department has a head
        for team in user.teams.all():
            if team.department.head:
                return team.department.head
        
        # Fallback to org admin
        return User.objects.filter(
            organization=user.organization,
            role=User.Role.ORG_ADMIN
        ).first()
