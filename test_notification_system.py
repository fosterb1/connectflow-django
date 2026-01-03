"""
Test script for Notification System
Tests notification count updates when marking as read
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Notification

User = get_user_model()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def test_notification_model():
    """Test 1: Verify Notification model has required fields"""
    print_header("TEST 1: Notification Model")
    
    try:
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Check if Notification model has required fields
        notification = Notification.objects.first()
        if notification:
            assert hasattr(notification, 'is_read'), "Missing is_read field"
            assert hasattr(notification, 'recipient'), "Missing recipient field"
            assert hasattr(notification, 'title'), "Missing title field"
            assert hasattr(notification, 'content'), "Missing content field"
            
            print_success("Notification model has all required fields")
            print_info(f"Sample notification: {notification.title}")
            print_info(f"Is read: {notification.is_read}")
            return True
        else:
            print_info("No notifications found (this is okay)")
            return True
            
    except Exception as e:
        print_error(f"Model test failed: {str(e)}")
        return False

def test_create_notification():
    """Test 2: Create a test notification"""
    print_header("TEST 2: Create Notification")
    
    try:
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Create test notification
        notification = Notification.objects.create(
            recipient=user,
            title="Test Notification",
            content="This is a test notification for testing purposes",
            notification_type=Notification.NotificationType.SYSTEM,
            is_read=False
        )
        
        print_success(f"Created notification: {notification.id}")
        print_info(f"Recipient: {user.username}")
        print_info(f"Is read: {notification.is_read}")
        
        return True
        
    except Exception as e:
        print_error(f"Create notification test failed: {str(e)}")
        return False

def test_mark_as_read():
    """Test 3: Mark notification as read"""
    print_header("TEST 3: Mark Notification as Read")
    
    try:
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Get an unread notification
        notification = user.notifications.filter(is_read=False).first()
        
        if not notification:
            print_info("No unread notifications found, creating one...")
            notification = Notification.objects.create(
                recipient=user,
                title="Test for Mark as Read",
                content="Testing mark as read functionality",
                notification_type=Notification.NotificationType.SYSTEM,
                is_read=False
            )
        
        print_info(f"Notification ID: {notification.id}")
        print_info(f"Before - Is read: {notification.is_read}")
        
        # Mark as read
        notification.is_read = True
        notification.save()
        
        # Refresh from database
        notification.refresh_from_db()
        
        print_info(f"After - Is read: {notification.is_read}")
        
        if notification.is_read:
            print_success("Successfully marked notification as read")
            return True
        else:
            print_error("Failed to mark notification as read")
            return False
            
    except Exception as e:
        print_error(f"Mark as read test failed: {str(e)}")
        return False

def test_unread_count():
    """Test 4: Test unread notification count"""
    print_header("TEST 4: Unread Count")
    
    try:
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Get initial count
        initial_count = user.notifications.filter(is_read=False).count()
        print_info(f"Initial unread count: {initial_count}")
        
        # Create a new unread notification
        Notification.objects.create(
            recipient=user,
            title="Test Unread Count",
            content="Testing unread count functionality",
            notification_type=Notification.NotificationType.MESSAGE,
            is_read=False
        )
        
        # Get new count
        new_count = user.notifications.filter(is_read=False).count()
        print_info(f"After creating notification: {new_count}")
        
        if new_count == initial_count + 1:
            print_success("Unread count correctly increased by 1")
            
            # Mark all as read
            user.notifications.filter(is_read=False).update(is_read=True)
            
            # Get final count
            final_count = user.notifications.filter(is_read=False).count()
            print_info(f"After marking all as read: {final_count}")
            
            if final_count == 0:
                print_success("All notifications successfully marked as read")
                return True
            else:
                print_error(f"Expected 0 unread, got {final_count}")
                return False
        else:
            print_error(f"Expected count {initial_count + 1}, got {new_count}")
            return False
            
    except Exception as e:
        print_error(f"Unread count test failed: {str(e)}")
        return False

def test_context_processor():
    """Test 5: Test notification context processor"""
    print_header("TEST 5: Context Processor")
    
    try:
        from apps.accounts.context_processors import notifications_processor
        from django.test import RequestFactory
        
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Create mock request
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        
        # Test context processor
        context = notifications_processor(request)
        
        assert 'unread_notifications_count' in context, "Missing unread_notifications_count"
        assert 'recent_notifications' in context, "Missing recent_notifications"
        
        print_success("Context processor returns correct keys")
        print_info(f"Unread count: {context['unread_notifications_count']}")
        print_info(f"Recent notifications: {len(list(context['recent_notifications']))}")
        
        return True
        
    except Exception as e:
        print_error(f"Context processor test failed: {str(e)}")
        return False

def test_notification_url():
    """Test 6: Test mark notification read URL"""
    print_header("TEST 6: Notification URL Configuration")
    
    try:
        from django.urls import reverse
        
        # Test mark all as read URL
        url_all = reverse('accounts:mark_notifications_read')
        print_success(f"Mark all as read URL: {url_all}")
        
        # Test mark single as read URL
        import uuid
        test_id = uuid.uuid4()
        url_single = reverse('accounts:mark_notification_read', kwargs={'notification_id': test_id})
        print_success(f"Mark single as read URL pattern: {url_single}")
        
        return True
        
    except Exception as e:
        print_error(f"URL configuration test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and print summary"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{'NOTIFICATION SYSTEM TEST SUITE'.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Notification Model", test_notification_model),
        ("Create Notification", test_create_notification),
        ("Mark as Read", test_mark_as_read),
        ("Unread Count", test_unread_count),
        ("Context Processor", test_context_processor),
        ("URL Configuration", test_notification_url),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}\n")
        print(f"{Colors.GREEN}Notification system is working correctly!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Review above for details.{Colors.END}\n")

if __name__ == '__main__':
    run_all_tests()
