from django.core.management.base import BaseCommand
from apps.accounts.models import User
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Clean up broken avatar references (files that no longer exist)'

    def handle(self, *args, **options):
        self.stdout.write('Checking for broken avatar references...\n')
        
        users_with_avatars = User.objects.exclude(avatar='').exclude(avatar__isnull=True)
        broken_count = 0
        fixed_count = 0
        
        for user in users_with_avatars:
            avatar_path = str(user.avatar)
            
            # Check if file exists in storage
            try:
                exists = default_storage.exists(user.avatar.name)
            except Exception as e:
                exists = False
                self.stdout.write(self.style.WARNING(f'Error checking {user.username}: {e}'))
            
            if not exists:
                self.stdout.write(
                    self.style.WARNING(
                        f'Broken avatar for {user.username}: {avatar_path}'
                    )
                )
                broken_count += 1
                
                # Clear the broken reference
                user.avatar = ''
                user.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Cleared broken avatar for {user.username}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Found {broken_count} broken avatars'))
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} broken references'))
        
        if broken_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All avatars are valid!'))
