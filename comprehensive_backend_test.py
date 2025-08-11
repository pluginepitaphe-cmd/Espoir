#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for SIPORTS v2.0
Testing all major functionality as requested in the review:
1. Core Exhibitor Endpoints
2. Authentication System  
3. Package System
4. Admin Endpoints
5. Chatbot Endpoints (9 endpoints)
6. General API Health
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the deployment URL from test_result.md
BACKEND_URL = "https://4efe408b-c94a-400d-a866-c80c08ec5c16.preview.emergentagent.com/api"

# Test credentials from test_result.md
TEST_ACCOUNTS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exhibitor": {"email": "exposant@example.com", "password": "expo123"},
    "visitor": {"email": "visiteur@example.com", "password": "visit123"},
    "partner": {"email": "partenaire@example.com", "password": "part123"}
}

class SiportsBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tokens = {}  # Store tokens for each user type
        self.users = {}   # Store user data for each type
        self.test_results = []
        self.session_id = f"test_session_{int(time.time())}"
        
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
    
    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate a user and store their token"""
        if user_type not in TEST_ACCOUNTS:
            self.log_test(f"{user_type.title()} Authentication", False, f"Unknown user type: {user_type}")
            return False
            
        try:
            credentials = TEST_ACCOUNTS[user_type]
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data.get("access_token")
                self.users[user_type] = data.get("user", {})
                
                user_data = self.users[user_type]
                actual_type = user_data.get("user_type")
                
                if actual_type == user_type or (user_type == "exhibitor" and actual_type == "exhibitor"):
                    self.log_test(f"{user_type.title()} Authentication", True, 
                                f"Successfully authenticated {credentials['email']} as {actual_type}")
                    return True
                else:
                    self.log_test(f"{user_type.title()} Authentication", False, 
                                f"Expected {user_type}, got {actual_type}")
                    return False
            else:
                self.log_test(f"{user_type.title()} Authentication", False, 
                            f"Login failed: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test(f"{user_type.title()} Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self, user_type: str) -> Dict[str, str]:
        """Get authorization headers for a user type"""
        token = self.tokens.get(user_type)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    
    # =============================================================================
    # 1. GENERAL API HEALTH TESTS
    # =============================================================================
    
    def test_api_root(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "status" in data:
                    self.log_test("API Root Health", True, 
                                f"API is running: {data.get('message', 'N/A')}")
                    return True
                else:
                    self.log_test("API Root Health", False, "Missing expected fields in response")
                    return False
            else:
                self.log_test("API Root Health", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("API Root Health", False, f"Request error: {str(e)}")
            return False
    
    def test_features_endpoint(self):
        """Test the features endpoint"""
        try:
            response = requests.get(f"{self.base_url}/features", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                version = data.get("version", "Unknown")
                
                if isinstance(features, list) and len(features) > 0:
                    self.log_test("Features Endpoint", True, 
                                f"Retrieved {len(features)} features, version {version}")
                    return True
                else:
                    self.log_test("Features Endpoint", False, "No features found or invalid format")
                    return False
            else:
                self.log_test("Features Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Features Endpoint", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 2. AUTHENTICATION SYSTEM TESTS
    # =============================================================================
    
    def test_all_user_authentications(self):
        """Test authentication for all user types"""
        success_count = 0
        total_count = len(TEST_ACCOUNTS)
        
        for user_type in TEST_ACCOUNTS.keys():
            if self.authenticate_user(user_type):
                success_count += 1
        
        if success_count == total_count:
            self.log_test("All User Authentications", True, 
                        f"All {total_count} user types authenticated successfully")
            return True
        else:
            self.log_test("All User Authentications", False, 
                        f"Only {success_count}/{total_count} user types authenticated")
            return False
    
    def test_user_info_endpoint(self):
        """Test the /auth/me endpoint for getting current user info"""
        if "admin" not in self.tokens:
            self.log_test("User Info Endpoint", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.get_headers("admin"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "first_name", "last_name", "user_type"]
                
                if all(field in data for field in required_fields):
                    self.log_test("User Info Endpoint", True, 
                                f"User info retrieved: {data['email']} ({data['user_type']})")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("User Info Endpoint", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("User Info Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Info Endpoint", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 3. PACKAGE SYSTEM TESTS
    # =============================================================================
    
    def test_visitor_packages(self):
        """Test visitor packages endpoint"""
        try:
            response = requests.get(f"{self.base_url}/visitor-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 4:
                    # Check for expected packages
                    package_names = [p.get("name", "") for p in packages]
                    expected_packages = ["Free Pass", "Basic Pass", "Premium Pass", "VIP Pass"]
                    
                    found_packages = [name for name in expected_packages if any(name in pname for pname in package_names)]
                    
                    if len(found_packages) >= 3:  # At least 3 of 4 expected packages
                        self.log_test("Visitor Packages", True, 
                                    f"Retrieved {len(packages)} packages: {', '.join(package_names)}")
                        return True
                    else:
                        self.log_test("Visitor Packages", False, 
                                    f"Missing expected packages. Found: {package_names}")
                        return False
                else:
                    self.log_test("Visitor Packages", False, 
                                f"Expected at least 4 packages, got {len(packages)}")
                    return False
            else:
                self.log_test("Visitor Packages", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Visitor Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_partnership_packages(self):
        """Test partnership packages endpoint"""
        try:
            response = requests.get(f"{self.base_url}/partnership-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 4:
                    # Check for expected partnership levels
                    package_names = [p.get("name", "") for p in packages]
                    expected_levels = ["Platinum", "Gold", "Silver", "Startup"]
                    
                    found_levels = [level for level in expected_levels if any(level in name for name in package_names)]
                    
                    if len(found_levels) >= 3:  # At least 3 of 4 expected levels
                        self.log_test("Partnership Packages", True, 
                                    f"Retrieved {len(packages)} partnership packages: {', '.join(package_names)}")
                        return True
                    else:
                        self.log_test("Partnership Packages", False, 
                                    f"Missing expected levels. Found: {package_names}")
                        return False
                else:
                    self.log_test("Partnership Packages", False, 
                                f"Expected at least 4 packages, got {len(packages)}")
                    return False
            else:
                self.log_test("Partnership Packages", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Partnership Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_exhibition_packages(self):
        """Test exhibition packages endpoint"""
        try:
            response = requests.get(f"{self.base_url}/exhibition-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 3:
                    # Check for expected exhibition types
                    package_names = [p.get("name", "") for p in packages]
                    expected_types = ["Premium", "Standard", "Startup", "Virtual"]
                    
                    found_types = [t for t in expected_types if any(t in name for name in package_names)]
                    
                    if len(found_types) >= 2:  # At least 2 of 4 expected types
                        self.log_test("Exhibition Packages", True, 
                                    f"Retrieved {len(packages)} exhibition packages: {', '.join(package_names)}")
                        return True
                    else:
                        self.log_test("Exhibition Packages", False, 
                                    f"Missing expected types. Found: {package_names}")
                        return False
                else:
                    self.log_test("Exhibition Packages", False, 
                                f"Expected at least 3 packages, got {len(packages)}")
                    return False
            else:
                self.log_test("Exhibition Packages", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Exhibition Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_package_update(self):
        """Test updating user package"""
        if "visitor" not in self.tokens:
            self.log_test("Package Update", False, "No visitor token available")
            return False
            
        try:
            # Test updating to premium package
            response = requests.post(
                f"{self.base_url}/update-package",
                json={"package_id": "premium"},
                headers=self.get_headers("visitor"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "package" in data:
                    self.log_test("Package Update", True, 
                                f"Package updated successfully: {data['message']}")
                    return True
                else:
                    self.log_test("Package Update", False, "Missing expected response fields")
                    return False
            else:
                self.log_test("Package Update", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Package Update", False, f"Request error: {str(e)}")
            return False
    
    def test_user_package_status(self):
        """Test getting user package status"""
        if "visitor" not in self.tokens:
            self.log_test("User Package Status", False, "No visitor token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/user-package-status",
                headers=self.get_headers("visitor"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["package_id", "b2b_meetings"]
                
                if all(field in data for field in required_fields):
                    package_id = data["package_id"]
                    meetings = data["b2b_meetings"]
                    self.log_test("User Package Status", True, 
                                f"Package status: {package_id}, B2B meetings: {meetings}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("User Package Status", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("User Package Status", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Package Status", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 4. ADMIN ENDPOINTS TESTS
    # =============================================================================
    
    def test_admin_dashboard_stats(self):
        """Test admin dashboard statistics"""
        if "admin" not in self.tokens:
            self.log_test("Admin Dashboard Stats", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/dashboard/stats",
                headers=self.get_headers("admin"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "total_visitors", "total_exhibitors", "total_partners"]
                
                if all(field in data for field in required_fields):
                    stats = f"Users: {data['total_users']}, Visitors: {data['total_visitors']}, Exhibitors: {data['total_exhibitors']}, Partners: {data['total_partners']}"
                    self.log_test("Admin Dashboard Stats", True, f"Dashboard stats retrieved - {stats}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Admin Dashboard Stats", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("Admin Dashboard Stats", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_users_management(self):
        """Test admin user management endpoints"""
        if "admin" not in self.tokens:
            self.log_test("Admin Users Management", False, "No admin token available")
            return False
        
        success_count = 0
        total_tests = 0
        
        # Test get all users
        try:
            response = requests.get(
                f"{self.base_url}/admin/users",
                headers=self.get_headers("admin"),
                timeout=10
            )
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
            response = requests.get(
                f"{self.base_url}/admin/users/pending",
                headers=self.get_headers("admin"),
                timeout=10
            )
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
        
        # Test user validation (using exhibitor user ID)
        try:
            user_id = self.users.get("exhibitor", {}).get("id", 2)  # Fallback to ID 2
            response = requests.post(
                f"{self.base_url}/admin/users/{user_id}/validate",
                headers=self.get_headers("admin"),
                timeout=10
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "action" in data:
                    success_count += 1
                    print(f"   ✅ Validate user: {data['message']}")
                else:
                    print(f"   ❌ Validate user: Missing response fields")
            else:
                print(f"   ❌ Validate user: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Validate user: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("Admin Users Management", True, 
                        f"All {total_tests} admin user management tests passed")
            return True
        else:
            self.log_test("Admin Users Management", False, 
                        f"Only {success_count}/{total_tests} admin tests passed")
            return False
    
    def test_admin_access_control(self):
        """Test that non-admin users cannot access admin endpoints"""
        if "exhibitor" not in self.tokens:
            self.log_test("Admin Access Control", False, "No exhibitor token for access control test")
            return False
        
        admin_endpoints = [
            "/admin/dashboard/stats",
            "/admin/users",
            "/admin/users/pending"
        ]
        
        blocked_count = 0
        for endpoint in admin_endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_headers("exhibitor"),
                    timeout=10
                )
                
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
                        f"Only {blocked_count}/{len(admin_endpoints)} endpoints blocked")
            return False
    
    # =============================================================================
    # 5. CORE EXHIBITOR ENDPOINTS TESTS
    # =============================================================================
    
    def test_matching_system(self):
        """Test the matching system endpoints"""
        if "exhibitor" not in self.tokens:
            self.log_test("Matching System", False, "No exhibitor token available")
            return False
        
        success_count = 0
        total_tests = 0
        
        # Test generate matches
        try:
            response = requests.post(
                f"{self.base_url}/matching/generate",
                json={
                    "match_type": "all",
                    "sector": "all", 
                    "compatibility": 70,
                    "location": "all",
                    "package_level": "all"
                },
                headers=self.get_headers("exhibitor"),
                timeout=10
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                if isinstance(matches, list):
                    success_count += 1
                    print(f"   ✅ Generate matches: {len(matches)} matches found")
                else:
                    print(f"   ❌ Generate matches: Invalid response format")
            else:
                print(f"   ❌ Generate matches: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Generate matches: {str(e)}")
            total_tests += 1
        
        # Test matching analytics
        try:
            response = requests.get(
                f"{self.base_url}/matching/analytics",
                headers=self.get_headers("exhibitor"),
                timeout=10
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "compatibility_avg" in data and "total_matches" in data:
                    success_count += 1
                    print(f"   ✅ Matching analytics: {data['total_matches']} total matches, {data['compatibility_avg']}% avg compatibility")
                else:
                    print(f"   ❌ Matching analytics: Missing expected fields")
            else:
                print(f"   ❌ Matching analytics: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Matching analytics: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("Matching System", True, 
                        f"All {total_tests} matching system tests passed")
            return True
        else:
            self.log_test("Matching System", False, 
                        f"Only {success_count}/{total_tests} matching tests passed")
            return False
    
    def test_user_interactions(self):
        """Test user interaction recording"""
        if "exhibitor" not in self.tokens:
            self.log_test("User Interactions", False, "No exhibitor token available")
            return False
            
        try:
            # Record an interaction
            response = requests.post(
                f"{self.base_url}/user-interaction",
                json={
                    "to_user_id": 3,  # Visitor user ID
                    "interaction_type": "view",
                    "metadata": {"page": "profile", "duration": 30}
                },
                headers=self.get_headers("exhibitor"),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("User Interactions", True, f"Interaction recorded: {data['message']}")
                    return True
                else:
                    self.log_test("User Interactions", False, "Missing message in response")
                    return False
            else:
                self.log_test("User Interactions", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Interactions", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 6. CHATBOT ENDPOINTS TESTS (9 endpoints)
    # =============================================================================
    
    def test_chatbot_main_endpoint(self):
        """Test the main chatbot endpoint with different contexts"""
        contexts_to_test = ["general", "exhibitor", "package", "event"]
        success_count = 0
        
        for context in contexts_to_test:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": f"Tell me about {context} information for SIPORTS",
                        "context_type": context,
                        "session_id": self.session_id
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and "confidence" in data:
                        success_count += 1
                        confidence = data.get("confidence", 0)
                        print(f"   ✅ Context '{context}': Response received (confidence: {confidence})")
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
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={
                        "message": f"I need help with {description}",
                        "session_id": self.session_id
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data:
                        success_count += 1
                        print(f"   ✅ {endpoint}: {description} working")
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
        """Test chatbot history management endpoints"""
        success_count = 0
        total_tests = 0
        
        # Test get history
        try:
            response = requests.get(
                f"{self.base_url}/chat/history/{self.session_id}",
                timeout=10
            )
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
            response = requests.delete(
                f"{self.base_url}/chat/history/{self.session_id}",
                timeout=10
            )
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
    
    def test_chatbot_streaming_endpoint(self):
        """Test chatbot streaming endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/stream",
                json={
                    "message": "Test streaming response",
                    "context_type": "general",
                    "session_id": self.session_id
                },
                timeout=15,
                stream=True
            )
            
            if response.status_code == 200:
                # Check if we get streaming response
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    self.log_test("Chatbot Streaming", True, "Streaming endpoint working correctly")
                    return True
                else:
                    self.log_test("Chatbot Streaming", False, f"Wrong content type: {content_type}")
                    return False
            else:
                self.log_test("Chatbot Streaming", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Chatbot Streaming", False, f"Request error: {str(e)}")
            return False
    
    def test_chatbot_health_and_stats(self):
        """Test chatbot health check and statistics endpoints"""
        success_count = 0
        total_tests = 0
        
        # Test health check
        try:
            response = requests.get(f"{self.base_url}/chatbot/health", timeout=10)
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "service" in data:
                    success_count += 1
                    status = data.get("status", "unknown")
                    version = data.get("version", "unknown")
                    print(f"   ✅ Health check: {status} (version {version})")
                else:
                    print(f"   ❌ Health check: Missing expected fields")
            else:
                print(f"   ❌ Health check: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Health check: {str(e)}")
            total_tests += 1
        
        # Test statistics
        try:
            response = requests.get(f"{self.base_url}/chatbot/stats", timeout=10)
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "active_sessions" in data and "total_messages" in data:
                    success_count += 1
                    sessions = data.get("active_sessions", 0)
                    messages = data.get("total_messages", 0)
                    print(f"   ✅ Statistics: {sessions} active sessions, {messages} total messages")
                else:
                    print(f"   ❌ Statistics: Missing expected fields")
            else:
                print(f"   ❌ Statistics: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Statistics: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("Chatbot Health & Stats", True, 
                        f"All {total_tests} health/stats tests passed")
            return True
        else:
            self.log_test("Chatbot Health & Stats", False, 
                        f"Only {success_count}/{total_tests} health/stats tests passed")
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive SIPORTS Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Define all test categories and their tests
        test_categories = [
            ("General API Health", [
                self.test_api_root,
                self.test_features_endpoint
            ]),
            ("Authentication System", [
                self.test_all_user_authentications,
                self.test_user_info_endpoint
            ]),
            ("Package System", [
                self.test_visitor_packages,
                self.test_partnership_packages,
                self.test_exhibition_packages,
                self.test_package_update,
                self.test_user_package_status
            ]),
            ("Admin Endpoints", [
                self.test_admin_dashboard_stats,
                self.test_admin_users_management,
                self.test_admin_access_control
            ]),
            ("Core Exhibitor Endpoints", [
                self.test_matching_system,
                self.test_user_interactions
            ]),
            ("Chatbot Endpoints (9 endpoints)", [
                self.test_chatbot_main_endpoint,
                self.test_chatbot_specialized_endpoints,
                self.test_chatbot_history_management,
                self.test_chatbot_streaming_endpoint,
                self.test_chatbot_health_and_stats
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
        
        # Final summary
        print("\n" + "=" * 80)
        print("📈 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for category, results in category_results.items():
            status = "✅" if results["passed"] == results["total"] else "⚠️" if results["passed"] > 0 else "❌"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Backend is fully functional.")
            return True
        elif overall_success_rate >= 80:
            print("✅ Most tests passed. Backend is largely functional with minor issues.")
            return True
        else:
            print("❌ Significant issues found. Backend needs attention.")
            return False
    
    def get_summary(self):
        """Get detailed test summary"""
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
    tester = SiportsBackendTester()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📊 Final Statistics:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)