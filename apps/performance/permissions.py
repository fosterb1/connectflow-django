"""
Permission checks for performance management system.

Enforces role-based access control for KPI metrics and reviews.
"""

from apps.accounts.models import User


class PerformancePermissions:
    """Centralized permission logic for performance features."""
    
    @staticmethod
    def can_create_kpi_metric(user):
        """
        Check if user can create KPI metrics.
        
        Only Admins and Managers can create KPIs.
        """
        return user.is_admin or user.is_manager
    
    @staticmethod
    def can_edit_kpi_metric(user, metric):
        """
        Check if user can edit a KPI metric.
        
        - Must be Admin or Manager
        - Must be in same organization
        """
        if not (user.is_admin or user.is_manager):
            return False
        
        return user.organization_id == metric.organization_id
    
    @staticmethod
    def can_deactivate_kpi_metric(user, metric):
        """
        Check if user can deactivate a KPI metric.
        
        Same rules as editing.
        """
        return PerformancePermissions.can_edit_kpi_metric(user, metric)
    
    @staticmethod
    def can_assign_kpi(user, target_user):
        """
        Check if user can assign KPIs to target_user.
        
        - Must be Admin or Manager
        - Must be in same organization
        - Managers can only assign to their team members
        """
        if not (user.is_admin or user.is_manager):
            return False
        
        if user.organization_id != target_user.organization_id:
            return False
        
        # Admins can assign to anyone in org
        if user.is_admin:
            return True
        
        # Managers can assign to their team members
        if user.role == User.Role.TEAM_MANAGER:
            return user.managed_teams.filter(members=target_user).exists()
        
        if user.role == User.Role.DEPT_HEAD:
            # Department heads can assign to anyone in their departments
            return user.headed_departments.filter(
                teams__members=target_user
            ).exists()
        
        return False
    
    @staticmethod
    def can_create_review(user, target_user):
        """
        Check if user can create a performance review for target_user.
        
        Same rules as KPI assignment.
        """
        return PerformancePermissions.can_assign_kpi(user, target_user)
    
    @staticmethod
    def can_edit_review(user, review):
        """
        Check if user can edit a performance review.
        
        - Review must not be finalized
        - User must be the reviewer or an admin
        - Must be in same organization
        """
        if review.status == review.ReviewStatus.FINALIZED:
            return False
        
        if user.organization_id != review.organization_id:
            return False
        
        # Admin can edit any review in their org
        if user.is_admin:
            return True
        
        # Reviewer can edit their own reviews
        return review.reviewer_id == user.id
    
    @staticmethod
    def can_override_score(user, score):
        """
        Check if user can manually override a score.
        
        - Must be reviewer or admin
        - Review must not be finalized
        """
        return PerformancePermissions.can_edit_review(user, score.review)
    
    @staticmethod
    def can_finalize_review(user, review):
        """
        Check if user can finalize a review.
        
        - Must be Admin or the reviewer
        - Review must be in draft status
        """
        if review.status != review.ReviewStatus.DRAFT:
            return False
        
        if user.organization_id != review.organization_id:
            return False
        
        return user.is_admin or review.reviewer_id == user.id
    
    @staticmethod
    def can_view_review(user, review):
        """
        Check if user can view a performance review.
        
        - Admins can view all reviews in their org
        - Managers can view reviews they conducted
        - Users can view their own reviews
        """
        if user.organization_id != review.organization_id:
            return False
        
        # Admins can view all
        if user.is_admin:
            return True
        
        # Reviewer can view
        if review.reviewer_id == user.id:
            return True
        
        # User can view their own reviews
        if review.user_id == user.id:
            return True
        
        return False
    
    @staticmethod
    def can_view_team_performance(user):
        """
        Check if user can view team-level performance data.
        
        Admins and Managers only.
        """
        return user.is_admin or user.is_manager
    
    @staticmethod
    def can_view_audit_logs(user):
        """
        Check if user can view performance audit logs.
        
        Admins only.
        """
        return user.is_admin
