"""
Utility functions for performance management.

Common helpers for period handling and data aggregation.
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ReviewPeriodHelper:
    """Helper for handling review periods."""
    
    @staticmethod
    def get_current_period(period_type='monthly'):
        """
        Get current period identifier.
        
        Args:
            period_type: 'monthly', 'quarterly', 'weekly'
        
        Returns:
            str: Period identifier (e.g., '2026-01', '2026-Q1', '2026-W01')
        """
        now = datetime.now()
        
        if period_type == 'monthly':
            return now.strftime('%Y-%m')
        elif period_type == 'quarterly':
            quarter = (now.month - 1) // 3 + 1
            return f"{now.year}-Q{quarter}"
        elif period_type == 'weekly':
            week = now.isocalendar()[1]
            return f"{now.year}-W{week:02d}"
        
        return now.strftime('%Y-%m')
    
    @staticmethod
    def get_period_dates(period_identifier):
        """
        Convert period identifier to start/end dates.
        
        Args:
            period_identifier: '2026-01', '2026-Q1', or '2026-W01'
        
        Returns:
            tuple: (start_date, end_date)
        """
        if '-Q' in period_identifier:
            # Quarterly
            year, quarter = period_identifier.split('-Q')
            year = int(year)
            quarter = int(quarter)
            
            start_month = (quarter - 1) * 3 + 1
            start_date = datetime(year, start_month, 1).date()
            
            end_month = start_month + 2
            end_date = (datetime(year, end_month, 1) + relativedelta(months=1, days=-1)).date()
            
            return start_date, end_date
        
        elif '-W' in period_identifier:
            # Weekly
            year, week = period_identifier.split('-W')
            year = int(year)
            week = int(week)
            
            # Get first day of week
            jan_1 = datetime(year, 1, 1)
            start_date = jan_1 + timedelta(weeks=week - 1)
            start_date = start_date - timedelta(days=start_date.weekday())
            
            end_date = start_date + timedelta(days=6)
            
            return start_date.date(), end_date.date()
        
        else:
            # Monthly (YYYY-MM)
            year, month = period_identifier.split('-')
            year = int(year)
            month = int(month)
            
            start_date = datetime(year, month, 1).date()
            end_date = (datetime(year, month, 1) + relativedelta(months=1, days=-1)).date()
            
            return start_date, end_date
    
    @staticmethod
    def get_previous_period(period_identifier):
        """
        Get the previous period identifier.
        
        Args:
            period_identifier: Current period
        
        Returns:
            str: Previous period identifier
        """
        if '-Q' in period_identifier:
            year, quarter = period_identifier.split('-Q')
            year = int(year)
            quarter = int(quarter)
            
            if quarter == 1:
                return f"{year - 1}-Q4"
            else:
                return f"{year}-Q{quarter - 1}"
        
        elif '-W' in period_identifier:
            year, week = period_identifier.split('-W')
            year = int(year)
            week = int(week)
            
            if week == 1:
                return f"{year - 1}-W52"
            else:
                return f"{year}-W{week - 1:02d}"
        
        else:
            year, month = period_identifier.split('-')
            year = int(year)
            month = int(month)
            
            if month == 1:
                return f"{year - 1}-12"
            else:
                return f"{year}-{month - 1:02d}"
    
    @staticmethod
    def get_next_period(period_identifier):
        """
        Get the next period identifier.
        
        Args:
            period_identifier: Current period
        
        Returns:
            str: Next period identifier
        """
        if '-Q' in period_identifier:
            year, quarter = period_identifier.split('-Q')
            year = int(year)
            quarter = int(quarter)
            
            if quarter == 4:
                return f"{year + 1}-Q1"
            else:
                return f"{year}-Q{quarter + 1}"
        
        elif '-W' in period_identifier:
            year, week = period_identifier.split('-W')
            year = int(year)
            week = int(week)
            
            if week >= 52:
                return f"{year + 1}-W01"
            else:
                return f"{year}-W{week + 1:02d}"
        
        else:
            year, month = period_identifier.split('-')
            year = int(year)
            month = int(month)
            
            if month == 12:
                return f"{year + 1}-01"
            else:
                return f"{year}-{month + 1:02d}"


class PerformanceMetrics:
    """Helper for performance metric calculations."""
    
    @staticmethod
    def calculate_trend(scores):
        """
        Calculate performance trend from list of scores.
        
        Args:
            scores: List of numerical scores
        
        Returns:
            str: 'improving', 'declining', or 'stable'
        """
        if len(scores) < 2:
            return 'stable'
        
        # Simple linear trend
        recent = scores[-3:] if len(scores) >= 3 else scores
        
        if len(recent) < 2:
            return 'stable'
        
        avg_early = sum(recent[:len(recent)//2]) / (len(recent)//2)
        avg_late = sum(recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
        
        diff = avg_late - avg_early
        
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        else:
            return 'stable'
    
    @staticmethod
    def get_performance_band(score):
        """
        Get performance band for a score.
        
        Args:
            score: Numerical score (0-100)
        
        Returns:
            str: 'excellent', 'good', 'satisfactory', 'needs_improvement', 'poor'
        """
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'satisfactory'
        elif score >= 40:
            return 'needs_improvement'
        else:
            return 'poor'
    
    @staticmethod
    def calculate_percentile(score, all_scores):
        """
        Calculate percentile rank for a score.
        
        Args:
            score: Individual score
            all_scores: List of all scores for comparison
        
        Returns:
            int: Percentile rank (0-100)
        """
        if not all_scores:
            return 50
        
        below = sum(1 for s in all_scores if s < score)
        equal = sum(1 for s in all_scores if s == score)
        
        percentile = ((below + 0.5 * equal) / len(all_scores)) * 100
        return int(percentile)
