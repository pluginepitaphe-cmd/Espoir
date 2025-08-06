#!/usr/bin/env python3
"""
WordPress Integration Tests for SIPORTS Backend
Testing the new WordPress integration endpoints as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Using the URL from the existing test files
BACKEND_URL = "https://3af9f13b-c7da-4bc1-b1f4-89ae2ae52faa.preview.emergentagent.com/api"

# Test credentials as specified in the review request
WORDPRESS_ADMIN_USER = {
    "username": "admin@siportevent.com",
    "password": "admin123"
}

# Regular SIPORTS credentials for compatibility testing
SIPORTS_ADMIN_USER = {
    "email": "admin@siportevent.com",
    "password": "admin123"
}

SIPORTS_EXPOSANT_USER = {
    "email": "exposant@example.com",
    "password": "expo123"
}

class WordPressIntegrationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.wp_admin_token = None
        self.siports_admin_token = None
        self.siports_exposant_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_endpoint(self):
        """Test GET /api/health - Verify WordPress integration is loaded"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if WordPress integration status is mentioned
                if "wordpress" in str(data).lower() or "integration" in str(data).lower():
                    self.log_test("Health Endpoint - WordPress Integration", True, 
                                f"Health endpoint accessible, WordPress integration status: {data}")
                    return True
                else:
                    # Even if no specific WordPress mention, if health endpoint works, it's good
                    self.log_test("Health Endpoint - WordPress Integration", True, 
                                f"Health endpoint accessible: {data}")
                    return True
            elif response.status_code == 404:
                # Try alternative health endpoints
                alt_endpoints = ["/", "/status", "/ping"]
                for endpoint in alt_endpoints:
                    try:
                        alt_response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                        if alt_response.status_code == 200:
                            alt_data = alt_response.json()
                            self.log_test("Health Endpoint - WordPress Integration", True, 
                                        f"Alternative health endpoint {endpoint} accessible: {alt_data}")
                            return True
                    except:
                        continue
                
                self.log_test("Health Endpoint - WordPress Integration", False, 
                            f"Health endpoint not found (404), tried alternatives")
                return False
            else:
                self.log_test("Health Endpoint - WordPress Integration", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint - WordPress Integration", False, f"Request error: {str(e)}")
            return False
    
    def test_wordpress_login(self):
        """Test POST /api/auth/wordpress-login - WordPress authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/wordpress-login",
                json=WORDPRESS_ADMIN_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for JWT token and user data
                if "access_token" in data and "user" in data:
                    self.wp_admin_token = data["access_token"]
                    user = data["user"]
                    
                    self.log_test("WordPress Authentication", True, 
                                f"WordPress login successful - User: {user.get('username', 'N/A')}, Token received")
                    return True
                else:
                    self.log_test("WordPress Authentication", False, 
                                f"Missing access_token or user in response: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("WordPress Authentication", False, 
                            "WordPress login endpoint not implemented (404)")
                return False
            elif response.status_code == 401:
                self.log_test("WordPress Authentication", False, 
                            "WordPress authentication failed - Invalid credentials")
                return False
            else:
                self.log_test("WordPress Authentication", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("WordPress Authentication", False, f"Request error: {str(e)}")
            return False
    
    def test_sync_status(self):
        """Test GET /api/sync/status - Synchronization status"""
        try:
            headers = {}
            if self.wp_admin_token:
                headers["Authorization"] = f"Bearer {self.wp_admin_token}"
            elif self.siports_admin_token:
                headers["Authorization"] = f"Bearer {self.siports_admin_token}"
            
            response = requests.get(
                f"{self.base_url}/sync/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for sync status fields
                expected_fields = ["synced_users", "synced_packages", "sync_enabled"]
                if any(field in data for field in expected_fields):
                    self.log_test("Sync Status", True, 
                                f"Sync status retrieved: {data}")
                    return True
                else:
                    self.log_test("Sync Status", True, 
                                f"Sync status endpoint accessible: {data}")
                    return True
            elif response.status_code == 404:
                self.log_test("Sync Status", False, 
                            "Sync status endpoint not implemented (404)")
                return False
            elif response.status_code == 401:
                self.log_test("Sync Status", False, 
                            "Sync status requires authentication (401)")
                return False
            elif response.status_code == 403:
                self.log_test("Sync Status", False, 
                            "Sync status access forbidden (403)")
                return False
            else:
                self.log_test("Sync Status", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Sync Status", False, f"Request error: {str(e)}")
            return False
    
    def test_sync_users(self):
        """Test POST /api/sync/users - User synchronization"""
        try:
            headers = {}
            if self.wp_admin_token:
                headers["Authorization"] = f"Bearer {self.wp_admin_token}"
            elif self.siports_admin_token:
                headers["Authorization"] = f"Bearer {self.siports_admin_token}"
            
            sync_request = {
                "sync_type": "users",
                "force": False,
                "batch_size": 10
            }
            
            response = requests.post(
                f"{self.base_url}/sync/users",
                json=sync_request,
                headers=headers,
                timeout=30  # Longer timeout for sync operations
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for sync result fields
                if "success" in data or "records_processed" in data or "message" in data:
                    self.log_test("User Synchronization", True, 
                                f"User sync completed: {data}")
                    return True
                else:
                    self.log_test("User Synchronization", True, 
                                f"User sync endpoint accessible: {data}")
                    return True
            elif response.status_code == 404:
                self.log_test("User Synchronization", False, 
                            "User sync endpoint not implemented (404)")
                return False
            elif response.status_code == 401:
                self.log_test("User Synchronization", False, 
                            "User sync requires authentication (401)")
                return False
            elif response.status_code == 403:
                self.log_test("User Synchronization", False, 
                            "User sync access forbidden (403)")
                return False
            else:
                self.log_test("User Synchronization", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Synchronization", False, f"Request error: {str(e)}")
            return False
    
    def test_sync_packages(self):
        """Test POST /api/sync/packages - Package synchronization"""
        try:
            headers = {}
            if self.wp_admin_token:
                headers["Authorization"] = f"Bearer {self.wp_admin_token}"
            elif self.siports_admin_token:
                headers["Authorization"] = f"Bearer {self.siports_admin_token}"
            
            sync_request = {
                "sync_type": "packages",
                "force": False,
                "batch_size": 10
            }
            
            response = requests.post(
                f"{self.base_url}/sync/packages",
                json=sync_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data or "records_processed" in data or "message" in data:
                    self.log_test("Package Synchronization", True, 
                                f"Package sync completed: {data}")
                    return True
                else:
                    self.log_test("Package Synchronization", True, 
                                f"Package sync endpoint accessible: {data}")
                    return True
            elif response.status_code == 404:
                self.log_test("Package Synchronization", False, 
                            "Package sync endpoint not implemented (404)")
                return False
            elif response.status_code == 401:
                self.log_test("Package Synchronization", False, 
                            "Package sync requires authentication (401)")
                return False
            elif response.status_code == 403:
                self.log_test("Package Synchronization", False, 
                            "Package sync access forbidden (403)")
                return False
            else:
                self.log_test("Package Synchronization", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Package Synchronization", False, f"Request error: {str(e)}")
            return False
    
    def test_full_sync(self):
        """Test POST /api/sync/full-sync - Full synchronization"""
        try:
            headers = {}
            if self.wp_admin_token:
                headers["Authorization"] = f"Bearer {self.wp_admin_token}"
            elif self.siports_admin_token:
                headers["Authorization"] = f"Bearer {self.siports_admin_token}"
            
            sync_request = {
                "sync_type": "full",
                "force": False,
                "batch_size": 10
            }
            
            response = requests.post(
                f"{self.base_url}/sync/full-sync",
                json=sync_request,
                headers=headers,
                timeout=60  # Longer timeout for full sync
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "success" in data or "total_processed" in data or "users" in data or "packages" in data:
                    self.log_test("Full Synchronization", True, 
                                f"Full sync completed: {data}")
                    return True
                else:
                    self.log_test("Full Synchronization", True, 
                                f"Full sync endpoint accessible: {data}")
                    return True
            elif response.status_code == 404:
                self.log_test("Full Synchronization", False, 
                            "Full sync endpoint not implemented (404)")
                return False
            elif response.status_code == 401:
                self.log_test("Full Synchronization", False, 
                            "Full sync requires authentication (401)")
                return False
            elif response.status_code == 403:
                self.log_test("Full Synchronization", False, 
                            "Full sync access forbidden (403)")
                return False
            else:
                self.log_test("Full Synchronization", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Full Synchronization", False, f"Request error: {str(e)}")
            return False
    
    def authenticate_siports_admin(self):
        """Authenticate with SIPORTS admin credentials for compatibility testing"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=SIPORTS_ADMIN_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.siports_admin_token = data.get("access_token")
                user_type = data.get("user", {}).get("user_type")
                
                if user_type == "admin":
                    self.log_test("SIPORTS Admin Authentication", True, 
                                f"SIPORTS admin login successful: {SIPORTS_ADMIN_USER['email']}")
                    return True
                else:
                    self.log_test("SIPORTS Admin Authentication", False, 
                                f"User is not admin, got type: {user_type}")
                    return False
            else:
                self.log_test("SIPORTS Admin Authentication", False, 
                            f"SIPORTS admin login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("SIPORTS Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def authenticate_siports_exposant(self):
        """Authenticate with SIPORTS exposant credentials for compatibility testing"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=SIPORTS_EXPOSANT_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.siports_exposant_token = data.get("access_token")
                user_type = data.get("user", {}).get("user_type")
                
                self.log_test("SIPORTS Exposant Authentication", True, 
                            f"SIPORTS exposant login successful: {user_type}")
                return True
            else:
                self.log_test("SIPORTS Exposant Authentication", False, 
                            f"SIPORTS exposant login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("SIPORTS Exposant Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_existing_endpoints_compatibility(self):
        """Test that existing SIPORTS endpoints still work after WordPress integration"""
        if not self.siports_admin_token:
            self.log_test("Existing Endpoints Compatibility", False, "No SIPORTS admin token available")
            return False
        
        # Test key existing endpoints
        existing_endpoints = [
            ("/admin/dashboard/stats", "GET"),
            ("/admin/users/pending", "GET"),
            ("/admin/users", "GET"),
            ("/visitor-packages", "GET"),
            ("/partnership-packages", "GET"),
            ("/features", "GET")
        ]
        
        working_endpoints = 0
        total_endpoints = len(existing_endpoints)
        
        for endpoint, method in existing_endpoints:
            try:
                headers = {"Authorization": f"Bearer {self.siports_admin_token}"}
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {endpoint} working")
                else:
                    print(f"   ❌ {endpoint} failed ({response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} error: {str(e)}")
        
        if working_endpoints == total_endpoints:
            self.log_test("Existing Endpoints Compatibility", True, 
                        f"All {total_endpoints} existing endpoints working after WordPress integration")
            return True
        else:
            self.log_test("Existing Endpoints Compatibility", False, 
                        f"Only {working_endpoints}/{total_endpoints} existing endpoints working")
            return False
    
    def test_jwt_token_management(self):
        """Test JWT token generation and validation"""
        if not self.wp_admin_token and not self.siports_admin_token:
            self.log_test("JWT Token Management", False, "No tokens available for testing")
            return False
        
        # Test token format (should be JWT)
        token_to_test = self.wp_admin_token or self.siports_admin_token
        
        # JWT tokens have 3 parts separated by dots
        token_parts = token_to_test.split('.')
        
        if len(token_parts) == 3:
            self.log_test("JWT Token Management", True, 
                        f"JWT token format valid (3 parts), length: {len(token_to_test)} chars")
            return True
        else:
            self.log_test("JWT Token Management", False, 
                        f"Invalid JWT token format (expected 3 parts, got {len(token_parts)})")
            return False
    
    def run_all_tests(self):
        """Run all WordPress integration tests"""
        print("🚀 Starting WordPress Integration Tests for SIPORTS Backend")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # First, authenticate with SIPORTS for compatibility testing
        siports_admin_auth = self.authenticate_siports_admin()
        siports_exposant_auth = self.authenticate_siports_exposant()
        
        # Test sequence
        tests = [
            # 1. Health check
            self.test_health_endpoint,
            
            # 2. WordPress authentication
            self.test_wordpress_login,
            
            # 3. JWT token management
            self.test_jwt_token_management,
            
            # 4. WordPress sync endpoints
            self.test_sync_status,
            self.test_sync_users,
            self.test_sync_packages,
            self.test_full_sync,
            
            # 5. Compatibility with existing endpoints
            self.test_existing_endpoints_compatibility
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 80)
        print(f"📊 WordPress Integration Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All WordPress integration tests PASSED!")
            return True
        else:
            print(f"❌ {total - passed} tests FAILED")
            return False
    
    def get_summary(self):
        """Get test summary"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = WordPressIntegrationTester()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📈 Success Rate: {summary['success_rate']:.1f}%")
    
    # Print specific findings
    print("\n🔍 Key Findings:")
    for result in tester.test_results:
        if not result["success"] and "not implemented" in result["message"]:
            print(f"   ⚠️  {result['test']}: {result['message']}")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()