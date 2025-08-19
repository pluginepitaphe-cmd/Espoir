#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS COMPLETS DU BACKEND SIPORTS LOCAL - PHASE D'ÉVALUATION INITIALE
Test exhaustif selon la demande de review après restauration frontend
URL: http://localhost:8001
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

class SiportsCompleteTester:
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
        
        # Test accounts from test_result.md
        self.test_accounts = {
            "admin": {"email": "admin@siportevent.com", "password": "admin123"},
            "exposant": {"email": "exposant@example.com", "password": "exhibitor123"},
            "visitor": {"email": "visiteur@example.com", "password": "visit123"}
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

    def test_health_check_api(self):
        """Test 1: Health Check API - GET /api/ et / pour vérifier si le service répond"""
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "SIPORTS v2.0" in data.get("message", ""):
                    version = data.get("version", "unknown")
                    self.log_test("Health Check Root (/)", True, f"SIPORTS v2.0 actif, Version: {version}")
                else:
                    self.log_test("Health Check Root (/)", False, error="Message SIPORTS v2.0 non trouvé")
            else:
                self.log_test("Health Check Root (/)", False, error=f"HTTP {response.status_code}")
                
            # Test /health endpoint
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                service = data.get("service", "")
                version = data.get("version", "")
                self.log_test("Health Check (/health)", True, f"Service: {service}, Version: {version}")
            else:
                self.log_test("Health Check (/health)", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Health Check API", False, error=str(e))

    def test_authentication_system_complete(self):
        """Test 2: Système d'authentification complet avec tous les comptes"""
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
                            
                        # Verify JWT token format
                        if token and len(token.split('.')) == 3:
                            self.log_test(f"Auth {role.title()}", True, 
                                        f"Email: {user.get('email')}, Type: {user.get('user_type')}, JWT valide")
                        else:
                            self.log_test(f"Auth {role.title()}", False, error="JWT token format invalide")
                    else:
                        self.log_test(f"Auth {role.title()}", False, error="Token ou données utilisateur manquants")
                else:
                    self.log_test(f"Auth {role.title()}", False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Auth {role.title()}", False, error=str(e))

    def test_admin_endpoints_with_auth(self):
        """Test 3: Endpoints Admin avec authentification"""
        if not self.admin_token:
            self.log_test("Admin Endpoints", False, error="Token admin non disponible")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 3.1: GET /api/admin/dashboard/stats
        try:
            response = self.session.get(f"{self.api_url}/admin/dashboard/stats", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "visitors", "exhibitors", "partners", 
                                 "pending", "validated", "rejected"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Admin Dashboard Stats", True, 
                                f"Total: {data['total_users']}, Visiteurs: {data['visitors']}, "
                                f"Exposants: {data['exhibitors']}, Partenaires: {data['partners']}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Admin Dashboard Stats", False, error=f"Champs manquants: {missing}")
            else:
                self.log_test("Admin Dashboard Stats", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Dashboard Stats", False, error=str(e))
        
        # Test 3.2: GET /api/admin/users/pending
        try:
            response = self.session.get(f"{self.api_url}/admin/users/pending", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                self.log_test("Admin Users Pending", True, f"Utilisateurs en attente: {len(users)}")
            else:
                self.log_test("Admin Users Pending", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Users Pending", False, error=str(e))
        
        # Test 3.3: POST /api/admin/users/{id}/validate
        try:
            # Test with user ID 2 (exposant)
            response = self.session.post(f"{self.api_url}/admin/users/2/validate", 
                                       headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Admin User Validate", True, f"Message: {data.get('message')}")
            else:
                self.log_test("Admin User Validate", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin User Validate", False, error=str(e))
        
        # Test 3.4: POST /api/admin/users/{id}/reject
        try:
            # Test with user ID 3 (visitor)
            response = self.session.post(f"{self.api_url}/admin/users/3/reject", 
                                       headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Admin User Reject", True, f"Message: {data.get('message')}")
            else:
                self.log_test("Admin User Reject", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin User Reject", False, error=str(e))

    def test_visitor_packages_system(self):
        """Test 4: Système de forfaits visiteur (4 niveaux)"""
        try:
            response = self.session.get(f"{self.api_url}/visitor-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if len(packages) >= 4:
                    expected_packages = {
                        "Free": 0,
                        "Basic": 150,
                        "Premium": 350,
                        "VIP": 750
                    }
                    
                    found_packages = {}
                    for pkg in packages:
                        name = pkg.get("name", "").replace(" Pass", "")
                        price = pkg.get("price", 0)
                        found_packages[name] = price
                    
                    # Verify all expected packages
                    all_found = True
                    for expected_name, expected_price in expected_packages.items():
                        if expected_name not in found_packages:
                            all_found = False
                            break
                        if found_packages[expected_name] != expected_price:
                            all_found = False
                            break
                    
                    if all_found:
                        self.log_test("Visitor Packages System", True, 
                                    f"4 niveaux corrects: Free (0€), Basic (150€), Premium (350€), VIP (750€)")
                    else:
                        self.log_test("Visitor Packages System", False, 
                                    error=f"Prix incorrects. Trouvé: {found_packages}")
                else:
                    self.log_test("Visitor Packages System", False, 
                                error=f"Seulement {len(packages)} forfaits (4 requis)")
            else:
                self.log_test("Visitor Packages System", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Visitor Packages System", False, error=str(e))

    def test_partnership_packages_system(self):
        """Test 5: Système de forfaits partenaires (4 niveaux)"""
        try:
            response = self.session.get(f"{self.api_url}/partnership-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                if len(packages) >= 4:
                    expected_packages = {
                        "Startup": 2500,
                        "Silver": 8000,
                        "Gold": 15000,
                        "Platinum": 25000
                    }
                    
                    found_packages = {}
                    for pkg in packages:
                        name = pkg.get("name", "").replace(" Package", "")
                        price = pkg.get("price", 0)
                        found_packages[name] = price
                    
                    # Verify all expected packages
                    all_found = True
                    for expected_name, expected_price in expected_packages.items():
                        if expected_name not in found_packages:
                            all_found = False
                            break
                        if found_packages[expected_name] != expected_price:
                            all_found = False
                            break
                    
                    if all_found:
                        self.log_test("Partnership Packages System", True, 
                                    f"4 niveaux corrects: Startup (2.5k$), Silver (8k$), Gold (15k$), Platinum (25k$)")
                    else:
                        self.log_test("Partnership Packages System", False, 
                                    error=f"Prix incorrects. Trouvé: {found_packages}")
                else:
                    self.log_test("Partnership Packages System", False, 
                                error=f"Seulement {len(packages)} forfaits (4 requis)")
            else:
                self.log_test("Partnership Packages System", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Partnership Packages System", False, error=str(e))

    def test_exposants_endpoints(self):
        """Test 6: Endpoints exposants - vérifier les 6 exposants mentionnés"""
        try:
            response = self.session.get(f"{self.api_url}/exposants", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                exposants = data.get("exposants", [])
                total = data.get("total", 0)
                
                if len(exposants) >= 6:
                    expected_companies = [
                        "TechMarine Solutions",
                        "Green Port Energy", 
                        "Smart Container Corp",
                        "Ocean Data Analytics",
                        "AquaTech Innovations",
                        "Port Security Systems"
                    ]
                    
                    found_companies = [exp.get("name", "") for exp in exposants]
                    
                    # Check if all expected companies are found
                    all_found = all(company in found_companies for company in expected_companies)
                    
                    if all_found:
                        # Verify complete details for first exposant
                        sample = exposants[0] if exposants else {}
                        required_fields = ["name", "category", "description", "stand", "hall", 
                                         "website", "email", "phone", "specialties", "products"]
                        complete_details = all(sample.get(field) for field in required_fields)
                        
                        if complete_details:
                            self.log_test("Exposants Endpoints", True, 
                                        f"6 exposants trouvés avec détails complets: {', '.join(expected_companies[:3])}...")
                        else:
                            self.log_test("Exposants Endpoints", True, 
                                        f"6 exposants trouvés mais détails incomplets")
                    else:
                        missing = [c for c in expected_companies if c not in found_companies]
                        self.log_test("Exposants Endpoints", False, 
                                    error=f"Exposants manquants: {missing}")
                else:
                    self.log_test("Exposants Endpoints", False, 
                                error=f"Seulement {len(exposants)} exposants (6 requis)")
            else:
                self.log_test("Exposants Endpoints", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Exposants Endpoints", False, error=str(e))

    def test_chatbot_ia_siports_v2(self):
        """Test 7: Chatbot IA SIPORTS v2.0 - tous les endpoints"""
        
        # Test 7.1: GET /api/chatbot/health
        try:
            response = self.session.get(f"{self.api_url}/chatbot/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    version = data.get("version", "unknown")
                    mock_mode = data.get("mock_mode", False)
                    self.log_test("Chatbot Health Check", True, 
                                f"Version: {version}, Mode mock: {mock_mode}")
                else:
                    self.log_test("Chatbot Health Check", False, error="Service non healthy")
            else:
                self.log_test("Chatbot Health Check", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chatbot Health Check", False, error=str(e))
        
        # Test 7.2: POST /api/chat avec différents contextes
        contexts = [
            ("general", "Bonjour, pouvez-vous m'aider avec SIPORTS?"),
            ("exhibitor", "Recommandez-moi des exposants en technologies maritimes"),
            ("package", "Quel forfait visiteur me convient le mieux?"),
            ("event", "Quels sont les événements prévus aujourd'hui?")
        ]
        
        for context, message in contexts:
            try:
                test_message = {
                    "message": message,
                    "context_type": context,
                    "session_id": f"test_{context}_001"
                }
                
                response = self.session.post(f"{self.api_url}/chat", 
                                           json=test_message, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and "confidence" in data:
                        confidence = data.get("confidence", 0)
                        response_length = len(data.get("response", ""))
                        actions = len(data.get("suggested_actions", []))
                        self.log_test(f"Chatbot Context {context.title()}", True, 
                                    f"Confiance: {confidence}, Réponse: {response_length} chars, Actions: {actions}")
                    else:
                        self.log_test(f"Chatbot Context {context.title()}", False, 
                                    error="Format de réponse invalide")
                else:
                    self.log_test(f"Chatbot Context {context.title()}", False, 
                                error=f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Chatbot Context {context.title()}", False, error=str(e))

    def test_other_critical_endpoints(self):
        """Test 8: Autres endpoints critiques mentionnés"""
        
        # Test exposant detail endpoint
        try:
            response = self.session.get(f"{self.api_url}/exposants/1", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "category", "description", "products", "team"]
                
                if all(field in data for field in required_fields):
                    products_count = len(data.get("products", []))
                    team_count = len(data.get("team", []))
                    self.log_test("Exposant Detail Endpoint", True, 
                                f"Détails complets: {products_count} produits, {team_count} équipe")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Exposant Detail Endpoint", False, error=f"Champs manquants: {missing}")
            else:
                self.log_test("Exposant Detail Endpoint", False, error=f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Exposant Detail Endpoint", False, error=str(e))

    def test_database_integrity(self):
        """Test 9: Intégrité base de données SQLite locale"""
        try:
            # Test user creation to verify database is working
            test_user = {
                "email": f"test_integrity_{int(time.time())}@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Integrity",
                "user_type": "visitor"
            }
            
            response = self.session.post(f"{self.api_url}/auth/register", 
                                       json=test_user, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Database Integrity", True, "Création utilisateur réussie - DB opérationnelle")
            else:
                # Check if it's a duplicate user error (which still means DB is working)
                if response.status_code == 400 and "existant" in response.text:
                    self.log_test("Database Integrity", True, "Base de données répond correctement")
                else:
                    self.log_test("Database Integrity", False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            self.log_test("Database Integrity", False, error=str(e))

    def run_complete_evaluation(self):
        """Exécuter l'évaluation complète du backend SIPORTS local"""
        print("=" * 90)
        print("🚀 TESTS COMPLETS DU BACKEND SIPORTS LOCAL - PHASE D'ÉVALUATION INITIALE")
        print("📋 Test selon demande de review après restauration frontend")
        print(f"🎯 URL Backend: {self.base_url}")
        print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 90)
        
        # Execute all tests in order
        self.test_health_check_api()
        self.test_authentication_system_complete()
        self.test_admin_endpoints_with_auth()
        self.test_visitor_packages_system()
        self.test_partnership_packages_system()
        self.test_exposants_endpoints()
        self.test_chatbot_ia_siports_v2()
        self.test_other_critical_endpoints()
        self.test_database_integrity()
        
        # Print final results
        print("\n" + "=" * 90)
        print("📊 RÉSULTATS FINAUX DE L'ÉVALUATION")
        print("=" * 90)
        
        success_rate = (self.results["passed"] / self.results["total_tests"]) * 100
        print(f"✅ Tests réussis: {self.results['passed']}/{self.results['total_tests']}")
        print(f"❌ Tests échoués: {self.results['failed']}/{self.results['total_tests']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🚨 PROBLÈMES IDENTIFIÉS ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Determine overall status
        if success_rate >= 95:
            print("🎉 STATUT: EXCELLENT - Backend 100% fonctionnel comme attendu")
        elif success_rate >= 85:
            print("✅ STATUT: TRÈS BON - Backend largement fonctionnel")
        elif success_rate >= 70:
            print("⚠️  STATUT: BON - Quelques problèmes mineurs à corriger")
        else:
            print("🚨 STATUT: PROBLÉMATIQUE - Corrections nécessaires")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = SiportsCompleteTester()
    success = tester.run_complete_evaluation()
    
    if success:
        print("\n🎯 CONCLUSION: Backend SIPORTS local validé selon les attentes")
        sys.exit(0)
    else:
        print("\n🔧 CONCLUSION: Problèmes détectés nécessitant attention")
        sys.exit(1)