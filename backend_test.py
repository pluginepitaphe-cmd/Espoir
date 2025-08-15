#!/usr/bin/env python3
"""
Backend API Tests for SIPORTS Admin Endpoints
Testing the new admin endpoints as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://siports-maritime.preview.emergentagent.com/api"

# Test credentials
ADMIN_USER = {
    "email": "admin@siportevent.com",
    "password": "admin123"
}

EXPOSANT_USER = {
    "email": "exposant@example.com",
    "password": "expo123"
}

VISITEUR_USER = {
    "email": "visiteur@example.com",
    "password": "visit123"
}

class AdminEndpointTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.admin_token = None
        self.admin_user_id = None
        self.non_admin_token = None
        self.non_admin_user_id = None
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
    
    def authenticate_admin(self):
        """Authenticate with admin credentials"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=ADMIN_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.admin_user_id = data.get("user", {}).get("id")
                user_type = data.get("user", {}).get("user_type")
                
                if user_type == "admin":
                    self.log_test("Admin Authentication", True, f"Successfully logged in as admin: {ADMIN_USER['email']}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, f"User is not admin, got type: {user_type}")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def authenticate_non_admin(self):
        """Authenticate with non-admin credentials for access control tests"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=EXPOSANT_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.non_admin_token = data.get("access_token")
                self.non_admin_user_id = data.get("user", {}).get("id")
                user_type = data.get("user", {}).get("user_type")
                
                self.log_test("Non-Admin Authentication", True, f"Successfully logged in as {user_type}: {EXPOSANT_USER['email']}")
                return True
            else:
                self.log_test("Non-Admin Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Non-Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin authentication token"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def get_non_admin_headers(self):
        """Get headers with non-admin authentication token"""
        if not self.non_admin_token:
            return {}
        return {"Authorization": f"Bearer {self.non_admin_token}"}
    
    def test_admin_dashboard_stats(self):
        """Test GET /api/admin/dashboard/stats endpoint"""
        if not self.admin_token:
            self.log_test("Admin Dashboard Stats", False, "No admin authentication token")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/dashboard/stats",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required stats fields
                required_fields = ["total_users", "total_visitors", "total_exhibitors", 
                                 "total_partners", "pending_accounts", "validated_accounts"]
                
                if all(field in data for field in required_fields):
                    stats_summary = f"Users: {data['total_users']}, Visitors: {data['total_visitors']}, Exhibitors: {data['total_exhibitors']}, Partners: {data['total_partners']}"
                    self.log_test("Admin Dashboard Stats", True, 
                                f"Dashboard stats retrieved successfully - {stats_summary}")
                    return True
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_test("Admin Dashboard Stats", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Dashboard Stats", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_users_pending(self):
        """Test GET /api/admin/users/pending endpoint"""
        if not self.admin_token:
            self.log_test("Admin Users Pending", False, "No admin authentication token")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/users/pending",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                if isinstance(users, list):
                    # Check user structure if users exist
                    if users:
                        sample_user = users[0]
                        required_fields = ["id", "email", "first_name", "last_name", "user_type", "created_at"]
                        
                        if all(field in sample_user for field in required_fields):
                            self.log_test("Admin Users Pending", True, 
                                        f"Retrieved {len(users)} pending users with proper structure")
                            return True
                        else:
                            missing_fields = [f for f in required_fields if f not in sample_user]
                            self.log_test("Admin Users Pending", False, 
                                        f"User missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Admin Users Pending", True, 
                                    "Pending users endpoint working (no pending users found)")
                        return True
                else:
                    self.log_test("Admin Users Pending", False, 
                                f"Expected users array, got: {type(users)}")
                    return False
            else:
                self.log_test("Admin Users Pending", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Users Pending", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_validate_user(self):
        """Test POST /api/admin/users/{id}/validate endpoint"""
        if not self.admin_token:
            self.log_test("Admin Validate User", False, "No admin authentication token")
            return False
            
        try:
            # Use exposant user ID (2) for validation test
            user_id = 2
            
            response = requests.post(
                f"{self.base_url}/admin/users/{user_id}/validate",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "user_id" in data and "action" in data:
                    if data["action"] == "validated" and data["user_id"] == user_id:
                        self.log_test("Admin Validate User", True, 
                                    f"Successfully validated user ID {user_id}: {data['message']}")
                        return True
                    else:
                        self.log_test("Admin Validate User", False, 
                                    f"Unexpected validation response: {data}")
                        return False
                else:
                    self.log_test("Admin Validate User", False, 
                                f"Missing required response fields: {data}")
                    return False
            else:
                self.log_test("Admin Validate User", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Validate User", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_reject_user(self):
        """Test POST /api/admin/users/{id}/reject endpoint"""
        if not self.admin_token:
            self.log_test("Admin Reject User", False, "No admin authentication token")
            return False
            
        try:
            # Use visiteur user ID (3) for rejection test
            user_id = 3
            
            response = requests.post(
                f"{self.base_url}/admin/users/{user_id}/reject",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "user_id" in data and "action" in data:
                    if data["action"] == "rejected" and data["user_id"] == user_id:
                        self.log_test("Admin Reject User", True, 
                                    f"Successfully rejected user ID {user_id}: {data['message']}")
                        return True
                    else:
                        self.log_test("Admin Reject User", False, 
                                    f"Unexpected rejection response: {data}")
                        return False
                else:
                    self.log_test("Admin Reject User", False, 
                                f"Missing required response fields: {data}")
                    return False
            else:
                self.log_test("Admin Reject User", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Reject User", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_get_all_users(self):
        """Test GET /api/admin/users endpoint"""
        if not self.admin_token:
            self.log_test("Admin Get All Users", False, "No admin authentication token")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/users",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                if isinstance(users, list):
                    # Check user structure if users exist
                    if users:
                        sample_user = users[0]
                        required_fields = ["id", "email", "first_name", "last_name", "user_type", "created_at"]
                        
                        if all(field in sample_user for field in required_fields):
                            # Count users by type
                            user_types = {}
                            for user in users:
                                user_type = user.get("user_type", "unknown")
                                user_types[user_type] = user_types.get(user_type, 0) + 1
                            
                            type_summary = ", ".join([f"{k}: {v}" for k, v in user_types.items()])
                            self.log_test("Admin Get All Users", True, 
                                        f"Retrieved {len(users)} users - {type_summary}")
                            return True
                        else:
                            missing_fields = [f for f in required_fields if f not in sample_user]
                            self.log_test("Admin Get All Users", False, 
                                        f"User missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Admin Get All Users", True, 
                                    "All users endpoint working (no users found)")
                        return True
                else:
                    self.log_test("Admin Get All Users", False, 
                                f"Expected users array, got: {type(users)}")
                    return False
            else:
                self.log_test("Admin Get All Users", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Get All Users", False, f"Request error: {str(e)}")
            return False
    
    def test_non_admin_access_control(self):
        """Test that non-admin users cannot access admin endpoints"""
        if not self.non_admin_token:
            self.log_test("Non-Admin Access Control", False, "No non-admin authentication token")
            return False
        
        # Test all admin endpoints with non-admin token
        admin_endpoints = [
            "/admin/dashboard/stats",
            "/admin/users/pending", 
            "/admin/users"
        ]
        
        blocked_count = 0
        total_endpoints = len(admin_endpoints)
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_non_admin_headers(),
                    timeout=10
                )
                
                if response.status_code == 403:
                    blocked_count += 1
                    print(f"   ✅ {endpoint} correctly blocked (403)")
                else:
                    print(f"   ❌ {endpoint} not blocked (got {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} test error: {str(e)}")
        
        # Test POST endpoints
        post_endpoints = [
            ("/admin/users/2/validate", {}),
            ("/admin/users/3/reject", {})
        ]
        
        for endpoint, data in post_endpoints:
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers=self.get_non_admin_headers(),
                    timeout=10
                )
                
                if response.status_code == 403:
                    blocked_count += 1
                    print(f"   ✅ {endpoint} correctly blocked (403)")
                else:
                    print(f"   ❌ {endpoint} not blocked (got {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} test error: {str(e)}")
        
        total_endpoints += len(post_endpoints)
        
        if blocked_count == total_endpoints:
            self.log_test("Non-Admin Access Control", True, 
                        f"All {total_endpoints} admin endpoints correctly blocked for non-admin users")
            return True
        else:
            self.log_test("Non-Admin Access Control", False, 
                        f"Only {blocked_count}/{total_endpoints} admin endpoints blocked")
            return False
    
    def test_unauthenticated_access_control(self):
        """Test that unauthenticated users cannot access admin endpoints"""
        admin_endpoints = [
            "/admin/dashboard/stats",
            "/admin/users/pending", 
            "/admin/users"
        ]
        
        blocked_count = 0
        total_endpoints = len(admin_endpoints)
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    blocked_count += 1
                    print(f"   ✅ {endpoint} correctly blocked ({response.status_code})")
                else:
                    print(f"   ❌ {endpoint} not blocked (got {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} test error: {str(e)}")
        
        if blocked_count == total_endpoints:
            self.log_test("Unauthenticated Access Control", True, 
                        f"All {total_endpoints} admin endpoints correctly blocked for unauthenticated users")
            return True
        else:
            self.log_test("Unauthenticated Access Control", False, 
                        f"Only {blocked_count}/{total_endpoints} admin endpoints blocked")
            return False
    
    def run_all_tests(self):
        """Run all admin endpoint tests"""
        print("🚀 Starting Backend API Tests for SIPORTS Admin Endpoints")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # First authenticate as admin
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot proceed with admin tests")
            return False
        
        # Authenticate as non-admin for access control tests
        if not self.authenticate_non_admin():
            print("⚠️  Non-admin authentication failed - skipping access control tests")
        
        # Test all admin endpoints
        admin_tests = [
            self.test_admin_dashboard_stats,
            self.test_admin_users_pending,
            self.test_admin_validate_user,
            self.test_admin_reject_user,
            self.test_admin_get_all_users
        ]
        
        # Access control tests
        access_control_tests = [
            self.test_unauthenticated_access_control
        ]
        
        if self.non_admin_token:
            access_control_tests.append(self.test_non_admin_access_control)
        
        all_tests = admin_tests + access_control_tests
        
        passed = 0
        total = len(all_tests)
        
        for test in all_tests:
            if test():
                passed += 1
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All admin endpoint tests PASSED!")
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
    tester = AdminEndpointTester()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📈 Success Rate: {summary['success_rate']:.1f}%")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()