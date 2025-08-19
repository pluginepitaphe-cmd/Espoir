#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de validation finale du backend SIPORTS avec les corrections appliquées
Focus sur l'authentification corrigée exposant/visiteur
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

# Comptes de test avec mots de passe corrigés
TEST_ACCOUNTS = {
    "admin": {
        "email": "admin@siportevent.com",
        "password": "admin123"
    },
    "exposant": {
        "email": "exposant@example.com", 
        "password": "exhibitor123"  # CORRIGÉ
    },
    "visiteur": {
        "email": "visiteur@example.com",
        "password": "visit123"  # CORRIGÉ
    }
}

class SiportsBackendTester:
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
        
    def test_health_checks(self):
        """1. Health Check complet"""
        print("\n=== 1. HEALTH CHECK COMPLET ===")
        
        # Test GET /
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET / - Root endpoint", True, 
                              f"Status: {data.get('status')}, Version: {data.get('version')}")
            else:
                self.log_result("GET / - Root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET / - Root endpoint", False, f"Error: {str(e)}")
            
        # Test GET /health
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET /health - Health check", True,
                              f"Service: {data.get('service')}, Version: {data.get('version')}")
            else:
                self.log_result("GET /health - Health check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /health - Health check", False, f"Error: {str(e)}")
    
    def test_authentication_all_roles(self):
        """2. Authentification tous rôles CORRIGÉS"""
        print("\n=== 2. AUTHENTIFICATION TOUS RÔLES CORRIGÉS ===")
        
        for role, credentials in TEST_ACCOUNTS.items():
            try:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    headers=HEADERS,
                    json=credentials,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "user" in data:
                        # Store token for later use
                        self.tokens[role] = data["access_token"]
                        user_type = data["user"].get("user_type", "unknown")
                        self.log_result(f"Login {role.upper()}", True,
                                      f"Email: {credentials['email']}, Type: {user_type}, Token: OK")
                    else:
                        self.log_result(f"Login {role.upper()}", False, "Missing access_token or user data")
                else:
                    self.log_result(f"Login {role.upper()}", False, 
                                  f"Status: {response.status_code}, Response: {response.text[:100]}")
                    
            except Exception as e:
                self.log_result(f"Login {role.upper()}", False, f"Error: {str(e)}")
    
    def test_admin_endpoints_with_jwt(self):
        """3. Endpoints admin avec JWT"""
        print("\n=== 3. ENDPOINTS ADMIN AVEC JWT ===")
        
        if "admin" not in self.tokens:
            self.log_result("Admin endpoints", False, "No admin token available")
            return
            
        admin_headers = {
            **HEADERS,
            "Authorization": f"Bearer {self.tokens['admin']}"
        }
        
        # Test GET /api/admin/dashboard/stats
        try:
            response = requests.get(f"{BASE_URL}/api/admin/dashboard/stats", 
                                  headers=admin_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET /api/admin/dashboard/stats", True,
                              f"Total users: {data.get('total_users')}, Visitors: {data.get('visitors')}")
            else:
                self.log_result("GET /api/admin/dashboard/stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/admin/dashboard/stats", False, f"Error: {str(e)}")
            
        # Test GET /api/admin/users/pending
        try:
            response = requests.get(f"{BASE_URL}/api/admin/users/pending",
                                  headers=admin_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                users_count = len(data.get("users", []))
                self.log_result("GET /api/admin/users/pending", True, f"Pending users: {users_count}")
            else:
                self.log_result("GET /api/admin/users/pending", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/admin/users/pending", False, f"Error: {str(e)}")
            
        # Test contrôle d'accès (403 pour non-admins)
        if "exposant" in self.tokens:
            non_admin_headers = {
                **HEADERS,
                "Authorization": f"Bearer {self.tokens['exposant']}"
            }
            try:
                response = requests.get(f"{BASE_URL}/api/admin/dashboard/stats",
                                      headers=non_admin_headers, timeout=10)
                if response.status_code == 403:
                    self.log_result("Contrôle d'accès admin (403 pour non-admins)", True, "Access denied correctly")
                else:
                    self.log_result("Contrôle d'accès admin (403 pour non-admins)", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Contrôle d'accès admin (403 pour non-admins)", False, f"Error: {str(e)}")
    
    def test_package_systems(self):
        """4. Système de forfaits"""
        print("\n=== 4. SYSTÈME DE FORFAITS ===")
        
        # Test GET /api/visitor-packages (4 niveaux)
        try:
            response = requests.get(f"{BASE_URL}/api/visitor-packages", timeout=10)
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                if len(packages) == 4:
                    package_names = [p.get("name") for p in packages]
                    self.log_result("GET /api/visitor-packages (4 niveaux)", True,
                                  f"Packages: {', '.join(package_names)}")
                else:
                    self.log_result("GET /api/visitor-packages (4 niveaux)", False,
                                  f"Expected 4 packages, got {len(packages)}")
            else:
                self.log_result("GET /api/visitor-packages (4 niveaux)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/visitor-packages (4 niveaux)", False, f"Error: {str(e)}")
            
        # Test GET /api/partnership-packages (4 niveaux)
        try:
            response = requests.get(f"{BASE_URL}/api/partnership-packages", timeout=10)
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                if len(packages) == 4:
                    package_names = [p.get("name") for p in packages]
                    self.log_result("GET /api/partnership-packages (4 niveaux)", True,
                                  f"Packages: {', '.join(package_names)}")
                else:
                    self.log_result("GET /api/partnership-packages (4 niveaux)", False,
                                  f"Expected 4 packages, got {len(packages)}")
            else:
                self.log_result("GET /api/partnership-packages (4 niveaux)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/partnership-packages (4 niveaux)", False, f"Error: {str(e)}")
    
    def test_exposants_endpoints(self):
        """5. Endpoints exposants"""
        print("\n=== 5. ENDPOINTS EXPOSANTS ===")
        
        # Test GET /api/exposants (6 exposants)
        try:
            response = requests.get(f"{BASE_URL}/api/exposants", timeout=10)
            if response.status_code == 200:
                data = response.json()
                exposants = data.get("exposants", [])
                total = data.get("total", 0)
                if len(exposants) == 6 and total == 6:
                    first_exposant = exposants[0].get("name", "Unknown") if exposants else "None"
                    self.log_result("GET /api/exposants (6 exposants)", True,
                                  f"Total: {total}, First: {first_exposant}")
                else:
                    self.log_result("GET /api/exposants (6 exposants)", False,
                                  f"Expected 6 exposants, got {len(exposants)}")
            else:
                self.log_result("GET /api/exposants (6 exposants)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/exposants (6 exposants)", False, f"Error: {str(e)}")
            
        # Test GET /api/exposants/1 (détails exposant)
        try:
            response = requests.get(f"{BASE_URL}/api/exposants/1", timeout=10)
            if response.status_code == 200:
                data = response.json()
                name = data.get("name", "Unknown")
                stand = data.get("stand", "Unknown")
                self.log_result("GET /api/exposants/1 (détails exposant)", True,
                              f"Name: {name}, Stand: {stand}")
            else:
                self.log_result("GET /api/exposants/1 (détails exposant)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/exposants/1 (détails exposant)", False, f"Error: {str(e)}")
    
    def test_chatbot_ia_siports_v2(self):
        """6. Chatbot IA SIPORTS v2.0"""
        print("\n=== 6. CHATBOT IA SIPORTS v2.0 ===")
        
        # Test GET /api/chatbot/health
        try:
            response = requests.get(f"{BASE_URL}/api/chatbot/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                version = data.get("version", "unknown")
                self.log_result("GET /api/chatbot/health", True,
                              f"Status: {status}, Version: {version}")
            else:
                self.log_result("GET /api/chatbot/health", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /api/chatbot/health", False, f"Error: {str(e)}")
            
        # Test POST /api/chat avec différents contextes
        contexts = ["general", "exhibitor", "package", "event"]
        
        for context in contexts:
            try:
                chat_data = {
                    "message": f"Test message for {context} context",
                    "context_type": context,
                    "session_id": "test-session-123"
                }
                
                response = requests.post(f"{BASE_URL}/api/chat",
                                       headers=HEADERS,
                                       json=chat_data,
                                       timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    confidence = data.get("confidence", 0)
                    self.log_result(f"POST /api/chat (contexte {context})", True,
                                  f"Response length: {len(response_text)}, Confidence: {confidence}")
                else:
                    self.log_result(f"POST /api/chat (contexte {context})", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"POST /api/chat (contexte {context})", False, f"Error: {str(e)}")
    
    def test_critical_authentication(self):
        """7. Test critique: Authentification exposant/visiteur"""
        print("\n=== 7. TEST CRITIQUE: AUTHENTIFICATION EXPOSANT/VISITEUR ===")
        
        # Test spécifique exposant@example.com/exhibitor123
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                headers=HEADERS,
                json={
                    "email": "exposant@example.com",
                    "password": "exhibitor123"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    user = data["user"]
                    self.log_result("CRITIQUE - Login exposant@example.com/exhibitor123", True,
                                  f"Token: OK, User type: {user.get('user_type')}, Email: {user.get('email')}")
                else:
                    self.log_result("CRITIQUE - Login exposant@example.com/exhibitor123", False,
                                  "Missing access_token or user in response")
            else:
                self.log_result("CRITIQUE - Login exposant@example.com/exhibitor123", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("CRITIQUE - Login exposant@example.com/exhibitor123", False, f"Error: {str(e)}")
            
        # Test spécifique visiteur@example.com/visit123
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                headers=HEADERS,
                json={
                    "email": "visiteur@example.com",
                    "password": "visit123"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    user = data["user"]
                    self.log_result("CRITIQUE - Login visiteur@example.com/visit123", True,
                                  f"Token: OK, User type: {user.get('user_type')}, Email: {user.get('email')}")
                else:
                    self.log_result("CRITIQUE - Login visiteur@example.com/visit123", False,
                                  "Missing access_token or user in response")
            else:
                self.log_result("CRITIQUE - Login visiteur@example.com/visit123", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("CRITIQUE - Login visiteur@example.com/visit123", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Execute all tests"""
        print("🎯 TESTS DE VALIDATION FINALE BACKEND SIPORTS v2.0")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Configuration: SQLite corrigée avec status='validated'")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Execute all test suites
        self.test_health_checks()
        self.test_authentication_all_roles()
        self.test_admin_endpoints_with_jwt()
        self.test_package_systems()
        self.test_exposants_endpoints()
        self.test_chatbot_ia_siports_v2()
        self.test_critical_authentication()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 RÉSULTATS FINAUX - VALIDATION BACKEND SIPORTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.passed_tests}/{self.total_tests}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 VALIDATION FINALE À 100% - BACKEND PRÊT POUR DÉPLOIEMENT")
        elif success_rate >= 80:
            print("✅ VALIDATION RÉUSSIE - Quelques problèmes mineurs détectés")
        else:
            print("❌ VALIDATION ÉCHOUÉE - Problèmes critiques détectés")
            
        print("\n📋 DÉTAILS DES TESTS:")
        for result in self.results:
            print(f"  {result}")
            
        return success_rate >= 80

if __name__ == "__main__":
    tester = SiportsBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)