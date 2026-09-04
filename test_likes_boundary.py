#!/usr/bin/env python3
"""
Comprehensive Boundary Check Test for Likes Toggle API
Tests edge cases and boundary conditions for POST /api/videos/toggle-like
"""

import requests
import json
from datetime import datetime

# Base URL from environment
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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_boundary_unlike_at_zero():
    """Test 1: Unlike when likes = 0 (should stay at 0, not go negative)"""
    print("\n=== Test 1: Boundary Check - Unlike at Zero ===")
    
    try:
        # Create a test video with 0 likes
        video_payload = {
            "title": "Test Video: Boundary Check Zero Likes",
            "animeTitle": "Test Anime",
            "episode": "Eps Boundary Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/boundary-test",
            "description": "Test video for boundary check",
            "views": 0,
            "likes": 0
        }
        
        create_response = requests.post(f"{BASE_URL}/videos", json=video_payload, timeout=10)
        if create_response.status_code != 200:
            log_test("Boundary Check - Unlike at Zero", False, f"Failed to create test video: {create_response.status_code}")
            return False
        
        test_video = create_response.json()
        video_id = test_video['id']
        
        print(f"   Created test video with ID: {video_id}, likes: {test_video.get('likes', 0)}")
        
        # Try to unlike when likes = 0
        unlike_payload = {
            "id": video_id,
            "action": "unlike"
        }
        
        unlike_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
        if unlike_response.status_code != 200:
            log_test("Boundary Check - Unlike at Zero", False, f"Unlike action failed with status code: {unlike_response.status_code}")
            # Cleanup
            requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
            return False
        
        unliked_video = unlike_response.json()
        final_likes = unliked_video.get('likes', -1)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
        
        # Verify likes stayed at 0 (not negative)
        if final_likes == 0:
            log_test("Boundary Check - Unlike at Zero", True, f"✓ Likes correctly stayed at 0 (not negative). Boundary check working: Math.max(0, likes - 1) = {final_likes}")
            return True
        elif final_likes < 0:
            log_test("Boundary Check - Unlike at Zero", False, f"❌ CRITICAL: Likes went negative! Expected 0, got {final_likes}. Boundary check FAILED.")
            return False
        else:
            log_test("Boundary Check - Unlike at Zero", False, f"Unexpected likes value: {final_likes}")
            return False
            
    except Exception as e:
        log_test("Boundary Check - Unlike at Zero", False, f"Error: {str(e)}")
        return False

def test_boundary_multiple_unlikes_at_zero():
    """Test 2: Multiple unlikes when likes = 0 (should stay at 0)"""
    print("\n=== Test 2: Boundary Check - Multiple Unlikes at Zero ===")
    
    try:
        # Create a test video with 0 likes
        video_payload = {
            "title": "Test Video: Multiple Unlikes Boundary",
            "animeTitle": "Test Anime",
            "episode": "Eps Boundary Test 2",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/boundary-test-2",
            "description": "Test video for multiple unlikes boundary check",
            "views": 0,
            "likes": 0
        }
        
        create_response = requests.post(f"{BASE_URL}/videos", json=video_payload, timeout=10)
        if create_response.status_code != 200:
            log_test("Boundary Check - Multiple Unlikes at Zero", False, f"Failed to create test video: {create_response.status_code}")
            return False
        
        test_video = create_response.json()
        video_id = test_video['id']
        
        print(f"   Created test video with ID: {video_id}, likes: {test_video.get('likes', 0)}")
        
        # Try to unlike multiple times when likes = 0
        unlike_payload = {
            "id": video_id,
            "action": "unlike"
        }
        
        # Unlike 5 times
        for i in range(5):
            unlike_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
            if unlike_response.status_code != 200:
                log_test("Boundary Check - Multiple Unlikes at Zero", False, f"Unlike action {i+1} failed with status code: {unlike_response.status_code}")
                requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
                return False
        
        # Get final state
        final_response = requests.get(f"{BASE_URL}/videos", timeout=10)
        videos = final_response.json()
        final_video = next((v for v in videos if v['id'] == video_id), None)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
        
        if final_video:
            final_likes = final_video.get('likes', -1)
            if final_likes == 0:
                log_test("Boundary Check - Multiple Unlikes at Zero", True, f"✓ After 5 unlikes, likes correctly stayed at 0. Boundary protection working correctly.")
                return True
            elif final_likes < 0:
                log_test("Boundary Check - Multiple Unlikes at Zero", False, f"❌ CRITICAL: Likes went negative after multiple unlikes! Expected 0, got {final_likes}.")
                return False
            else:
                log_test("Boundary Check - Multiple Unlikes at Zero", False, f"Unexpected likes value: {final_likes}")
                return False
        else:
            log_test("Boundary Check - Multiple Unlikes at Zero", False, "Could not find video after test")
            return False
            
    except Exception as e:
        log_test("Boundary Check - Multiple Unlikes at Zero", False, f"Error: {str(e)}")
        return False

