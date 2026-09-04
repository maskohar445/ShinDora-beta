#!/usr/bin/env python3
"""
Focused test for Login, Forgot Password, and Reset Password endpoints
Testing after theme flash and reload optimizations in layout.js and login/page.js
"""

import requests
import json
from datetime import datetime
import os
from pathlib import Path

# Load .env file
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()
BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/') + "/api"

def test_login_endpoints():
    """Test all login scenarios"""
    print("\n" + "="*70)
    print("TESTING LOGIN ENDPOINTS")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: Register a new user
    print("\n[Test 1] POST /api/auth/register - Register new user")
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        register_payload = {
            "name": "Budi Santoso",
            "email": f"budi.santoso.{timestamp}@gmail.com",
            "password": "budisantoso123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_payload, timeout=10)
        if response.status_code == 200:
            user = response.json()
            if 'id' in user and 'email' in user:
                print(f"✅ PASS: User registered successfully - {user['name']} ({user['email']})")
                results["passed"] += 1
                results["tests"].append({"name": "Register", "status": "PASS", "user": user})
            else:
                print(f"❌ FAIL: Invalid response structure")
                results["failed"] += 1
                results["tests"].append({"name": "Register", "status": "FAIL"})
                return results
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Register", "status": "FAIL"})
            return results
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Register", "status": "FAIL"})
        return results
    
    user = results["tests"][0]["user"]
    
    # Test 2: Login with registered user
    print("\n[Test 2] POST /api/auth/login - Regular user login")
    try:
        login_payload = {
            "email": user['email'],
            "password": "budisantoso123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        if response.status_code == 200:
            logged_user = response.json()
            if 'id' in logged_user and logged_user['email'] == user['email']:
                print(f"✅ PASS: Login successful - {logged_user['name']}")
                results["passed"] += 1
                results["tests"].append({"name": "Regular Login", "status": "PASS"})
            else:
                print(f"❌ FAIL: Invalid login response")
                results["failed"] += 1
                results["tests"].append({"name": "Regular Login", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Regular Login", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Regular Login", "status": "FAIL"})
    
    # Test 3: Admin login with isStaffOnly=true
    print("\n[Test 3] POST /api/auth/login - Admin login with isStaffOnly=true")
    try:
        admin_payload = {
            "email": "admin@shindora.com",
            "password": "Emilia9@#$",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=admin_payload, timeout=10)
        if response.status_code == 200:
            admin = response.json()
            if 'role' in admin and admin['role'] == 'admin':
                print(f"✅ PASS: Admin login successful - {admin['name']} (role: {admin['role']})")
                results["passed"] += 1
                results["tests"].append({"name": "Admin Staff Login", "status": "PASS"})
            else:
                print(f"❌ FAIL: Admin role not found")
                results["failed"] += 1
                results["tests"].append({"name": "Admin Staff Login", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Admin Staff Login", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Admin Staff Login", "status": "FAIL"})
    
    # Test 4: Admin regular login (without isStaffOnly)
    print("\n[Test 4] POST /api/auth/login - Admin regular login")
    try:
        admin_payload = {
            "email": "admin@shindora.com",
            "password": "Emilia9@#$"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=admin_payload, timeout=10)
        if response.status_code == 200:
            admin = response.json()
            if 'role' in admin and admin['role'] == 'admin':
                print(f"✅ PASS: Admin regular login successful - {admin['name']}")
                results["passed"] += 1
                results["tests"].append({"name": "Admin Regular Login", "status": "PASS"})
            else:
                print(f"❌ FAIL: Admin role not found")
                results["failed"] += 1
                results["tests"].append({"name": "Admin Regular Login", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Admin Regular Login", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Admin Regular Login", "status": "FAIL"})
    
    # Test 5: Staff-only validation (regular user should be rejected)
    print("\n[Test 5] POST /api/auth/login - Regular user with isStaffOnly=true (should fail)")
    try:
        staff_payload = {
            "email": user['email'],
            "password": "budisantoso123",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=staff_payload, timeout=10)
        if response.status_code == 403:
            error_data = response.json()
            if 'error' in error_data:
                print(f"✅ PASS: Correctly rejected with 403 - {error_data['error']}")
                results["passed"] += 1
                results["tests"].append({"name": "Staff Validation", "status": "PASS"})
            else:
                print(f"❌ FAIL: 403 but no error message")
                results["failed"] += 1
                results["tests"].append({"name": "Staff Validation", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Expected 403, got {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Staff Validation", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Staff Validation", "status": "FAIL"})
    
    # Test 6: Moderator login with isStaffOnly=true
    print("\n[Test 6] POST /api/auth/login - Moderator login with isStaffOnly=true")
    try:
        mod_payload = {
            "email": "mod@shindora.com",
            "password": "mod123",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=mod_payload, timeout=10)
        if response.status_code == 200:
            moderator = response.json()
            if 'role' in moderator and moderator['role'] == 'moderator':
                print(f"✅ PASS: Moderator login successful - {moderator['name']} (role: {moderator['role']})")
                results["passed"] += 1
                results["tests"].append({"name": "Moderator Staff Login", "status": "PASS"})
            else:
                print(f"❌ FAIL: Moderator role not found")
                results["failed"] += 1
                results["tests"].append({"name": "Moderator Staff Login", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Moderator Staff Login", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Moderator Staff Login", "status": "FAIL"})
    
    return results

def test_forgot_password_endpoints():
    """Test forgot password and reset password scenarios"""
    print("\n" + "="*70)
    print("TESTING FORGOT PASSWORD & RESET PASSWORD ENDPOINTS")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: Forgot password with unregistered email (should fail)
    print("\n[Test 1] POST /api/auth/forgot-password - Unregistered email (should fail)")
    try:
        forgot_payload = {
            "email": "tidakterdaftar@example.com"
        }
        
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_payload, timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            if 'error' in error_data:
                print(f"✅ PASS: Correctly rejected with 404 - {error_data['error']}")
                results["passed"] += 1
                results["tests"].append({"name": "Forgot Password - Unregistered", "status": "PASS"})
            else:
                print(f"❌ FAIL: 404 but no error message")
                results["failed"] += 1
                results["tests"].append({"name": "Forgot Password - Unregistered", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Forgot Password - Unregistered", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Forgot Password - Unregistered", "status": "FAIL"})
    
    # Test 2: Reset password with invalid PIN (should fail)
    print("\n[Test 2] POST /api/auth/reset-password - Invalid PIN (should fail)")
    try:
        # First request forgot password to ensure user has a PIN
        requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": "admin@shindora.com"}, timeout=10)
        
        reset_payload = {
            "email": "admin@shindora.com",
            "pinCode": "999999",  # Wrong PIN
            "newPassword": "NewPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            if 'error' in error_data and 'salah' in error_data['error'].lower():
                print(f"✅ PASS: Correctly rejected with 400 - {error_data['error']}")
                results["passed"] += 1
                results["tests"].append({"name": "Reset Password - Invalid PIN", "status": "PASS"})
            else:
                print(f"❌ FAIL: 400 but unexpected error - {error_data.get('error', 'No error')}")
                results["failed"] += 1
                results["tests"].append({"name": "Reset Password - Invalid PIN", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Reset Password - Invalid PIN", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Reset Password - Invalid PIN", "status": "FAIL"})
    
    # Test 3: Reset password with missing fields (should fail)
    print("\n[Test 3] POST /api/auth/reset-password - Missing fields (should fail)")
    try:
        reset_payload = {
            "email": "admin@shindora.com",
            "pinCode": "123456"
            # Missing newPassword
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            if 'error' in error_data and 'wajib' in error_data['error'].lower():
                print(f"✅ PASS: Correctly rejected with 400 - {error_data['error']}")
                results["passed"] += 1
                results["tests"].append({"name": "Reset Password - Missing Fields", "status": "PASS"})
            else:
                print(f"❌ FAIL: 400 but unexpected error - {error_data.get('error', 'No error')}")
                results["failed"] += 1
                results["tests"].append({"name": "Reset Password - Missing Fields", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Reset Password - Missing Fields", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Reset Password - Missing Fields", "status": "FAIL"})
    
    # Test 4: Reset password with unregistered email (should fail)
    print("\n[Test 4] POST /api/auth/reset-password - Unregistered email (should fail)")
    try:
        reset_payload = {
            "email": "tidakterdaftar@example.com",
            "pinCode": "123456",
            "newPassword": "NewPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            if 'error' in error_data and 'tidak ditemukan' in error_data['error'].lower():
                print(f"✅ PASS: Correctly rejected with 404 - {error_data['error']}")
                results["passed"] += 1
                results["tests"].append({"name": "Reset Password - Unregistered Email", "status": "PASS"})
            else:
                print(f"❌ FAIL: 404 but unexpected error - {error_data.get('error', 'No error')}")
                results["failed"] += 1
                results["tests"].append({"name": "Reset Password - Unregistered Email", "status": "FAIL"})
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            results["failed"] += 1
            results["tests"].append({"name": "Reset Password - Unregistered Email", "status": "FAIL"})
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Reset Password - Unregistered Email", "status": "FAIL"})
    
    return results

def print_summary(login_results, forgot_results):
    """Print test summary"""
    total_passed = login_results["passed"] + forgot_results["passed"]
    total_failed = login_results["failed"] + forgot_results["failed"]
    total_tests = total_passed + total_failed
    
    print("\n" + "="*70)
    print("TEST SUMMARY - AUTH ENDPOINTS VERIFICATION")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    print("="*70)
    
    print("\n📋 LOGIN ENDPOINTS:")
    for test in login_results["tests"]:
        status_icon = "✅" if test["status"] == "PASS" else "❌"
        print(f"  {status_icon} {test['name']}")
    
    print("\n📋 FORGOT PASSWORD & RESET PASSWORD ENDPOINTS:")
    for test in forgot_results["tests"]:
        status_icon = "✅" if test["status"] == "PASS" else "❌"
        print(f"  {status_icon} {test['name']}")
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    if total_failed == 0:
        print("✅ ALL AUTH ENDPOINTS WORKING PERFECTLY!")
        print("   Login, forgot password, and reset password APIs are functioning")
        print("   correctly after theme flash and reload optimizations.")
    else:
        print(f"⚠️  {total_failed} test(s) failed. Please review the failed tests above.")
    print("="*70)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AUTH ENDPOINTS VERIFICATION TEST")
    print("Testing after theme flash and reload optimizations")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    login_results = test_login_endpoints()
    forgot_results = test_forgot_password_endpoints()
    
    print_summary(login_results, forgot_results)
