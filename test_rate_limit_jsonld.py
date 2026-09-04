#!/usr/bin/env python3
"""
Focused test for Rate Limiting and JSON-LD Schema validation
"""

import requests
import json
import time
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

BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/')
API_URL = f"{BASE_URL}/api"

print("="*80)
print("FOCUSED TEST: Rate Limiting & JSON-LD Schema Validation")
print("="*80)
print(f"Base URL: {BASE_URL}")
print(f"API URL: {API_URL}")
print()

# Test 1: Rate Limiting
print("="*80)
print("TEST 1: Rate Limiting Middleware")
print("="*80)
print("Testing rate limiting by making rapid requests...")
print("Middleware config: 100 requests per minute per IP")
print()

success_count = 0
rate_limited_count = 0
error_count = 0
rate_limit_triggered = False

# Make requests in batches to avoid connection issues
batch_size = 20
total_requests = 110

for batch in range(0, total_requests, batch_size):
    print(f"Batch {batch//batch_size + 1}: Requests {batch+1}-{min(batch+batch_size, total_requests)}")
    
    for i in range(batch, min(batch + batch_size, total_requests)):
        try:
            response = requests.get(f"{API_URL}/videos", timeout=10)
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                rate_limit_triggered = True
                
                print(f"\n✅ RATE LIMIT TRIGGERED at request #{i+1}")
                print(f"   Status: 429 Too Many Requests")
                
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('error', 'N/A')}")
                except:
                    print(f"   Response body: {response.text[:200]}")
                
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    print(f"   Retry-After header: {retry_after} seconds")
                
                print(f"\n📊 STATISTICS:")
                print(f"   ✓ Successful requests before rate limit: {success_count}")
                print(f"   ✓ Rate limited requests: {rate_limited_count}")
                print(f"   ✓ Total requests made: {i+1}")
                
                break
            else:
                error_count += 1
                print(f"   Request #{i+1}: Unexpected status {response.status_code}")
                
        except requests.exceptions.Timeout:
            error_count += 1
            print(f"   Request #{i+1}: Timeout")
        except Exception as e:
            error_count += 1
            print(f"   Request #{i+1}: Error - {str(e)[:100]}")
    
    if rate_limit_triggered:
        break
    
    # Small delay between batches
    time.sleep(0.5)

print(f"\n📊 FINAL STATISTICS:")
print(f"   Successful requests: {success_count}")
print(f"   Rate limited requests: {rate_limited_count}")
print(f"   Error/timeout requests: {error_count}")
print(f"   Total requests: {success_count + rate_limited_count + error_count}")

if rate_limit_triggered:
    print(f"\n✅ RESULT: Rate limiting is WORKING")
    print(f"   Middleware successfully blocked requests after {success_count} successful requests")
else:
    print(f"\n⚠️  RESULT: Rate limiting NOT triggered")
    print(f"   Made {success_count} successful requests without hitting 429 status")
    print(f"   This could indicate:")
    print(f"   - Rate limit threshold is higher than expected")
    print(f"   - Middleware is not properly applied")
    print(f"   - Connection issues prevented reaching the limit")

# Test 2: JSON-LD Schema
print("\n" + "="*80)
print("TEST 2: JSON-LD Schema Validation (VideoObject)")
print("="*80)