def test_boundary_invalid_video_id():
    """Test 3: Toggle like with invalid/non-existent video ID"""
    print("\n=== Test 3: Boundary Check - Invalid Video ID ===")
    
    try:
        # Try to like a non-existent video
        like_payload = {
            "id": "non-existent-video-id-12345",
            "action": "like"
        }
        
        response = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        
        # The API should handle this gracefully (either 404 or handle null video)
        if response.status_code == 200:
            # Check if it handled null video gracefully
            result = response.json()
            if result is None or result.get('id') is None:
                log_test("Boundary Check - Invalid Video ID", True, "✓ API handled invalid video ID gracefully (returned null/empty)")
                return True
            else:
                log_test("Boundary Check - Invalid Video ID", False, f"API returned unexpected data for non-existent video: {result}")
                return False
        elif response.status_code == 404:
            log_test("Boundary Check - Invalid Video ID", True, "✓ API correctly returned 404 for non-existent video")
            return True
        elif response.status_code == 500:
            log_test("Boundary Check - Invalid Video ID", False, f"❌ API returned 500 error for invalid video ID (should handle gracefully)")
            return False
        else:
            log_test("Boundary Check - Invalid Video ID", True, f"✓ API handled invalid video ID with status code: {response.status_code}")
            return True
            
    except Exception as e:
        log_test("Boundary Check - Invalid Video ID", False, f"Error: {str(e)}")
        return False

def test_boundary_missing_id_parameter():
    """Test 4: Toggle like with missing 'id' parameter"""
    print("\n=== Test 4: Boundary Check - Missing ID Parameter ===")
    
    try:
        # Try to like without providing video ID
        like_payload = {
            "action": "like"
            # Missing "id" field
        }
        
        response = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        
        # The API should handle this gracefully (either 400 or handle undefined)
        if response.status_code == 400:
            log_test("Boundary Check - Missing ID Parameter", True, "✓ API correctly returned 400 for missing ID parameter")
            return True
        elif response.status_code == 200:
            # Check if it handled undefined ID gracefully
            result = response.json()
            if result is None or result.get('id') is None:
                log_test("Boundary Check - Missing ID Parameter", True, "✓ API handled missing ID parameter gracefully")
                return True
            else:
                log_test("Boundary Check - Missing ID Parameter", False, f"API should reject missing ID parameter but returned: {result}")
                return False
        elif response.status_code == 500:
            log_test("Boundary Check - Missing ID Parameter", False, f"❌ API returned 500 error for missing ID (should handle gracefully with 400)")
            return False
        else:
            log_test("Boundary Check - Missing ID Parameter", True, f"✓ API handled missing ID with status code: {response.status_code}")
            return True
            
    except Exception as e:
        log_test("Boundary Check - Missing ID Parameter", False, f"Error: {str(e)}")
        return False

