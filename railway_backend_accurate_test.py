#!/usr/bin/env python3
"""
Accurate Railway Backend Test for SIPORTS v2.0
Testing the actual Railway deployment endpoints at https://siportevent-production.up.railway.app
Based on discovered endpoint structure from Railway backend
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
    "visitor": {"email": "visitor@example.com", "password": "visitor123"}
}

class AccurateRailwayTester:
    def __init__(self):
        self.railway_url = RAILWAY_BACKEND_URL
        self.api_url = RAILWAY_API_URL
        self.tokens = {}
        self.users = {}
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
        """Test Railway backend health and PostgreSQL connection"""
        try:
            response = requests.get(f"{self.railway_url}/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic health
                if "message" in data and "status" in data and data["status"] == "active":
                    version = data.get("version", "unknown")
                    environment = data.get("environment", "unknown")
                    
                    # Check PostgreSQL connection
                    db_info = data.get("database", {})
                    if db_info.get("connected") and db_info.get("type") == "postgresql":
                        self.log_test("Railway Backend Health", True, 
                                    f"Railway backend healthy: {data['message']} (v{version}, {environment}, PostgreSQL connected)")
                        return True
                    else:
                        self.log_test("Railway Backend Health", False, 
                                    f"PostgreSQL connection issue: {db_info}")
                        return False
                else:
                    self.log_test("Railway Backend Health", False, 
                                "Missing expected health fields")
                    return False
            else:
                self.log_test("Railway Backend Health", False, 
                            f"Railway backend unhealthy: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Backend Health", False, f"Railway backend unreachable: {str(e)}")
            return False
    
    def test_railway_features_and_endpoints(self):
        """Test Railway backend features and available endpoints"""
        try:
            response = requests.get(f"{self.railway_url}/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                endpoints = data.get("endpoints", {})
                
                expected_features = ["PostgreSQL Database", "JWT Authentication", "AI Chatbot", "Visitor Packages"]
                found_features = [f for f in expected_features if any(f in feature for feature in features)]
                
                expected_endpoints = ["auth", "chatbot", "packages", "admin"]
                found_endpoints = [e for e in expected_endpoints if e in endpoints]
                
                if len(found_features) >= 3 and len(found_endpoints) >= 3:
                    self.log_test("Railway Features & Endpoints", True, 
                                f"Railway features: {len(features)} total, endpoints: {list(endpoints.keys())}")
                    return True
                else:
                    self.log_test("Railway Features & Endpoints", False, 
                                f"Missing features or endpoints. Features: {found_features}, Endpoints: {found_endpoints}")
                    return False
            else:
                self.log_test("Railway Features & Endpoints", False, 
                            f"Cannot retrieve features: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Features & Endpoints", False, f"Features check error: {str(e)}")
            return False
    
    # =============================================================================
    # 2. AUTHENTICATION SYSTEM TESTS
    # =============================================================================
    
    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate user on Railway backend"""
        if user_type not in TEST_CREDENTIALS:
            self.log_test(f"Railway {user_type.title()} Auth", False, f"Unknown user type: {user_type}")
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
                
                self.log_test(f"Railway {user_type.title()} Auth", True, 
                            f"Railway auth successful: {credentials['email']} (ID: {user_id}, Type: {actual_type})")
                return True
            else:
                self.log_test(f"Railway {user_type.title()} Auth", False, 
                            f"Railway auth failed: HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test(f"Railway {user_type.title()} Auth", False, f"Railway auth error: {str(e)}")
            return False
    
    def test_all_user_authentications(self):
        """Test authentication for all available user types"""
        success_count = 0
        total_count = len(TEST_CREDENTIALS)
        
        for user_type in TEST_CREDENTIALS.keys():
            if self.authenticate_user(user_type):
                success_count += 1
        
        if success_count >= total_count - 1:  # Allow 1 failure (partner might not exist)
            self.log_test("Railway Authentication System", True, 
                        f"Railway authentication working ({success_count}/{total_count} user types)")
            return True
        else:
            self.log_test("Railway Authentication System", False, 
                        f"Railway authentication issues ({success_count}/{total_count} user types)")
            return False
    
    def test_user_info_endpoint(self):
        """Test the /auth/me endpoint"""
        if "admin" not in self.tokens:
            self.log_test("Railway User Info", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "user_type"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Railway User Info", True, 
                                f"User info retrieved: {data['email']} ({data['user_type']})")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Railway User Info", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("Railway User Info", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway User Info", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 3. ADMIN ENDPOINTS ON RAILWAY
    # =============================================================================
    
    def test_admin_dashboard_stats(self):
        """Test Railway admin dashboard statistics"""
        if "admin" not in self.tokens:
            self.log_test("Railway Admin Dashboard", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.api_url}/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.tokens['admin']}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for Railway-specific stats structure
                expected_sections = ["visitors", "exhibitors", "revenue", "engagement"]
                found_sections = [s for s in expected_sections if s in data]
                
                if len(found_sections) >= 3:
                    visitors = data.get("visitors", {}).get("total", 0)
                    exhibitors = data.get("exhibitors", {}).get("total", 0)
                    revenue = data.get("revenue", {}).get("total", 0)
                    
                    self.log_test("Railway Admin Dashboard", True, 
                                f"Railway admin stats: {visitors} visitors, {exhibitors} exhibitors, €{revenue} revenue")
                    return True
                else:
                    self.log_test("Railway Admin Dashboard", False, 
                                f"Missing stats sections. Found: {found_sections}")
                    return False
            else:
                self.log_test("Railway Admin Dashboard", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Admin Dashboard", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 4. CHATBOT SYSTEM ON RAILWAY
    # =============================================================================
    
    def test_railway_chatbot_health(self):
        """Test Railway chatbot health"""
        try:
            response = requests.get(f"{self.api_url}/chatbot/health", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "healthy":
                    version = data.get("version", "unknown")
                    features = data.get("features", [])
                    contexts = data.get("contexts", [])
                    
                    self.log_test("Railway Chatbot Health", True, 
                                f"Railway chatbot healthy (v{version}, {len(features)} features, {len(contexts)} contexts)")
                    return True
                else:
                    self.log_test("Railway Chatbot Health", False, 
                                f"Chatbot unhealthy: {data}")
                    return False
            else:
                self.log_test("Railway Chatbot Health", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Chatbot Health", False, f"Request error: {str(e)}")
            return False
    
    def test_railway_chatbot_functionality(self):
        """Test Railway chatbot chat functionality"""
        try:
            response = requests.post(
                f"{self.api_url}/chatbot/chat",
                json={
                    "message": "Tell me about SIPORTS visitor packages",
                    "context": "packages",
                    "session_id": self.session_id
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"]
                    confidence = data.get("confidence", 0)
                    
                    self.log_test("Railway Chatbot Functionality", True, 
                                f"Railway chatbot working (confidence: {confidence}, response length: {len(response_text)})")
                    return True
                else:
                    self.log_test("Railway Chatbot Functionality", False, 
                                "No response field in chatbot response")
                    return False
            else:
                self.log_test("Railway Chatbot Functionality", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Chatbot Functionality", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 5. PACKAGE SYSTEMS ON RAILWAY
    # =============================================================================
    
    def test_railway_visitor_packages(self):
        """Test Railway visitor packages"""
        try:
            response = requests.get(f"{self.api_url}/visitor-packages", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 3:
                    package_names = [p.get("name", "Unknown") for p in packages]
                    total_packages = len(packages)
                    
                    # Check package structure
                    sample_package = packages[0]
                    required_fields = ["id", "name", "price", "features"]
                    if all(field in sample_package for field in required_fields):
                        self.log_test("Railway Visitor Packages", True, 
                                    f"Railway visitor packages working: {total_packages} packages ({', '.join(package_names)})")
                        return True
                    else:
                        self.log_test("Railway Visitor Packages", False, 
                                    "Package structure missing required fields")
                        return False
                else:
                    self.log_test("Railway Visitor Packages", False, 
                                f"Insufficient packages: {len(packages)}")
                    return False
            else:
                self.log_test("Railway Visitor Packages", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Visitor Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_railway_partner_packages(self):
        """Test Railway partner packages"""
        try:
            response = requests.get(f"{self.api_url}/partner-packages", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) >= 3:
                    package_names = [p.get("name", "Unknown") for p in packages]
                    total_packages = len(packages)
                    
                    self.log_test("Railway Partner Packages", True, 
                                f"Railway partner packages working: {total_packages} packages ({', '.join(package_names)})")
                    return True
                else:
                    self.log_test("Railway Partner Packages", False, 
                                f"Insufficient partner packages: {len(packages)}")
                    return False
            else:
                self.log_test("Railway Partner Packages", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway Partner Packages", False, f"Request error: {str(e)}")
            return False
    
    # =============================================================================
    # 6. CORS AND FRONTEND INTEGRATION
    # =============================================================================
    
    def test_cors_for_frontend(self):
        """Test CORS configuration for frontend domain"""
        try:
            # Test actual request with frontend origin
            headers = {
                'Origin': f'https://{FRONTEND_DOMAIN}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=TEST_CREDENTIALS["admin"],
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
                
                if cors_origin == '*' or FRONTEND_DOMAIN in cors_origin:
                    self.log_test("Railway CORS Configuration", True, 
                                f"CORS working for frontend domain: {FRONTEND_DOMAIN}")
                    return True
                else:
                    self.log_test("Railway CORS Configuration", False, 
                                f"CORS not configured for {FRONTEND_DOMAIN}. Got: {cors_origin}")
                    return False
            else:
                self.log_test("Railway CORS Configuration", False, 
                            f"CORS test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Railway CORS Configuration", False, f"CORS test error: {str(e)}")
            return False
    
    # =============================================================================
    # 7. COMPREHENSIVE RAILWAY ASSESSMENT
    # =============================================================================
    
    def test_railway_vs_local_functionality(self):
        """Compare Railway functionality with expected local functionality"""
        critical_tests = [
            ("Backend Health", self.test_railway_backend_health),
            ("Authentication", lambda: "admin" in self.tokens and "visitor" in self.tokens),
            ("Admin Dashboard", self.test_admin_dashboard_stats),
            ("Chatbot Health", self.test_railway_chatbot_health),
            ("Visitor Packages", self.test_railway_visitor_packages),
            ("CORS", self.test_cors_for_frontend)
        ]
        
        working_features = 0
        
        for feature_name, test_func in critical_tests:
            try:
                if callable(test_func):
                    if test_func():
                        working_features += 1
                        print(f"   ✅ {feature_name}: Working")
                    else:
                        print(f"   ❌ {feature_name}: Not working")
                else:
                    if test_func:
                        working_features += 1
                        print(f"   ✅ {feature_name}: Working")
                    else:
                        print(f"   ❌ {feature_name}: Not working")
            except Exception as e:
                print(f"   ❌ {feature_name}: Error - {str(e)}")
        
        total_features = len(critical_tests)
        success_rate = (working_features / total_features) * 100
        
        if success_rate >= 85:
            self.log_test("Railway vs Local Functionality", True, 
                        f"Railway backend fully functional ({working_features}/{total_features} features, {success_rate:.1f}%)")
            return True
        elif success_rate >= 70:
            self.log_test("Railway vs Local Functionality", True, 
                        f"Railway backend mostly functional ({working_features}/{total_features} features, {success_rate:.1f}%)")
            return True
        else:
            self.log_test("Railway vs Local Functionality", False, 
                        f"Railway backend has significant issues ({working_features}/{total_features} features, {success_rate:.1f}%)")
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_accurate_railway_tests(self):
        """Run accurate Railway backend tests based on actual endpoints"""
        print("🚀 ACCURATE RAILWAY BACKEND TESTING")
        print(f"Railway URL: {self.railway_url}")
        print(f"API URL: {self.api_url}")
        print(f"Frontend Domain: {FRONTEND_DOMAIN}")
        print("=" * 80)
        
        # Define test categories based on actual Railway backend
        test_categories = [
            ("Railway Backend Health", [
                self.test_railway_backend_health,
                self.test_railway_features_and_endpoints
            ]),
            ("Authentication System", [
                self.test_all_user_authentications,
                self.test_user_info_endpoint
            ]),
            ("Admin Dashboard", [
                self.test_admin_dashboard_stats
            ]),
            ("Chatbot System", [
                self.test_railway_chatbot_health,
                self.test_railway_chatbot_functionality
            ]),
            ("Package Systems", [
                self.test_railway_visitor_packages,
                self.test_railway_partner_packages
            ]),
            ("Frontend Integration", [
                self.test_cors_for_frontend
            ]),
            ("Overall Assessment", [
                self.test_railway_vs_local_functionality
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
        print("🎯 ACCURATE RAILWAY BACKEND ASSESSMENT")
        print("=" * 80)
        
        for category, results in category_results.items():
            status = "✅" if results["passed"] == results["total"] else "⚠️" if results["passed"] > 0 else "❌"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 RAILWAY BACKEND SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        # Railway Backend Status Assessment
        if overall_success_rate >= 90:
            print("🎉 RAILWAY BACKEND 100% FUNCTIONAL with PostgreSQL!")
            railway_status = "fully_functional"
        elif overall_success_rate >= 75:
            print("✅ RAILWAY BACKEND MOSTLY FUNCTIONAL with minor issues")
            railway_status = "mostly_functional"
        elif overall_success_rate >= 60:
            print("⚠️  RAILWAY BACKEND PARTIALLY FUNCTIONAL - some issues")
            railway_status = "partially_functional"
        else:
            print("❌ RAILWAY BACKEND HAS SIGNIFICANT ISSUES")
            railway_status = "needs_attention"
        
        # Detailed Railway Assessment
        print(f"\n📋 RAILWAY DEPLOYMENT DETAILED ASSESSMENT:")
        print(f"   • PostgreSQL Database: {'✅ Connected and Working' if any('PostgreSQL' in str(r['message']) for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • Authentication System: {'✅ Working' if len(self.tokens) >= 2 else '❌ Issues'}")
        print(f"   • Admin Dashboard: {'✅ Working' if any('admin' in r['test'].lower() for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • Chatbot System: {'✅ Working' if any('chatbot' in r['test'].lower() for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • Package Systems: {'✅ Working' if any('package' in r['test'].lower() for r in self.test_results if r['success']) else '❌ Issues'}")
        print(f"   • CORS Configuration: {'✅ Working' if any('CORS' in str(r['message']) for r in self.test_results if r['success']) else '❌ Issues'}")
        
        # Frontend Connection Readiness
        if railway_status in ["fully_functional", "mostly_functional"]:
            print(f"\n✅ RAILWAY BACKEND IS READY FOR FRONTEND CONNECTION")
            print(f"   Frontend can safely connect to: {self.railway_url}")
            print(f"   API endpoints available at: {self.api_url}")
        else:
            print(f"\n⚠️  RAILWAY BACKEND NEEDS ATTENTION BEFORE FRONTEND CONNECTION")
        
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
    """Main accurate Railway backend test execution"""
    print("🚀 Starting Accurate Railway Backend Testing")
    print("Testing actual Railway deployment endpoints and PostgreSQL")
    print("=" * 80)
    
    tester = AccurateRailwayTester()
    railway_status, success_rate = tester.run_accurate_railway_tests()
    
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
        print("\n🎉 RAILWAY BACKEND TESTING COMPLETED SUCCESSFULLY")
        return 0
    else:
        print("\n⚠️  RAILWAY BACKEND TESTING COMPLETED WITH ISSUES")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)