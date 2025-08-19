#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS COMPLETS DU BACKEND SIPORTS - VALIDATION PRODUCTION
Test exhaustif du backend Railway en production
URL: https://siportevent-production.up.railway.app
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class SiportsRailwayTester:
    def __init__(self):
        self.base_url = "https://siportevent-production.up.railway.app"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.admin_token = None
        self.exposant_token = None
        self.visitor_token = None
        self.partner_token = None
        
        # Test results
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": []
        }
        
        # Test accounts
        self.test_accounts = {
            "admin": {"email": "admin@siportevent.com", "password": "admin123"},
            "exposant": {"email": "exposant@example.com", "password": "exhibitor123"},
            "visitor": {"email": "visitor@example.com", "password": "visitor123"},
            "partner": {"email": "partenaire@example.com", "password": "part123"}
        }

    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
            if error:
                self.results["errors"].append(f"{test_name}: {error}")
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        if error:
            result += f" | ERROR: {error}"
            
        self.results["details"].append(result)
        print(result)

    def test_health_check(self):
        """Test 1: Health check général"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "SIPORTS" in data.get("message", ""):
                    self.log_test("Health Check Root", True, f"Status: {data.get('status')}, Version: {data.get('version')}")
                else:
                    self.log_test("Health Check Root", False, error="Invalid response format")
            else:
                self.log_test("Health Check Root", False, error=f"HTTP {response.status_code}")
                
            # Test /health endpoint
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check Endpoint", True, f"Service: {data.get('service')}")
            else:
                self.log_test("Health Check Endpoint", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))

    def test_authentication_all_roles(self):
        """Test 2: Authentification multi-rôles"""
        for role, credentials in self.test_accounts.items():
            try:
                response = self.session.post(
                    f"{self.api_url}/auth/login",
                    json=credentials,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "user" in data:
                        token = data["access_token"]
                        user = data["user"]
                        
                        # Store tokens for later use
                        if role == "admin":
                            self.admin_token = token
                        elif role == "exposant":
                            self.exposant_token = token
                        elif role == "visitor":
                            self.visitor_token = token
                        elif role == "partner":
                            self.partner_token = token
                            
                        self.log_test(f"Auth {role.title()}", True, 
                                    f"User: {user.get('email')}, Type: {user.get('user_type')}")
                    else:
                        self.log_test(f"Auth {role.title()}", False, error="Missing token or user data")
                else:
                    self.log_test(f"Auth {role.title()}", False, error=f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Auth {role.title()}", False, error=str(e))

    def test_exposants_endpoint(self):
        """Test 3: GET /api/exposants (liste complète)"""
        try:
            response = self.session.get(f"{self.api_url}/exposants", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                exposants = data.get("exposants", [])
                total = data.get("total", 0)
                
                if len(exposants) >= 6:  # Minimum 6 entreprises attendues
                    # Vérifier les détails complets
                    complete_details = True
                    for exp in exposants[:3]:  # Check first 3 for details
                        required_fields = ["name", "category", "description", "stand", "hall", 
                                         "website", "email", "phone", "specialties", "products"]
                        for field in required_fields:
                            if not exp.get(field):
                                complete_details = False
                                break
                    
                    if complete_details:
                        self.log_test("Exposants List", True, 
                                    f"Total: {total}, Détails complets vérifiés")
                    else:
                        self.log_test("Exposants List", False, error="Détails incomplets")
                else:
                    self.log_test("Exposants List", False, 
                                error=f"Seulement {len(exposants)} exposants (minimum 6 requis)")
            else:
                self.log_test("Exposants List", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Exposants List", False, error=str(e))

    def test_visitor_packages(self):
        """Test 4: GET /api/visitor-packages (forfaits visiteur)"""
        try:
            response = self.session.get(f"{self.api_url}/visitor-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if len(packages) >= 4:  # 4 niveaux attendus
                    expected_names = ["Free Pass", "Basic Pass", "Premium Pass", "VIP Pass"]
                    found_names = [pkg.get("name") for pkg in packages]
                    
                    if all(name in found_names for name in expected_names):
                        # Vérifier les prix
                        prices = [pkg.get("price") for pkg in packages]
                        self.log_test("Visitor Packages", True, 
                                    f"4 niveaux trouvés: {found_names}, Prix: {prices}")
                    else:
                        self.log_test("Visitor Packages", False, 
                                    error=f"Noms incorrects: {found_names}")
                else:
                    self.log_test("Visitor Packages", False, 
                                error=f"Seulement {len(packages)} forfaits (4 requis)")
            else:
                self.log_test("Visitor Packages", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Visitor Packages", False, error=str(e))

    def test_partnership_packages(self):
        """Test 5: GET /api/partnership-packages (forfaits partenaire)"""
        try:
            response = self.session.get(f"{self.api_url}/partnership-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if len(packages) >= 4:  # 4 niveaux attendus
                    expected_names = ["Startup Package", "Silver Package", "Gold Package", "Platinum Package"]
                    found_names = [pkg.get("name") for pkg in packages]
                    
                    if all(name in found_names for name in expected_names):
                        # Vérifier les prix
                        prices = [pkg.get("price") for pkg in packages]
                        self.log_test("Partnership Packages", True, 
                                    f"4 niveaux trouvés: {found_names}, Prix: {prices}")
                    else:
                        self.log_test("Partnership Packages", False, 
                                    error=f"Noms incorrects: {found_names}")
                else:
                    self.log_test("Partnership Packages", False, 
                                error=f"Seulement {len(packages)} forfaits (4 requis)")
            else:
                self.log_test("Partnership Packages", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Partnership Packages", False, error=str(e))

    def test_admin_dashboard_stats(self):
        """Test 6: GET /api/admin/dashboard/stats (stats admin)"""
        if not self.admin_token:
            self.log_test("Admin Dashboard Stats", False, error="No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.api_url}/admin/dashboard/stats", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "visitors", "exhibitors", "partners", 
                                 "pending", "validated", "rejected"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Admin Dashboard Stats", True, 
                                f"Total users: {data['total_users']}, "
                                f"Visitors: {data['visitors']}, "
                                f"Exhibitors: {data['exhibitors']}")
                else:
                    self.log_test("Admin Dashboard Stats", False, error="Missing required fields")
            else:
                self.log_test("Admin Dashboard Stats", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, error=str(e))

    def test_chatbot_endpoint(self):
        """Test 7: POST /api/chat (chatbot IA)"""
        try:
            test_message = {
                "message": "Bonjour, pouvez-vous me recommander des exposants spécialisés en IoT maritime?",
                "context_type": "exhibitor",
                "session_id": "test_session_001"
            }
            
            response = self.session.post(f"{self.api_url}/chat", 
                                       json=test_message, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "confidence" in data:
                    confidence = data.get("confidence", 0)
                    response_length = len(data.get("response", ""))
                    self.log_test("Chatbot IA", True, 
                                f"Confiance: {confidence}, Réponse: {response_length} chars")
                else:
                    self.log_test("Chatbot IA", False, error="Format de réponse invalide")
            else:
                self.log_test("Chatbot IA", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chatbot IA", False, error=str(e))

    def test_chatbot_health(self):
        """Test 8: GET /api/chatbot/health"""
        try:
            response = self.session.get(f"{self.api_url}/chatbot/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    version = data.get("version", "unknown")
                    mock_mode = data.get("mock_mode", False)
                    self.log_test("Chatbot Health", True, 
                                f"Version: {version}, Mock mode: {mock_mode}")
                else:
                    self.log_test("Chatbot Health", False, error="Service not healthy")
            else:
                self.log_test("Chatbot Health", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chatbot Health", False, error=str(e))

    def test_admin_users_management(self):
        """Test 9: Admin user management endpoints"""
        if not self.admin_token:
            self.log_test("Admin Users Management", False, error="No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test pending users
        try:
            response = self.session.get(f"{self.api_url}/admin/users/pending", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                self.log_test("Admin Pending Users", True, f"Pending users: {len(users)}")
            else:
                self.log_test("Admin Pending Users", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Pending Users", False, error=str(e))

    def test_cors_configuration(self):
        """Test 10: Configuration CORS pour Vercel"""
        try:
            # Test preflight request
            headers = {
                "Origin": "https://siports-maritime.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            response = self.session.options(f"{self.api_url}/auth/login", 
                                          headers=headers, timeout=10)
            
            cors_headers = response.headers
            if "Access-Control-Allow-Origin" in cors_headers:
                self.log_test("CORS Configuration", True, 
                            f"CORS headers present: {list(cors_headers.keys())}")
            else:
                self.log_test("CORS Configuration", False, error="Missing CORS headers")
                
        except Exception as e:
            self.log_test("CORS Configuration", False, error=str(e))

    def test_performance_stability(self):
        """Test 11: Performance et stabilité"""
        try:
            # Test multiple rapid requests
            start_time = time.time()
            successful_requests = 0
            
            for i in range(5):
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                time.sleep(0.2)  # Small delay between requests
            
            end_time = time.time()
            total_time = end_time - start_time
            
            if successful_requests >= 4:  # At least 80% success
                self.log_test("Performance Stability", True, 
                            f"{successful_requests}/5 requests successful in {total_time:.2f}s")
            else:
                self.log_test("Performance Stability", False, 
                            error=f"Only {successful_requests}/5 requests successful")
                
        except Exception as e:
            self.log_test("Performance Stability", False, error=str(e))

    def test_error_handling(self):
        """Test 12: Gestion d'erreurs"""
        try:
            # Test invalid endpoint
            response = self.session.get(f"{self.api_url}/invalid-endpoint", timeout=10)
            if response.status_code == 404:
                self.log_test("Error Handling 404", True, "Correct 404 response")
            else:
                self.log_test("Error Handling 404", False, 
                            error=f"Expected 404, got {response.status_code}")
            
            # Test invalid authentication
            headers = {"Authorization": "Bearer invalid-token"}
            response = self.session.get(f"{self.api_url}/admin/dashboard/stats", 
                                      headers=headers, timeout=10)
            if response.status_code == 401:
                self.log_test("Error Handling Auth", True, "Correct 401 response")
            else:
                self.log_test("Error Handling Auth", False, 
                            error=f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling", False, error=str(e))

    def test_database_postgresql(self):
        """Test 13: Base de données PostgreSQL"""
        # Test through API endpoints that require database
        try:
            # Test user creation (which requires database)
            test_user = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User",
                "user_type": "visitor"
            }
            
            response = self.session.post(f"{self.api_url}/auth/register", 
                                       json=test_user, timeout=10)
            
            if response.status_code == 200:
                self.log_test("PostgreSQL Database", True, "User registration successful")
            else:
                # Check if it's a duplicate user error (which still means DB is working)
                if response.status_code == 400 and "existant" in response.text:
                    self.log_test("PostgreSQL Database", True, "Database responding (duplicate user)")
                else:
                    self.log_test("PostgreSQL Database", False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            self.log_test("PostgreSQL Database", False, error=str(e))

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("=" * 80)
        print("🚀 TESTS COMPLETS DU BACKEND SIPORTS - VALIDATION PRODUCTION")
        print(f"🎯 URL: {self.base_url}")
        print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Execute all tests
        self.test_health_check()
        self.test_authentication_all_roles()
        self.test_exposants_endpoint()
        self.test_visitor_packages()
        self.test_partnership_packages()
        self.test_admin_dashboard_stats()
        self.test_chatbot_endpoint()
        self.test_chatbot_health()
        self.test_admin_users_management()
        self.test_cors_configuration()
        self.test_performance_stability()
        self.test_error_handling()
        self.test_database_postgresql()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS FINAUX")
        print("=" * 80)
        
        success_rate = (self.results["passed"] / self.results["total_tests"]) * 100
        print(f"✅ Tests réussis: {self.results['passed']}/{self.results['total_tests']}")
        print(f"❌ Tests échoués: {self.results['failed']}/{self.results['total_tests']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 ERREURS CRITIQUES ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 STATUT: EXCELLENT - Backend prêt pour production")
        elif success_rate >= 75:
            print("✅ STATUT: BON - Backend fonctionnel avec améliorations mineures")
        elif success_rate >= 50:
            print("⚠️  STATUT: MOYEN - Problèmes à corriger avant production")
        else:
            print("🚨 STATUT: CRITIQUE - Corrections majeures requises")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = SiportsRailwayTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: Backend Railway validé pour production finale")
    else:
        print("\n🔧 CONCLUSION: Corrections nécessaires avant validation finale")