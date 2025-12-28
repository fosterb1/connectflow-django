from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, SubscriptionPlan
from .models import Ticket, TicketMessage

User = get_user_model()

class TicketModelTest(TestCase):
    def setUp(self):
        # Create Plans
        self.basic_plan = SubscriptionPlan.objects.create(
            name="Basic",
            has_priority_support=False,
            price_monthly=10.00
        )
        self.pro_plan = SubscriptionPlan.objects.create(
            name="Pro",
            has_priority_support=True,
            price_monthly=50.00
        )

        # Create Organizations
        self.basic_org = Organization.objects.create(
            name="Basic Org",
            code="BASIC",
            subscription_plan=self.basic_plan
        )
        self.pro_org = Organization.objects.create(
            name="Pro Org",
            code="PRO",
            subscription_plan=self.pro_plan
        )

        # Create Users
        self.basic_user = User.objects.create_user(
            username='basic_user',
            email='basic@example.com',
            password='password123',
            email_verified=True
        )
        self.basic_user.organization = self.basic_org
        self.basic_user.save()

        self.pro_user = User.objects.create_user(
            username='pro_user',
            email='pro@example.com',
            password='password123',
            email_verified=True
        )
        self.pro_user.organization = self.pro_org
        self.pro_user.save()

    def test_ticket_creation_defaults(self):
        ticket = Ticket.objects.create(
            requester=self.basic_user,
            subject="Help me"
        )
        self.assertEqual(ticket.organization, self.basic_org)
        self.assertFalse(ticket.is_priority_support)
        self.assertEqual(ticket.priority, Ticket.Priority.MEDIUM)

    def test_priority_support_auto_detection(self):
        # Refresh from DB to ensure relationships are loaded? 
        # Usually not needed if object is fresh, but let's be safe.
        self.pro_user.refresh_from_db()
        
        ticket = Ticket.objects.create(
            requester=self.pro_user,
            subject="Urgent help needed"
        )
        self.assertEqual(ticket.organization, self.pro_org)
        self.assertTrue(ticket.is_priority_support)
        self.assertEqual(ticket.priority, Ticket.Priority.HIGH)

    def test_manual_priority_override_on_creation(self):
        self.pro_user.refresh_from_db()
        
        ticket = Ticket.objects.create(
            requester=self.pro_user,
            subject="Low priority issue",
            priority=Ticket.Priority.LOW
        )
        self.assertTrue(ticket.is_priority_support) # Still flagged as priority support account
        self.assertEqual(ticket.priority, Ticket.Priority.LOW) # But priority remains LOW

class TicketViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            email_verified=True
        )
        self.client.force_login(self.user)
        self.url_list = reverse('support:ticket_list')
        self.url_create = reverse('support:ticket_create')

    def test_ticket_list_view(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/ticket_list.html')

    def test_ticket_create_view_get(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/ticket_create.html')

    def test_ticket_create_view_post(self):
        data = {
            'subject': 'New Issue',
            'category': Ticket.Category.TECHNICAL,
            'priority': Ticket.Priority.MEDIUM,
            'content': 'This is the message body' # This goes to TicketMessageForm
        }
        response = self.client.post(self.url_create, data)
        self.assertEqual(response.status_code, 302) # Redirects to detail
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(TicketMessage.objects.count(), 1)
        
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.subject, 'New Issue')
        self.assertEqual(ticket.messages.first().content, 'This is the message body')
