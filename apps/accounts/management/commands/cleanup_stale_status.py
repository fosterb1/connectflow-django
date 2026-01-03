from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Reset status to OFFLINE for users who haven\'t been seen in 30+ minutes'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(minutes=30)
        
        stale_users = User.objects.filter(
            status='ONLINE',
            last_seen__lt=cutoff_time
        )
        
        count = stale_users.update(status=User.Status.OFFLINE)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Reset {count} stale ONLINE statuses to OFFLINE')
        )
