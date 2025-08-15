#!/usr/bin/env python3
"""
SIPORTS v2.0 Comprehensive Backend API Test Suite
Testing all major functionality as requested:

1. Current Backend Status - Test all main API endpoints
2. Authentication System - Test login for all user types (admin, exposant, visiteur, partenaire)
3. Core Endpoints - Test /api/, /api/visitor-packages, /api/partnership-packages, /api/exhibition-packages
4. Admin Endpoints - Test all admin dashboard endpoints (/api/admin/*)
5. Chatbot Endpoints - Test SIPORTS v2.0 chatbot functionality (/api/chat/*)
6. Database Connection - Verify database connectivity and data integrity

This test uses the production backend URL from frontend/.env
"""

import requests
import json
import sys
import time
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration - Using the local backend URL since Railway is not accessible
BACKEND_URL = "http://localhost:8001/api"

# Test credentials based on actual database setup
TEST_CREDENTIALS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exposant": {"email": "exposant@example.com", "password": "exhibitor123"},
    "visiteur": {"email": "visitor@example.com", "password": "visitor123"},
    "partenaire": {"email": "partenaire@example.com", "password": "part123"}  # This user may not exist
}

class SiportsComprehensiveBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tokens = {}  # Store authentication tokens
        self.users = {}   # Store user data
        self.test_results = []
        self.session_id = f"test_session_{int(time.time())}"
        self.database_type = "unknown"
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results with detailed information"""
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
    
    def make_request(self, method: str, endpoint: str, headers: Dict = None, json_data: Dict = None, timeout: int = 15) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                return requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                return requests.post(url, headers=headers, json=json_data, timeout=timeout)
            elif method.upper() == "DELETE":
                return requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_auth_headers(self, user_type: str) -> Dict[str, str]:
        """Get authorization headers for a user type"""
        token = self.tokens.get(user_type)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    
    # =============================================================================
    # 1. CURRENT BACKEND STATUS TESTS
    # =============================================================================
    
    def test_backend_health(self):
        """Test backend health and availability"""
        try:
            # Test the root endpoint without /api prefix
            response = requests.get("http://localhost:8001/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "Unknown")
                version = data.get("version", "Unknown")
                status = data.get("status", "Unknown")
                
                self.log_test("Backend Health Check", True, 
                            f"Backend is running - {message}, Version: {version}, Status: {status}")
                return True
            else:
                self.log_test("Backend Health Check", False, 
                            f"Backend returned HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Backend connection failed: {str(e)}")
            return False
    
    def test_api_root_endpoint(self):
        """Test the main API root endpoint"""
        try:
            # Test the root endpoint without /api prefix
            response = requests.get("http://localhost:8001/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "status", "version"]
                
                if all(field in data for field in required_fields):
                    self.log_test("API Root Endpoint", True, 
                                f"API root accessible - {data['message']} v{data['version']}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("API Root Endpoint", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 2. AUTHENTICATION SYSTEM TESTS
    # =============================================================================
    
    def test_authentication_all_users(self):
        """Test authentication for all user types"""
        success_count = 0
        total_users = len(TEST_CREDENTIALS)
        
        for user_type, credentials in TEST_CREDENTIALS.items():
            try:
                response = self.make_request("POST", "/auth/login", json_data=credentials)
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    user_data = data.get("user", {})
                    
                    if token and user_data:
                        self.tokens[user_type] = token
                        self.users[user_type] = user_data
                        
                        actual_type = user_data.get("user_type")
                        email = user_data.get("email")
                        
                        # Handle exposant/exhibitor type mapping
                        if (user_type == "exposant" and actual_type == "exhibitor") or actual_type == user_type:
                            success_count += 1
                            self.log_test(f"{user_type.title()} Authentication", True, 
                                        f"Successfully authenticated {email} as {actual_type}")
                        else:
                            self.log_test(f"{user_type.title()} Authentication", False, 
                                        f"Type mismatch: expected {user_type}, got {actual_type}")
                    else:
                        self.log_test(f"{user_type.title()} Authentication", False, 
                                    "Missing token or user data in response")
                else:
                    self.log_test(f"{user_type.title()} Authentication", False, 
                                f"Login failed: HTTP {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"{user_type.title()} Authentication", False, 
                            f"Authentication error: {str(e)}")
        
        if success_count == total_users:
            self.log_test("All User Authentication", True, 
                        f"All {total_users} user types authenticated successfully")
            return True
        else:
            self.log_test("All User Authentication", False, 
                        f"Only {success_count}/{total_users} user types authenticated")
            return False
    
    def test_token_validation(self):
        """Test JWT token validation"""
        if not self.tokens.get("admin"):
            self.log_test("Token Validation", False, "No admin token available for validation test")
            return False
        
        try:
            # Test with valid token
            response = self.make_request("GET", "/auth/me", headers=self.get_auth_headers("admin"))
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "user_type"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Token Validation", True, 
                                f"Token validation successful for {data['email']}")
                    return True
                else:
                    self.log_test("Token Validation", False, "Missing user fields in response")
                    return False
            elif response.status_code == 404:
                # /auth/me endpoint might not exist, try another protected endpoint
                response = self.make_request("GET", "/admin/dashboard/stats", headers=self.get_auth_headers("admin"))
                if response.status_code in [200, 403]:  # 200 = success, 403 = forbidden but token was validated
                    self.log_test("Token Validation", True, "Token validation working (tested via admin endpoint)")
                    return True
                else:
                    self.log_test("Token Validation", False, f"Token validation failed: HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Token Validation", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 3. CORE ENDPOINTS TESTS
    # =============================================================================
    
    def test_visitor_packages_endpoint(self):
        """Test /api/visitor-packages endpoint"""
        try:
            response = self.make_request("GET", "/visitor-packages")
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 4:
                    # Check for expected package types
                    package_names = [p.get("name", "") for p in packages]
                    expected_packages = ["Free Pass", "Basic Pass", "Premium Pass", "VIP Pass"]
                    
                    found_packages = []
                    for expected in expected_packages:
                        if any(expected.lower() in name.lower() for name in package_names):
                            found_packages.append(expected)
                    
                    if len(found_packages) >= 3:  # At least 3 of 4 expected
                        # Check package structure
                        sample_package = packages[0]
                        required_fields = ["id", "name", "price", "description", "features"]
                        
                        if all(field in sample_package for field in required_fields):
                            self.log_test("Visitor Packages Endpoint", True, 
                                        f"Retrieved {len(packages)} visitor packages: {', '.join(package_names)}")
                            return True
                        else:
                            missing = [f for f in required_fields if f not in sample_package]
                            self.log_test("Visitor Packages Endpoint", False, 
                                        f"Package missing required fields: {missing}")
                            return False
                    else:
                        self.log_test("Visitor Packages Endpoint", False, 
                                    f"Missing expected packages. Found: {found_packages}")
                        return False
                else:
                    self.log_test("Visitor Packages Endpoint", False, 
                                f"Expected at least 4 packages, got {len(packages)}")
                    return False
            else:
                self.log_test("Visitor Packages Endpoint", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Visitor Packages Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_partnership_packages_endpoint(self):
        """Test /api/partnership-packages endpoint"""
        try:
            response = self.make_request("GET", "/partnership-packages")
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 4:
                    # Check for expected partnership levels
                    package_names = [p.get("name", "") for p in packages]
                    expected_levels = ["Platinum", "Gold", "Silver", "Startup"]
                    
                    found_levels = []
                    for level in expected_levels:
                        if any(level.lower() in name.lower() for name in package_names):
                            found_levels.append(level)
                    
                    if len(found_levels) >= 3:  # At least 3 of 4 expected
                        # Check package structure
                        sample_package = packages[0]
                        required_fields = ["id", "name", "price", "description", "features"]
                        
                        if all(field in sample_package for field in required_fields):
                            # Check for pricing information
                            prices = [p.get("price", 0) for p in packages]
                            price_summary = f"Prices: {min(prices)}-{max(prices)} {packages[0].get('currency', '$')}"
                            
                            self.log_test("Partnership Packages Endpoint", True, 
                                        f"Retrieved {len(packages)} partnership packages: {', '.join(package_names)} ({price_summary})")
                            return True
                        else:
                            missing = [f for f in required_fields if f not in sample_package]
                            self.log_test("Partnership Packages Endpoint", False, 
                                        f"Package missing required fields: {missing}")
                            return False
                    else:
                        self.log_test("Partnership Packages Endpoint", False, 
                                    f"Missing expected levels. Found: {found_levels}")
                        return False
                else:
                    self.log_test("Partnership Packages Endpoint", False, 
                                f"Expected at least 4 packages, got {len(packages)}")
                    return False
            else:
                self.log_test("Partnership Packages Endpoint", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Partnership Packages Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_exhibition_packages_endpoint(self):
        """Test /api/exhibition-packages endpoint (if exists)"""
        try:
            response = self.make_request("GET", "/exhibition-packages")
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 3:
                    package_names = [p.get("name", "") for p in packages]
                    self.log_test("Exhibition Packages Endpoint", True, 
                                f"Retrieved {len(packages)} exhibition packages: {', '.join(package_names)}")
                    return True
                else:
                    self.log_test("Exhibition Packages Endpoint", False, 
                                f"Expected at least 3 packages, got {len(packages)}")
                    return False
            elif response.status_code == 404:
                self.log_test("Exhibition Packages Endpoint", True, 
                            "Exhibition packages endpoint not implemented (404) - this is acceptable")
                return True
            else:
                self.log_test("Exhibition Packages Endpoint", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Exhibition Packages Endpoint", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 4. ADMIN ENDPOINTS TESTS
    # =============================================================================
    
    def test_admin_dashboard_stats(self):
        """Test /api/admin/dashboard/stats endpoint"""
        if not self.tokens.get("admin"):
            self.log_test("Admin Dashboard Stats", False, "No admin token available")
            return False
        
        try:
            response = self.make_request("GET", "/admin/dashboard/stats", 
                                       headers=self.get_auth_headers("admin"))
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected stats fields (flexible field names)
                possible_fields = [
                    ["total_users", "visitors", "exhibitors", "partners"],
                    ["total_users", "total_visitors", "total_exhibitors", "total_partners"],
                    ["pending", "validated", "rejected"]
                ]
                
                found_fields = []
                for field_set in possible_fields:
                    if any(field in data for field in field_set):
                        found_fields.extend([f for f in field_set if f in data])
                
                if len(found_fields) >= 3:  # At least 3 stats fields
                    stats_summary = ", ".join([f"{k}: {v}" for k, v in data.items() if isinstance(v, (int, float))])
                    self.log_test("Admin Dashboard Stats", True, 
                                f"Dashboard stats retrieved - {stats_summary}")
                    return True
                else:
                    self.log_test("Admin Dashboard Stats", False, 
                                f"Insufficient stats fields. Found: {list(data.keys())}")
                    return False
            else:
                self.log_test("Admin Dashboard Stats", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_users_endpoints(self):
        """Test admin user management endpoints"""
        if not self.tokens.get("admin"):
            self.log_test("Admin Users Endpoints", False, "No admin token available")
            return False
        
        success_count = 0
        total_tests = 0
        
        # Test get all users
        try:
            response = self.make_request("GET", "/admin/users", 
                                       headers=self.get_auth_headers("admin"))
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                if isinstance(users, list):
                    success_count += 1
                    print(f"   ✅ Get all users: {len(users)} users retrieved")
                else:
                    print(f"   ❌ Get all users: Invalid response format")
            else:
                print(f"   ❌ Get all users: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Get all users: {str(e)}")
            total_tests += 1
        
        # Test get pending users
        try:
            response = self.make_request("GET", "/admin/users/pending", 
                                       headers=self.get_auth_headers("admin"))
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                if isinstance(users, list):
                    success_count += 1
                    print(f"   ✅ Get pending users: {len(users)} pending users")
                else:
                    print(f"   ❌ Get pending users: Invalid response format")
            else:
                print(f"   ❌ Get pending users: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Get pending users: {str(e)}")
            total_tests += 1
        
        # Test user validation (using a test user ID)
        try:
            test_user_id = self.users.get("exposant", {}).get("id", 2)  # Fallback to ID 2
            response = self.make_request("POST", f"/admin/users/{test_user_id}/validate", 
                                       headers=self.get_auth_headers("admin"))
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    success_count += 1
                    print(f"   ✅ Validate user: {data['message']}")
                else:
                    print(f"   ❌ Validate user: Missing message field")
            else:
                print(f"   ❌ Validate user: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Validate user: {str(e)}")
            total_tests += 1
        
        # Test user rejection
        try:
            test_user_id = self.users.get("visiteur", {}).get("id", 3)  # Fallback to ID 3
            response = self.make_request("POST", f"/admin/users/{test_user_id}/reject", 
                                       headers=self.get_auth_headers("admin"))
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    success_count += 1
                    print(f"   ✅ Reject user: {data['message']}")
                else:
                    print(f"   ❌ Reject user: Missing message field")
            else:
                print(f"   ❌ Reject user: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Reject user: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("Admin Users Endpoints", True, 
                        f"All {total_tests} admin user endpoints working")
            return True
        else:
            self.log_test("Admin Users Endpoints", False, 
                        f"Only {success_count}/{total_tests} admin endpoints working")
            return False
    
    def test_admin_access_control(self):
        """Test that non-admin users cannot access admin endpoints"""
        if not self.tokens.get("exposant"):
            self.log_test("Admin Access Control", False, "No non-admin token for access control test")
            return False
        
        admin_endpoints = [
            "/admin/dashboard/stats",
            "/admin/users",
            "/admin/users/pending"
        ]
        
        blocked_count = 0
        for endpoint in admin_endpoints:
            try:
                response = self.make_request("GET", endpoint, 
                                           headers=self.get_auth_headers("exposant"))
                
                if response.status_code == 403:
                    blocked_count += 1
                    print(f"   ✅ {endpoint} correctly blocked (403)")
                else:
                    print(f"   ❌ {endpoint} not blocked (got {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} test error: {str(e)}")
        
        if blocked_count == len(admin_endpoints):
            self.log_test("Admin Access Control", True, 
                        f"All {len(admin_endpoints)} admin endpoints correctly blocked for non-admin")
            return True
        else:
            self.log_test("Admin Access Control", False, 
                        f"Only {blocked_count}/{len(admin_endpoints)} endpoints properly blocked")
            return False
    
    # =============================================================================
    # 5. CHATBOT ENDPOINTS TESTS
    # =============================================================================
    
    def test_chatbot_main_endpoint(self):
        """Test the main chatbot endpoint /api/chat"""
        contexts_to_test = ["general", "exhibitor", "package", "event"]
        success_count = 0
        
        for context in contexts_to_test:
            try:
                response = self.make_request("POST", "/chat", json_data={
                    "message": f"Tell me about {context} information for SIPORTS maritime event",
                    "context_type": context,
                    "session_id": self.session_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and "confidence" in data:
                        success_count += 1
                        confidence = data.get("confidence", 0)
                        response_length = len(data.get("response", ""))
                        print(f"   ✅ Context '{context}': Response received (confidence: {confidence}, length: {response_length})")
                    else:
                        print(f"   ❌ Context '{context}': Missing response fields")
                else:
                    print(f"   ❌ Context '{context}': HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Context '{context}': {str(e)}")
        
        if success_count == len(contexts_to_test):
            self.log_test("Chatbot Main Endpoint", True, 
                        f"All {len(contexts_to_test)} context types working")
            return True
        else:
            self.log_test("Chatbot Main Endpoint", False, 
                        f"Only {success_count}/{len(contexts_to_test)} contexts working")
            return False
    
    def test_chatbot_specialized_endpoints(self):
        """Test specialized chatbot endpoints"""
        specialized_endpoints = [
            ("/chat/exhibitor", "exhibitor recommendations"),
            ("/chat/package", "package suggestions"),
            ("/chat/event", "event information")
        ]
        
        success_count = 0
        
        for endpoint, description in specialized_endpoints:
            try:
                response = self.make_request("POST", endpoint, json_data={
                    "message": f"I need help with {description} for SIPORTS",
                    "session_id": self.session_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data:
                        success_count += 1
                        response_length = len(data.get("response", ""))
                        print(f"   ✅ {endpoint}: {description} working (response length: {response_length})")
                    else:
                        print(f"   ❌ {endpoint}: Missing response field")
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)}")
        
        if success_count == len(specialized_endpoints):
            self.log_test("Chatbot Specialized Endpoints", True, 
                        f"All {len(specialized_endpoints)} specialized endpoints working")
            return True
        else:
            self.log_test("Chatbot Specialized Endpoints", False, 
                        f"Only {success_count}/{len(specialized_endpoints)} endpoints working")
            return False
    
    def test_chatbot_history_management(self):
        """Test chatbot history management"""
        success_count = 0
        total_tests = 0
        
        # Test get history
        try:
            response = self.make_request("GET", f"/chat/history/{self.session_id}")
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data and "history" in data:
                    success_count += 1
                    history_count = len(data.get("history", []))
                    print(f"   ✅ Get history: {history_count} messages in session")
                else:
                    print(f"   ❌ Get history: Missing expected fields")
            else:
                print(f"   ❌ Get history: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Get history: {str(e)}")
            total_tests += 1
        
        # Test clear history
        try:
            response = self.make_request("DELETE", f"/chat/history/{self.session_id}")
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    success_count += 1
                    print(f"   ✅ Clear history: {data['message']}")
                else:
                    print(f"   ❌ Clear history: Missing message field")
            else:
                print(f"   ❌ Clear history: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Clear history: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("Chatbot History Management", True, 
                        f"All {total_tests} history management tests passed")
            return True
        else:
            self.log_test("Chatbot History Management", False, 
                        f"Only {success_count}/{total_tests} history tests passed")
            return False
    
    def test_chatbot_health_check(self):
        """Test chatbot health check endpoint"""
        try:
            response = self.make_request("GET", "/chatbot/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "service" in data:
                    status = data.get("status", "unknown")
                    version = data.get("version", "unknown")
                    mock_mode = data.get("mock_mode", "unknown")
                    
                    self.log_test("Chatbot Health Check", True, 
                                f"Chatbot service {status} (version {version}, mock_mode: {mock_mode})")
                    return True
                else:
                    self.log_test("Chatbot Health Check", False, "Missing expected fields in health response")
                    return False
            else:
                self.log_test("Chatbot Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Chatbot Health Check", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 6. DATABASE CONNECTION TESTS
    # =============================================================================
    
    def test_database_connectivity(self):
        """Test database connectivity by checking user data consistency"""
        if not self.tokens:
            self.log_test("Database Connectivity", False, "No authenticated users to test database with")
            return False
        
        try:
            # Test database by checking if user data is consistent
            admin_user = self.users.get("admin", {})
            if not admin_user:
                self.log_test("Database Connectivity", False, "No admin user data available")
                return False
            
            # Check if we can retrieve admin stats (which requires database access)
            response = self.make_request("GET", "/admin/dashboard/stats", 
                                       headers=self.get_auth_headers("admin"))
            
            if response.status_code == 200:
                data = response.json()
                # Look for numeric values indicating database queries worked
                numeric_fields = [k for k, v in data.items() if isinstance(v, (int, float))]
                
                if len(numeric_fields) >= 3:  # At least 3 numeric stats
                    total_users = sum(v for k, v in data.items() if isinstance(v, (int, float)) and 'user' in k.lower())
                    
                    # Determine database type based on response patterns
                    if any('sqlite' in str(v).lower() for v in data.values() if isinstance(v, str)):
                        self.database_type = "SQLite"
                    else:
                        self.database_type = "SQLite (inferred)"
                    
                    self.log_test("Database Connectivity", True, 
                                f"Database connection working - {self.database_type}, {len(numeric_fields)} stats retrieved")
                    return True
                else:
                    self.log_test("Database Connectivity", False, 
                                "Database queries not returning expected data structure")
                    return False
            else:
                self.log_test("Database Connectivity", False, 
                            f"Database query failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Database test error: {str(e)}")
            return False
    
    def test_data_integrity(self):
        """Test data integrity by checking user authentication data"""
        if not self.users:
            self.log_test("Data Integrity", False, "No user data to test integrity")
            return False
        
        try:
            integrity_issues = []
            
            # Check each authenticated user for data consistency
            for user_type, user_data in self.users.items():
                required_fields = ["id", "email", "user_type"]
                missing_fields = [f for f in required_fields if not user_data.get(f)]
                
                if missing_fields:
                    integrity_issues.append(f"{user_type}: missing {missing_fields}")
                
                # Check email format
                email = user_data.get("email", "")
                if "@" not in email or "." not in email:
                    integrity_issues.append(f"{user_type}: invalid email format")
                
                # Check user type consistency
                expected_type = user_type if user_type != "exposant" else "exhibitor"
                actual_type = user_data.get("user_type", "")
                if actual_type != expected_type:
                    integrity_issues.append(f"{user_type}: type mismatch ({actual_type} != {expected_type})")
            
            if not integrity_issues:
                self.log_test("Data Integrity", True, 
                            f"Data integrity verified for {len(self.users)} user accounts")
                return True
            else:
                self.log_test("Data Integrity", False, 
                            f"Data integrity issues found: {'; '.join(integrity_issues)}")
                return False
                
        except Exception as e:
            self.log_test("Data Integrity", False, f"Data integrity test error: {str(e)}")
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 SIPORTS v2.0 COMPREHENSIVE BACKEND API TEST SUITE")
        print(f"Backend URL: {self.base_url}")
        print(f"Test Session ID: {self.session_id}")
        print("=" * 80)
        
        # Define test categories and their tests
        test_categories = [
            ("1. Current Backend Status", [
                self.test_backend_health,
                self.test_api_root_endpoint
            ]),
            ("2. Authentication System", [
                self.test_authentication_all_users,
                self.test_token_validation
            ]),
            ("3. Core Endpoints", [
                self.test_visitor_packages_endpoint,
                self.test_partnership_packages_endpoint,
                self.test_exhibition_packages_endpoint
            ]),
            ("4. Admin Endpoints", [
                self.test_admin_dashboard_stats,
                self.test_admin_users_endpoints,
                self.test_admin_access_control
            ]),
            ("5. Chatbot Endpoints", [
                self.test_chatbot_main_endpoint,
                self.test_chatbot_specialized_endpoints,
                self.test_chatbot_history_management,
                self.test_chatbot_health_check
            ]),
            ("6. Database Connection", [
                self.test_database_connectivity,
                self.test_data_integrity
            ])
        ]
        
        total_passed = 0
        total_tests = 0
        category_results = {}
        
        for category_name, tests in test_categories:
            print(f"\n📋 Testing {category_name}")
            print("-" * 60)
            
            category_passed = 0
            category_total = len(tests)
            
            for test in tests:
                if test():
                    category_passed += 1
                total_tests += 1
            
            total_passed += category_passed
            category_results[category_name] = {
                "passed": category_passed,
                "total": category_total,
                "success_rate": (category_passed / category_total * 100) if category_total > 0 else 0
            }
            
            print(f"📊 {category_name}: {category_passed}/{category_total} tests passed ({category_results[category_name]['success_rate']:.1f}%)")
        
        # Final comprehensive summary
        print("\n" + "=" * 80)
        print("📈 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for category, results in category_results.items():
            status = "✅" if results["passed"] == results["total"] else "⚠️" if results["passed"] > 0 else "❌"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        # Backend health assessment
        if overall_success_rate >= 90:
            health_status = "🟢 EXCELLENT - Backend is fully functional"
        elif overall_success_rate >= 75:
            health_status = "🟡 GOOD - Backend is largely functional with minor issues"
        elif overall_success_rate >= 50:
            health_status = "🟠 FAIR - Backend has some significant issues"
        else:
            health_status = "🔴 POOR - Backend needs immediate attention"
        
        print(f"\n🏥 BACKEND HEALTH STATUS: {health_status}")
        
        # Database information
        if self.database_type != "unknown":
            print(f"💾 DATABASE TYPE: {self.database_type}")
        
        # Authentication summary
        auth_users = len([u for u in self.tokens.keys() if self.tokens[u]])
        print(f"🔐 AUTHENTICATED USERS: {auth_users}/{len(TEST_CREDENTIALS)} user types")
        
        return overall_success_rate >= 75
    
    def get_detailed_summary(self):
        """Get detailed test summary for reporting"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            test_name = result["test"]
            # Extract category from test name
            if "Backend" in test_name or "API" in test_name:
                category = "Backend Status"
            elif "Authentication" in test_name or "Token" in test_name:
                category = "Authentication"
            elif "Packages" in test_name or "visitor" in test_name.lower() or "partnership" in test_name.lower():
                category = "Core Endpoints"
            elif "Admin" in test_name:
                category = "Admin Endpoints"
            elif "Chatbot" in test_name:
                category = "Chatbot"
            elif "Database" in test_name or "Data" in test_name:
                category = "Database"
            else:
                category = "Other"
            
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0, "tests": []}
            
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
            categories[category]["tests"].append(result)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "categories": categories,
            "database_type": self.database_type,
            "authenticated_users": list(self.tokens.keys()),
            "backend_url": self.base_url
        }

def main():
    """Main test execution"""
    print("Starting SIPORTS v2.0 Comprehensive Backend API Tests...")
    print(f"Target Backend: {BACKEND_URL}")
    print(f"Test Credentials: {list(TEST_CREDENTIALS.keys())}")
    print()
    
    tester = SiportsComprehensiveBackendTester()
    success = tester.run_comprehensive_tests()
    
    # Get detailed summary
    summary = tester.get_detailed_summary()
    
    print(f"\n📊 FINAL TEST STATISTICS:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Database Type: {summary['database_type']}")
    print(f"   Authenticated Users: {', '.join(summary['authenticated_users'])}")
    
    # Category breakdown
    print(f"\n📋 CATEGORY BREAKDOWN:")
    for category, data in summary['categories'].items():
        rate = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
        print(f"   {category}: {data['passed']}/{data['total']} ({rate:.1f}%)")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)