"""
Test Cloudinary file upload
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from io import BytesIO

try:
    # Create a small test file
    test_content = b"This is a test file for Cloudinary upload"
    test_file = BytesIO(test_content)
    test_file.name = 'test_upload.txt'
    
    print("Attempting test upload to Cloudinary...")
    
    # Try to upload
    result = cloudinary.uploader.upload(
        test_file,
        folder='test',
        resource_type='raw'
    )
    
    print(f"\n✅ Upload successful!")
    print(f"URL: {result.get('url')}")
    print(f"Public ID: {result.get('public_id')}")
    print(f"Format: {result.get('format')}")
    print(f"Bytes: {result.get('bytes')}")
    
    # Try to delete the test file
    print("\nCleaning up test file...")
    cloudinary.uploader.destroy(result.get('public_id'), resource_type='raw')
    print("✅ Cleanup successful!")
    
except Exception as e:
    print(f"\n❌ Upload failed: {e}")
    import traceback
    traceback.print_exc()
