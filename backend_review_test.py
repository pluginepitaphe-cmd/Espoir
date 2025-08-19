#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Review Test - SIPORTS v2.0
Testing backend functionality after implementing:
1. Fixed JSX syntax errors in AI networking pages
2. Created enhanced exhibitor mini-site with comprehensive features

Focus Areas:
- Basic API health checks (GET /, GET /health)
- Authentication endpoints (login for admin, exposant, visiteur)
- Existing exhibitor-related endpoints (GET /api/exposants, exhibitor data endpoints)
- AI/matching related endpoints if they exist
- General backend functionality to ensure no regressions
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

# Test accounts from backend server.py
TEST_ACCOUNTS = {
    "admin": {
        "email": "admin@siportevent.com",
        "password": "admin123"
    },
    "exposant": {
        "email": "exposant@example.com", 
        "password": "exhibitor123"
    },
    "visiteur": {
        "email": "visiteur@example.com",
        "password": "visit123"
    }
}

class BackendReviewTester:
    def __init__(self):
        self.results = []
        self.tokens = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        self.results.append(result)
        print(result)
        
    def test_health_endpoints(self):
        """Test basic API health checks"""
        print("\n🔍 TESTING HEALTH ENDPOINTS")
        print("=" * 50)
        
        # Test root endpoint
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "SIPORTS v2.0 API" in data.get("message", ""):
                    self.log_result("GET / - Root endpoint", True, f"Status: {data.get('status')}, Version: {data.get('version')}")
                else:
                    self.log_result("GET / - Root endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_result("GET / - Root endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET / - Root endpoint", False, f"Error: {str(e)}")
            
        # Test health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("GET /health - Health check", True, f"Service: {data.get('service')}, Version: {data.get('version')}")
                else:
                    self.log_result("GET /health - Health check", False, f"Unhealthy status: {data}")
            else:
                self.log_result("GET /health - Health check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /health - Health check", False, f"Error: {str(e)}")
    
    def test_authentication_endpoints(self):
        """Test authentication for all user types"""
        print("\n🔐 TESTING AUTHENTICATION ENDPOINTS")
        print("=" * 50)
        
        for user_type, credentials in TEST_ACCOUNTS.items():
            try:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    headers=HEADERS,
                    json=credentials
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "user" in data:
                        # Store token for later use
                        self.tokens[user_type] = data["access_token"]
                        user_info = data["user"]
                        self.log_result(
                            f"Login {user_type} ({credentials['email']})", 
                            True, 
                            f"User type: {user_info.get('user_type')}, Name: {user_info.get('first_name')} {user_info.get('last_name')}"
                        )
                    else:
                        self.log_result(f"Login {user_type}", False, f"Missing token or user data: {data}")
                else:
                    self.log_result(f"Login {user_type}", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Login {user_type}", False, f"Error: {str(e)}")
    
    def test_exhibitor_endpoints(self):
        """Test exhibitor-related endpoints"""
        print("\n🏢 TESTING EXHIBITOR ENDPOINTS")
        print("=" * 50)
        
        # Test GET /api/exposants (exhibitors list)
        try:
            response = requests.get(f"{BASE_URL}/api/exposants")
            if response.status_code == 200:
                data = response.json()
                if "exposants" in data and "total" in data:
                    exposants = data["exposants"]
                    total = data["total"]
                    if len(exposants) > 0:
                        # Check first exposant structure
                        first_exposant = exposants[0]
                        required_fields = ["id", "name", "category", "description", "stand", "hall"]
                        missing_fields = [field for field in required_fields if field not in first_exposant]
                        
                        if not missing_fields:
                            self.log_result(
                                "GET /api/exposants - Exhibitors list", 
                                True, 
                                f"Found {total} exhibitors, First: {first_exposant['name']} at {first_exposant['stand']}"
                            )
                        else:
                            self.log_result("GET /api/exposants - Exhibitors list", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("GET /api/exposants - Exhibitors list", False, "No exhibitors found")
                else:
                    self.log_result("GET /api/exposants - Exhibitors list", False, f"Invalid response structure: {data}")
            else:
                self.log_result("GET /api/exposants - Exhibitors list", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/exposants - Exhibitors list", False, f"Error: {str(e)}")
        
        # Test GET /api/exposants/{id} (specific exhibitor details)
        try:
            response = requests.get(f"{BASE_URL}/api/exposants/1")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "name", "category", "description", "products", "team", "certifications"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result(
                        "GET /api/exposants/1 - Exhibitor details", 
                        True, 
                        f"Exhibitor: {data['name']}, Products: {len(data.get('products', []))}, Team: {len(data.get('team', []))}"
                    )
                else:
                    self.log_result("GET /api/exposants/1 - Exhibitor details", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET /api/exposants/1 - Exhibitor details", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/exposants/1 - Exhibitor details", False, f"Error: {str(e)}")
    
    def test_package_endpoints(self):
        """Test package-related endpoints"""
        print("\n📦 TESTING PACKAGE ENDPOINTS")
        print("=" * 50)
        
        # Test visitor packages
        try:
            response = requests.get(f"{BASE_URL}/api/visitor-packages")
            if response.status_code == 200:
                data = response.json()
                if "packages" in data:
                    packages = data["packages"]
                    if len(packages) >= 4:  # Should have Free, Basic, Premium, VIP
                        package_names = [p["name"] for p in packages]
                        self.log_result(
                            "GET /api/visitor-packages - Visitor packages", 
                            True, 
                            f"Found {len(packages)} packages: {', '.join(package_names)}"
                        )
                    else:
                        self.log_result("GET /api/visitor-packages - Visitor packages", False, f"Expected 4+ packages, got {len(packages)}")
                else:
                    self.log_result("GET /api/visitor-packages - Visitor packages", False, "Missing packages in response")
            else:
                self.log_result("GET /api/visitor-packages - Visitor packages", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/visitor-packages - Visitor packages", False, f"Error: {str(e)}")
        
        # Test partnership packages
        try:
            response = requests.get(f"{BASE_URL}/api/partnership-packages")
            if response.status_code == 200:
                data = response.json()
                if "packages" in data:
                    packages = data["packages"]
                    if len(packages) >= 4:  # Should have Startup, Silver, Gold, Platinum
                        package_names = [p["name"] for p in packages]
                        self.log_result(
                            "GET /api/partnership-packages - Partnership packages", 
                            True, 
                            f"Found {len(packages)} packages: {', '.join(package_names)}"
                        )
                    else:
                        self.log_result("GET /api/partnership-packages - Partnership packages", False, f"Expected 4+ packages, got {len(packages)}")
                else:
                    self.log_result("GET /api/partnership-packages - Partnership packages", False, "Missing packages in response")
            else:
                self.log_result("GET /api/partnership-packages - Partnership packages", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/partnership-packages - Partnership packages", False, f"Error: {str(e)}")
    
    def test_ai_matching_endpoints(self):
        """Test AI/matching related endpoints if they exist"""
        print("\n🤖 TESTING AI/MATCHING ENDPOINTS")
        print("=" * 50)
        
        # Need authentication for these endpoints
        if "exposant" not in self.tokens:
            self.log_result("AI/Matching endpoints", False, "No exposant token available for testing")
            return
        
        auth_headers = {
            **HEADERS,
            "Authorization": f"Bearer {self.tokens['exposant']}"
        }
        
        # Test networking profiles endpoint
        try:
            test_filters = {
                "match_type": "all",
                "sector": "all",
                "compatibility_min": 70,
                "location": "all",
                "budget": "all",
                "language": "all",
                "semantic_search": False
            }
            
            response = requests.post(
                f"{BASE_URL}/api/networking/profiles",
                headers=auth_headers,
                json=test_filters
            )
            
            if response.status_code == 200:
                data = response.json()
                if "profiles" in data:
                    profiles = data["profiles"]
                    self.log_result(
                        "POST /api/networking/profiles - AI matching profiles", 
                        True, 
                        f"Found {len(profiles)} matching profiles"
                    )
                else:
                    self.log_result("POST /api/networking/profiles - AI matching profiles", False, "Missing profiles in response")
            else:
                self.log_result("POST /api/networking/profiles - AI matching profiles", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("POST /api/networking/profiles - AI matching profiles", False, f"Error: {str(e)}")
        
        # Test AI suggestions endpoint
        try:
            response = requests.post(
                f"{BASE_URL}/api/networking/ai-suggestions",
                headers=auth_headers,
                json={}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "suggestions" in data:
                    suggestions = data["suggestions"]
                    self.log_result(
                        "POST /api/networking/ai-suggestions - AI suggestions", 
                        True, 
                        f"Found {len(suggestions)} AI suggestions"
                    )
                else:
                    self.log_result("POST /api/networking/ai-suggestions - AI suggestions", False, "Missing suggestions in response")
            else:
                self.log_result("POST /api/networking/ai-suggestions - AI suggestions", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("POST /api/networking/ai-suggestions - AI suggestions", False, f"Error: {str(e)}")
    
    def test_chatbot_endpoints(self):
        """Test AI chatbot endpoints"""
        print("\n💬 TESTING AI CHATBOT ENDPOINTS")
        print("=" * 50)
        
        # Test chatbot health check
        try:
            response = requests.get(f"{BASE_URL}/api/chatbot/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result(
                        "GET /api/chatbot/health - Chatbot health", 
                        True, 
                        f"Service: {data.get('service')}, Version: {data.get('version')}, Mock mode: {data.get('mock_mode')}"
                    )
                else:
                    self.log_result("GET /api/chatbot/health - Chatbot health", False, f"Unhealthy status: {data}")
            else:
                self.log_result("GET /api/chatbot/health - Chatbot health", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/chatbot/health - Chatbot health", False, f"Error: {str(e)}")
        
        # Test main chat endpoint
        try:
            chat_request = {
                "message": "Bonjour, pouvez-vous me recommander des exposants spécialisés en technologies maritimes?",
                "context_type": "exhibitor",
                "session_id": "test-session-123"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/chat",
                headers=HEADERS,
                json=chat_request
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "confidence" in data:
                    self.log_result(
                        "POST /api/chat - Main chatbot endpoint", 
                        True, 
                        f"Response length: {len(data['response'])}, Confidence: {data['confidence']}"
                    )
                else:
                    self.log_result("POST /api/chat - Main chatbot endpoint", False, f"Missing response fields: {data}")
            else:
                self.log_result("POST /api/chat - Main chatbot endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("POST /api/chat - Main chatbot endpoint", False, f"Error: {str(e)}")
    
    def test_admin_endpoints(self):
        """Test admin endpoints with proper authentication"""
        print("\n👑 TESTING ADMIN ENDPOINTS")
        print("=" * 50)
        
        if "admin" not in self.tokens:
            self.log_result("Admin endpoints", False, "No admin token available for testing")
            return
        
        auth_headers = {
            **HEADERS,
            "Authorization": f"Bearer {self.tokens['admin']}"
        }
        
        # Test admin dashboard stats
        try:
            response = requests.get(f"{BASE_URL}/api/admin/dashboard/stats", headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "visitors", "exhibitors", "partners", "pending", "validated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result(
                        "GET /api/admin/dashboard/stats - Admin statistics", 
                        True, 
                        f"Total users: {data['total_users']}, Pending: {data['pending']}, Validated: {data['validated']}"
                    )
                else:
                    self.log_result("GET /api/admin/dashboard/stats - Admin statistics", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET /api/admin/dashboard/stats - Admin statistics", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/admin/dashboard/stats - Admin statistics", False, f"Error: {str(e)}")
        
        # Test pending users endpoint
        try:
            response = requests.get(f"{BASE_URL}/api/admin/users/pending", headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                if "users" in data:
                    pending_users = data["users"]
                    self.log_result(
                        "GET /api/admin/users/pending - Pending users", 
                        True, 
                        f"Found {len(pending_users)} pending users"
                    )
                else:
                    self.log_result("GET /api/admin/users/pending - Pending users", False, "Missing users in response")
            else:
                self.log_result("GET /api/admin/users/pending - Pending users", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/admin/users/pending - Pending users", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING BACKEND REVIEW TESTS - SIPORTS v2.0")
        print("=" * 60)
        print(f"Testing backend at: {BASE_URL}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_authentication_endpoints()
        self.test_exhibitor_endpoints()
        self.test_package_endpoints()
        self.test_ai_matching_endpoints()
        self.test_chatbot_endpoints()
        self.test_admin_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Backend is highly functional!")
        elif success_rate >= 75:
            print("✅ GOOD - Backend is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Backend has some significant issues")
        else:
            print("❌ CRITICAL - Backend has major functionality problems")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        for result in self.results:
            print(result)
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = BackendReviewTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Backend review tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Backend review tests found significant issues!")
        sys.exit(1)