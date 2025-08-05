#!/usr/bin/env python3
"""
Additional Backend API Tests for SIPORTS
Testing mini-site endpoints and other functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://ec48b228-5fe8-445c-98da-33775eea8a9d.preview.emergentagent.com/api"

# Test credentials
ADMIN_USER = {
    "email": "admin@siportevent.com",
    "password": "admin123"
}

EXPOSANT_USER = {
    "email": "exposant@example.com",
    "password": "expo123"
}

class AdditionalEndpointTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.admin_token = None
        self.exposant_token = None
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
                user_type = data.get("user", {}).get("user_type")
                
                if user_type == "admin":
                    self.log_test("Admin Authentication", True, f"Successfully logged in as admin")
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
    
    def authenticate_exposant(self):
        """Authenticate with exposant credentials"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=EXPOSANT_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.exposant_token = data.get("access_token")
                user_type = data.get("user", {}).get("user_type")
                
                self.log_test("Exposant Authentication", True, f"Successfully logged in as {user_type}")
                return True
            else:
                self.log_test("Exposant Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Exposant Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin authentication token"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def get_exposant_headers(self):
        """Get headers with exposant authentication token"""
        if not self.exposant_token:
            return {}
        return {"Authorization": f"Bearer {self.exposant_token}"}
    
    def test_visitor_packages(self):
        """Test visitor packages endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/visitor-packages",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) > 0:
                    package_names = [p.get("name", "Unknown") for p in packages]
                    self.log_test("Visitor Packages", True, 
                                f"Retrieved {len(packages)} visitor packages: {', '.join(package_names)}")
                    return True
                else:
                    self.log_test("Visitor Packages", False, "No packages found or invalid format")
                    return False
            else:
                self.log_test("Visitor Packages", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Visitor Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_partnership_packages(self):
        """Test partnership packages endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/partnership-packages",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) > 0:
                    package_names = [p.get("name", "Unknown") for p in packages]
                    self.log_test("Partnership Packages", True, 
                                f"Retrieved {len(packages)} partnership packages: {', '.join(package_names)}")
                    return True
                else:
                    self.log_test("Partnership Packages", False, "No packages found or invalid format")
                    return False
            else:
                self.log_test("Partnership Packages", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Partnership Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_exhibition_packages(self):
        """Test exhibition packages endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/exhibition-packages",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if isinstance(packages, list) and len(packages) > 0:
                    package_names = [p.get("name", "Unknown") for p in packages]
                    self.log_test("Exhibition Packages", True, 
                                f"Retrieved {len(packages)} exhibition packages: {', '.join(package_names)}")
                    return True
                else:
                    self.log_test("Exhibition Packages", False, "No packages found or invalid format")
                    return False
            else:
                self.log_test("Exhibition Packages", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Exhibition Packages", False, f"Request error: {str(e)}")
            return False
    
    def test_matching_generate(self):
        """Test matching generation endpoint"""
        if not self.exposant_token:
            self.log_test("Matching Generate", False, "No exposant authentication token")
            return False
            
        try:
            filters = {
                "match_type": "all",
                "sector": "all",
                "compatibility": 70,
                "location": "all",
                "package_level": "all"
            }
            
            response = requests.post(
                f"{self.base_url}/matching/generate",
                json=filters,
                headers=self.get_exposant_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                if isinstance(matches, list):
                    self.log_test("Matching Generate", True, 
                                f"Generated {len(matches)} matches successfully")
                    return True
                else:
                    self.log_test("Matching Generate", False, "Invalid matches format")
                    return False
            else:
                self.log_test("Matching Generate", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Matching Generate", False, f"Request error: {str(e)}")
            return False
    
    def test_matching_analytics(self):
        """Test matching analytics endpoint"""
        if not self.exposant_token:
            self.log_test("Matching Analytics", False, "No exposant authentication token")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/matching/analytics",
                headers=self.get_exposant_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["compatibility_avg", "quality_matches", "response_rate", "total_matches"]
                if all(field in data for field in required_fields):
                    self.log_test("Matching Analytics", True, 
                                f"Analytics retrieved: {data['total_matches']} total matches, {data['compatibility_avg']}% avg compatibility")
                    return True
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_test("Matching Analytics", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Matching Analytics", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Matching Analytics", False, f"Request error: {str(e)}")
            return False
    
    def test_user_package_status(self):
        """Test user package status endpoint"""
        if not self.exposant_token:
            self.log_test("User Package Status", False, "No exposant authentication token")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/user-package-status",
                headers=self.get_exposant_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["package_id", "is_expired", "b2b_meetings"]
                if all(field in data for field in required_fields):
                    package_id = data.get("package_id", "unknown")
                    meetings = data.get("b2b_meetings", {})
                    self.log_test("User Package Status", True, 
                                f"Package status retrieved: {package_id} package, {meetings.get('remaining', 0)} meetings remaining")
                    return True
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_test("User Package Status", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("User Package Status", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Package Status", False, f"Request error: {str(e)}")
            return False
    
    def test_features_endpoint(self):
        """Test features endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/features",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "features" in data and "version" in data:
                    features = data.get("features", [])
                    version = data.get("version", "unknown")
                    self.log_test("Features Endpoint", True, 
                                f"Features retrieved: {len(features)} features, version {version}")
                    return True
                else:
                    self.log_test("Features Endpoint", False, "Missing features or version in response")
                    return False
            else:
                self.log_test("Features Endpoint", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Features Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_visitor_login(self):
        """Test visitor login endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/visitor-login",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data and "user" in data:
                    user = data.get("user", {})
                    user_type = user.get("user_type", "unknown")
                    self.log_test("Visitor Login", True, 
                                f"Visitor login successful, user_type: {user_type}")
                    return True
                else:
                    self.log_test("Visitor Login", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test("Visitor Login", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Visitor Login", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all additional endpoint tests"""
        print("🚀 Starting Additional Backend API Tests for SIPORTS")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Authenticate
        admin_auth = self.authenticate_admin()
        exposant_auth = self.authenticate_exposant()
        
        # Public endpoints (no auth required)
        public_tests = [
            self.test_visitor_packages,
            self.test_partnership_packages,
            self.test_exhibition_packages,
            self.test_features_endpoint,
            self.test_visitor_login
        ]
        
        # Authenticated endpoints
        auth_tests = []
        if exposant_auth:
            auth_tests.extend([
                self.test_matching_generate,
                self.test_matching_analytics,
                self.test_user_package_status
            ])
        
        all_tests = public_tests + auth_tests
        
        passed = 0
        total = len(all_tests)
        
        for test in all_tests:
            if test():
                passed += 1
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All additional endpoint tests PASSED!")
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
    tester = AdditionalEndpointTester()
    success = tester.run_all_tests()
    
    # Print detailed summary
    summary = tester.get_summary()
    print(f"\n📈 Success Rate: {summary['success_rate']:.1f}%")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()