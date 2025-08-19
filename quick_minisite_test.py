#!/usr/bin/env python3
"""Quick test for specific failing scenarios"""

import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_specific_issues():
    session = requests.Session()
    
    # Test 1: Login as admin
    admin_login = session.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": "admin@siportevent.com", 
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_data = admin_login.json()
        admin_token = admin_data.get("access_token")
        admin_user = admin_data.get("user", {})
        admin_id = admin_user.get("id")
        print(f"✅ Admin login successful, ID: {admin_id}")
        
        # Test admin accessing their own data
        response = session.get(
            f"{BACKEND_URL}/api/minisite/enhanced/{admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Admin accessing own data: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
    
    # Test 2: Login as visitor
    visitor_login = session.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": "visiteur@example.com", 
        "password": "visit123"
    })
    
    if visitor_login.status_code == 200:
        visitor_data = visitor_login.json()
        visitor_user = visitor_data.get("user", {})
        visitor_id = visitor_user.get("id")
        print(f"✅ Visitor login successful, ID: {visitor_id}, Type: {visitor_user.get('user_type')}")
        
        # Test public access for visitor (should fail since visitor is not exhibitor/partner)
        response = session.get(f"{BACKEND_URL}/api/minisite/enhanced/{visitor_id}/public")
        print(f"Public access for visitor: {response.status_code}")
        if response.status_code != 200:
            print(f"Expected error: {response.text}")
    
    # Test 3: Invalid user ID
    session.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": "exposant@example.com", 
        "password": "exhibitor123"
    })
    
    response = session.get(f"{BACKEND_URL}/api/minisite/enhanced/99999")
    print(f"Invalid user ID test: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    test_specific_issues()