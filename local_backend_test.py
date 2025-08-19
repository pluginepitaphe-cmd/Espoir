#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS COMPLETS DU BACKEND SIPORTS LOCAL - VALIDATION FONCTIONNELLE
Test exhaustif du backend local avant déploiement Railway
URL: http://localhost:8001
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class SiportsLocalTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.admin_token = None
        self.exposant_token = None
        self.visitor_token = None
        
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
            "visitor": {"email": "visitor@example.com", "password": "visitor123"}
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
                    sample_exposant = exposants[0] if exposants else {}
                    required_fields = ["name", "category", "description", "stand", "hall", 
                                     "website", "email", "phone", "specialties", "products"]
                    missing_fields = []
                    for field in required_fields:
                        if not sample_exposant.get(field):
                            missing_fields.append(field)
                            complete_details = False
                    
                    if complete_details:
                        self.log_test("Exposants List", True, 
                                    f"Total: {total}, Détails complets vérifiés")
                    else:
                        self.log_test("Exposants List", True, 
                                    f"Total: {total}, Champs manquants: {missing_fields}")
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
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Admin Dashboard Stats", False, error=f"Missing fields: {missing}")
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
                self.log_test("Chatbot IA", False, error=f"HTTP {response.status_code}: {response.text}")
                
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

    def test_database_sqlite(self):
        """Test 10: Base de données SQLite"""
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
                self.log_test("SQLite Database", True, "User registration successful")
            else:
                # Check if it's a duplicate user error (which still means DB is working)
                if response.status_code == 400 and "existant" in response.text:
                    self.log_test("SQLite Database", True, "Database responding (duplicate user)")
                else:
                    self.log_test("SQLite Database", False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            self.log_test("SQLite Database", False, error=str(e))

    def test_exposant_detail(self):
        """Test 11: GET /api/exposants/{id} (détail exposant)"""
        try:
            # Test with exposant ID 1
            response = self.session.get(f"{self.api_url}/exposants/1", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "category", "description", "products", "team"]
                
                if all(field in data for field in required_fields):
                    products_count = len(data.get("products", []))
                    team_count = len(data.get("team", []))
                    self.log_test("Exposant Detail", True, 
                                f"Produits: {products_count}, Équipe: {team_count}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Exposant Detail", False, error=f"Missing fields: {missing}")
            else:
                self.log_test("Exposant Detail", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Exposant Detail", False, error=str(e))

    def test_specialized_chatbot_endpoints(self):
        """Test 12: Endpoints chatbot spécialisés"""
        endpoints = [
            ("exhibitor", "Recommandez-moi des exposants en technologies marines"),
            ("package", "Quel forfait visiteur me recommandez-vous?"),
            ("event", "Quels sont les événements prévus aujourd'hui?")
        ]
        
        for endpoint, message in endpoints:
            try:
                test_message = {
                    "message": message,
                    "session_id": f"test_{endpoint}_001"
                }
                
                response = self.session.post(f"{self.api_url}/chat/{endpoint}", 
                                           json=test_message, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data:
                        self.log_test(f"Chatbot {endpoint.title()}", True, 
                                    f"Réponse: {len(data['response'])} chars")
                    else:
                        self.log_test(f"Chatbot {endpoint.title()}", False, 
                                    error="Missing response field")
                else:
                    self.log_test(f"Chatbot {endpoint.title()}", False, 
                                error=f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Chatbot {endpoint.title()}", False, error=str(e))

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("=" * 80)
        print("🚀 TESTS COMPLETS DU BACKEND SIPORTS LOCAL - VALIDATION FONCTIONNELLE")
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
        self.test_database_sqlite()
        self.test_exposant_detail()
        self.test_specialized_chatbot_endpoints()
        
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
    tester = SiportsLocalTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: Backend local validé - Prêt pour déploiement Railway")
    else:
        print("\n🔧 CONCLUSION: Corrections nécessaires avant déploiement Railway")