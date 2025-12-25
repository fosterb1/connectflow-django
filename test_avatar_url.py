#!/usr/bin/env python
"""
Test script to verify avatar URL generation works correctly.
Run this to confirm the fix before restarting the server.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.conf import settings
from apps.accounts.models import User

print("=" * 60)
print("AVATAR URL TEST")
print("=" * 60)

print(f"\n✓ MEDIA_URL: {settings.MEDIA_URL}")
print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Check context processors
context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
has_media_processor = 'django.template.context_processors.media' in context_processors
print(f"\n✓ Media context processor installed: {has_media_processor}")

if not has_media_processor:
    print("  ⚠️  WARNING: Media context processor is missing!")
    print("  The fix requires server restart to take effect.")

print("\n" + "=" * 60)
print("USER AVATARS IN DATABASE")
print("=" * 60)

users_with_avatars = User.objects.filter(avatar__isnull=False).exclude(avatar='')
if users_with_avatars.exists():
    for user in users_with_avatars:
        print(f"\n👤 User: {user.username}")
        try:
            if user.avatar:
                print(f"   Avatar field: {user.avatar}")
                try:
                    print(f"   Avatar URL: {user.avatar.url}")
                except Exception as e:
                    print(f"   Avatar URL: Error - {e}")
            else:
                print("   Avatar: None")
        except Exception as e:
            print(f"   Error accessing avatar: {e}")
else:
    print("\n⚠️  No users with avatars found in database.")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
print("\n1. RESTART your Django development server")
print("2. Hard refresh your browser (Ctrl+Shift+R or Ctrl+F5)")
print("3. Check the profile page - images should now display correctly")
print("\n" + "=" * 60)
