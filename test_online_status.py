"""
Test script for Online/Offline Status System
Tests all aspects of the presence tracking implementation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.urls import reverse

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

def test_database_model():
    """Test 1: Verify User model has status fields"""
    print_header("TEST 1: Database Model")
    
    try:
        # Check if status field exists
        user = User.objects.first()
        if user:
            assert hasattr(user, 'status'), "User model missing 'status' field"
            assert hasattr(user, 'last_seen'), "User model missing 'last_seen' field"
            
            # Check status choices
            status_choices = [choice[0] for choice in User.Status.choices]
            assert 'ONLINE' in status_choices, "ONLINE status missing"
            assert 'OFFLINE' in status_choices, "OFFLINE status missing"
            assert 'AWAY' in status_choices, "AWAY status missing"
            assert 'BUSY' in status_choices, "BUSY status missing"
            
            print_success("User model has correct status field")
            print_success("Status choices: ONLINE, OFFLINE, AWAY, BUSY")
            print_info(f"Current user status: {user.status}")
            print_info(f"Last seen: {user.last_seen}")
            return True
        else:
            print_error("No users found in database")
            return False
    except Exception as e:
        print_error(f"Database model test failed: {str(e)}")
        return False

def test_status_update():
    """Test 2: Test status update functionality"""
    print_header("TEST 2: Status Update Functionality")
    
    try:
        user = User.objects.first()
        if not user:
            print_error("No users found")
            return False
        
        # Test setting status to ONLINE
        original_status = user.status
        user.status = User.Status.ONLINE
        user.save(update_fields=['status', 'last_seen'])
        user.refresh_from_db()
        
        assert user.status == 'ONLINE', "Failed to set status to ONLINE"
        print_success("Successfully set status to ONLINE")
        
        # Test setting status to AWAY
        user.status = User.Status.AWAY
        user.save(update_fields=['status', 'last_seen'])
        user.refresh_from_db()
        
        assert user.status == 'AWAY', "Failed to set status to AWAY"
        print_success("Successfully set status to AWAY")
        
        # Test setting status to OFFLINE
        user.status = User.Status.OFFLINE
        user.save(update_fields=['status', 'last_seen'])
        user.refresh_from_db()
        
        assert user.status == 'OFFLINE', "Failed to set status to OFFLINE"
        print_success("Successfully set status to OFFLINE")
        
        # Restore original status
        user.status = original_status
        user.save(update_fields=['status'])
        
        return True
    except Exception as e:
        print_error(f"Status update test failed: {str(e)}")
        return False

def test_presence_consumer():
    """Test 3: Check if PresenceConsumer exists"""
    print_header("TEST 3: Presence Consumer")
    
    try:
        from apps.accounts.consumers import PresenceConsumer
        
        print_success("PresenceConsumer imported successfully")
        
        # Check if required methods exist
        required_methods = ['connect', 'disconnect', 'receive', 'set_status', 'update_activity']
        for method in required_methods:
            assert hasattr(PresenceConsumer, method), f"Missing method: {method}"
            print_success(f"Method '{method}' exists")
        
        return True
    except ImportError as e:
        print_error(f"Failed to import PresenceConsumer: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Presence consumer test failed: {str(e)}")
        return False

def test_routing():
    """Test 4: Check WebSocket routing"""
    print_header("TEST 4: WebSocket Routing")
    
    try:
        from apps.accounts.routing import websocket_urlpatterns
        
        # Check if presence route exists
        presence_route_exists = any(
            'presence' in str(pattern.pattern) 
            for pattern in websocket_urlpatterns
        )
        
        if presence_route_exists:
            print_success("Presence WebSocket route configured")
        else:
            print_error("Presence WebSocket route NOT found")
            return False
        
        # List all WebSocket routes
        print_info("Configured WebSocket routes:")
        for pattern in websocket_urlpatterns:
            print(f"  - {pattern.pattern}")
        
        return True
    except Exception as e:
        print_error(f"Routing test failed: {str(e)}")
        return False

def test_stale_status_cleanup():
    """Test 5: Test cleanup_stale_status command"""
    print_header("TEST 5: Stale Status Cleanup Command")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Create a test user with stale status
        test_user = User.objects.first()
        if test_user:
            old_time = timezone.now() - timedelta(minutes=35)
            
            # Manually set status and last_seen
            User.objects.filter(id=test_user.id).update(
                status='ONLINE',
                last_seen=old_time
            )
            
            print_info(f"Created stale user: {test_user.username}")
            print_info(f"Set last_seen to 35 minutes ago")
            
            # Run cleanup command
            out = StringIO()
            call_command('cleanup_stale_status', stdout=out)
            
            # Refresh and check status
            test_user.refresh_from_db()
            
            if test_user.status == 'OFFLINE':
                print_success("Cleanup command reset stale status to OFFLINE")
                print_info(out.getvalue().strip())
                return True
            else:
                print_error(f"Status still: {test_user.status} (expected OFFLINE)")
                return False
        else:
            print_error("No test user available")
            return False
            
    except Exception as e:
        print_error(f"Cleanup command test failed: {str(e)}")
        return False

def test_login_status_update():
    """Test 6: Check if login updates status"""
    print_header("TEST 6: Login Status Update")
    
    try:
        # Check if LoginView exists and has status update logic
        import inspect
        from apps.accounts.views import LoginView
        
        source = inspect.getsource(LoginView.post)
        
        if 'user.status' in source and 'ONLINE' in source:
            print_success("LoginView updates user status to ONLINE")
        else:
            print_error("LoginView does NOT update status")
            return False
        
        if 'last_seen' in source:
            print_success("LoginView updates last_seen timestamp")
        else:
            print_error("LoginView does NOT update last_seen")
            return False
        
        return True
    except Exception as e:
        print_error(f"Login status test failed: {str(e)}")
        return False

def test_logout_status_update():
    """Test 7: Check if logout updates status"""
    print_header("TEST 7: Logout Status Update")
    
    try:
        import inspect
        from apps.accounts.views import LogoutView
        
        source = inspect.getsource(LogoutView.get)
        
        if 'user.status' in source and 'OFFLINE' in source:
            print_success("LogoutView updates user status to OFFLINE")
        else:
            print_error("LogoutView does NOT update status")
            return False
        
        if 'last_seen' in source:
            print_success("LogoutView updates last_seen timestamp")
        else:
            print_error("LogoutView does NOT update last_seen")
            return False
        
        return True
    except Exception as e:
        print_error(f"Logout status test failed: {str(e)}")
        return False

def test_visual_indicators():
    """Test 8: Check if templates have status indicators"""
    print_header("TEST 8: Visual Status Indicators")
    
    template_files = [
        'templates/chat_channels/channel_detail.html',
        'templates/chat_channels/channel_list.html',
        'templates/organizations/member_directory.html',
        'templates/accounts/profile_detail.html',
    ]
    
    all_passed = True
    for template_path in template_files:
        full_path = os.path.join('D:\\Projects\\connectflow-django', template_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for status indicators (either status-dot class or inline status checks)
            has_status_indicator = (
                ('status-dot' in content or 'status_dot' in content) or
                ('.status' in content and 'ONLINE' in content and 'bg-green-500' in content)
            )
            
            if has_status_indicator:
                print_success(f"✓ {template_path}")
            else:
                print_error(f"✗ {template_path} (no status indicators found)")
                all_passed = False
        else:
            print_info(f"⊘ {template_path} (file not found)")
    
    return all_passed

def test_idle_detection():
    """Test 9: Check if idle detection is implemented"""
    print_header("TEST 9: Idle Detection in Frontend")
    
    try:
        base_template_path = 'D:\\Projects\\connectflow-django\\templates\\base.html'
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'idleTimeout variable': 'idleTimeout' in content,
            'resetIdleTimer function': 'resetIdleTimer' in content,
            'setUserStatus function': 'setUserStatus' in content,
            'Activity event listeners': 'mousedown' in content and 'keydown' in content,
            '5 minute AWAY timeout': '5 * 60 * 1000' in content,
            '30 minute OFFLINE timeout': '30 * 60 * 1000' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print_success(check_name)
            else:
                print_error(check_name)
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_error(f"Idle detection test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and print summary"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{'ONLINE/OFFLINE STATUS SYSTEM TEST SUITE'.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Database Model", test_database_model),
        ("Status Update", test_status_update),
        ("Presence Consumer", test_presence_consumer),
        ("WebSocket Routing", test_routing),
        ("Stale Status Cleanup", test_stale_status_cleanup),
        ("Login Status Update", test_login_status_update),
        ("Logout Status Update", test_logout_status_update),
        ("Visual Indicators", test_visual_indicators),
        ("Idle Detection", test_idle_detection),
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
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Review above for details.{Colors.END}\n")

if __name__ == '__main__':
    run_all_tests()
