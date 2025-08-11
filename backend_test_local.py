#!/usr/bin/env python3
"""
Quick Backend API Tests for SIPORTS v2.0 - Local Testing
Testing key functionality to verify everything is working correctly.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Local backend URL
BACKEND_URL = "http://localhost:8001/api"

# Test credentials
TEST_ACCOUNTS = {
    "admin": {"email": "admin@siportevent.com", "password": "admin123"},
    "exhibitor": {"email": "exposant@example.com", "password": "expo123"},
    "visitor": {"email": "visiteur@example.com", "password": "visit123"},
}

def test_authentication():
    """Test authentication for key user types"""
    print("🔐 TESTING AUTHENTICATION")
    
    for user_type, credentials in TEST_ACCOUNTS.items():
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=credentials,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                print(f"✅ {user_type.upper()}: {credentials['email']} → {user_data.get('user_type')}")
            else:
                print(f"❌ {user_type.upper()}: Failed - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {user_type.upper()}: Error - {str(e)}")

def test_packages():
    """Test package endpoints"""
    print("\n📦 TESTING PACKAGES")
    
    # Test visitor packages
    try:
        response = requests.get(f"{BACKEND_URL}/visitor-packages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("packages", []))
            print(f"✅ VISITOR PACKAGES: {count} packages available")
        else:
            print(f"❌ VISITOR PACKAGES: Failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ VISITOR PACKAGES: Error - {str(e)}")
    
    # Test partnership packages
    try:
        response = requests.get(f"{BACKEND_URL}/partnership-packages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("packages", []))
            print(f"✅ PARTNERSHIP PACKAGES: {count} packages available")
        else:
            print(f"❌ PARTNERSHIP PACKAGES: Failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ PARTNERSHIP PACKAGES: Error - {str(e)}")

def test_admin_endpoints():
    """Test admin functionality"""
    print("\n👨‍💼 TESTING ADMIN ENDPOINTS")
    
    # Get admin token
    try:
        auth_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=TEST_ACCOUNTS["admin"],
            timeout=5
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test dashboard stats
            stats_response = requests.get(f"{BACKEND_URL}/admin/dashboard/stats", headers=headers, timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ ADMIN STATS: {stats.get('total_users')} total users, {stats.get('pending_accounts')} pending")
            else:
                print(f"❌ ADMIN STATS: Failed - HTTP {stats_response.status_code}")
                
        else:
            print(f"❌ ADMIN AUTH: Failed to get token")
            
    except Exception as e:
        print(f"❌ ADMIN ENDPOINTS: Error - {str(e)}")

def test_chatbot():
    """Test chatbot endpoints"""
    print("\n🤖 TESTING CHATBOT")
    
    try:
        # Health check
        health_response = requests.get(f"{BACKEND_URL}/chatbot/health", timeout=5)
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"✅ CHATBOT HEALTH: {health.get('status')} - Version {health.get('version')}")
        else:
            print(f"❌ CHATBOT HEALTH: Failed - HTTP {health_response.status_code}")
        
        # Test chat endpoint
        chat_response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": "Bonjour, pouvez-vous me parler des forfaits visiteurs?",
                "context": "general",
                "session_id": "test_session_123"
            },
            timeout=10
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            response_text = chat_data.get("response", "")[:100]
            print(f"✅ CHATBOT RESPONSE: {len(response_text)} chars - {response_text}...")
        else:
            print(f"❌ CHATBOT CHAT: Failed - HTTP {chat_response.status_code}")
            
    except Exception as e:
        print(f"❌ CHATBOT: Error - {str(e)}")

def test_exhibitor_functionality():
    """Test exhibitor-related endpoints"""
    print("\n🏢 TESTING EXHIBITOR FUNCTIONALITY")
    
    try:
        # Test matching system
        matching_response = requests.post(
            f"{BACKEND_URL}/matching/generate",
            json={
                "user_type": "visitor",
                "interests": ["IoT", "Automation"],
                "location": "Morocco",
                "budget_range": "medium"
            },
            timeout=5
        )
        
        if matching_response.status_code == 200:
            matches = matching_response.json()
            count = len(matches.get("matches", []))
            print(f"✅ MATCHING SYSTEM: Generated {count} matches")
        else:
            print(f"❌ MATCHING SYSTEM: Failed - HTTP {matching_response.status_code}")
            
    except Exception as e:
        print(f"❌ EXHIBITOR FUNCTIONALITY: Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 SIPORTS BACKEND API TESTING - LOCAL")
    print("=" * 50)
    
    # Test core functionality
    test_authentication()
    test_packages()
    test_admin_endpoints()
    test_chatbot()
    test_exhibitor_functionality()
    
    print("\n" + "=" * 50)
    print("✅ BACKEND TESTING COMPLETED")