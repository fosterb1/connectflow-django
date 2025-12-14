from django.core.management.base import BaseCommand
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Creates a demo organization for testing'

    def handle(self, *args, **kwargs):
        org, created = Organization.objects.get_or_create(
            code='DEMO2025',
            defaults={
                'name': 'Demo Corporation',
                'description': 'A demo organization for testing ConnectFlow Pro',
                'timezone': 'America/New_York',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created organization: {org.name}'))
            self.stdout.write(self.style.SUCCESS(f'📝 Organization Code: {org.code}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Organization already exists: {org.name}'))
            self.stdout.write(self.style.SUCCESS(f'📝 Organization Code: {org.code}'))
