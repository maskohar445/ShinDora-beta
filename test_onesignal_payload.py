#!/usr/bin/env python3
"""
Test script to verify OneSignal payload updates in route.js
"""
import os
import re

def test_env_variables():
    """Test that OneSignal environment variables are present in .env"""
    print("\n=== Testing .env OneSignal Variables ===")
    env_path = "/app/.env"
    
    with open(env_path, "r") as f:
        content = f.read()
    
    # Check for OneSignal variables
    has_app_id = "NEXT_PUBLIC_ONESIGNAL_APP_ID" in content
    has_rest_key = "ONESIGNAL_REST_API_KEY" in content
    
    print(f"✓ NEXT_PUBLIC_ONESIGNAL_APP_ID present: {has_app_id}")
    print(f"✓ ONESIGNAL_REST_API_KEY present: {has_rest_key}")
    
    if has_app_id and has_rest_key:
        print("✅ TEST PASSED: All OneSignal environment variables are present")
        return True
    else:
        print("❌ TEST FAILED: Missing OneSignal environment variables")
        return False

def test_onesignal_payload():
    """Test that OneSignal payload in route.js has been updated correctly"""
    print("\n=== Testing OneSignal Payload in route.js ===")
    route_path = "/app/app/api/[[...path]]/route.js"
    
    with open(route_path, "r") as f:
        content = f.read()
    
    # Check for the new payload structure with animeTitle and episode
    has_anime_title_in_headings = re.search(r'headings:\s*{\s*en:\s*`Episode Baru:\s*\$\{video\.animeTitle', content)
    has_episode_in_contents = re.search(r'contents:\s*{\s*en:\s*`Tonton.*\$\{video\.episode', content)
    
    print(f"✓ Headings include animeTitle: {bool(has_anime_title_in_headings)}")
    print(f"✓ Contents include episode: {bool(has_episode_in_contents)}")
    
    # Extract the actual payload for verification
    payload_match = re.search(r'const payload = \{([^}]+\{[^}]+\}[^}]+)\}', content, re.DOTALL)
    if payload_match:
        payload_text = payload_match.group(0)
        print("\n✓ Found OneSignal payload:")
        print(payload_text[:300] + "..." if len(payload_text) > 300 else payload_text)
    
    if has_anime_title_in_headings and has_episode_in_contents:
        print("\n✅ TEST PASSED: OneSignal payload correctly includes animeTitle and episode")
        return True
    else:
        print("\n❌ TEST FAILED: OneSignal payload missing animeTitle or episode")
        return False

def test_payload_structure():
    """Test that the payload structure matches expected format"""
    print("\n=== Testing Payload Structure ===")
    route_path = "/app/app/api/[[...path]]/route.js"
    
    with open(route_path, "r") as f:
        content = f.read()
    
    # Check for specific expected strings
    checks = {
        "Episode Baru heading": 'Episode Baru: ${video.animeTitle' in content,
        "Retro Anime fallback": '"Retro Anime"' in content,
        "Tonton content": 'Tonton ${video.title}' in content,
        "Episode in parentheses": '(${video.episode' in content,
        "Eps 1 fallback": '"Eps 1"' in content,
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}: {result}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST PASSED: All payload structure checks passed")
        return True
    else:
        print("\n❌ TEST FAILED: Some payload structure checks failed")
        return False

def main():
    print("=" * 60)
    print("OneSignal Payload Update Verification Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Environment Variables", test_env_variables()))
    results.append(("OneSignal Payload", test_onesignal_payload()))
    results.append(("Payload Structure", test_payload_structure()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! OneSignal integration is correctly configured.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
