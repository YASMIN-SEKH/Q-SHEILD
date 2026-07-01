#!/usr/bin/env python3
"""
Q-Shield v2 Integration Test Suite
Tests all endpoints and verifies model loading
"""

import requests
import json
import time
from typing import Dict, Any

API_URL = "http://localhost:8000"

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(endpoint: str, status: str, data: Any = None):
    emoji = "✅" if status == "pass" else "❌"
    print(f"\n{emoji} {endpoint}")
    if data:
        print(f"   {data}")

def test_health():
    """Test health endpoint"""
    print_header("Testing Health Endpoint")
    try:
        resp = requests.get(f"{API_URL}/health")
        data = resp.json()
        
        assert resp.status_code == 200
        assert data['status'] == 'healthy'
        assert data['models_loaded'] == True
        assert data['enrolled_subjects'] == 51
        
        print_result("/health", "pass", f"Status: {data['status']}, Models: {data['models_loaded']}")
        return True
    except Exception as e:
        print_result("/health", "fail", str(e))
        return False

def test_analytics():
    """Test analytics endpoint"""
    print_header("Testing Analytics Endpoint")
    try:
        resp = requests.get(f"{API_URL}/analytics/summary")
        data = resp.json()
        
        assert resp.status_code == 200
        assert data['total_subjects'] == 51
        assert data['models_loaded'] == True
        assert data['average_eer'] < 1.0  # EER should be < 1%
        
        print_result("/analytics/summary", "pass", 
                    f"Subjects: {data['total_subjects']}, Avg EER: {data['average_eer']:.4f}%")
        return True
    except Exception as e:
        print_result("/analytics/summary", "fail", str(e))
        return False

def test_eer_metrics():
    """Test EER metrics endpoint"""
    print_header("Testing EER Metrics Endpoint")
    try:
        resp = requests.get(f"{API_URL}/metrics/eer")
        data = resp.json()
        
        assert resp.status_code == 200
        assert data['subjects'] == 51
        assert len(data['data']) > 0
        
        # Sample first subject
        first = data['data'][0]
        print_result("/metrics/eer", "pass", 
                    f"Subjects: {data['subjects']}, Avg EER: {data['average_eer']:.4f}%")
        print(f"   Sample (s003): EER={first['eer_pct']}%, AUC={first['auc']}, Separation={first['separation']}")
        
        return True
    except Exception as e:
        print_result("/metrics/eer", "fail", str(e))
        return False

def test_enrollment():
    """Test enrollment endpoint"""
    print_header("Testing Enrollment Endpoint")
    try:
        payload = {
            "user_id": f"testuser_{int(time.time())}",
            "username": "Test User",
            "email": "test@example.com",
            "keystroke_samples": [
                [
                    {"key": "t", "dwellTime": 120, "flightTime": 100, "latency": 50, "holdTime": 120, "timestamp": 0},
                    {"key": "e", "dwellTime": 95, "flightTime": 80, "latency": 45, "holdTime": 95, "timestamp": 100},
                ],
                [
                    {"key": "t", "dwellTime": 125, "flightTime": 105, "latency": 52, "holdTime": 125, "timestamp": 0},
                    {"key": "e", "dwellTime": 92, "flightTime": 78, "latency": 43, "holdTime": 92, "timestamp": 105},
                ]
            ]
        }
        
        resp = requests.post(f"{API_URL}/auth/enroll", json=payload)
        data = resp.json()
        
        assert resp.status_code == 200
        assert data['success'] == True
        assert data['user_id'] == payload['user_id']
        
        print_result("/auth/enroll", "pass", f"User: {data['user_id']}, Samples: {data['samples_processed']}")
        return True, payload['user_id']
    except Exception as e:
        print_result("/auth/enroll", "fail", str(e))
        return False, None

def test_authentication(user_id: str):
    """Test authentication endpoint"""
    print_header("Testing Authentication Endpoint")
    try:
        payload = {
            "user_id": user_id,
            "keystrokes": [
                {"key": "t", "dwellTime": 118, "flightTime": 102, "latency": 51, "holdTime": 118, "timestamp": 0},
                {"key": "e", "dwellTime": 94, "flightTime": 79, "latency": 44, "holdTime": 94, "timestamp": 102},
            ],
            "session_id": f"session_{int(time.time())}"
        }
        
        resp = requests.post(f"{API_URL}/auth/authenticate", json=payload)
        data = resp.json()
        
        assert resp.status_code == 200
        assert 'fused_score' in data
        assert 'anomaly_zone' in data
        
        result = "ACCEPT" if data['authenticated'] else "REJECT"
        print_result("/auth/authenticate", "pass", 
                    f"Decision: {result}, Score: {data['fused_score']:.4f}, Zone: {data['anomaly_zone']}")
        return True
    except Exception as e:
        print_result("/auth/authenticate", "fail", str(e))
        return False

def test_user_profile(user_id: str):
    """Test user profile endpoint"""
    print_header("Testing User Profile Endpoint")
    try:
        resp = requests.get(f"{API_URL}/users/{user_id}")
        data = resp.json()
        
        assert resp.status_code == 200
        assert data['user_id'] == user_id
        assert data['enrolled'] == True
        
        print_result(f"/users/{user_id}", "pass", 
                    f"Username: {data['username']}, Authentications: {data['total_authentications']}")
        return True
    except Exception as e:
        print_result(f"/users/{user_id}", "fail", str(e))
        return False

def test_auth_history():
    """Test authentication history endpoint"""
    print_header("Testing Authentication History Endpoint")
    try:
        resp = requests.get(f"{API_URL}/auth/history")
        data = resp.json()
        
        assert resp.status_code == 200
        assert 'records' in data
        
        print_result("/auth/history", "pass", f"Total records: {data['total_records']}")
        return True
    except Exception as e:
        print_result("/auth/history", "fail", str(e))
        return False

def run_all_tests():
    """Run all integration tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Q-SHIELD v2 INTEGRATION TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Analytics
    results.append(("Analytics", test_analytics()))
    
    # Test 3: EER Metrics
    results.append(("EER Metrics", test_eer_metrics()))
    
    # Test 4: Enrollment
    enroll_ok, user_id = test_enrollment()
    results.append(("Enrollment", enroll_ok))
    
    if user_id:
        # Test 5: Authentication
        results.append(("Authentication", test_authentication(user_id)))
        
        # Test 6: User Profile
        results.append(("User Profile", test_user_profile(user_id)))
    
    # Test 7: History
    results.append(("Auth History", test_auth_history()))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for test_name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed! Q-Shield v2 is fully operational.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
