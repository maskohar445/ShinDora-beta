#!/usr/bin/env python3
"""
Test rate limiting directly on localhost to bypass ingress
"""

import requests
import time

BASE_URL = "http://localhost:3000"
API_URL = f"{BASE_URL}/api"

print("="*80)
print("DIRECT LOCALHOST TEST: Rate Limiting Middleware")
print("="*80)
print(f"Testing directly on: {API_URL}")
print("Bypassing Kubernetes ingress to test middleware directly")
print()

success_count = 0
rate_limited_count = 0
rate_limit_triggered = False

print("Making 110 rapid requests...")

for i in range(110):
    try:
        response = requests.get(f"{API_URL}/videos", timeout=5)
        
        if response.status_code == 200:
            success_count += 1
            if i % 20 == 19:
                print(f"   Requests 1-{i+1}: {success_count} successful")
        elif response.status_code == 429:
            rate_limited_count += 1
            rate_limit_triggered = True
            
            print(f"\n✅ RATE LIMIT TRIGGERED at request #{i+1}")
            print(f"   Status: 429 Too Many Requests")
            
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('error', 'N/A')}")
            except:
                print(f"   Response: {response.text[:200]}")
            
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                print(f"   Retry-After: {retry_after} seconds")
            
            print(f"\n📊 STATISTICS:")
            print(f"   Successful requests: {success_count}")
            print(f"   Rate limited requests: {rate_limited_count}")
            print(f"   Total requests: {i+1}")
            
            break
            
    except Exception as e:
        print(f"   Request #{i+1}: Error - {str(e)[:100]}")

print(f"\n📊 FINAL RESULT:")
print(f"   Successful requests: {success_count}")
print(f"   Rate limited requests: {rate_limited_count}")

if rate_limit_triggered:
    print(f"\n✅ Rate limiting is WORKING on localhost")
else:
    print(f"\n⚠️  Rate limiting NOT triggered on localhost either")
    print(f"   This suggests the middleware may not be properly configured")
