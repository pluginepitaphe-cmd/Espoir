#!/usr/bin/env python3
"""
Railway Backend Comprehensive Test for SIPORTS v2.0
Testing the Railway deployment at https://siportevent-production.up.railway.app
Focus: PostgreSQL database, all API endpoints, authentication, CORS, chatbot system
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Railway Backend Configuration
RAILWAY_BACKEND_URL = "https://siportevent-production.up.railway.app"
RAILWAY_API_URL = f"{RAILWAY_BACKEND_URL}/api"
FRONTEND_DOMAIN = "siports-maritime.preview.emergentagent.com"

# Test credentials as specified in the review request
TEST_CREDENTIALS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exposant": {"email": "exposant@example.com", "password": "exhibitor123"},
    "visitor": {"email": "visitor@example.com", "password": "visitor123"},
    "partner": {"email": "partner@example.com", "password": "partner123"}
}

class RailwayBackendTester:
    def __init__(self):
        self.railway_url = RAILWAY_BACKEND_URL
        self.api_url = RAILWAY_API_URL
        self.tokens = {}  # Store authentication tokens
        self.users = {}   # Store user data
        self.test_results = []
        self.session_id = f"railway_test_{int(time.time())}"
        
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
    
    # =============================================================================
    # 1. RAILWAY BACKEND HEALTH CHECK
    # =============================================================================
    
    def test_railway_backend_health(self):
        """Test Railway backend health and availability"""
        try:
            # Test root endpoint
            response = requests.get(f"{self.railway_url}/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "status" in data:
                    version = data.get("version", "unknown")
                    self.log_test("Railway Backend Health", True, 
                                f"Railway backend is healthy: {data['message']} (v{version})")
                    return True
                else:
                    self.log_test("Railway Backend Health", False, 
                                "Missing expected fields in health response")
                    return False
            else:
                self.log_test("Railway Backend Health", False, 
                            f"Railway backend unhealthy: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Railway Backend Health", False, f"Railway backend unreachable: {str(e)}")
            return False
    
    def test_railway_api_health(self):
        """Test Railway API endpoints health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    service = data.get("service", "unknown")
                    version = data.get("version", "unknown")
                    self.log_test("Railway API Health", True, 
                                f"Railway API healthy: {service} v{version}")
                    return True
                else:
                    self.log_test("Railway API Health", False, 
                                f"Railway API unhealthy status: {data}")
                    return False
            else:
                self.log_test("Railway API Health", False, 
                            f"Railway API health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway API Health", False, f"Railway API health check error: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend domain"""
        try:
            # Test preflight request
            headers = {
                'Origin': f'https://{FRONTEND_DOMAIN}',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = requests.options(f"{self.api_url}/auth/login", headers=headers, timeout=10)
            
            if response.status_code in [200, 204]:
                cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
                cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
                cors_headers = response.headers.get('Access-Control-Allow-Headers', '')
                
                if cors_origin == '*' or FRONTEND_DOMAIN in cors_origin:
                    self.log_test("CORS Configuration", True, 
                                f"CORS properly configured for {FRONTEND_DOMAIN}")
                    return True
                else:
                    self.log_test("CORS Configuration", False, 
                                f"CORS not configured for {FRONTEND_DOMAIN}. Origin: {cors_origin}")
                    return False
            else:
                self.log_test("CORS Configuration", False, 
                            f"CORS preflight failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"CORS test error: {str(e)}")
            return False
    
    # =============================================================================
    # 2. POSTGRESQL DATABASE OPERATIONS
    # =============================================================================
    
    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate user and test PostgreSQL database operations"""
        if user_type not in TEST_CREDENTIALS:
            self.log_test(f"PostgreSQL {user_type.title()} Auth", False, f"Unknown user type: {user_type}")
            return False
            
        try:
            credentials = TEST_CREDENTIALS[user_type]
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=credentials,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data.get("access_token")
                self.users[user_type] = data.get("user", {})
                
                user_data = self.users[user_type]
                actual_type = user_data.get("user_type")
                user_id = user_data.get("id")
                
                # Test PostgreSQL data integrity
                required_fields = ["id", "email", "first_name", "last_name", "user_type"]
                missing_fields = [f for f in required_fields if not user_data.get(f)]
                
                if missing_fields:
                    self.log_test(f"PostgreSQL {user_type.title()} Auth", False, 
                                f"Missing PostgreSQL fields: {missing_fields}")
                    return False
                
                self.log_test(f"PostgreSQL {user_type.title()} Auth", True, 
                            f"PostgreSQL auth successful: {credentials['email']} (ID: {user_id}, Type: {actual_type})")
                return True
            else:
                self.log_test(f"PostgreSQL {user_type.title()} Auth", False, 
                            f"PostgreSQL auth failed: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test(f"PostgreSQL {user_type.title()} Auth", False, f"PostgreSQL auth error: {str(e)}")
            return False
    
    def test_postgresql_data_operations(self):
        """Test PostgreSQL database operations through API"""
        if "admin" not in self.tokens:
            self.log_test("PostgreSQL Data Operations", False, "No admin token for database testing")
            return False
        
        success_count = 0
        total_tests = 0
        
        # Test user data retrieval (PostgreSQL SELECT operations)
        try:
            response = requests.get(
                f"{self.api_url}/admin/users",
                headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                timeout=15
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                if isinstance(users, list) and len(users) > 0:
                    success_count += 1
                    print(f"   ✅ PostgreSQL SELECT: Retrieved {len(users)} users from database")
                    
                    # Verify PostgreSQL data structure
                    sample_user = users[0]
                    pg_fields = ["id", "email", "created_at", "user_type"]
                    if all(field in sample_user for field in pg_fields):
                        print(f"   ✅ PostgreSQL Schema: All required fields present")
                    else:
                        print(f"   ⚠️  PostgreSQL Schema: Some fields missing")
                else:
                    print(f"   ❌ PostgreSQL SELECT: No users retrieved")
            else:
                print(f"   ❌ PostgreSQL SELECT: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ PostgreSQL SELECT: {str(e)}")
            total_tests += 1
        
        # Test user status update (PostgreSQL UPDATE operations)
        try:
            # Try to validate a user (UPDATE operation)
            test_user_id = self.users.get("exposant", {}).get("id", 2)
            response = requests.post(
                f"{self.api_url}/admin/users/{test_user_id}/validate",
                headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                timeout=15
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    success_count += 1
                    print(f"   ✅ PostgreSQL UPDATE: User validation successful")
                else:
                    print(f"   ❌ PostgreSQL UPDATE: Invalid response format")
            else:
                print(f"   ❌ PostgreSQL UPDATE: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ PostgreSQL UPDATE: {str(e)}")
            total_tests += 1
        
        # Test statistics aggregation (PostgreSQL aggregate functions)
        try:
            response = requests.get(
                f"{self.api_url}/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                timeout=15
            )
            total_tests += 1
            
            if response.status_code == 200:
                data = response.json()
                stats_fields = ["total_users", "visitors", "exhibitors", "partners"]
                if all(field in data for field in stats_fields):
                    success_count += 1
                    total = data["total_users"]
                    visitors = data["visitors"]
                    exhibitors = data["exhibitors"]
                    partners = data["partners"]
                    print(f"   ✅ PostgreSQL AGGREGATES: Stats computed (Total: {total}, V: {visitors}, E: {exhibitors}, P: {partners})")
                else:
                    print(f"   ❌ PostgreSQL AGGREGATES: Missing stats fields")
            else:
                print(f"   ❌ PostgreSQL AGGREGATES: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ PostgreSQL AGGREGATES: {str(e)}")
            total_tests += 1
        
        if success_count == total_tests:
            self.log_test("PostgreSQL Data Operations", True, 
                        f"All {total_tests} PostgreSQL operations successful")
            return True
        else:
            self.log_test("PostgreSQL Data Operations", False, 
                        f"Only {success_count}/{total_tests} PostgreSQL operations successful")
            return False
    
    # =============================================================================
    # 3. AUTHENTICATION SYSTEM TESTS
    # =============================================================================
    
    def test_all_user_types_authentication(self):
        """Test authentication for all user types on Railway"""
        success_count = 0
        total_count = len(TEST_CREDENTIALS)
        
        for user_type in TEST_CREDENTIALS.keys():
            if self.authenticate_user(user_type):
                success_count += 1
        
        if success_count == total_count:
            self.log_test("Railway Authentication System", True, 
                        f"All {total_count} user types authenticated on Railway PostgreSQL")
            return True
        else:
            self.log_test("Railway Authentication System", False, 
                        f"Only {success_count}/{total_count} user types authenticated on Railway")
            return False
    
    # =============================================================================
    # 4. ADMIN ENDPOINTS ON RAILWAY
    # =============================================================================
    
    def test_admin_dashboard_endpoints(self):
        """Test all admin dashboard endpoints on Railway"""
        if "admin" not in self.tokens:
            self.log_test("Railway Admin Endpoints", False, "No admin token available")
            return False
        
        admin_endpoints = [
            ("/admin/dashboard/stats", "Dashboard Statistics"),
            ("/admin/users/pending", "Pending Users"),
            ("/admin/users", "All Users")
        ]
        
        success_count = 0
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        for endpoint, description in admin_endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if endpoint == "/admin/dashboard/stats":
                        if "total_users" in data:
                            success_count += 1
                            print(f"   ✅ {description}: {data['total_users']} total users")
                        else:
                            print(f"   ❌ {description}: Missing stats data")
                    elif endpoint in ["/admin/users/pending", "/admin/users"]:
                        users = data.get("users", [])
                        if isinstance(users, list):
                            success_count += 1
                            print(f"   ✅ {description}: {len(users)} users retrieved")
                        else:
                            print(f"   ❌ {description}: Invalid users data")
                    else:
                        success_count += 1
                        print(f"   ✅ {description}: Working")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {description}: {str(e)}")
        
        # Test admin actions (validate/reject)
        try:
            test_user_id = self.users.get("exposant", {}).get("id", 2)
            response = requests.post(
                f"{self.api_url}/admin/users/{test_user_id}/validate",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ User Validation: User {test_user_id} validated")
            else:
                print(f"   ❌ User Validation: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ User Validation: {str(e)}")
        
        total_tests = len(admin_endpoints) + 1  # +1 for validation test
        
        if success_count == total_tests:
            self.log_test("Railway Admin Endpoints", True, 
                        f"All {total_tests} admin endpoints working on Railway")
            return True
        else:
            self.log_test("Railway Admin Endpoints", False, 
                        f"Only {success_count}/{total_tests} admin endpoints working on Railway")
            return False
    
    # =============================================================================
    # 5. CHATBOT SYSTEM ON RAILWAY
    # =============================================================================
    
    def test_railway_chatbot_system(self):
        """Test SIPORTS v2.0 chatbot system on Railway"""
        chatbot_endpoints = [
            ("/chat", "Main Chat Endpoint"),
            ("/chat/exhibitor", "Exhibitor Chat"),
            ("/chat/package", "Package Chat"),
            ("/chat/event", "Event Chat"),
            ("/chatbot/health", "Chatbot Health")
        ]
        
        success_count = 0
        
        for endpoint, description in chatbot_endpoints:
            try:
                if endpoint == "/chatbot/health":
                    # GET request for health check
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=15)
                else:
                    # POST request for chat endpoints
                    response = requests.post(
                        f"{self.api_url}{endpoint}",
                        json={
                            "message": f"Test message for {description}",
                            "context_type": "general",
                            "session_id": self.session_id
                        },
                        timeout=20
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/chatbot/health":
                        if "status" in data and data["status"] == "healthy":
                            success_count += 1
                            version = data.get("version", "unknown")
                            mode = data.get("mock_mode", "unknown")
                            print(f"   ✅ {description}: Healthy (v{version}, mock: {mode})")
                        else:
                            print(f"   ❌ {description}: Unhealthy status")
                    else:
                        if "response" in data:
                            success_count += 1
                            confidence = data.get("confidence", 0)
                            print(f"   ✅ {description}: Response received (confidence: {confidence})")
                        else:
                            print(f"   ❌ {description}: No response field")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {description}: {str(e)}")
        
        # Test chatbot history management
        try:
            response = requests.get(f"{self.api_url}/chat/history/{self.session_id}", timeout=15)
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Chat History: History retrieved")
            else:
                print(f"   ❌ Chat History: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Chat History: {str(e)}")
        
        total_tests = len(chatbot_endpoints) + 1  # +1 for history test
        
        if success_count >= total_tests * 0.8:  # 80% success rate acceptable for chatbot
            self.log_test("Railway Chatbot System", True, 
                        f"Chatbot system working on Railway ({success_count}/{total_tests} endpoints)")
            return True
        else:
            self.log_test("Railway Chatbot System", False, 
                        f"Chatbot system issues on Railway ({success_count}/{total_tests} endpoints)")
            return False
    
    # =============================================================================
    # 6. PACKAGE SYSTEMS ON RAILWAY
    # =============================================================================
    
    def test_railway_package_systems(self):
        """Test visitor and partner package systems on Railway"""
        package_endpoints = [
            ("/visitor-packages", "Visitor Packages"),
            ("/partnership-packages", "Partnership Packages")
        ]
        
        success_count = 0
        
        for endpoint, description in package_endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    packages = data.get("packages", [])
                    
                    if isinstance(packages, list) and len(packages) >= 3:
                        success_count += 1
                        package_names = [p.get("name", "Unknown") for p in packages]
                        print(f"   ✅ {description}: {len(packages)} packages ({', '.join(package_names[:3])}...)")
                        
                        # Verify package structure
                        sample_package = packages[0]
                        required_fields = ["id", "name", "price", "features"]
                        if all(field in sample_package for field in required_fields):
                            print(f"   ✅ {description} Structure: All required fields present")
                        else:
                            print(f"   ⚠️  {description} Structure: Some fields missing")
                    else:
                        print(f"   ❌ {description}: Insufficient packages ({len(packages)})")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {description}: {str(e)}")
        
        # Test package update functionality
        if "visitor" in self.tokens:
            try:
                response = requests.post(
                    f"{self.api_url}/visitor-packages/update",
                    json={"package_type": "Premium", "user_id": self.users["visitor"]["id"]},
                    headers={"Authorization": f"Bearer {self.tokens['visitor']}"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"   ✅ Package Update: Visitor package updated successfully")
                else:
                    print(f"   ❌ Package Update: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Package Update: {str(e)}")
        
        total_tests = len(package_endpoints) + (1 if "visitor" in self.tokens else 0)
        
        if success_count >= total_tests * 0.8:  # 80% success rate acceptable
            self.log_test("Railway Package Systems", True, 
                        f"Package systems working on Railway ({success_count}/{total_tests} tests)")
            return True
        else:
            self.log_test("Railway Package Systems", False, 
                        f"Package systems issues on Railway ({success_count}/{total_tests} tests)")
            return False
    
    # =============================================================================
    # 7. COMPREHENSIVE ENDPOINT COMPARISON
    # =============================================================================
    
    def test_railway_vs_local_endpoints(self):
        """Compare Railway endpoints with expected local functionality"""
        critical_endpoints = [
            "/",
            "/health", 
            "/auth/login",
            "/visitor-packages",
            "/partnership-packages",
            "/admin/dashboard/stats",
            "/chat",
            "/chatbot/health"
        ]
        
        working_endpoints = 0
        
        for endpoint in critical_endpoints:
            try:
                if endpoint == "/auth/login":
                    # POST request
                    response = requests.post(
                        f"{self.api_url}{endpoint}",
                        json=TEST_CREDENTIALS["admin"],
                        timeout=15
                    )
                elif endpoint in ["/chat"]:
                    # POST request
                    response = requests.post(
                        f"{self.api_url}{endpoint}",
                        json={"message": "test", "context_type": "general"},
                        timeout=15
                    )
                else:
                    # GET request
                    url = f"{self.api_url}{endpoint}" if endpoint not in ["/", "/health"] else f"{self.railway_url}{endpoint}"
                    headers = {"Authorization": f"Bearer {self.tokens['admin']}"} if endpoint.startswith("/admin") else {}
                    response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {endpoint}: Working")
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)}")
        
        total_endpoints = len(critical_endpoints)
        success_rate = (working_endpoints / total_endpoints) * 100
        
        if success_rate >= 90:
            self.log_test("Railway vs Local Comparison", True, 
                        f"Railway backend fully functional ({working_endpoints}/{total_endpoints} endpoints, {success_rate:.1f}%)")
            return True
        elif success_rate >= 70:
            self.log_test("Railway vs Local Comparison", True, 
                        f"Railway backend mostly functional ({working_endpoints}/{total_endpoints} endpoints, {success_rate:.1f}%)")
            return True
        else:
            self.log_test("Railway vs Local Comparison", False, 
                        f"Railway backend has issues ({working_endpoints}/{total_endpoints} endpoints, {success_rate:.1f}%)")
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_comprehensive_railway_tests(self):
        """Run all Railway backend tests"""
        print("🚀 RAILWAY BACKEND COMPREHENSIVE TESTING")
        print(f"Railway URL: {self.railway_url}")
        print(f"API URL: {self.api_url}")
        print(f"Frontend Domain: {FRONTEND_DOMAIN}")
        print("=" * 80)
        
        # Define test categories
        test_categories = [
            ("Railway Backend Health", [
                self.test_railway_backend_health,
                self.test_railway_api_health,
                self.test_cors_configuration
            ]),
            ("PostgreSQL Database", [
                self.test_all_user_types_authentication,
                self.test_postgresql_data_operations
            ]),
            ("Admin Endpoints", [
                self.test_admin_dashboard_endpoints
            ]),
            ("Chatbot System", [
                self.test_railway_chatbot_system
            ]),
            ("Package Systems", [
                self.test_railway_package_systems
            ]),
            ("Endpoint Comparison", [
                self.test_railway_vs_local_endpoints
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
        
        # Final Railway Backend Assessment
        print("\n" + "=" * 80)
        print("🎯 RAILWAY BACKEND ASSESSMENT RESULTS")
        print("=" * 80)
        
        for category, results in category_results.items():
            status = "✅" if results["passed"] == results["total"] else "⚠️" if results["passed"] > 0 else "❌"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 RAILWAY BACKEND SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        # Railway Backend Status Assessment
        if overall_success_rate >= 95:
            print("🎉 RAILWAY BACKEND 100% FUNCTIONAL - Ready for production!")
            railway_status = "fully_functional"
        elif overall_success_rate >= 85:
            print("✅ RAILWAY BACKEND MOSTLY FUNCTIONAL - Minor issues detected")
            railway_status = "mostly_functional"
        elif overall_success_rate >= 70:
            print("⚠️  RAILWAY BACKEND PARTIALLY FUNCTIONAL - Some issues need attention")
            railway_status = "partially_functional"
        else:
            print("❌ RAILWAY BACKEND HAS SIGNIFICANT ISSUES - Needs immediate attention")
            railway_status = "needs_attention"
        
        # Summary for user
        print(f"\n📋 RAILWAY DEPLOYMENT SUMMARY:")
        print(f"   • PostgreSQL Database: {'✅ Working' if 'PostgreSQL Database' in category_results and category_results['PostgreSQL Database']['success_rate'] >= 80 else '❌ Issues'}")
        print(f"   • Authentication System: {'✅ Working' if any('Auth' in str(r) for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • Admin Endpoints: {'✅ Working' if 'Admin Endpoints' in category_results and category_results['Admin Endpoints']['success_rate'] >= 80 else '❌ Issues'}")
        print(f"   • Chatbot System: {'✅ Working' if 'Chatbot System' in category_results and category_results['Chatbot System']['success_rate'] >= 80 else '❌ Issues'}")
        print(f"   • CORS Configuration: {'✅ Working' if any('CORS' in str(r) for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • Package Systems: {'✅ Working' if 'Package Systems' in category_results and category_results['Package Systems']['success_rate'] >= 80 else '❌ Issues'}")
        
        return railway_status, overall_success_rate
    
    def get_detailed_summary(self):
        """Get detailed test summary for reporting"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        return {
            "railway_url": self.railway_url,
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "authenticated_users": list(self.tokens.keys()),
            "test_results": self.test_results
        }

def main():
    """Main Railway backend test execution"""
    print("🚀 Starting Railway Backend Comprehensive Testing")
    print("Testing Railway deployment with PostgreSQL database")
    print("=" * 80)
    
    tester = RailwayBackendTester()
    railway_status, success_rate = tester.run_comprehensive_railway_tests()
    
    # Get detailed summary
    summary = tester.get_detailed_summary()
    
    print(f"\n📊 FINAL RAILWAY BACKEND STATISTICS:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Authenticated Users: {', '.join(summary['authenticated_users'])}")
    
    # Return status for integration
    if railway_status in ["fully_functional", "mostly_functional"]:
        print("\n✅ RAILWAY BACKEND IS READY FOR FRONTEND CONNECTION")
        return 0
    else:
        print("\n❌ RAILWAY BACKEND NEEDS FIXES BEFORE FRONTEND CONNECTION")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)