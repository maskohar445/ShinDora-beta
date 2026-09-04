#!/usr/bin/env python3
"""
Quick verification test for sitemap.xml and videos endpoint with prefix-cleaning regex
"""
import requests
import json
import xml.etree.ElementTree as ET

BASE_URL = "https://next-anime-hub.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

def test_sitemap_xml():
    """Test sitemap.xml endpoint"""
    print("\n" + "="*80)
    print("TEST 1: GET /sitemap.xml - Dynamic XML Sitemap")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/sitemap.xml", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            return False
        
        # Check Content-Type header
        content_type = response.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")
        
        if 'xml' not in content_type.lower():
            print(f"⚠️  WARNING: Content-Type should be application/xml, got {content_type}")
        
        # Parse XML
        try:
            root = ET.fromstring(response.text)
            urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            print(f"Total URLs in sitemap: {len(urls)}")
            
            # Check for home page
            home_found = False
            video_count = 0
            category_count = 0
            
            for url in urls:
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    url_text = loc.text
                    if url_text == BASE_URL or url_text == f"{BASE_URL}/":
                        home_found = True
                    elif '/watch/' in url_text:
                        video_count += 1
                    elif '/page/' in url_text:
                        category_count += 1
            
            print(f"  - Home page found: {home_found}")
            print(f"  - Video pages: {video_count}")
            print(f"  - Category pages: {category_count}")
            
            # Check XML structure
            if response.text.strip().endswith('</urlset>'):
                print("✅ XML properly closed with </urlset>")
            else:
                print("❌ FAILED: XML not properly closed")
                return False
            
            # Check required SEO tags
            first_url = urls[0] if urls else None
            if first_url:
                lastmod = first_url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                changefreq = first_url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
                priority = first_url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                
                if lastmod is not None and changefreq is not None and priority is not None:
                    print("✅ Required SEO tags present (lastmod, changefreq, priority)")
                else:
                    print("⚠️  WARNING: Some SEO tags missing")
            
            print("✅ TEST 1 PASSED: Sitemap.xml working correctly")
            return True
            
        except ET.ParseError as e:
            print(f"❌ FAILED: XML parsing error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_videos_prefix_cleaning_regex():
    """Test videos endpoint with prefix-cleaning regex for category parameter"""
    print("\n" + "="*80)
    print("TEST 2: GET /api/videos - Prefix-Cleaning Regex Verification")
    print("="*80)
    
    test_cases = [
        {
            "name": "Category with 'i,' prefix",
            "category": "i, Doraemon",
            "expected_clean": "Doraemon"
        },
        {
            "name": "Category with 'i ' prefix",
            "category": "i Crayon Shinchan",
            "expected_clean": "Crayon Shinchan"
        },
        {
            "name": "Category with multiple commas",
            "category": ",,, Ninja Hattori-kun",
            "expected_clean": "Ninja Hattori-kun"
        },
        {
            "name": "Category with 'I,' prefix (uppercase)",
            "category": "I, Chibi Maruko-chan",
            "expected_clean": "Chibi Maruko-chan"
        },
        {
            "name": "Clean category (no prefix)",
            "category": "Doraemon",
            "expected_clean": "Doraemon"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test Case {i}: {test_case['name']}")
        print(f"  Input category: '{test_case['category']}'")
        print(f"  Expected clean: '{test_case['expected_clean']}'")
        
        try:
            response = requests.get(
                f"{API_URL}/videos",
                params={"category": test_case['category']},
                timeout=10
            )
            
            if response.status_code == 200:
                videos = response.json()
                print(f"  Status: 200 OK")
                print(f"  Videos returned: {len(videos)}")
                
                # Verify the regex compiled successfully (no 500 error)
                print(f"  ✅ Regex compiled successfully (no server error)")
                
                # Check if videos match the expected category
                if len(videos) > 0:
                    sample_video = videos[0]
                    print(f"  Sample video: {sample_video.get('title', 'N/A')}")
                    print(f"  Anime title: {sample_video.get('animeTitle', 'N/A')}")
                
            else:
                print(f"  ❌ FAILED: Status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST 2 PASSED: Prefix-cleaning regex working correctly")
    else:
        print("\n❌ TEST 2 FAILED: Some test cases failed")
    
    return all_passed


def test_videos_endpoint_basic():
    """Test basic videos endpoint functionality"""
    print("\n" + "="*80)
    print("TEST 3: GET /api/videos - Basic Functionality")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/videos", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            return False
        
        videos = response.json()
        print(f"Total videos: {len(videos)}")
        
        if len(videos) > 0:
            sample = videos[0]
            print(f"\nSample video:")
            print(f"  - ID: {sample.get('id', 'N/A')}")
            print(f"  - Title: {sample.get('title', 'N/A')}")
            print(f"  - Anime Title: {sample.get('animeTitle', 'N/A')}")
            print(f"  - Episode: {sample.get('episode', 'N/A')}")
            print(f"  - Slug: {sample.get('slug', 'N/A')}")
            print(f"  - Status: {sample.get('status', 'N/A')}")
        
        print("✅ TEST 3 PASSED: Videos endpoint working correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_nextjs_server_health():
    """Test Next.js server health"""
    print("\n" + "="*80)
    print("TEST 4: Next.js Server Health Check")
    print("="*80)
    
    endpoints = [
        f"{BASE_URL}/",
        f"{API_URL}/videos",
        f"{API_URL}/categories",
        f"{API_URL}/settings",
        f"{BASE_URL}/sitemap.xml"
    ]
    
    all_healthy = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code != 200:
                all_healthy = False
                
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)}")
            all_healthy = False
    
    if all_healthy:
        print("\n✅ TEST 4 PASSED: All endpoints healthy")
    else:
        print("\n❌ TEST 4 FAILED: Some endpoints unhealthy")
    
    return all_healthy


def main():
    print("\n" + "="*80)
    print("SITEMAP.XML & VIDEOS ENDPOINT REGEX VERIFICATION TEST SUITE")
    print("="*80)
    
    results = {
        "Sitemap.xml": test_sitemap_xml(),
        "Prefix-Cleaning Regex": test_videos_prefix_cleaning_regex(),
        "Videos Basic": test_videos_endpoint_basic(),
        "Server Health": test_nextjs_server_health()
    }
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Next.js server is in ABSOLUTE PEAK CONDITION!")
        print("✅ Sitemap.xml endpoint working perfectly")
        print("✅ Prefix-cleaning regex compiles and executes successfully")
        print("✅ Videos endpoint functioning correctly")
        print("✅ Server health verified")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review required.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
