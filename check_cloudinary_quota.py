"""
Check Cloudinary configuration and quota
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

import cloudinary
import cloudinary.api

try:
    # Test API connection
    print("Testing Cloudinary connection...")
    print(f"Cloud Name: {cloudinary.config().cloud_name}")
    
    # Get usage stats
    usage = cloudinary.api.usage()
    
    print("\n=== Cloudinary Usage Stats ===")
    print(f"Plan: {usage.get('plan', 'N/A')}")
    print(f"Credits used: {usage.get('credits', {}).get('used', 0)}")
    print(f"Credits limit: {usage.get('credits', {}).get('limit', 0)}")
    
    if 'transformations' in usage:
        print(f"\nTransformations used: {usage['transformations'].get('used', 0)}")
        print(f"Transformations limit: {usage['transformations'].get('limit', 0)}")
    
    if 'storage' in usage:
        storage_used_mb = usage['storage'].get('used', 0) / (1024 * 1024)
        storage_limit_mb = usage['storage'].get('limit', 0) / (1024 * 1024)
        print(f"\nStorage used: {storage_used_mb:.2f} MB")
        print(f"Storage limit: {storage_limit_mb:.2f} MB")
        
        # Check if approaching limit
        if storage_limit_mb > 0:
            usage_percent = (storage_used_mb / storage_limit_mb) * 100
            print(f"Storage usage: {usage_percent:.1f}%")
            
            if usage_percent > 90:
                print("\n⚠️  WARNING: Storage quota is over 90% full!")
            elif usage_percent > 75:
                print("\n⚠️  WARNING: Storage quota is over 75% full!")
    
    print("\n✅ Cloudinary connection successful!")
    
except cloudinary.exceptions.Error as e:
    print(f"\n❌ Cloudinary Error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
