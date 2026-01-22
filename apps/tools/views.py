from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from apps.tools.forms.models import Form
from apps.tools.documents.models import Document
from apps.tools.announcements.models import Announcement
from apps.tools.bookings.models import Booking
from apps.tools.timeoff.models import LeaveRequest

@login_required
def dashboard(request):
    """Corporate Tools Dashboard with summary metrics."""
    org = request.user.organization
    
    # Summary Counts
    form_count = Form.objects.filter(organization=org, is_active=True).count()
    doc_count = Document.objects.filter(organization=org).count()
    announcement_count = Announcement.objects.filter(organization=org, is_published=True).count()
    pending_leave = LeaveRequest.objects.filter(
        leave_type__organization=org, 
        status=LeaveRequest.Status.PENDING
    ).exclude(user=request.user).count() if (request.user.is_admin or request.user.role == 'TEAM_MANAGER') else 0
    
    # Recent Activity
    recent_announcements = Announcement.objects.filter(
        organization=org, 
        is_published=True
    ).order_by('-created_at')[:3]
    
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status=Booking.Status.CONFIRMED,
        start_time__gte=timezone.now()
    ).select_related('resource').order_by('start_time')[:3]
    
    context = {
        'form_count': form_count,
        'doc_count': doc_count,
        'announcement_count': announcement_count,
        'pending_leave_requests': pending_leave,
        'recent_announcements': recent_announcements,
        'upcoming_bookings': upcoming_bookings,
    }
    return render(request, 'tools/dashboard.html', context)
