#!/usr/bin/env python3
"""
Anti Developer Tools Feature Test
Tests the antiDevToolsActive setting in the Settings API
"""

import requests
import json
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

# Base URL from environment
BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/') + "/api"

print("=" * 60)
print("Anti Developer Tools Feature Test")
print("=" * 60)
print(f"Base URL: {BASE_URL}")
print()

# Test results
passed = 0
failed = 0

def test_anti_devtools_setting():
    """Test antiDevToolsActive setting CRUD operations"""
    global passed, failed
    
    print("=== Test 1: GET /api/settings - Check if antiDevToolsActive exists ===")
    try:
        response = requests.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            settings = response.json()
            has_field = 'antiDevToolsActive' in settings
            print(f"✅ PASS: Settings retrieved successfully")
            print(f"   antiDevToolsActive field exists: {has_field}")
            if has_field:
                print(f"   Current value: {settings['antiDevToolsActive']}")
            passed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()
    
    print("=== Test 2: POST /api/settings - Enable antiDevToolsActive ===")
    try:
        response = requests.post(
            f"{BASE_URL}/settings",
            json={"antiDevToolsActive": True},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            settings = response.json()
            if settings.get('antiDevToolsActive') == True:
                print(f"✅ PASS: antiDevToolsActive enabled successfully")
                print(f"   Value: {settings['antiDevToolsActive']}")
                passed += 1
            else:
                print(f"❌ FAIL: Value not set correctly. Got: {settings.get('antiDevToolsActive')}")
                failed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()
    
    print("=== Test 3: GET /api/settings - Verify persistence (enabled) ===")
    try:
        response = requests.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            settings = response.json()
            if settings.get('antiDevToolsActive') == True:
                print(f"✅ PASS: antiDevToolsActive persisted correctly as enabled")
                print(f"   Value: {settings['antiDevToolsActive']}")
                passed += 1
            else:
                print(f"❌ FAIL: Value not persisted. Got: {settings.get('antiDevToolsActive')}")
                failed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()
    
    print("=== Test 4: POST /api/settings - Disable antiDevToolsActive ===")
    try:
        response = requests.post(
            f"{BASE_URL}/settings",
            json={"antiDevToolsActive": False},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            settings = response.json()
            if settings.get('antiDevToolsActive') == False:
                print(f"✅ PASS: antiDevToolsActive disabled successfully")
                print(f"   Value: {settings['antiDevToolsActive']}")
                passed += 1
            else:
                print(f"❌ FAIL: Value not set correctly. Got: {settings.get('antiDevToolsActive')}")
                failed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()
    
    print("=== Test 5: GET /api/settings - Verify persistence (disabled) ===")
    try:
        response = requests.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            settings = response.json()
            if settings.get('antiDevToolsActive') == False:
                print(f"✅ PASS: antiDevToolsActive persisted correctly as disabled")
                print(f"   Value: {settings['antiDevToolsActive']}")
                passed += 1
            else:
                print(f"❌ FAIL: Value not persisted. Got: {settings.get('antiDevToolsActive')}")
                failed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()
    
    print("=== Test 6: POST /api/settings - Partial update (keep antiDevToolsActive) ===")
    try:
        # First enable it
        requests.post(
            f"{BASE_URL}/settings",
            json={"antiDevToolsActive": True},
            headers={"Content-Type": "application/json"}
        )
        
        # Then update another field
        response = requests.post(
            f"{BASE_URL}/settings",
            json={"announcementBadge": "TEST BADGE"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            settings = response.json()
            if settings.get('antiDevToolsActive') == True and settings.get('announcementBadge') == "TEST BADGE":
                print(f"✅ PASS: Partial update successful, antiDevToolsActive preserved")
                print(f"   antiDevToolsActive: {settings['antiDevToolsActive']}")
                print(f"   announcementBadge: {settings['announcementBadge']}")
                passed += 1
            else:
                print(f"❌ FAIL: Partial update failed")
                print(f"   antiDevToolsActive: {settings.get('antiDevToolsActive')}")
                print(f"   announcementBadge: {settings.get('announcementBadge')}")
                failed += 1
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        failed += 1
    print()

# Run tests
test_anti_devtools_setting()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Total Tests: {passed + failed}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print("=" * 60)

if failed > 0:
    print("\n⚠️  Some tests failed. Please review the output above.")
    exit(1)
else:
    print("\n✅ All tests passed! Anti Developer Tools feature is working correctly.")
    exit(0)
