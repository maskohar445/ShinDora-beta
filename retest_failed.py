#!/usr/bin/env python3
"""
Re-test failed tests to check for transient errors
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://next-shindora.preview.emergentagent.com/api"

def test_vote_quota_check_duplicate():
    """Test 48: POST /api/polling/vote - Duplicate vote should be rejected (Quota Check)"""
    print("\n=== Re-Test 48: POST /api/polling/vote - Quota Check (Duplicate Vote) ===")
    
    try:
        # Create a new poll
        poll_data = {
            "title": "Test Poll for Quota Check Retest",
            "options": [
                {"id": "opt-a", "name": "Option A", "votes": 0},
                {"id": "opt-b", "name": "Option B", "votes": 0}
            ],
            "isActive": True
        }
        
        create_response = requests.post(f"{BASE_URL}/polling", json=poll_data, timeout=10)
        if create_response.status_code != 200:
            print(f"❌ FAIL: Failed to create test poll: {create_response.status_code}")
            return False
        
        poll = create_response.json()
        print(f"✅ Poll created: {poll['id']}")
        
        # First vote with userId
        vote_data = {
            "pollId": poll['id'],
            "optionId": "opt-a",
            "userId": "test-user-retest-456"
        }
        
        first_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if first_response.status_code != 200:
            print(f"❌ FAIL: First vote failed: {first_response.status_code}")
            return False
        
        print(f"✅ First vote successful")
        
        # Try to vote again with same userId (should be rejected)
        second_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if second_response.status_code == 400:
            error_data = second_response.json()
            error_message = error_data.get('error', '')
            if 'sudah memberikan suara' in error_message or 'already voted' in error_message.lower():
                print(f"✅ PASS: Duplicate vote correctly rejected with error: '{error_message}'")
                # Clean up test poll
                try:
                    requests.delete(f"{BASE_URL}/polling?id={poll['id']}", timeout=10)
                except Exception:
                    pass
                return True
            else:
                print(f"❌ FAIL: Got 400 error but wrong message: {error_message}")
                return False
        else:
            print(f"❌ FAIL: Duplicate vote was not rejected. Status code: {second_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error: {str(e)}")
        return False

def test_vote_different_user():
    """Test 49: POST /api/polling/vote - Different user should be able to vote"""
    print("\n=== Re-Test 49: POST /api/polling/vote - Different User Vote ===")
    
    try:
        # Create a new poll
        poll_data = {
            "title": "Test Poll for Multiple Users Retest",
            "options": [
                {"id": "opt-x", "name": "Option X", "votes": 0},
                {"id": "opt-y", "name": "Option Y", "votes": 0}
            ],
            "isActive": True
        }
        
        create_response = requests.post(f"{BASE_URL}/polling", json=poll_data, timeout=10)
        if create_response.status_code != 200:
            print(f"❌ FAIL: Failed to create test poll: {create_response.status_code}")
            return False
        
        poll = create_response.json()
        print(f"✅ Poll created: {poll['id']}")
        
        # First user votes
        vote_data_user1 = {
            "pollId": poll['id'],
            "optionId": "opt-x",
            "userId": "test-user-retest-789"
        }
        
        first_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data_user1, timeout=10)
        if first_response.status_code != 200:
            print(f"❌ FAIL: First user vote failed: {first_response.status_code}")
            return False
        
        print(f"✅ First user vote successful")
        
        # Second user votes (should succeed)
        vote_data_user2 = {
            "pollId": poll['id'],
            "optionId": "opt-y",
            "userId": "test-user-retest-999"
        }
        
        second_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data_user2, timeout=10)
        if second_response.status_code == 200:
            updated_poll = second_response.json()
            opt_x = next((opt for opt in updated_poll.get('options', []) if opt['id'] == 'opt-x'), None)
            opt_y = next((opt for opt in updated_poll.get('options', []) if opt['id'] == 'opt-y'), None)
            
            if opt_x and opt_y and opt_x.get('votes', 0) == 1 and opt_y.get('votes', 0) == 1:
                print(f"✅ PASS: Different users can vote successfully. Option X: {opt_x['votes']} vote, Option Y: {opt_y['votes']} vote")
                # Clean up test poll
                try:
                    requests.delete(f"{BASE_URL}/polling?id={poll['id']}", timeout=10)
                except Exception:
                    pass
                return True
            else:
                print(f"❌ FAIL: Vote counts incorrect")
                return False
        else:
            print(f"❌ FAIL: Second user vote failed: {second_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Re-testing Failed Tests")
    print("="*60)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test48_passed = test_vote_quota_check_duplicate()
    test49_passed = test_vote_different_user()
    
    print("\n" + "="*60)
    print("RE-TEST SUMMARY")
    print("="*60)
    print(f"Test 48 (Quota Check): {'✅ PASSED' if test48_passed else '❌ FAILED'}")
    print(f"Test 49 (Different User): {'✅ PASSED' if test49_passed else '❌ FAILED'}")
    print("="*60)
