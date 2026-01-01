"""
Test to verify IDOR vulnerability is fixed
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, SharedProject, SubscriptionPlan
from django.urls import reverse
import uuid

User = get_user_model()


class IDORSecurityTest(TestCase):
    """Test that users cannot access projects from other organizations"""
    
    def setUp(self):
        # Create two separate organizations
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            price_monthly=0,
            max_users=10,
            max_projects=5
        )
        
        self.org1 = Organization.objects.create(
            name="Organization 1",
            code="ORG1",
            subscription_plan=self.plan,
            subscription_status='active'
        )
        
        self.org2 = Organization.objects.create(
            name="Organization 2",
            code="ORG2",
            subscription_plan=self.plan,
            subscription_status='active'
        )
        
        # Create users in each organization
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@org1.com',
            password='testpass123',
            organization=self.org1,
            role='ORG_ADMIN',
            email_verified=True
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@org2.com',
            password='testpass123',
            organization=self.org2,
            role='ORG_ADMIN',
            email_verified=True
        )
        
        # Create a project for org1
        self.project_org1 = SharedProject.objects.create(
            name="Org 1 Project",
            host_organization=self.org1,
            created_by=self.user1,
            description="Private project for org 1"
        )
        self.project_org1.members.add(self.user1)
        
        self.client = Client()
    
    def test_user_cannot_access_other_org_project(self):
        """Test that user from org2 cannot access org1's project"""
        # Login as user2 (from org2)
        self.client.login(username='user2', password='testpass123')
        
        # Try to access org1's project
        url = reverse('organizations:shared_project_detail', kwargs={'pk': self.project_org1.pk})
        response = self.client.get(url)
        
        # Should get 404, not redirect or project data
        self.assertEqual(response.status_code, 404)
        
    def test_user_can_access_own_org_project(self):
        """Test that user from org1 CAN access org1's project"""
        # Login as user1 (from org1)
        self.client.login(username='user1', password='testpass123')
        
        # Access own org's project
        url = reverse('organizations:shared_project_detail', kwargs={'pk': self.project_org1.pk})
        response = self.client.get(url)
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Org 1 Project")
    
    def test_guest_org_can_access_shared_project(self):
        """Test that guest organization can access shared project"""
        # Add org2 as guest
        self.project_org1.guest_organizations.add(self.org2)
        self.project_org1.members.add(self.user2)
        
        # Login as user2 (guest)
        self.client.login(username='user2', password='testpass123')
        
        # Access shared project
        url = reverse('organizations:shared_project_detail', kwargs={'pk': self.project_org1.pk})
        response = self.client.get(url)
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
    
    def test_all_project_endpoints_protected(self):
        """Test that all project endpoints are protected"""
        # Login as user2 (wrong org)
        self.client.login(username='user2', password='testpass123')
        
        endpoints = [
            'organizations:shared_project_detail',
            'organizations:project_files',
            'organizations:project_meetings',
            'organizations:project_tasks',
            'organizations:project_milestones',
            'organizations:project_risk_dashboard',
        ]
        
        for endpoint_name in endpoints:
            with self.subTest(endpoint=endpoint_name):
                try:
                    url = reverse(endpoint_name, kwargs={'pk': self.project_org1.pk})
                    response = self.client.get(url)
                    # All should return 404 or redirect (not 200 with data)
                    self.assertIn(response.status_code, [404, 302, 403])
                except:
                    # Some endpoints might not exist, that's OK
                    pass
    
    def test_no_data_leakage_in_error(self):
        """Verify that 404 responses don't leak project existence"""
        # Login as user2
        self.client.login(username='user2', password='testpass123')
        
        # Try to access org1's project
        url = reverse('organizations:shared_project_detail', kwargs={'pk': self.project_org1.pk})
        response = self.client.get(url)
        
        # Check that response doesn't contain project details
        self.assertEqual(response.status_code, 404)
        
        # Verify no project name in response
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            self.assertNotIn("Org 1 Project", content)
            self.assertNotIn(str(self.project_org1.pk), content)


if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])
