from apps.support.models import Ticket
from apps.organizations.models import SharedProject

def get_my_tickets(user_id):
    """
    Retrieves the 5 most recent support tickets for the user.
    Returns their ID, Subject, Status, and Priority.
    """
    # Note: We pass user_id (int/str) or user object? 
    # To be safe for Gemini, we'll rely on the consumer to bind the user.
    # This function expects the actual User object to be bound via partial later, 
    # or we can assume the user is passed if we handle it manually.
    # But for "Automatic Function Calling", the AI provides the arguments.
    # The AI doesn't know the 'user' object. 
    # TRICK: We will define the actual callable in the consumer to close over 'self.user'.
    pass

# We will implement the logic as standalone functions that take a 'user' object,
# and then in the Consumer, we will wrap them so the AI doesn't need to provide the user.

def _db_get_tickets(user):
    tickets = Ticket.objects.filter(requester=user).order_by('-created_at')[:5]
    if not tickets.exists():
        return "You have no open tickets."
    
    results = []
    for t in tickets:
        results.append(f"Ticket #{str(t.id)[:8]}... | Status: {t.status} | Subject: {t.subject}")
    return "\n".join(results)

def _db_get_projects(user):
    projects = user.shared_projects.all()[:5]
    if not projects.exists():
        return "You are not listed as a member of any active shared projects."
    
    results = []
    for p in projects:
        results.append(f"Project: {p.name} | Host: {p.host_organization.name}")
    return "\n".join(results)

