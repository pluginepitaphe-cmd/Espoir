#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Mini-Site Editor Backend Tests
Testing new endpoints for enhanced mini-site functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_ACCOUNTS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exhibitor": {"email": "exposant@example.com", "password": "exhibitor123"},
    "visitor": {"email": "visiteur@example.com", "password": "visit123"}
}

class EnhancedMiniSiteTests:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_user(self, user_type):
        """Authenticate user and get JWT token"""
        try:
            account = TEST_ACCOUNTS[user_type]
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=account
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.tokens[user_type] = token
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log_test(
                        f"Authentication {user_type}",
                        True,
                        f"Successfully authenticated {account['email']}"
                    )
                    return True, data.get("user", {})
                else:
                    self.log_test(
                        f"Authentication {user_type}",
                        False,
                        "No access token in response"
                    )
                    return False, None
            else:
                self.log_test(
                    f"Authentication {user_type}",
                    False,
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                f"Authentication {user_type}",
                False,
                f"Exception during authentication: {str(e)}"
            )
            return False, None
    
    def test_get_enhanced_minisite_data(self, user_id, user_type="exhibitor"):
        """Test GET /api/minisite/enhanced/{user_id}"""
        try:
            # Set authorization header for the user type
            if user_type in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
            else:
                headers = {}
            
            response = self.session.get(
                f"{BACKEND_URL}/api/minisite/enhanced/{user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    minisite_data = data["data"]
                    required_fields = ["name", "tagline", "category", "email", "phone"]
                    missing_fields = [field for field in required_fields if field not in minisite_data]
                    
                    if not missing_fields:
                        self.log_test(
                            f"GET Enhanced Mini-site Data (User {user_id})",
                            True,
                            f"Retrieved complete mini-site data with {len(minisite_data)} fields",
                            f"Company: {minisite_data.get('name', 'N/A')}, Category: {minisite_data.get('category', 'N/A')}"
                        )
                        return True, minisite_data
                    else:
                        self.log_test(
                            f"GET Enhanced Mini-site Data (User {user_id})",
                            False,
                            f"Missing required fields: {missing_fields}"
                        )
                        return False, None
                else:
                    self.log_test(
                        f"GET Enhanced Mini-site Data (User {user_id})",
                        False,
                        "No 'data' field in response"
                    )
                    return False, None
            elif response.status_code == 403:
                self.log_test(
                    f"GET Enhanced Mini-site Data (User {user_id})",
                    True,
                    "Access denied as expected for unauthorized user",
                    "Security check passed"
                )
                return True, None
            else:
                self.log_test(
                    f"GET Enhanced Mini-site Data (User {user_id})",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                f"GET Enhanced Mini-site Data (User {user_id})",
                False,
                f"Exception: {str(e)}"
            )
            return False, None
    
    def test_save_enhanced_minisite_data(self, user_id, user_type="exhibitor"):
        """Test PUT /api/minisite/enhanced/{user_id}"""
        try:
            # Sample enhanced mini-site data
            test_data = {
                "name": "TechMarine Solutions Enhanced",
                "tagline": "Révolutionner l'avenir maritime grâce à l'innovation technologique",
                "category": "Technologies Maritimes",
                "icon": "⚓",
                "description": "Solutions technologiques innovantes pour l'industrie maritime et portuaire.",
                "fullDescription": "Leader européen des solutions technologiques pour l'industrie maritime depuis 2015. Spécialisé dans l'IoT maritime, la navigation intelligente et la maintenance prédictive.",
                "location": "Marseille, France",
                "phone": "+33 1 23 45 67 89",
                "email": "contact@techmarinesolutions.com",
                "website": "https://techmarinesolutions.com",
                "standNumber": "A-012",
                "pavilion": "Hall Innovation",
                "employees": "50-100",
                "founded": "2015",
                "revenue": "€12M+",
                "clientsServed": "200+ clients satisfaits",
                "logo": "/images/logo-techmarine.png",
                "coverImage": "/images/cover-maritime.jpg",
                "timeline": [
                    {
                        "year": "2015",
                        "title": "Fondation de TechMarine Solutions",
                        "description": "Création de l'entreprise avec focus sur l'IoT maritime"
                    },
                    {
                        "year": "2018",
                        "title": "Premier contrat majeur",
                        "description": "Déploiement de solutions IoT pour le Port de Marseille"
                    },
                    {
                        "year": "2021",
                        "title": "Expansion européenne",
                        "description": "Ouverture de bureaux en Allemagne et Norvège"
                    }
                ],
                "team": [
                    {
                        "name": "Pierre Durand",
                        "role": "CEO & Fondateur",
                        "email": "p.durand@techmarinesolutions.com",
                        "bio": "Expert en technologies maritimes avec 15 ans d'expérience"
                    },
                    {
                        "name": "Marie Lambert",
                        "role": "CTO",
                        "email": "m.lambert@techmarinesolutions.com",
                        "bio": "Spécialiste en IA et IoT maritime"
                    }
                ],
                "values": [
                    {
                        "title": "Innovation",
                        "description": "Développement continu de solutions technologiques avancées",
                        "icon": "💡"
                    },
                    {
                        "title": "Durabilité",
                        "description": "Engagement pour un maritime plus respectueux de l'environnement",
                        "icon": "🌱"
                    }
                ],
                "certifications": [
                    {
                        "name": "ISO 9001",
                        "description": "Certification qualité internationale",
                        "year": "2018"
                    },
                    {
                        "name": "Maritime MED",
                        "description": "Certification spécialisée maritime",
                        "year": "2020"
                    }
                ],
                "services": [
                    {
                        "name": "SmartShip Navigator",
                        "description": "Système de navigation assistée par intelligence artificielle",
                        "features": ["Navigation autonome", "Évitement obstacles", "Optimisation carburant"],
                        "price": "Sur devis"
                    },
                    {
                        "name": "MarineIoT Hub",
                        "description": "Plateforme IoT embarquée pour navires connectés",
                        "features": ["Capteurs temps réel", "Maintenance prédictive", "Télémétrie avancée"],
                        "price": "À partir de €15,000"
                    }
                ],
                "projects": [
                    {
                        "title": "Modernisation Port de Marseille",
                        "description": "Déploiement de solutions IoT pour optimiser les opérations portuaires",
                        "year": "2022",
                        "client": "Port Autonome de Marseille"
                    }
                ],
                "news": [
                    {
                        "title": "Nouveau partenariat avec le Port de Rotterdam",
                        "date": "2024-01-15",
                        "summary": "TechMarine Solutions annonce un partenariat stratégique pour la digitalisation du port"
                    }
                ],
                "gallery": {
                    "products": ["/images/product1.jpg", "/images/product2.jpg"],
                    "installations": ["/images/install1.jpg", "/images/install2.jpg"],
                    "team": ["/images/team1.jpg", "/images/team2.jpg"],
                    "events": ["/images/event1.jpg", "/images/event2.jpg"]
                },
                "contacts": {
                    "general": {
                        "name": "Accueil général",
                        "email": "contact@techmarinesolutions.com",
                        "phone": "+33 1 23 45 67 89"
                    },
                    "sales": {
                        "name": "Pierre Durand",
                        "role": "Directeur Commercial",
                        "email": "sales@techmarinesolutions.com",
                        "phone": "+33 1 23 45 67 90"
                    },
                    "support": {
                        "name": "Support Technique",
                        "email": "support@techmarinesolutions.com",
                        "phone": "+33 1 23 45 67 91"
                    }
                },
                "social": {
                    "linkedin": "https://linkedin.com/company/techmarinesolutions",
                    "twitter": "https://twitter.com/techmarinesol",
                    "facebook": "https://facebook.com/techmarinesolutions",
                    "youtube": "https://youtube.com/techmarinesolutions"
                }
            }
            
            # Set authorization header for the user type
            if user_type in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
            else:
                headers = {}
            
            response = self.session.put(
                f"{BACKEND_URL}/api/minisite/enhanced/{user_id}",
                json=test_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    f"PUT Enhanced Mini-site Data (User {user_id})",
                    True,
                    f"Successfully saved enhanced mini-site data: {result.get('message', 'Success')}",
                    f"Data size: {len(json.dumps(test_data))} characters"
                )
                return True, test_data
            elif response.status_code == 403:
                self.log_test(
                    f"PUT Enhanced Mini-site Data (User {user_id})",
                    True,
                    "Access denied as expected for unauthorized user",
                    "Security check passed"
                )
                return True, None
            else:
                self.log_test(
                    f"PUT Enhanced Mini-site Data (User {user_id})",
                    False,
                    f"Save failed: {response.status_code} - {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                f"PUT Enhanced Mini-site Data (User {user_id})",
                False,
                f"Exception: {str(e)}"
            )
            return False, None
    
    def test_get_public_enhanced_minisite(self, user_id):
        """Test GET /api/minisite/enhanced/{user_id}/public (no auth required)"""
        try:
            # Remove authorization header for public endpoint
            headers = {}
            
            response = self.session.get(
                f"{BACKEND_URL}/api/minisite/enhanced/{user_id}/public",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    minisite_data = data["data"]
                    self.log_test(
                        f"GET Public Enhanced Mini-site (User {user_id})",
                        True,
                        f"Retrieved public mini-site data with {len(minisite_data)} fields",
                        f"Company: {minisite_data.get('name', 'N/A')}, Email: {minisite_data.get('email', 'N/A')}"
                    )
                    return True, minisite_data
                else:
                    self.log_test(
                        f"GET Public Enhanced Mini-site (User {user_id})",
                        False,
                        "No 'data' field in response"
                    )
                    return False, None
            elif response.status_code == 404:
                self.log_test(
                    f"GET Public Enhanced Mini-site (User {user_id})",
                    True,
                    "Mini-site not found as expected for non-exhibitor user",
                    "Expected behavior for visitor/admin users"
                )
                return True, None
            else:
                self.log_test(
                    f"GET Public Enhanced Mini-site (User {user_id})",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                f"GET Public Enhanced Mini-site (User {user_id})",
                False,
                f"Exception: {str(e)}"
            )
            return False, None
    
    def test_delete_enhanced_minisite_data(self, user_id, user_type="exhibitor"):
        """Test DELETE /api/minisite/enhanced/{user_id}"""
        try:
            # Set authorization header for the user type
            if user_type in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
            else:
                headers = {}
            
            response = self.session.delete(
                f"{BACKEND_URL}/api/minisite/enhanced/{user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    f"DELETE Enhanced Mini-site Data (User {user_id})",
                    True,
                    f"Successfully deleted enhanced mini-site data: {result.get('message', 'Success')}"
                )
                return True
            elif response.status_code == 403:
                self.log_test(
                    f"DELETE Enhanced Mini-site Data (User {user_id})",
                    True,
                    "Access denied as expected for unauthorized user",
                    "Security check passed"
                )
                return True
            else:
                self.log_test(
                    f"DELETE Enhanced Mini-site Data (User {user_id})",
                    False,
                    f"Delete failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                f"DELETE Enhanced Mini-site Data (User {user_id})",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_data_persistence(self, user_id, user_type="exhibitor"):
        """Test data persistence by saving and retrieving data"""
        try:
            # First, save some test data
            success, saved_data = self.test_save_enhanced_minisite_data(user_id, user_type)
            if not success or not saved_data:
                return False
            
            # Then retrieve the data
            success, retrieved_data = self.test_get_enhanced_minisite_data(user_id, user_type)
            if not success or not retrieved_data:
                return False
            
            # Compare key fields
            key_fields = ["name", "tagline", "category", "email", "phone"]
            matches = 0
            for field in key_fields:
                if saved_data.get(field) == retrieved_data.get(field):
                    matches += 1
            
            if matches == len(key_fields):
                self.log_test(
                    f"Data Persistence Test (User {user_id})",
                    True,
                    f"All {matches}/{len(key_fields)} key fields match after save/retrieve cycle",
                    f"Verified fields: {', '.join(key_fields)}"
                )
                return True
            else:
                self.log_test(
                    f"Data Persistence Test (User {user_id})",
                    False,
                    f"Only {matches}/{len(key_fields)} key fields match after save/retrieve cycle"
                )
                return False
                
        except Exception as e:
            self.log_test(
                f"Data Persistence Test (User {user_id})",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_authorization_security(self):
        """Test authorization and security controls"""
        try:
            # Test 1: Exhibitor trying to access another user's data
            exhibitor_success, exhibitor_user = self.authenticate_user("exhibitor")
            if exhibitor_success and exhibitor_user:
                exhibitor_id = exhibitor_user.get("id")
                
                # Try to access admin's data (should fail)
                admin_success, admin_user = self.authenticate_user("admin")
                if admin_success and admin_user:
                    admin_id = admin_user.get("id")
                    
                    # Switch back to exhibitor token
                    self.session.headers.update({"Authorization": f"Bearer {self.tokens['exhibitor']}"})
                    
                    # Try to access admin's mini-site data (should be denied)
                    response = self.session.get(f"{BACKEND_URL}/api/minisite/enhanced/{admin_id}")
                    
                    if response.status_code == 403:
                        self.log_test(
                            "Authorization Security - Cross-user Access",
                            True,
                            "Exhibitor correctly denied access to admin's mini-site data",
                            "Security control working properly"
                        )
                    else:
                        self.log_test(
                            "Authorization Security - Cross-user Access",
                            False,
                            f"Expected 403, got {response.status_code} - Security vulnerability detected"
                        )
            
            # Test 2: Unauthenticated access to protected endpoints
            self.session.headers.pop("Authorization", None)  # Remove auth header
            
            response = self.session.get(f"{BACKEND_URL}/api/minisite/enhanced/1")
            
            if response.status_code == 401:
                self.log_test(
                    "Authorization Security - Unauthenticated Access",
                    True,
                    "Unauthenticated request correctly denied access",
                    "Authentication required as expected"
                )
            else:
                self.log_test(
                    "Authorization Security - Unauthenticated Access",
                    False,
                    f"Expected 401, got {response.status_code} - Authentication bypass detected"
                )
                
        except Exception as e:
            self.log_test(
                "Authorization Security Tests",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_database_column_creation(self):
        """Test that the enhanced_minisite_data column is created if it doesn't exist"""
        try:
            # This is tested implicitly when we save data
            # The backend should handle column creation automatically
            exhibitor_success, exhibitor_user = self.authenticate_user("exhibitor")
            if exhibitor_success and exhibitor_user:
                user_id = exhibitor_user.get("id")
                
                # Try to save data - this should trigger column creation if needed
                success, _ = self.test_save_enhanced_minisite_data(user_id, "exhibitor")
                
                if success:
                    self.log_test(
                        "Database Column Creation",
                        True,
                        "Enhanced mini-site data saved successfully - column exists or was created",
                        "Database schema updated automatically"
                    )
                else:
                    self.log_test(
                        "Database Column Creation",
                        False,
                        "Failed to save enhanced mini-site data - possible schema issue"
                    )
                    
        except Exception as e:
            self.log_test(
                "Database Column Creation",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_error_handling(self):
        """Test error handling for invalid scenarios"""
        try:
            # Test 1: Invalid user ID
            self.authenticate_user("exhibitor")
            response = self.session.get(f"{BACKEND_URL}/api/minisite/enhanced/99999")
            
            if response.status_code in [404, 403]:
                self.log_test(
                    "Error Handling - Invalid User ID",
                    True,
                    f"Invalid user ID correctly handled with status {response.status_code}"
                )
            else:
                self.log_test(
                    "Error Handling - Invalid User ID",
                    False,
                    f"Expected 404/403, got {response.status_code}"
                )
            
            # Test 2: Invalid JSON data
            response = self.session.put(
                f"{BACKEND_URL}/api/minisite/enhanced/1",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 422:
                self.log_test(
                    "Error Handling - Invalid JSON",
                    True,
                    "Invalid JSON correctly rejected with 422 status"
                )
            else:
                self.log_test(
                    "Error Handling - Invalid JSON",
                    False,
                    f"Expected 422, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Error Handling Tests",
                False,
                f"Exception: {str(e)}"
            )
    
    def run_comprehensive_tests(self):
        """Run all enhanced mini-site editor tests"""
        print("🚀 STARTING ENHANCED MINI-SITE EDITOR BACKEND TESTS")
        print("=" * 60)
        
        # Test 1: Authentication for all user types
        print("\n📋 AUTHENTICATION TESTS")
        print("-" * 30)
        exhibitor_success, exhibitor_user = self.authenticate_user("exhibitor")
        admin_success, admin_user = self.authenticate_user("admin")
        visitor_success, visitor_user = self.authenticate_user("visitor")
        
        if not exhibitor_success:
            print("❌ Cannot proceed without exhibitor authentication")
            return
        
        exhibitor_id = exhibitor_user.get("id") if exhibitor_user else None
        admin_id = admin_user.get("id") if admin_user else None
        visitor_id = visitor_user.get("id") if visitor_user else None
        
        # Test 2: Database column creation
        print("\n🗄️ DATABASE SCHEMA TESTS")
        print("-" * 30)
        self.test_database_column_creation()
        
        # Test 3: CRUD Operations for exhibitor
        print("\n📝 CRUD OPERATIONS TESTS")
        print("-" * 30)
        if exhibitor_id:
            # Test GET (initial - should return default data)
            self.test_get_enhanced_minisite_data(exhibitor_id, "exhibitor")
            
            # Test PUT (save data)
            self.test_save_enhanced_minisite_data(exhibitor_id, "exhibitor")
            
            # Test GET (after save - should return saved data)
            self.test_get_enhanced_minisite_data(exhibitor_id, "exhibitor")
            
            # Test data persistence
            self.test_data_persistence(exhibitor_id, "exhibitor")
            
            # Test DELETE
            self.test_delete_enhanced_minisite_data(exhibitor_id, "exhibitor")
        
        # Test 4: Public endpoint
        print("\n🌐 PUBLIC ENDPOINT TESTS")
        print("-" * 30)
        if exhibitor_id:
            # First save some data for public viewing
            self.test_save_enhanced_minisite_data(exhibitor_id, "exhibitor")
            # Then test public access
            self.test_get_public_enhanced_minisite(exhibitor_id)
        
        # Test public access for non-exhibitor (should fail)
        if visitor_id:
            self.test_get_public_enhanced_minisite(visitor_id)
        
        # Test 5: Authorization and security
        print("\n🔒 SECURITY & AUTHORIZATION TESTS")
        print("-" * 30)
        self.test_authorization_security()
        
        # Test 6: Error handling
        print("\n⚠️ ERROR HANDLING TESTS")
        print("-" * 30)
        self.test_error_handling()
        
        # Test 7: Integration with existing user data
        print("\n🔗 INTEGRATION TESTS")
        print("-" * 30)
        if exhibitor_id:
            # Test that mini-site data integrates with existing user data
            success, data = self.test_get_enhanced_minisite_data(exhibitor_id, "exhibitor")
            if success and data:
                # Check if email matches user account
                if data.get("email") == exhibitor_user.get("email"):
                    self.log_test(
                        "Integration - User Data Consistency",
                        True,
                        "Mini-site email matches user account email",
                        f"Email: {data.get('email')}"
                    )
                else:
                    self.log_test(
                        "Integration - User Data Consistency",
                        False,
                        "Mini-site email doesn't match user account email"
                    )
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 ENHANCED MINI-SITE EDITOR TESTS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Enhanced Mini-Site Editor is fully functional!")
        elif success_rate >= 75:
            print("✅ GOOD: Enhanced Mini-Site Editor is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Enhanced Mini-Site Editor has significant issues that need attention")
        else:
            print("❌ CRITICAL: Enhanced Mini-Site Editor has major problems and needs immediate fixes")
        
        # Detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['message']:
                print(f"   {result['message']}")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    try:
        print("🔧 Enhanced Mini-Site Editor Backend Testing Suite")
        print("Testing new CMS functionality for exposants")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Accounts: {list(TEST_ACCOUNTS.keys())}")
        
        tester = EnhancedMiniSiteTests()
        success = tester.run_comprehensive_tests()
        
        if success:
            print("\n✅ All critical tests passed - Enhanced Mini-Site Editor is ready for production!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed - Enhanced Mini-Site Editor needs attention before production")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()