try:
    # First check if the service is responding
    print("Checking service health...")
    health_response = requests.get(f"{API_URL}/videos", timeout=10)
    
    if health_response.status_code != 200:
        print(f"❌ Service not responding properly: {health_response.status_code}")
        print("Skipping JSON-LD test due to service unavailability")
    else:
        videos = health_response.json()
        print(f"✓ Service is healthy, found {len(videos)} videos")
        
        if not videos:
            print("❌ No videos found in database")
        else:
            # Get first video
            test_video = videos[0]
            video_slug = test_video.get('slug')
            video_title = test_video.get('title', 'Unknown')
            
            print(f"\nTesting with video: {video_title}")
            print(f"Slug: {video_slug}")
            
            # Fetch the video page
            page_url = f"{BASE_URL}/watch/{video_slug}"
            print(f"Fetching: {page_url}")
            
            page_response = requests.get(page_url, timeout=15)
            
            if page_response.status_code != 200:
                print(f"❌ Failed to fetch video page: {page_response.status_code}")
                print(f"   This might be a temporary infrastructure issue (502/503)")
            else:
                print(f"✓ Page fetched successfully ({len(page_response.text)} bytes)")
                
                # Extract JSON-LD
                import re
                json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
                matches = re.findall(json_ld_pattern, page_response.text, re.DOTALL)
                
                if not matches:
                    print("❌ No JSON-LD script found in page HTML")
                else:
                    print(f"✓ Found {len(matches)} JSON-LD script(s)")
                    
                    # Parse JSON-LD
                    json_ld_str = matches[0].strip()
                    try:
                        json_ld = json.loads(json_ld_str)
                        print("✓ JSON-LD is valid JSON")
                        
                        # Validate structure
                        print("\n📋 JSON-LD Structure:")
                        print(f"   @context: {json_ld.get('@context')}")
                        print(f"   @type: {json_ld.get('@type')}")
                        print(f"   name: {json_ld.get('name')}")
                        print(f"   description: {json_ld.get('description', '')[:60]}...")
                        print(f"   thumbnailUrl: {json_ld.get('thumbnailUrl')}")
                        print(f"   uploadDate: {json_ld.get('uploadDate')}")
                        print(f"   embedUrl: {json_ld.get('embedUrl', 'N/A')}")
                        
                        if 'interactionStatistic' in json_ld:
                            interaction = json_ld['interactionStatistic']
                            print(f"   interactionStatistic:")
                            print(f"      @type: {interaction.get('@type')}")
                            print(f"      interactionType: {interaction.get('interactionType')}")
                            print(f"      userInteractionCount: {interaction.get('userInteractionCount')}")
                        
                        # Validate required fields
                        required_fields = ['@context', '@type', 'name', 'description', 'thumbnailUrl', 'uploadDate']
                        missing_fields = [f for f in required_fields if f not in json_ld]
                        
                        if missing_fields:
                            print(f"\n❌ Missing required fields: {', '.join(missing_fields)}")
                        else:
                            print("\n✓ All required fields present")
                        
                        # Validate values
                        errors = []
                        
                        if json_ld.get('@context') != 'https://schema.org':
                            errors.append(f"Invalid @context: {json_ld.get('@context')}")
                        
                        if json_ld.get('@type') != 'VideoObject':
                            errors.append(f"Invalid @type: {json_ld.get('@type')}")
                        
                        if not json_ld.get('name'):
                            errors.append("Empty name field")
                        
                        if not json_ld.get('description'):
                            errors.append("Empty description field")
                        
                        thumbnail_url = json_ld.get('thumbnailUrl')
                        if not isinstance(thumbnail_url, list) or len(thumbnail_url) == 0:
                            errors.append("thumbnailUrl should be a non-empty array")
                        
                        # Validate uploadDate format
                        upload_date = json_ld.get('uploadDate')
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        except:
                            errors.append(f"Invalid uploadDate format: {upload_date}")
                        
                        if errors:
                            print("\n❌ Validation errors:")
                            for error in errors:
                                print(f"   - {error}")
                        else:
                            print("\n✅ RESULT: JSON-LD VideoObject schema is VALID and HEALTHY")
                            print("   All required fields present and properly formatted")
                            print("   Schema.org VideoObject structure verified")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON-LD format: {str(e)}")
                        print(f"   JSON-LD content: {json_ld_str[:200]}...")
                        
except Exception as e:
    print(f"❌ Error during JSON-LD test: {str(e)}")
    import traceback
    print(traceback.format_exc())

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