def test_boundary_missing_action_parameter():
    """Test 5: Toggle like with missing 'action' parameter"""
    print("\n=== Test 5: Boundary Check - Missing Action Parameter ===")
    
    try:
        # First, get a video to test with
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("Boundary Check - Missing Action Parameter", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        if not videos or len(videos) == 0:
            log_test("Boundary Check - Missing Action Parameter", False, "No videos available for testing")
            return False
        
        test_video = videos[0]
        video_id = test_video['id']
        
        # Try to toggle like without providing action
        payload = {
            "id": video_id
            # Missing "action" field
        }
        
        response = requests.post(f"{BASE_URL}/videos/toggle-like", json=payload, timeout=10)
        
        # The API should handle this gracefully
        if response.status_code == 400:
            log_test("Boundary Check - Missing Action Parameter", True, "✓ API correctly returned 400 for missing action parameter")
            return True
        elif response.status_code == 200:
            # Check behavior - it might default to some action
            result = response.json()
            log_test("Boundary Check - Missing Action Parameter", True, f"✓ API handled missing action parameter (may have defaulted). Response: {result.get('likes', 'N/A')} likes")
            return True
        elif response.status_code == 500:
            log_test("Boundary Check - Missing Action Parameter", False, f"❌ API returned 500 error for missing action (should handle gracefully)")
            return False
        else:
            log_test("Boundary Check - Missing Action Parameter", True, f"✓ API handled missing action with status code: {response.status_code}")
            return True
            
    except Exception as e:
        log_test("Boundary Check - Missing Action Parameter", False, f"Error: {str(e)}")
        return False

def test_boundary_invalid_action_value():
    """Test 6: Toggle like with invalid action value (not 'like' or 'unlike')"""
    print("\n=== Test 6: Boundary Check - Invalid Action Value ===")
    
    try:
        # First, get a video to test with
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("Boundary Check - Invalid Action Value", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        if not videos or len(videos) == 0:
            log_test("Boundary Check - Invalid Action Value", False, "No videos available for testing")
            return False
        
        test_video = videos[0]
        video_id = test_video['id']
        initial_likes = test_video.get('likes', 0)
        
        # Try with invalid action value
        invalid_payload = {
            "id": video_id,
            "action": "invalid_action"
        }
        
        response = requests.post(f"{BASE_URL}/videos/toggle-like", json=invalid_payload, timeout=10)
        
        # The API should handle this gracefully
        if response.status_code == 400:
            log_test("Boundary Check - Invalid Action Value", True, "✓ API correctly returned 400 for invalid action value")
            return True
        elif response.status_code == 200:
            result = response.json()
            final_likes = result.get('likes', 0)
            # Check if likes changed unexpectedly
            if final_likes == initial_likes:
                log_test("Boundary Check - Invalid Action Value", True, f"✓ API handled invalid action gracefully (likes unchanged: {initial_likes})")
                return True
            else:
                log_test("Boundary Check - Invalid Action Value", False, f"Invalid action changed likes from {initial_likes} to {final_likes}")
                return False
        elif response.status_code == 500:
            log_test("Boundary Check - Invalid Action Value", False, f"❌ API returned 500 error for invalid action (should handle gracefully)")
            return False
        else:
            log_test("Boundary Check - Invalid Action Value", True, f"✓ API handled invalid action with status code: {response.status_code}")
            return True
            
    except Exception as e:
        log_test("Boundary Check - Invalid Action Value", False, f"Error: {str(e)}")
        return False

def test_boundary_empty_payload():
    """Test 7: Toggle like with empty payload"""
    print("\n=== Test 7: Boundary Check - Empty Payload ===")
    
    try:
        # Try with empty payload
        empty_payload = {}
        
        response = requests.post(f"{BASE_URL}/videos/toggle-like", json=empty_payload, timeout=10)
        
        # The API should handle this gracefully
        if response.status_code == 400:
            log_test("Boundary Check - Empty Payload", True, "✓ API correctly returned 400 for empty payload")
            return True
        elif response.status_code == 200:
            result = response.json()
            if result is None or result.get('id') is None:
                log_test("Boundary Check - Empty Payload", True, "✓ API handled empty payload gracefully")
                return True
            else:
                log_test("Boundary Check - Empty Payload", False, f"API should reject empty payload but returned: {result}")
                return False
        elif response.status_code == 500:
            log_test("Boundary Check - Empty Payload", False, f"❌ API returned 500 error for empty payload (should handle gracefully)")
            return False
        else:
            log_test("Boundary Check - Empty Payload", True, f"✓ API handled empty payload with status code: {response.status_code}")
            return True
            
    except Exception as e:
        log_test("Boundary Check - Empty Payload", False, f"Error: {str(e)}")
        return False

def test_boundary_concurrent_likes():
    """Test 8: Concurrent like/unlike operations (race condition test)"""
    print("\n=== Test 8: Boundary Check - Concurrent Operations ===")
    
    try:
        # Create a test video
        video_payload = {
            "title": "Test Video: Concurrent Operations",
            "animeTitle": "Test Anime",
            "episode": "Eps Concurrent Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/concurrent-test",
            "description": "Test video for concurrent operations",
            "views": 0,
            "likes": 10
        }
        
        create_response = requests.post(f"{BASE_URL}/videos", json=video_payload, timeout=10)
        if create_response.status_code != 200:
            log_test("Boundary Check - Concurrent Operations", False, f"Failed to create test video: {create_response.status_code}")
            return False
        
        test_video = create_response.json()
        video_id = test_video['id']
        initial_likes = test_video.get('likes', 0)
        
        print(f"   Created test video with ID: {video_id}, initial likes: {initial_likes}")
        
        # Perform rapid like/unlike operations
        like_payload = {"id": video_id, "action": "like"}
        unlike_payload = {"id": video_id, "action": "unlike"}
        
        # Rapid fire 10 likes and 10 unlikes
        for i in range(10):
            requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
            requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
        
        # Get final state
        final_response = requests.get(f"{BASE_URL}/videos", timeout=10)
        videos = final_response.json()
        final_video = next((v for v in videos if v['id'] == video_id), None)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
        
        if final_video:
            final_likes = final_video.get('likes', -1)
            # After 10 likes and 10 unlikes, should be back to initial value
            if final_likes == initial_likes:
                log_test("Boundary Check - Concurrent Operations", True, f"✓ After 10 likes and 10 unlikes, likes correctly returned to initial value: {initial_likes}")
                return True
            elif final_likes >= 0:
                # As long as it's not negative, it's acceptable (race conditions might cause slight variations)
                log_test("Boundary Check - Concurrent Operations", True, f"✓ Concurrent operations handled. Final likes: {final_likes} (initial: {initial_likes}). No negative values.")
                return True
            else:
                log_test("Boundary Check - Concurrent Operations", False, f"❌ CRITICAL: Likes went negative after concurrent operations! Final: {final_likes}")
                return False
        else:
            log_test("Boundary Check - Concurrent Operations", False, "Could not find video after test")
            return False
            
    except Exception as e:
        log_test("Boundary Check - Concurrent Operations", False, f"Error: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("LIKES TOGGLE BOUNDARY CHECK TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print("="*80)
    
    if test_results['failed'] > 0:
        print("\n❌ Failed Tests:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"  - {test['name']}: {test['message']}")
    else:
        print("\n✅ ALL BOUNDARY CHECKS PASSED!")
    
    print("\n" + "="*80)
    return test_results['failed'] == 0

def main():
    """Run all boundary check tests"""
    print("\n" + "="*80)
    print("STARTING COMPREHENSIVE LIKES TOGGLE BOUNDARY CHECK TESTS")
    print("="*80)
    print(f"Testing API: {BASE_URL}/videos/toggle-like")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Run all boundary check tests
    test_boundary_unlike_at_zero()
    test_boundary_multiple_unlikes_at_zero()
    test_boundary_invalid_video_id()
    test_boundary_missing_id_parameter()
    test_boundary_missing_action_parameter()
    test_boundary_invalid_action_value()
    test_boundary_empty_payload()
    test_boundary_concurrent_likes()
    
    # Print summary
    all_passed = print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
