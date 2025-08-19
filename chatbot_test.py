#!/usr/bin/env python3
"""
Tests pour les nouveaux endpoints du chatbot IA SIPORTS v2.0
Test complet des 9 nouveaux endpoints chatbot implémentés
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://siports-maritime-1.preview.emergentagent.com/api"

# Comptes de test
TEST_USERS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exposant": {"email": "exposant@example.com", "password": "expo123"},
    "visiteur": {"email": "visiteur@example.com", "password": "visit123"}
}

class ChatbotTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.test_results = []
        self.session_ids = []  # Pour nettoyer après les tests
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Enregistre les résultats de test"""
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
            print(f"   Détails: {details}")
    
    def authenticate(self, user_type: str = "exposant") -> bool:
        """Authentification avec un utilisateur de test"""
        try:
            user_creds = TEST_USERS.get(user_type)
            if not user_creds:
                self.log_test("Authentication", False, f"Utilisateur {user_type} non trouvé")
                return False
                
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=user_creds,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test("Authentication", True, 
                            f"Authentifié comme {user_info.get('user_type', 'unknown')}: {user_creds['email']}")
                return True
            else:
                self.log_test("Authentication", False, 
                            f"Échec login: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Erreur authentification: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Headers avec token d'authentification"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    def test_main_chat_endpoint(self) -> bool:
        """Test POST /api/chat - Endpoint principal du chatbot"""
        try:
            test_messages = [
                {
                    "message": "Bonjour, pouvez-vous m'aider avec SIPORTS ?",
                    "context_type": "general",
                    "expected_keywords": ["bonjour", "siports", "assistant", "aide"]
                },
                {
                    "message": "Quels sont les forfaits disponibles ?",
                    "context_type": "package", 
                    "expected_keywords": ["forfait", "free", "basic", "premium", "vip"]
                },
                {
                    "message": "Recommandez-moi des exposants en technologie maritime",
                    "context_type": "exhibitor",
                    "expected_keywords": ["exposant", "technologie", "maritime", "smart"]
                },
                {
                    "message": "Quel est le programme des événements ?",
                    "context_type": "event",
                    "expected_keywords": ["événement", "programme", "conférence", "horaire"]
                }
            ]
            
            success_count = 0
            for i, test_case in enumerate(test_messages):
                try:
                    response = requests.post(
                        f"{self.base_url}/chat",
                        json={
                            "message": test_case["message"],
                            "context_type": test_case["context_type"],
                            "user_id": "test_user_123"
                        },
                        headers=self.get_auth_headers(),
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Vérifier structure réponse
                        required_fields = ["response", "response_type", "confidence", "suggested_actions", "session_id", "timestamp"]
                        if all(field in data for field in required_fields):
                            
                            # Vérifier contenu pertinent
                            response_text = data["response"].lower()
                            keywords_found = sum(1 for keyword in test_case["expected_keywords"] 
                                               if keyword in response_text)
                            
                            if keywords_found >= 1:  # Au moins 1 mot-clé pertinent
                                success_count += 1
                                # Stocker session_id pour nettoyage
                                if data["session_id"] not in self.session_ids:
                                    self.session_ids.append(data["session_id"])
                                    
                                print(f"   ✅ Test {i+1}: Contexte {test_case['context_type']} - Réponse pertinente")
                                print(f"      Confiance: {data.get('confidence', 'N/A')}, Actions: {len(data.get('suggested_actions', []))}")
                            else:
                                print(f"   ❌ Test {i+1}: Réponse non pertinente pour contexte {test_case['context_type']}")
                        else:
                            missing = [f for f in required_fields if f not in data]
                            print(f"   ❌ Test {i+1}: Champs manquants: {missing}")
                    else:
                        print(f"   ❌ Test {i+1}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Test {i+1}: Erreur - {str(e)}")
            
            if success_count == len(test_messages):
                self.log_test("Main Chat Endpoint", True, 
                            f"Tous les {len(test_messages)} contextes testés avec succès")
                return True
            else:
                self.log_test("Main Chat Endpoint", False, 
                            f"Seulement {success_count}/{len(test_messages)} contextes réussis")
                return False
                
        except Exception as e:
            self.log_test("Main Chat Endpoint", False, f"Erreur test: {str(e)}")
            return False
    
    def test_specialized_endpoints(self) -> bool:
        """Test des endpoints spécialisés /api/chat/{type}"""
        endpoints = [
            {
                "url": "/chat/exhibitor",
                "message": "Trouvez-moi des exposants en IoT maritime",
                "expected_context": "exhibitor"
            },
            {
                "url": "/chat/package", 
                "message": "Quel forfait me recommandez-vous pour 2 jours ?",
                "expected_context": "package"
            },
            {
                "url": "/chat/event",
                "message": "À quelle heure sont les conférences ?", 
                "expected_context": "event"
            }
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint['url']}",
                    json={"message": endpoint["message"]},
                    headers=self.get_auth_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if (data.get("response_type") == endpoint["expected_context"] and 
                        len(data.get("response", "")) > 10):
                        success_count += 1
                        # Stocker session_id
                        if data.get("session_id") and data["session_id"] not in self.session_ids:
                            self.session_ids.append(data["session_id"])
                        print(f"   ✅ {endpoint['url']}: Contexte {endpoint['expected_context']} correct")
                    else:
                        print(f"   ❌ {endpoint['url']}: Contexte incorrect ou réponse vide")
                else:
                    print(f"   ❌ {endpoint['url']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint['url']}: Erreur - {str(e)}")
        
        if success_count == len(endpoints):
            self.log_test("Specialized Endpoints", True, 
                        f"Tous les {len(endpoints)} endpoints spécialisés fonctionnels")
            return True
        else:
            self.log_test("Specialized Endpoints", False, 
                        f"Seulement {success_count}/{len(endpoints)} endpoints réussis")
            return False
    
    def test_chat_history_endpoints(self) -> bool:
        """Test des endpoints d'historique GET/DELETE /api/chat/history/{session_id}"""
        try:
            # D'abord créer une conversation pour avoir un historique
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": "Test historique conversation",
                    "context_type": "general",
                    "session_id": "test_history_session"
                },
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Chat History Setup", False, "Impossible de créer conversation test")
                return False
            
            session_id = "test_history_session"
            self.session_ids.append(session_id)
            
            # Test GET historique
            get_response = requests.get(
                f"{self.base_url}/chat/history/{session_id}",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            get_success = False
            if get_response.status_code == 200:
                history_data = get_response.json()
                if ("session_id" in history_data and 
                    "history" in history_data and 
                    isinstance(history_data["history"], list)):
                    get_success = True
                    print(f"   ✅ GET history: {len(history_data['history'])} messages récupérés")
                else:
                    print("   ❌ GET history: Structure réponse incorrecte")
            else:
                print(f"   ❌ GET history: HTTP {get_response.status_code}")
            
            # Test DELETE historique
            delete_response = requests.delete(
                f"{self.base_url}/chat/history/{session_id}",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            delete_success = False
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                if "message" in delete_data:
                    delete_success = True
                    print("   ✅ DELETE history: Historique effacé avec succès")
                else:
                    print("   ❌ DELETE history: Réponse incorrecte")
            else:
                print(f"   ❌ DELETE history: HTTP {delete_response.status_code}")
            
            if get_success and delete_success:
                self.log_test("Chat History Endpoints", True, 
                            "GET et DELETE historique fonctionnels")
                return True
            else:
                self.log_test("Chat History Endpoints", False, 
                            f"GET: {'✅' if get_success else '❌'}, DELETE: {'✅' if delete_success else '❌'}")
                return False
                
        except Exception as e:
            self.log_test("Chat History Endpoints", False, f"Erreur test: {str(e)}")
            return False
    
    def test_streaming_endpoint(self) -> bool:
        """Test POST /api/chat/stream - Endpoint streaming"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/stream",
                json={
                    "message": "Test streaming response",
                    "context_type": "general"
                },
                headers=self.get_auth_headers(),
                timeout=20,
                stream=True
            )
            
            if response.status_code == 200:
                # Vérifier headers streaming
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    
                    # Lire quelques chunks du stream
                    chunks_received = 0
                    session_id_found = None
                    
                    for line in response.iter_lines(decode_unicode=True):
                        if line.startswith("data: "):
                            try:
                                chunk_data = json.loads(line[6:])  # Enlever "data: "
                                chunks_received += 1
                                
                                if "session_id" in chunk_data:
                                    session_id_found = chunk_data["session_id"]
                                
                                # Arrêter après quelques chunks ou si final
                                if chunks_received >= 5 or chunk_data.get("is_final"):
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    if chunks_received > 0:
                        if session_id_found and session_id_found not in self.session_ids:
                            self.session_ids.append(session_id_found)
                        
                        self.log_test("Streaming Endpoint", True, 
                                    f"Streaming fonctionnel - {chunks_received} chunks reçus")
                        return True
                    else:
                        self.log_test("Streaming Endpoint", False, "Aucun chunk reçu")
                        return False
                else:
                    self.log_test("Streaming Endpoint", False, 
                                f"Content-Type incorrect: {content_type}")
                    return False
            else:
                self.log_test("Streaming Endpoint", False, 
                            f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Streaming Endpoint", False, f"Erreur test: {str(e)}")
            return False
    
    def test_health_check_endpoint(self) -> bool:
        """Test GET /api/chatbot/health - Health check chatbot"""
        try:
            response = requests.get(
                f"{self.base_url}/chatbot/health",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["status", "service", "version", "mock_mode", "model"]
                if all(field in data for field in required_fields):
                    
                    if data["status"] == "healthy":
                        self.log_test("Health Check Endpoint", True, 
                                    f"Service healthy - Version {data.get('version')}, Mode: {'mock' if data.get('mock_mode') else 'ollama'}")
                        return True
                    else:
                        self.log_test("Health Check Endpoint", False, 
                                    f"Service unhealthy: {data.get('status')}")
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Health Check Endpoint", False, 
                                f"Champs manquants: {missing}")
                    return False
            else:
                self.log_test("Health Check Endpoint", False, 
                            f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check Endpoint", False, f"Erreur test: {str(e)}")
            return False
    
    def test_stats_endpoint(self) -> bool:
        """Test GET /api/chatbot/stats - Statistiques chatbot"""
        try:
            response = requests.get(
                f"{self.base_url}/chatbot/stats",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["active_sessions", "total_messages", "service_mode", "model_name"]
                if all(field in data for field in required_fields):
                    
                    stats_summary = (f"Sessions: {data.get('active_sessions')}, "
                                   f"Messages: {data.get('total_messages')}, "
                                   f"Mode: {data.get('service_mode')}")
                    
                    self.log_test("Stats Endpoint", True, 
                                f"Statistiques récupérées - {stats_summary}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Stats Endpoint", False, 
                                f"Champs manquants: {missing}")
                    return False
            else:
                self.log_test("Stats Endpoint", False, 
                            f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Erreur test: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test gestion d'erreurs et validation des données"""
        try:
            error_tests = [
                {
                    "name": "Message vide",
                    "data": {"message": "", "context_type": "general"},
                    "expected_status": [400, 422]  # Validation error
                },
                {
                    "name": "Message trop long", 
                    "data": {"message": "x" * 1001, "context_type": "general"},
                    "expected_status": [400, 422]
                },
                {
                    "name": "Contexte invalide",
                    "data": {"message": "test", "context_type": "invalid_context"},
                    "expected_status": [400, 422]
                }
            ]
            
            success_count = 0
            for test in error_tests:
                try:
                    response = requests.post(
                        f"{self.base_url}/chat",
                        json=test["data"],
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    
                    if response.status_code in test["expected_status"]:
                        success_count += 1
                        print(f"   ✅ {test['name']}: Erreur correctement gérée ({response.status_code})")
                    else:
                        print(f"   ❌ {test['name']}: Status inattendu {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {test['name']}: Erreur - {str(e)}")
            
            if success_count >= 2:  # Au moins 2/3 tests d'erreur réussis
                self.log_test("Error Handling", True, 
                            f"{success_count}/{len(error_tests)} validations d'erreur correctes")
                return True
            else:
                self.log_test("Error Handling", False, 
                            f"Seulement {success_count}/{len(error_tests)} validations correctes")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Erreur test: {str(e)}")
            return False
    
    def cleanup_test_sessions(self):
        """Nettoie les sessions de test créées"""
        cleaned = 0
        for session_id in self.session_ids:
            try:
                response = requests.delete(
                    f"{self.base_url}/chat/history/{session_id}",
                    headers=self.get_auth_headers(),
                    timeout=5
                )
                if response.status_code == 200:
                    cleaned += 1
            except:
                pass  # Ignore cleanup errors
        
        if cleaned > 0:
            print(f"🧹 Nettoyage: {cleaned} sessions de test supprimées")
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests chatbot"""
        print("🤖 Démarrage des tests chatbot IA SIPORTS v2.0")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Authentification
        if not self.authenticate("exposant"):
            print("❌ Authentification échouée - impossible de continuer")
            return False
        
        # Liste des tests à exécuter
        tests = [
            ("Main Chat Endpoint", self.test_main_chat_endpoint),
            ("Specialized Endpoints", self.test_specialized_endpoints), 
            ("Chat History Endpoints", self.test_chat_history_endpoints),
            ("Streaming Endpoint", self.test_streaming_endpoint),
            ("Health Check Endpoint", self.test_health_check_endpoint),
            ("Stats Endpoint", self.test_stats_endpoint),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Test: {test_name}")
            if test_func():
                passed += 1
        
        # Nettoyage
        self.cleanup_test_sessions()
        
        print("=" * 80)
        print(f"📊 Résultats tests chatbot: {passed}/{total} tests réussis")
        
        if passed == total:
            print("✅ Tous les tests chatbot RÉUSSIS!")
            return True
        else:
            print(f"❌ {total - passed} tests ÉCHOUÉS")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Résumé des tests"""
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
    """Exécution principale des tests"""
    tester = ChatbotTester()
    success = tester.run_all_tests()
    
    # Résumé détaillé
    summary = tester.get_summary()
    print(f"\n📈 Taux de réussite: {summary['success_rate']:.1f}%")
    
    # Code de sortie approprié
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()