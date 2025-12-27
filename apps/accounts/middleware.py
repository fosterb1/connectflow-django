from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class EmailVerificationMiddleware:
    """
    Middleware to ensure users have verified their email addresses.
    Redirects unverified users to the verification page.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require verification
        self.exempt_urls = [
            reverse('accounts:login'),
            reverse('accounts:register'),
            reverse('accounts:logout'),
            reverse('accounts:verify_email'),
            reverse('accounts:sync_email_verification'),
            reverse('accounts:register_api'),
            reverse('accounts:create_organization_api'),
            reverse('accounts:organization_signup'),
            '/admin/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Check if user is verified
        if not getattr(request.user, 'email_verified', False):
            # Allow access if the path is in the exempt list
            path = request.path_info
            if not any(path.startswith(url) for url in self.exempt_urls):
                return redirect('accounts:verify_email')

        return self.get_response(request)
