"""
Test Script for API Modules

This script tests that all modules can be imported and basic functionality works.
It doesn't require actual API credentials and focuses on testing the structure.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing module imports...")
    
    try:
        # Test utility imports
        from utils.auth import AuthManager
        from utils.error_handling import APIError, AuthenticationError, RateLimitError
        print("✓ Utility modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import utility modules: {e}")
        return False
    
    try:
        # Test Coda API imports
        from coda_api import CodaClient
        print("✓ Coda API module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Coda API module: {e}")
        return False
    
    try:
        # Test GitHub API imports
        from github_api import GitHubClient
        print("✓ GitHub API module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import GitHub API module: {e}")
        return False
    
    try:
        # Test Google Calendar API imports
        from google_calendar_api import GoogleCalendarClient
        print("✓ Google Calendar API module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Google Calendar API module: {e}")
        return False
    
    return True


def test_client_initialization():
    """Test that clients can be initialized (will fail without credentials, but should not crash)."""
    print("\nTesting client initialization...")
    
    # Test Coda client initialization
    try:
        from coda_api import CodaClient
        # This will fail without credentials, but should raise a proper error
        client = CodaClient()
        print("✓ Coda client initialized (with credentials)")
    except Exception as e:
        if "CODA_API_TOKEN" in str(e) or "authentication" in str(e).lower():
            print("✓ Coda client initialization test passed (expected auth error)")
        else:
            print(f"✗ Unexpected error initializing Coda client: {e}")
            return False
    
    # Test GitHub client initialization
    try:
        from github_api import GitHubClient
        client = GitHubClient()
        print("✓ GitHub client initialized (with credentials)")
    except Exception as e:
        if "GITHUB_TOKEN" in str(e) or "authentication" in str(e).lower():
            print("✓ GitHub client initialization test passed (expected auth error)")
        else:
            print(f"✗ Unexpected error initializing GitHub client: {e}")
            return False
    
    # Test Google Calendar client initialization
    try:
        from google_calendar_api import GoogleCalendarClient
        client = GoogleCalendarClient()
        print("✓ Google Calendar client initialized (with credentials)")
    except Exception as e:
        if "credentials" in str(e).lower() or "authentication" in str(e).lower():
            print("✓ Google Calendar client initialization test passed (expected auth error)")
        else:
            print(f"✗ Unexpected error initializing Google Calendar client: {e}")
            return False
    
    return True


def test_error_handling():
    """Test that error handling classes work correctly."""
    print("\nTesting error handling...")
    
    try:
        from utils.error_handling import APIError, AuthenticationError, RateLimitError, ValidationError
        
        # Test error instantiation
        api_error = APIError("Test API error", 400, {"message": "test"})
        auth_error = AuthenticationError("Test auth error", 401, {"message": "unauthorized"})
        rate_error = RateLimitError("Test rate limit error", 429, {"message": "rate limited"})
        val_error = ValidationError("Test validation error")
        
        print("✓ All error classes instantiated successfully")
        
        # Test error properties
        assert api_error.status_code == 400
        assert auth_error.status_code == 401
        assert rate_error.status_code == 429
        assert "Test" in str(api_error)
        
        print("✓ Error properties work correctly")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False
    
    return True


def test_validation():
    """Test that validation functions work correctly."""
    print("\nTesting validation functions...")
    
    try:
        from utils.error_handling import validate_input
        
        # Test valid input
        test_data = {"name": "test", "email": "test@example.com"}
        validate_input(test_data, ["name", "email"], "test data")
        print("✓ Valid input validation passed")
        
        # Test invalid input (should raise ValidationError)
        try:
            validate_input(None, ["name"], "test data")
            print("✗ Validation should have failed for None input")
            return False
        except Exception as e:
            if "ValidationError" in str(type(e).__name__):
                print("✓ Invalid input validation correctly raised error")
            else:
                print(f"✗ Unexpected error type: {type(e).__name__}")
                return False
        
        # Test missing required fields
        try:
            validate_input({"name": "test"}, ["name", "email"], "test data")
            print("✗ Validation should have failed for missing fields")
            return False
        except Exception as e:
            if "ValidationError" in str(type(e).__name__):
                print("✓ Missing fields validation correctly raised error")
            else:
                print(f"✗ Unexpected error type: {type(e).__name__}")
                return False
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False
    
    return True


def test_documentation():
    """Test that modules have proper documentation."""
    print("\nTesting documentation...")
    
    try:
        from coda_api import CodaClient
        from github_api import GitHubClient
        from google_calendar_api import GoogleCalendarClient
        
        # Check that classes have docstrings
        if CodaClient.__doc__:
            print("✓ CodaClient has documentation")
        else:
            print("✗ CodaClient missing documentation")
            return False
        
        if GitHubClient.__doc__:
            print("✓ GitHubClient has documentation")
        else:
            print("✗ GitHubClient missing documentation")
            return False
        
        if GoogleCalendarClient.__doc__:
            print("✓ GoogleCalendarClient has documentation")
        else:
            print("✗ GoogleCalendarClient missing documentation")
            return False
        
        # Check that methods have docstrings
        methods_to_check = [
            (CodaClient, 'list_documents'),
            (CodaClient, 'get_document'),
            (GitHubClient, 'get_user_info'),
            (GitHubClient, 'get_user_repositories'),
            (GoogleCalendarClient, 'list_calendars'),
            (GoogleCalendarClient, 'list_events')
        ]
        
        for cls, method_name in methods_to_check:
            method = getattr(cls, method_name, None)
            if method and method.__doc__:
                print(f"✓ {cls.__name__}.{method_name} has documentation")
            else:
                print(f"✗ {cls.__name__}.{method_name} missing documentation")
                return False
        
    except Exception as e:
        print(f"✗ Documentation test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("API MODULES TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Client Initialization", test_client_initialization),
        ("Error Handling", test_error_handling),
        ("Validation", test_validation),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ API modules are ready for use")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 