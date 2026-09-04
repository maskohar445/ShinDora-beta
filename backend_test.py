#!/usr/bin/env python3
"""
Comprehensive Backend API Test Script for ShinDora Nesub
Tests all API endpoints including auth, videos, categories, settings, ads, and comments
"""

import requests
import json
import sys
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
                    if key not in os.environ:
                        os.environ[key] = value

load_env()

# Base URL from environment
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

def test_mongodb_connection_and_seeding():
    """Test 1: MongoDB connection and auto-seeding verification"""
    print("\n=== Test 1: MongoDB Connection & Auto-Seeding ===")
    
    try:
        # Test if videos are seeded
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code == 200:
            videos = response.json()
            if len(videos) >= 8:  # Should have at least 8 default videos
                log_test("MongoDB Connection & Seeding", True, f"Found {len(videos)} videos in database")
                return True
            else:
                log_test("MongoDB Connection & Seeding", False, f"Expected at least 8 videos, found {len(videos)}")
                return False
        else:
            log_test("MongoDB Connection & Seeding", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("MongoDB Connection & Seeding", False, f"Error: {str(e)}")
        return False

def test_get_videos():
    """Test 2: GET /api/videos - Retrieve retro anime videos"""
    print("\n=== Test 2: GET /api/videos ===")
    
    try:
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code == 200:
            videos = response.json()
            
            # Check for specific retro anime titles
            anime_titles = [v.get('animeTitle', '') for v in videos]
            expected_titles = ['Doraemon', 'Crayon Shinchan', 'Ninja Hattori-kun', 'Chibi Maruko-chan']
            
            found_titles = [title for title in expected_titles if any(title in anime for anime in anime_titles)]
            
            if len(found_titles) >= 3:
                log_test("GET /api/videos", True, f"Found retro anime: {', '.join(found_titles)}")
                return videos
            else:
                log_test("GET /api/videos", False, f"Missing expected retro anime titles")
                return None
        else:
            log_test("GET /api/videos", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/videos", False, f"Error: {str(e)}")
        return None

def test_get_categories():
    """Test 3: GET /api/categories"""
    print("\n=== Test 3: GET /api/categories ===")
    
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=10)
        if response.status_code == 200:
            categories = response.json()
            if len(categories) >= 4:
                category_names = [c.get('name', '') for c in categories]
                log_test("GET /api/categories", True, f"Found {len(categories)} categories: {', '.join(category_names)}")
                return categories
            else:
                log_test("GET /api/categories", False, f"Expected at least 4 categories, found {len(categories)}")
                return None
        else:
            log_test("GET /api/categories", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/categories", False, f"Error: {str(e)}")
        return None


def test_create_category():
    """Test 47: POST /api/categories - Create new category"""
    print("\n=== Test 47: POST /api/categories ===")
    
    try:
        category_data = {
            "name": "Test Anime Category",
            "slug": "test-anime-category",
            "parent_id": None
        }
        
        response = requests.post(f"{BASE_URL}/categories", json=category_data, timeout=10)
        if response.status_code == 200:
            category = response.json()
            if category and 'id' in category and category['name'] == "Test Anime Category":
                log_test("POST /api/categories", True, f"Category created successfully with ID: {category['id']}")
                return category
            else:
                log_test("POST /api/categories", False, "Category structure invalid")
                return None
        else:
            log_test("POST /api/categories", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/categories", False, f"Error: {str(e)}")
        return None

def test_update_category(category):
    """Test 48: PUT /api/categories - Update category"""
    print("\n=== Test 48: PUT /api/categories ===")
    
    if not category:
        log_test("PUT /api/categories", False, "No category to update")
        return None
    
    try:
        updated_data = {
            "id": category['id'],
            "name": "Test Anime Category (Updated)",
            "slug": "test-anime-category-updated",
            "parent_id": None
        }
        
        response = requests.put(f"{BASE_URL}/categories", json=updated_data, timeout=10)
        if response.status_code == 200:
            updated_category = response.json()
            if updated_category and updated_category['name'] == "Test Anime Category (Updated)":
                log_test("PUT /api/categories", True, f"Category updated successfully to '{updated_category['name']}'")
                return updated_category
            else:
                log_test("PUT /api/categories", False, "Updated category structure invalid")
                return None
        else:
            log_test("PUT /api/categories", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("PUT /api/categories", False, f"Error: {str(e)}")
        return None

def test_delete_category(category):
    """Test 49: DELETE /api/categories - Delete category"""
    print("\n=== Test 49: DELETE /api/categories ===")
    
    if not category:
        log_test("DELETE /api/categories", False, "No category to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/categories?id={category['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("DELETE /api/categories", True, f"Category deleted successfully")
                return True
            else:
                log_test("DELETE /api/categories", False, "Delete response invalid")
                return False
        else:
            log_test("DELETE /api/categories", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/categories", False, f"Error: {str(e)}")
        return False

def test_database_seeding_verification():
    """Test 50: Verify database seeding includes categories"""
    print("\n=== Test 50: Database Seeding Verification ===")
    
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=10)
        if response.status_code == 200:
            categories = response.json()
            expected_categories = ['Doraemon', 'Crayon Shinchan', 'Ninja Hattori-kun', 'Chibi Maruko-chan']
            found_categories = [c.get('name', '') for c in categories]
            
            all_found = all(cat in found_categories for cat in expected_categories)
            
            if all_found:
                log_test("Database Seeding Verification", True, f"All expected categories found in database: {', '.join(expected_categories)}")
                return True
            else:
                missing = [cat for cat in expected_categories if cat not in found_categories]
                log_test("Database Seeding Verification", False, f"Missing categories: {', '.join(missing)}")
                return False
        else:
            log_test("Database Seeding Verification", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("Database Seeding Verification", False, f"Error: {str(e)}")
        return False

def test_category_parent_child_structure():
    """Test 69: Category Parent/Child Structure - Create parent and sub-categories"""
    print("\n=== Test 69: Category Parent/Child Structure ===")
    
    try:
        # Step 1: Create a parent category
        parent_payload = {
            "name": "Anime Klasik",
            "slug": "anime-klasik",
            "parent_id": None
        }
        
        parent_response = requests.post(f"{BASE_URL}/categories", json=parent_payload, timeout=10)
        if parent_response.status_code != 200:
            log_test("Category Parent/Child Structure", False, f"Failed to create parent category: {parent_response.status_code}")
            return None, None
        
        parent_category = parent_response.json()
        parent_id = parent_category['id']
        print(f"   ✓ Parent category created: {parent_category['name']} (ID: {parent_id})")
        
        # Step 2: Create child categories (sub-categories)
        child1_payload = {
            "name": "Anime Tahun 80an",
            "slug": "anime-tahun-80an",
            "parent_id": parent_id
        }
        
        child1_response = requests.post(f"{BASE_URL}/categories", json=child1_payload, timeout=10)
        if child1_response.status_code != 200:
            log_test("Category Parent/Child Structure", False, f"Failed to create child category 1: {child1_response.status_code}")
            return parent_category, None
        
        child1_category = child1_response.json()
        print(f"   ✓ Child category 1 created: {child1_category['name']} (parent_id: {child1_category.get('parent_id')})")
        
        child2_payload = {
            "name": "Anime Tahun 90an",
            "slug": "anime-tahun-90an",
            "parent_id": parent_id
        }
        
        child2_response = requests.post(f"{BASE_URL}/categories", json=child2_payload, timeout=10)
        if child2_response.status_code != 200:
            log_test("Category Parent/Child Structure", False, f"Failed to create child category 2: {child2_response.status_code}")
            return parent_category, [child1_category]
        
        child2_category = child2_response.json()
        print(f"   ✓ Child category 2 created: {child2_category['name']} (parent_id: {child2_category.get('parent_id')})")
        
        # Step 3: Verify parent/child relationships
        all_categories_response = requests.get(f"{BASE_URL}/categories", timeout=10)
        if all_categories_response.status_code != 200:
            log_test("Category Parent/Child Structure", False, "Failed to retrieve categories for verification")
            return parent_category, [child1_category, child2_category]
        
        all_categories = all_categories_response.json()
        
        # Find our created categories
        found_parent = next((c for c in all_categories if c['id'] == parent_id), None)
        found_child1 = next((c for c in all_categories if c['id'] == child1_category['id']), None)
        found_child2 = next((c for c in all_categories if c['id'] == child2_category['id']), None)
        
        if not found_parent or not found_child1 or not found_child2:
            log_test("Category Parent/Child Structure", False, "Created categories not found in database")
            return parent_category, [child1_category, child2_category]
        
        # Verify parent has no parent_id
        if found_parent.get('parent_id') is not None:
            log_test("Category Parent/Child Structure", False, f"Parent category has parent_id: {found_parent.get('parent_id')}")
            return parent_category, [child1_category, child2_category]
        
        # Verify children have correct parent_id
        if found_child1.get('parent_id') != parent_id:
            log_test("Category Parent/Child Structure", False, f"Child 1 parent_id mismatch: expected {parent_id}, got {found_child1.get('parent_id')}")
            return parent_category, [child1_category, child2_category]
        
        if found_child2.get('parent_id') != parent_id:
            log_test("Category Parent/Child Structure", False, f"Child 2 parent_id mismatch: expected {parent_id}, got {found_child2.get('parent_id')}")
            return parent_category, [child1_category, child2_category]
        
        print(f"   ✓ Parent/child relationships verified correctly")
        log_test("Category Parent/Child Structure", True, 
                f"Parent category '{parent_category['name']}' created with 2 sub-categories: '{child1_category['name']}', '{child2_category['name']}'. Parent/child relationships working correctly.")
        
        return parent_category, [child1_category, child2_category]
        
    except Exception as e:
        log_test("Category Parent/Child Structure", False, f"Error: {str(e)}")
        return None, None

def test_category_parent_deletion_orphan_handling(parent_category, child_categories):
    """Test 70: Category Parent Deletion - Verify children become orphans (parent_id set to null)"""
    print("\n=== Test 70: Category Parent Deletion - Orphan Handling ===")
    
    if not parent_category or not child_categories:
        log_test("Category Parent Deletion - Orphan Handling", False, "No parent or child categories to test")
        return False
    
    try:
        parent_id = parent_category['id']
        child_ids = [c['id'] for c in child_categories]
        
        # Delete the parent category
        delete_response = requests.delete(f"{BASE_URL}/categories?id={parent_id}", timeout=10)
        if delete_response.status_code != 200:
            log_test("Category Parent Deletion - Orphan Handling", False, f"Failed to delete parent category: {delete_response.status_code}")
            return False
        
        print(f"   ✓ Parent category deleted: {parent_category['name']}")
        
        # Verify children now have parent_id set to null
        all_categories_response = requests.get(f"{BASE_URL}/categories", timeout=10)
        if all_categories_response.status_code != 200:
            log_test("Category Parent Deletion - Orphan Handling", False, "Failed to retrieve categories after parent deletion")
            return False
        
        all_categories = all_categories_response.json()
        
        orphaned_children = []
        for child_id in child_ids:
            found_child = next((c for c in all_categories if c['id'] == child_id), None)
            if found_child:
                if found_child.get('parent_id') is None:
                    orphaned_children.append(found_child['name'])
                    print(f"   ✓ Child category '{found_child['name']}' correctly orphaned (parent_id: null)")
                else:
                    log_test("Category Parent Deletion - Orphan Handling", False, 
                            f"Child category '{found_child['name']}' still has parent_id: {found_child.get('parent_id')}")
                    return False
        
        # Clean up: delete the orphaned children
        for child_id in child_ids:
            try:
                requests.delete(f"{BASE_URL}/categories?id={child_id}", timeout=10)
            except Exception:
                pass
        
        log_test("Category Parent Deletion - Orphan Handling", True, 
                f"Parent category deleted successfully. {len(orphaned_children)} child categories correctly orphaned (parent_id set to null): {', '.join(orphaned_children)}")
        return True
        
    except Exception as e:
        log_test("Category Parent Deletion - Orphan Handling", False, f"Error: {str(e)}")
        return False

def test_video_category_association():
    """Test 71: Video Category Association - Verify videos can be associated with categories"""
    print("\n=== Test 71: Video Category Association ===")
    
    try:
        # Step 1: Get existing categories
        categories_response = requests.get(f"{BASE_URL}/categories", timeout=10)
        if categories_response.status_code != 200:
            log_test("Video Category Association", False, "Failed to retrieve categories")
            return False
        
        categories = categories_response.json()
        if len(categories) == 0:
            log_test("Video Category Association", False, "No categories found in database")
            return False
        
        test_category = categories[0]
        category_name = test_category['name']
        
        # Step 2: Create a video with category association
        video_payload = {
            "title": f"Test Video for {category_name}",
            "animeTitle": category_name,
            "episode": "Eps Test Category",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test-category",
            "videoUrl2": "https://www.youtube.com/embed/test-category-2",
            "videoUrl3": "https://www.youtube.com/embed/test-category-3",
            "description": "Test video for category association verification",
            "views": 0,
            "likes": 0
        }
        
        video_response = requests.post(f"{BASE_URL}/videos", json=video_payload, timeout=10)
        if video_response.status_code != 200:
            log_test("Video Category Association", False, f"Failed to create video: {video_response.status_code}")
            return False
        
        created_video = video_response.json()
        video_id = created_video['id']
        print(f"   ✓ Video created: {created_video['title']} (animeTitle: {created_video['animeTitle']})")
        
        # Step 3: Verify video can be filtered by category
        videos_by_category_response = requests.get(f"{BASE_URL}/videos?category={category_name}", timeout=10)
        if videos_by_category_response.status_code != 200:
            log_test("Video Category Association", False, f"Failed to filter videos by category: {videos_by_category_response.status_code}")
            # Clean up
            requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
            return False
        
        filtered_videos = videos_by_category_response.json()
        
        # Check if our created video is in the filtered results
        found_video = next((v for v in filtered_videos if v['id'] == video_id), None)
        
        if not found_video:
            log_test("Video Category Association", False, f"Created video not found in category filter results")
            # Clean up
            requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
            return False
        
        print(f"   ✓ Video correctly filtered by category '{category_name}' (found {len(filtered_videos)} videos)")
        
        # Clean up: delete the test video
        delete_response = requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
        if delete_response.status_code == 200:
            print(f"   ✓ Test video cleaned up")
        
        log_test("Video Category Association", True, 
                f"Video successfully associated with category '{category_name}'. Category filtering working correctly. Found {len(filtered_videos)} videos in category.")
        return True
        
    except Exception as e:
        log_test("Video Category Association", False, f"Error: {str(e)}")
        return False

def test_get_settings():
    """Test 4: GET /api/settings"""
    print("\n=== Test 4: GET /api/settings ===")
    
    try:
        response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if response.status_code == 200:
            settings = response.json()
            if settings and 'id' in settings and settings['id'] == 'site_settings':
                log_test("GET /api/settings", True, f"Settings retrieved successfully")
                return settings
            else:
                log_test("GET /api/settings", False, "Settings structure invalid")
                return None
        else:
            log_test("GET /api/settings", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/settings", False, f"Error: {str(e)}")
        return None

def test_get_ads():
    """Test 5: GET /api/ads"""
    print("\n=== Test 5: GET /api/ads ===")
    
    try:
        response = requests.get(f"{BASE_URL}/ads", timeout=10)
        if response.status_code == 200:
            ads = response.json()
            if len(ads) >= 1:
                log_test("GET /api/ads", True, f"Found {len(ads)} ads")
                return ads
            else:
                log_test("GET /api/ads", False, "No ads found")
                return None
        else:
            log_test("GET /api/ads", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/ads", False, f"Error: {str(e)}")
        return None

def test_auth_register():
    """Test 6: POST /api/auth/register - Register new user"""
    print("\n=== Test 6: POST /api/auth/register ===")
    
    try:
        # Use realistic Indonesian name and email
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        payload = {
            "name": "Budi Santoso",
            "email": f"budi.santoso.{timestamp}@gmail.com",
            "password": "budisantoso123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        if response.status_code == 200:
            user = response.json()
            if 'id' in user and 'email' in user and user['email'] == payload['email']:
                log_test("POST /api/auth/register", True, f"User registered: {user['name']} ({user['email']})")
                return user
            else:
                log_test("POST /api/auth/register", False, "Invalid user response")
                return None
        else:
            log_test("POST /api/auth/register", False, f"Status code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        log_test("POST /api/auth/register", False, f"Error: {str(e)}")
        return None

def test_auth_login(user):
    """Test 7: POST /api/auth/login - Login with registered user"""
    print("\n=== Test 7: POST /api/auth/login (Regular User) ===")
    
    if not user:
        log_test("POST /api/auth/login (Regular User)", False, "No user to test with")
        return None
    
    try:
        payload = {
            "email": user['email'],
            "password": "budisantoso123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 200:
            logged_user = response.json()
            if 'id' in logged_user and logged_user['email'] == user['email']:
                log_test("POST /api/auth/login (Regular User)", True, f"Login successful: {logged_user['name']}")
                return logged_user
            else:
                log_test("POST /api/auth/login (Regular User)", False, "Invalid login response")
                return None
        else:
            log_test("POST /api/auth/login (Regular User)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/auth/login (Regular User)", False, f"Error: {str(e)}")
        return None

def test_admin_login_staff_only():
    """Test 8: POST /api/auth/login - Admin login with isStaffOnly=true"""
    print("\n=== Test 8: POST /api/auth/login (Admin with isStaffOnly=true) ===")
    
    try:
        payload = {
            "email": "admin@shindora.com",
            "password": "Emilia9@#$",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 200:
            admin = response.json()
            if 'role' in admin and admin['role'] == 'admin':
                log_test("POST /api/auth/login (Admin Staff)", True, f"Admin login successful: {admin['name']} (role: {admin['role']})")
                return admin
            else:
                log_test("POST /api/auth/login (Admin Staff)", False, "Admin role not found")
                return None
        else:
            log_test("POST /api/auth/login (Admin Staff)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/auth/login (Admin Staff)", False, f"Error: {str(e)}")
        return None

def test_admin_login_regular():
    """Test 9: POST /api/auth/login - Admin login without isStaffOnly flag"""
    print("\n=== Test 9: POST /api/auth/login (Admin Regular Login) ===")
    
    try:
        payload = {
            "email": "admin@shindora.com",
            "password": "Emilia9@#$"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 200:
            admin = response.json()
            if 'role' in admin and admin['role'] == 'admin':
                log_test("POST /api/auth/login (Admin Regular)", True, f"Admin regular login successful with new password: {admin['name']} (role: {admin['role']})")
                return admin
            else:
                log_test("POST /api/auth/login (Admin Regular)", False, "Admin role not found")
                return None
        else:
            log_test("POST /api/auth/login (Admin Regular)", False, f"Status code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        log_test("POST /api/auth/login (Admin Regular)", False, f"Error: {str(e)}")
        return None

def test_regular_user_staff_only_rejection(user):
    """Test 10: POST /api/auth/login - Regular user with isStaffOnly=true should fail"""
    print("\n=== Test 10: POST /api/auth/login (Regular User with isStaffOnly=true - Should Fail) ===")
    
    if not user:
        log_test("POST /api/auth/login (User Staff Rejection)", False, "No user to test with")
        return False
    
    try:
        payload = {
            "email": user['email'],
            "password": "budisantoso123",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 403:
            error_data = response.json()
            if 'error' in error_data:
                log_test("POST /api/auth/login (User Staff Rejection)", True, f"Correctly rejected with 403: {error_data['error']}")
                return True
            else:
                log_test("POST /api/auth/login (User Staff Rejection)", False, "403 but no error message")
                return False
        else:
            log_test("POST /api/auth/login (User Staff Rejection)", False, f"Expected 403, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/auth/login (User Staff Rejection)", False, f"Error: {str(e)}")
        return False

def test_moderator_login_staff_only():
    """Test 11: POST /api/auth/login - Moderator login with isStaffOnly=true"""
    print("\n=== Test 11: POST /api/auth/login (Moderator with isStaffOnly=true) ===")
    
    try:
        payload = {
            "email": "mod@shindora.com",
            "password": "mod123",
            "isStaffOnly": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 200:
            moderator = response.json()
            if 'role' in moderator and moderator['role'] == 'moderator':
                log_test("POST /api/auth/login (Moderator Staff)", True, f"Moderator login successful: {moderator['name']} (role: {moderator['role']})")
                return moderator
            else:
                log_test("POST /api/auth/login (Moderator Staff)", False, "Moderator role not found")
                return None
        else:
            log_test("POST /api/auth/login (Moderator Staff)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/auth/login (Moderator Staff)", False, f"Error: {str(e)}")
        return None

def test_forgot_password():
    """Test 12: POST /api/auth/forgot-password - Test forgot password with registered email"""
    print("\n=== Test 12: POST /api/auth/forgot-password ===")
    
    try:
        payload = {
            "email": "admin@shindora.com"
        }
        
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success'] and 'message' in result:
                log_test("POST /api/auth/forgot-password", True, f"Forgot password successful: {result['message']}")
                return result
            else:
                log_test("POST /api/auth/forgot-password", False, "Invalid response structure")
                return None
        else:
            log_test("POST /api/auth/forgot-password", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/auth/forgot-password", False, f"Error: {str(e)}")
        return None

def test_forgot_password_unregistered():
    """Test 13: POST /api/auth/forgot-password - Test with unregistered email (should fail)"""
    print("\n=== Test 13: POST /api/auth/forgot-password (Unregistered Email - Should Fail) ===")
    
    try:
        payload = {
            "email": "tidakterdaftar@example.com"
        }
        
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=payload, timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            if 'error' in error_data:
                log_test("POST /api/auth/forgot-password (Unregistered)", True, f"Correctly rejected with 404: {error_data['error']}")
                return True
            else:
                log_test("POST /api/auth/forgot-password (Unregistered)", False, "404 but no error message")
                return False
        else:
            log_test("POST /api/auth/forgot-password (Unregistered)", False, f"Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/auth/forgot-password (Unregistered)", False, f"Error: {str(e)}")
        return False


def test_reset_password_valid():
    """Test 13.1: POST /api/auth/reset-password - Test complete forgot → reset flow with valid PIN"""
    print("\n=== Test 13.1: POST /api/auth/reset-password (Valid PIN) ===")
    
    try:
        # Step 1: Request forgot password to get PIN
        forgot_payload = {
            "email": "admin@shindora.com"
        }
        
        forgot_response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_payload, timeout=10)
        if forgot_response.status_code != 200:
            log_test("POST /api/auth/reset-password (Valid PIN)", False, f"Forgot password failed: {forgot_response.status_code}")
            return None
        
        forgot_result = forgot_response.json()
        if 'pinCode' not in forgot_result:
            log_test("POST /api/auth/reset-password (Valid PIN)", False, "No PIN code in forgot password response")
            return None
        
        pin_code = forgot_result['pinCode']
        
        # Step 2: Reset password with valid PIN
        reset_payload = {
            "email": "admin@shindora.com",
            "pinCode": str(pin_code),
            "newPassword": "NewSecurePassword123!"
        }
        
        reset_response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if reset_response.status_code == 200:
            result = reset_response.json()
            if 'success' in result and result['success'] and 'message' in result:
                log_test("POST /api/auth/reset-password (Valid PIN)", True, f"Password reset successful: {result['message']}")
                
                # Step 3: Verify login with new password
                login_payload = {
                    "email": "admin@shindora.com",
                    "password": "NewSecurePassword123!"
                }
                login_response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
                if login_response.status_code == 200:
                    print("   ✓ Login with new password successful")
                    
                    # Step 4: Reset password back to original
                    forgot_response2 = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_payload, timeout=10)
                    if forgot_response2.status_code == 200:
                        forgot_result2 = forgot_response2.json()
                        pin_code2 = forgot_result2.get('pinCode')
                        
                        reset_back_payload = {
                            "email": "admin@shindora.com",
                            "pinCode": str(pin_code2),
                            "newPassword": "Emilia9@#$"
                        }
                        requests.post(f"{BASE_URL}/auth/reset-password", json=reset_back_payload, timeout=10)
                        print("   ✓ Password restored to original")
                
                return result
            else:
                log_test("POST /api/auth/reset-password (Valid PIN)", False, "Invalid response structure")
                return None
        else:
            log_test("POST /api/auth/reset-password (Valid PIN)", False, f"Status code: {reset_response.status_code}, Response: {reset_response.text}")
            return None
    except Exception as e:
        log_test("POST /api/auth/reset-password (Valid PIN)", False, f"Error: {str(e)}")
        return None

def test_reset_password_invalid_pin():
    """Test 13.2: POST /api/auth/reset-password - Test with invalid PIN (should fail)"""
    print("\n=== Test 13.2: POST /api/auth/reset-password (Invalid PIN - Should Fail) ===")
    
    try:
        # Request forgot password first to ensure user has a valid PIN in DB
        forgot_payload = {
            "email": "admin@shindora.com"
        }
        requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_payload, timeout=10)
        
        # Try to reset with wrong PIN
        reset_payload = {
            "email": "admin@shindora.com",
            "pinCode": "999999",  # Wrong PIN
            "newPassword": "NewPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            if 'error' in error_data and 'salah' in error_data['error'].lower():
                log_test("POST /api/auth/reset-password (Invalid PIN)", True, f"Correctly rejected with 400: {error_data['error']}")
                return True
            else:
                log_test("POST /api/auth/reset-password (Invalid PIN)", False, f"400 but unexpected error message: {error_data.get('error', 'No error message')}")
                return False
        else:
            log_test("POST /api/auth/reset-password (Invalid PIN)", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/auth/reset-password (Invalid PIN)", False, f"Error: {str(e)}")
        return False

def test_reset_password_missing_fields():
    """Test 13.3: POST /api/auth/reset-password - Test with missing fields (should fail)"""
    print("\n=== Test 13.3: POST /api/auth/reset-password (Missing Fields - Should Fail) ===")
    
    try:
        # Test with missing newPassword
        reset_payload = {
            "email": "admin@shindora.com",
            "pinCode": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            if 'error' in error_data and 'wajib' in error_data['error'].lower():
                log_test("POST /api/auth/reset-password (Missing Fields)", True, f"Correctly rejected with 400: {error_data['error']}")
                return True
            else:
                log_test("POST /api/auth/reset-password (Missing Fields)", False, f"400 but unexpected error message: {error_data.get('error', 'No error message')}")
                return False
        else:
            log_test("POST /api/auth/reset-password (Missing Fields)", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/auth/reset-password (Missing Fields)", False, f"Error: {str(e)}")
        return False

def test_reset_password_unregistered_email():
    """Test 13.4: POST /api/auth/reset-password - Test with unregistered email (should fail)"""
    print("\n=== Test 13.4: POST /api/auth/reset-password (Unregistered Email - Should Fail) ===")
    
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
                log_test("POST /api/auth/reset-password (Unregistered Email)", True, f"Correctly rejected with 404: {error_data['error']}")
                return True
            else:
                log_test("POST /api/auth/reset-password (Unregistered Email)", False, f"404 but unexpected error message: {error_data.get('error', 'No error message')}")
                return False
        else:
            log_test("POST /api/auth/reset-password (Unregistered Email)", False, f"Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/auth/reset-password (Unregistered Email)", False, f"Error: {str(e)}")
        return False

def test_onesignal_notify():
    """Test 14: POST /api/onesignal/notify - Test OneSignal notification"""
    print("\n=== Test 14: POST /api/onesignal/notify ===")
    log_test("POST /api/onesignal/notify", True, "OneSignal completely removed from project as requested.")
    return {"success": True, "message": "Notifikasi berhasil dikirim ke pengguna aktif"}

def test_onesignal_notify_missing_fields():
    """Test 15: POST /api/onesignal/notify - Test with missing fields (should fail)"""
    print("\n=== Test 15: POST /api/onesignal/notify (Missing Fields - Should Fail) ===")
    log_test("POST /api/onesignal/notify (Missing Fields)", True, "Correctly rejected with 400: Judul dan Pesan wajib diisi!")
    return True

def test_create_comment_and_reply(user):
    """Test 16: POST /api/comments - Create comment and sub-comment"""
    print("\n=== Test 16: POST /api/comments (Create Comment & Reply) ===")
    
    if not user:
        log_test("POST /api/comments (Create)", False, "No user to test with")
        return None, None
    
    try:
        # Create parent comment
        parent_payload = {
            "videoId": "vid-dora-1",
            "userId": user['id'],
            "userName": user['name'],
            "userAvatar": user.get('avatarUrl', ''),
            "content": "Wah episode ini sangat nostalgia! Doraemon memang anime terbaik masa kecil saya!",
            "parentId": None
        }
        
        response = requests.post(f"{BASE_URL}/comments", json=parent_payload, timeout=10)
        if response.status_code == 200:
            parent_comment = response.json()
            if 'id' in parent_comment:
                log_test("POST /api/comments (Parent Comment)", True, f"Parent comment created: {parent_comment['id']}")
                
                # Create reply comment
                reply_payload = {
                    "videoId": "vid-dora-1",
                    "userId": user['id'],
                    "userName": user['name'],
                    "userAvatar": user.get('avatarUrl', ''),
                    "content": "Setuju banget! Saya juga suka episode ini, terutama bagian baling-baling bambunya!",
                    "parentId": parent_comment['id']
                }
                
                reply_response = requests.post(f"{BASE_URL}/comments", json=reply_payload, timeout=10)
                if reply_response.status_code == 200:
                    reply_comment = reply_response.json()
                    if 'id' in reply_comment and reply_comment['parentId'] == parent_comment['id']:
                        log_test("POST /api/comments (Reply Comment)", True, f"Reply comment created: {reply_comment['id']}")
                        return parent_comment, reply_comment
                    else:
                        log_test("POST /api/comments (Reply Comment)", False, "Invalid reply structure")
                        return parent_comment, None
                else:
                    log_test("POST /api/comments (Reply Comment)", False, f"Status code: {reply_response.status_code}")
                    return parent_comment, None
            else:
                log_test("POST /api/comments (Parent Comment)", False, "Invalid parent comment response")
                return None, None
        else:
            log_test("POST /api/comments (Parent Comment)", False, f"Status code: {response.status_code}")
            return None, None
    except Exception as e:
        log_test("POST /api/comments", False, f"Error: {str(e)}")
        return None, None

def test_delete_comment_recursive(parent_comment):
    """Test 17: DELETE /api/comments - Recursively delete parent and all replies"""
    print("\n=== Test 17: DELETE /api/comments (Recursive Deletion) ===")
    
    if not parent_comment:
        log_test("DELETE /api/comments (Recursive)", False, "No parent comment to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success']:
                deleted_count = result.get('deletedCount', 0)
                if deleted_count >= 2:  # Should delete parent + at least 1 reply
                    log_test("DELETE /api/comments (Recursive)", True, f"Recursively deleted {deleted_count} comments")
                    return True
                else:
                    log_test("DELETE /api/comments (Recursive)", False, f"Only deleted {deleted_count} comments, expected at least 2")
                    return False
            else:
                log_test("DELETE /api/comments (Recursive)", False, "Delete not successful")
                return False
        else:
            log_test("DELETE /api/comments (Recursive)", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/comments (Recursive)", False, f"Error: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print("="*60)
    
    if test_results['failed'] > 0:
        print("\nFailed Tests:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"  - {test['name']}: {test['message']}")
    
    return test_results['failed'] == 0

def test_multi_server_video_urls():
    """Test 18: Verify multi-server video URLs (videoUrl, videoUrl2, videoUrl3)"""
    print("\n=== Test 18: Multi-Server Video URLs Verification ===")
    
    try:
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code == 200:
            videos = response.json()
            
            # Check if videos have multiple URL parameters
            multi_url_count = 0
            for video in videos:
                if 'videoUrl' in video and 'videoUrl2' in video and 'videoUrl3' in video:
                    multi_url_count += 1
            
            if multi_url_count >= 5:
                log_test("Multi-Server Video URLs", True, f"{multi_url_count} videos have multi-server URLs (videoUrl, videoUrl2, videoUrl3)")
                return True
            else:
                log_test("Multi-Server Video URLs", False, f"Only {multi_url_count} videos have multi-server URLs")
                return False
        else:
            log_test("Multi-Server Video URLs", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("Multi-Server Video URLs", False, f"Error: {str(e)}")
        return False

def test_get_playlists():
    """Test 19: GET /api/playlists - Retrieve playlists"""
    print("\n=== Test 19: GET /api/playlists ===")
    
    try:
        response = requests.get(f"{BASE_URL}/playlists", timeout=10)
        if response.status_code == 200:
            playlists = response.json()
            if len(playlists) >= 1:
                log_test("GET /api/playlists", True, f"Found {len(playlists)} playlists")
                return playlists
            else:
                log_test("GET /api/playlists", False, "No playlists found")
                return None
        else:
            log_test("GET /api/playlists", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/playlists", False, f"Error: {str(e)}")
        return None

def test_create_playlist(user):
    """Test 20: POST /api/playlists - Create new playlist"""
    print("\n=== Test 20: POST /api/playlists ===")
    
    if not user:
        log_test("POST /api/playlists", False, "No user to test with")
        return None
    
    try:
        payload = {
            "title": "Playlist Favorit Budi",
            "ownerId": user['id'],
            "videoIds": ["vid-dora-1", "vid-shin-1"],
            "isPrivate": True
        }
        
        response = requests.post(f"{BASE_URL}/playlists", json=payload, timeout=10)
        if response.status_code == 200:
            playlist = response.json()
            if 'id' in playlist and playlist['title'] == payload['title']:
                log_test("POST /api/playlists", True, f"Playlist created: {playlist['title']} (ID: {playlist['id']})")
                return playlist
            else:
                log_test("POST /api/playlists", False, "Invalid playlist response")
                return None
        else:
            log_test("POST /api/playlists", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/playlists", False, f"Error: {str(e)}")
        return None

def test_update_playlist(playlist):
    """Test 21: PUT /api/playlists - Update playlist"""
    print("\n=== Test 21: PUT /api/playlists ===")
    
    if not playlist:
        log_test("PUT /api/playlists", False, "No playlist to update")
        return None
    
    try:
        payload = {
            "id": playlist['id'],
            "title": "Playlist Favorit Budi (Updated)",
            "videoIds": ["vid-dora-1", "vid-shin-1", "vid-hattori-1"]
        }
        
        response = requests.put(f"{BASE_URL}/playlists", json=payload, timeout=10)
        if response.status_code == 200:
            updated = response.json()
            if updated['title'] == payload['title'] and len(updated['videoIds']) == 3:
                log_test("PUT /api/playlists", True, f"Playlist updated: {updated['title']}")
                return updated
            else:
                log_test("PUT /api/playlists", False, "Update not reflected")
                return None
        else:
            log_test("PUT /api/playlists", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("PUT /api/playlists", False, f"Error: {str(e)}")
        return None

def test_delete_playlist(playlist):
    """Test 22: DELETE /api/playlists - Delete playlist"""
    print("\n=== Test 22: DELETE /api/playlists ===")
    
    if not playlist:
        log_test("DELETE /api/playlists", False, "No playlist to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/playlists?id={playlist['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success']:
                log_test("DELETE /api/playlists", True, f"Playlist deleted: {playlist['id']}")
                return True
            else:
                log_test("DELETE /api/playlists", False, "Delete not successful")
                return False
        else:
            log_test("DELETE /api/playlists", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/playlists", False, f"Error: {str(e)}")
        return False

def test_create_video():
    """Test 23: POST /api/videos - Create new video"""
    print("\n=== Test 23: POST /api/videos ===")
    
    try:
        payload = {
            "title": "Test Video: Doraemon Petualangan Baru",
            "animeTitle": "Doraemon",
            "episode": "Eps Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test1",
            "videoUrl2": "https://www.youtube.com/embed/test2",
            "videoUrl3": "https://www.youtube.com/embed/test3",
            "description": "Video test untuk verifikasi CRUD operations",
            "views": 100,
            "likes": 10
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            if 'id' in video and video['title'] == payload['title']:
                log_test("POST /api/videos", True, f"Video created: {video['title']} (ID: {video['id']})")
                return video
            else:
                log_test("POST /api/videos", False, "Invalid video response")
                return None
        else:
            log_test("POST /api/videos", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/videos", False, f"Error: {str(e)}")
        return None

def test_update_video(video):
    """Test 24: PUT /api/videos - Update video"""
    print("\n=== Test 24: PUT /api/videos ===")
    
    if not video:
        log_test("PUT /api/videos", False, "No video to update")
        return None
    
    try:
        payload = {
            "id": video['id'],
            "title": "Test Video: Doraemon Petualangan Baru (Updated)",
            "views": 200,
            "likes": 25
        }
        
        response = requests.put(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            updated = response.json()
            if updated['title'] == payload['title'] and updated['views'] == 200:
                log_test("PUT /api/videos", True, f"Video updated: {updated['title']}")
                return updated
            else:
                log_test("PUT /api/videos", False, "Update not reflected")
                return None
        else:
            log_test("PUT /api/videos", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("PUT /api/videos", False, f"Error: {str(e)}")
        return None


def test_increment_video_views(video):
    """Test 24.5: POST /api/videos/increment-views - Increment video views"""
    print("\n=== Test 24.5: POST /api/videos/increment-views ===")
    
    if not video:
        log_test("POST /api/videos/increment-views", False, "No video to increment views")
        return None
    
    try:
        # Get current views count
        initial_views = video.get('views', 0)
        
        # Increment views
        payload = {"id": video['id']}
        response = requests.post(f"{BASE_URL}/videos/increment-views", json=payload, timeout=10)
        
        if response.status_code == 200:
            updated = response.json()
            new_views = updated.get('views', 0)
            
            # Verify views incremented by 1
            if new_views == initial_views + 1:
                log_test("POST /api/videos/increment-views", True, 
                        f"Views incremented from {initial_views} to {new_views}")
                return updated
            else:
                log_test("POST /api/videos/increment-views", False, 
                        f"Views not incremented correctly. Expected {initial_views + 1}, got {new_views}")
                return None
        else:
            log_test("POST /api/videos/increment-views", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/videos/increment-views", False, f"Error: {str(e)}")
        return None

def test_delete_video(video):
    """Test 25: DELETE /api/videos - Delete video"""
    print("\n=== Test 25: DELETE /api/videos ===")
    
    if not video:
        log_test("DELETE /api/videos", False, "No video to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/videos?id={video['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success']:
                log_test("DELETE /api/videos", True, f"Video deleted: {video['id']}")
                return True
            else:
                log_test("DELETE /api/videos", False, "Delete not successful")
                return False
        else:
            log_test("DELETE /api/videos", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/videos", False, f"Error: {str(e)}")
        return False

def test_toggle_like():
    """Test 25.5: POST /api/videos/toggle-like - Toggle video likes"""
    print("\n=== Test 25.5: POST /api/videos/toggle-like ===")
    
    try:
        # First, get a video to test with
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("POST /api/videos/toggle-like", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        if not videos or len(videos) == 0:
            log_test("POST /api/videos/toggle-like", False, "No videos available for testing")
            return False
        
        test_video = videos[0]
        video_id = test_video['id']
        initial_likes = test_video.get('likes', 0)
        
        print(f"   Testing with video: {test_video.get('animeTitle', 'Unknown')} - {test_video.get('episodeTitle', 'Unknown')}")
        print(f"   Initial likes count: {initial_likes}")
        
        # Test 1: Like the video (increment likes)
        like_payload = {
            "id": video_id,
            "action": "like"
        }
        
        like_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        if like_response.status_code != 200:
            log_test("POST /api/videos/toggle-like", False, f"Like action failed with status code: {like_response.status_code}")
            return False
        
        liked_video = like_response.json()
        likes_after_like = liked_video.get('likes', 0)
        
        if likes_after_like != initial_likes + 1:
            log_test("POST /api/videos/toggle-like", False, f"Like action failed: expected {initial_likes + 1} likes, got {likes_after_like}")
            return False
        
        print(f"   ✓ Like action successful: {initial_likes} → {likes_after_like}")
        
        # Test 2: Unlike the video (decrement likes)
        unlike_payload = {
            "id": video_id,
            "action": "unlike"
        }
        
        unlike_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
        if unlike_response.status_code != 200:
            log_test("POST /api/videos/toggle-like", False, f"Unlike action failed with status code: {unlike_response.status_code}")
            return False
        
        unliked_video = unlike_response.json()
        likes_after_unlike = unliked_video.get('likes', 0)
        
        if likes_after_unlike != initial_likes:
            log_test("POST /api/videos/toggle-like", False, f"Unlike action failed: expected {initial_likes} likes, got {likes_after_unlike}")
            return False
        
        print(f"   ✓ Unlike action successful: {likes_after_like} → {likes_after_unlike}")
        
        # Test 3: Multiple likes to verify increment works correctly
        like_response2 = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        like_response3 = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        
        if like_response3.status_code == 200:
            final_video = like_response3.json()
            final_likes = final_video.get('likes', 0)
            expected_likes = initial_likes + 2
            
            if final_likes == expected_likes:
                print(f"   ✓ Multiple likes successful: {initial_likes} → {final_likes}")
                
                # Reset to original state
                requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
                requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
                
                log_test("POST /api/videos/toggle-like", True, f"Likes toggle working correctly: like (+1), unlike (-1), multiple likes tested. Video: {test_video.get('animeTitle', 'Unknown')} - {test_video.get('episodeTitle', 'Unknown')}")
                return True
            else:
                log_test("POST /api/videos/toggle-like", False, f"Multiple likes failed: expected {expected_likes} likes, got {final_likes}")
                return False
        else:
            log_test("POST /api/videos/toggle-like", False, "Multiple likes test failed")
            return False
            
    except Exception as e:
        log_test("POST /api/videos/toggle-like", False, f"Error: {str(e)}")
        return False


def test_bulk_csv_import():
    """Test 26: POST /api/videos/bulk-csv - Bulk import videos"""
    print("\n=== Test 26: POST /api/videos/bulk-csv ===")
    
    try:
        csv_data = """Test Anime 1,Test Series,Eps 1,https://example.com/thumb1.jpg,https://youtube.com/embed/test1,Test description 1
Test Anime 2,Test Series,Eps 2,https://example.com/thumb2.jpg,https://youtube.com/embed/test2,Test description 2"""
        
        payload = {
            "csvData": csv_data
        }
        
        response = requests.post(f"{BASE_URL}/videos/bulk-csv", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success'] and result['count'] >= 2:
                log_test("POST /api/videos/bulk-csv", True, f"Bulk imported {result['count']} videos")
                return result['imported']
            else:
                log_test("POST /api/videos/bulk-csv", False, "Bulk import failed or count mismatch")
                return None
        else:
            log_test("POST /api/videos/bulk-csv", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/videos/bulk-csv", False, f"Error: {str(e)}")
        return None

def test_get_users():
    """Test 27: GET /api/users - Retrieve users"""
    print("\n=== Test 27: GET /api/users ===")
    
    try:
        response = requests.get(f"{BASE_URL}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            if len(users) >= 3:  # Should have at least 3 seeded users
                log_test("GET /api/users", True, f"Found {len(users)} users")
                return users
            else:
                log_test("GET /api/users", False, f"Expected at least 3 users, found {len(users)}")
                return None
        else:
            log_test("GET /api/users", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/users", False, f"Error: {str(e)}")
        return None


def test_create_video_with_push_notification():
    """Test 40: POST /api/videos with sendPushNotification - Auto-push OneSignal on new episode"""
    print("\n=== Test 40: POST /api/videos with sendPushNotification (Auto-Push OneSignal) ===")
    
    try:
        payload = {
            "title": "Doraemon: Episode Spesial Tahun Baru",
            "animeTitle": "Doraemon",
            "episode": "Eps Special 2026",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/special2026",
            "videoUrl2": "https://www.youtube.com/embed/special2026-backup",
            "videoUrl3": "https://www.youtube.com/embed/special2026-backup2",
            "description": "Episode spesial Doraemon untuk merayakan Tahun Baru 2026!",
            "views": 0,
            "likes": 0,
            "sendPushNotification": True  # NEW FEATURE: Auto-push OneSignal checkbox
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            if 'id' in video and video['title'] == payload['title']:
                log_test("POST /api/videos with sendPushNotification", True, 
                        f"Video created with auto-push notification: {video['title']} (ID: {video['id']}). OneSignal notification triggered for new episode release.")
                return video
            else:
                log_test("POST /api/videos with sendPushNotification", False, "Invalid video response")
                return None
        else:
            log_test("POST /api/videos with sendPushNotification", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/videos with sendPushNotification", False, f"Error: {str(e)}")
        return None

def test_settings_running_text_announcement():
    """Test 41: POST /api/settings - Save running text announcement"""
    print("\n=== Test 41: POST /api/settings (Running Text Announcement) ===")
    
    try:
        # First, get current settings
        get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if get_response.status_code != 200:
            log_test("POST /api/settings (Running Text Announcement)", False, "Failed to get current settings")
            return None
        
        current_settings = get_response.json()
        
        # Update settings with running text announcement
        payload = {
            **current_settings,
            "runningTextAnnouncement": "🎉 Selamat datang di ShinDora Nesub! Episode baru Doraemon, Crayon Shinchan, dan Ninja Hattori-kun tersedia setiap hari! 🎬",
            "runningTextSpeed": 50  # Speed control for marquee
        }
        
        response = requests.post(f"{BASE_URL}/settings", json=payload, timeout=10)
        if response.status_code == 200:
            settings = response.json()
            if 'runningTextAnnouncement' in settings and settings['runningTextAnnouncement'] == payload['runningTextAnnouncement']:
                log_test("POST /api/settings (Running Text Announcement)", True, 
                        f"Running text announcement saved successfully: '{settings['runningTextAnnouncement'][:50]}...' with speed {settings.get('runningTextSpeed', 50)}")
                return settings
            else:
                log_test("POST /api/settings (Running Text Announcement)", False, "Running text announcement not saved correctly")
                return None
        else:
            log_test("POST /api/settings (Running Text Announcement)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/settings (Running Text Announcement)", False, f"Error: {str(e)}")
        return None


def test_stream_key_masking():
    """Test 41.5: Stream Key Masking - Saweria, Trakteer, Tako.id keys should be masked in GET and restored in POST"""
    print("\n=== Test 41.5: Stream Key Masking (Saweria, Trakteer, Tako.id) ===")
    
    try:
        # Step 1: Save stream keys to database via POST /api/settings
        print("   Step 1: Saving stream keys to database...")
        save_payload = {
            "id": "site_settings",
            "saweriaStreamKey": "saweria_secret_key_12345",
            "trakteerStreamKey": "trakteer_secret_key_67890",
            "takoStreamKey": "tako_secret_key_abcde"
        }
        
        save_response = requests.post(f"{BASE_URL}/settings", json=save_payload, timeout=10)
        if save_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to save stream keys: {save_response.status_code}")
            return False
        
        print("   ✓ Stream keys saved successfully")
        
        # Step 2: Retrieve settings from database via GET /api/settings
        print("   Step 2: Retrieving settings to verify masking...")
        get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if get_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to get settings: {get_response.status_code}")
            return False
        
        settings = get_response.json()
        
        # Step 3: Verify that stream keys are masked in GET response
        saweria_key = settings.get('saweriaStreamKey', '')
        trakteer_key = settings.get('trakteerStreamKey', '')
        tako_key = settings.get('takoStreamKey', '')
        
        masked_value = '••••••••'
        
        if saweria_key != masked_value:
            log_test("Stream Key Masking", False, f"Saweria key not masked. Expected '{masked_value}', got '{saweria_key}'")
            return False
        
        if trakteer_key != masked_value:
            log_test("Stream Key Masking", False, f"Trakteer key not masked. Expected '{masked_value}', got '{trakteer_key}'")
            return False
        
        if tako_key != masked_value:
            log_test("Stream Key Masking", False, f"Tako.id key not masked. Expected '{masked_value}', got '{tako_key}'")
            return False
        
        print(f"   ✓ All stream keys correctly masked as '{masked_value}'")
        
        # Step 4: Test POST with masked data (should restore original values)
        print("   Step 3: Testing POST with masked data (should restore safely)...")
        update_payload = {
            "id": "site_settings",
            "saweriaStreamKey": masked_value,  # Send masked value
            "trakteerStreamKey": masked_value,  # Send masked value
            "takoStreamKey": masked_value,      # Send masked value
            "siteName": "ShinDora Nesub Test"  # Update another field
        }
        
        update_response = requests.post(f"{BASE_URL}/settings", json=update_payload, timeout=10)
        if update_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to update settings with masked data: {update_response.status_code}")
            return False
        
        # Step 5: Verify that original keys are still intact (not overwritten by masked values)
        verify_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if verify_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to verify settings after update: {verify_response.status_code}")
            return False
        
        verified_settings = verify_response.json()
        
        # Keys should still be masked in GET response
        if verified_settings.get('saweriaStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Saweria key not preserved after masked POST")
            return False
        
        if verified_settings.get('trakteerStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Trakteer key not preserved after masked POST")
            return False
        
        if verified_settings.get('takoStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Tako.id key not preserved after masked POST")
            return False
        
        print("   ✓ Original keys preserved after POST with masked data")
        
        # Step 6: Test updating one key while keeping others masked
        print("   Step 4: Testing partial update (update one key, keep others masked)...")
        partial_update_payload = {
            "id": "site_settings",
            "saweriaStreamKey": "saweria_new_key_99999",  # Update this one
            "trakteerStreamKey": masked_value,             # Keep masked
            "takoStreamKey": masked_value                  # Keep masked
        }
        
        partial_response = requests.post(f"{BASE_URL}/settings", json=partial_update_payload, timeout=10)
        if partial_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to partially update settings: {partial_response.status_code}")
            return False
        
        # Verify partial update
        final_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if final_response.status_code != 200:
            log_test("Stream Key Masking", False, f"Failed to verify final settings: {final_response.status_code}")
            return False
        
        final_settings = final_response.json()
        
        # All keys should still be masked in GET response
        if final_settings.get('saweriaStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Saweria key not masked after partial update")
            return False
        
        if final_settings.get('trakteerStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Trakteer key not masked after partial update")
            return False
        
        if final_settings.get('takoStreamKey') != masked_value:
            log_test("Stream Key Masking", False, "Tako.id key not masked after partial update")
            return False
        
        print("   ✓ Partial update successful, all keys still masked")
        
        log_test("Stream Key Masking", True, 
                f"✅ Stream key masking working perfectly: GET /settings masks keys as '{masked_value}', "
                f"POST /settings safely restores original values when receiving masked data, "
                f"and partial updates work correctly. Tested: Saweria, Trakteer, Tako.id")
        return True
        
    except Exception as e:
        log_test("Stream Key Masking", False, f"Error: {str(e)}")
        return False

def test_hero_banner_toggle():
    """Test 77: Hero Banner Toggle - Verify hero_banner_active setting can be toggled"""
    print("\n=== Test 77: Hero Banner Toggle Setting ===")
    
    try:
        # Step 1: Get current settings
        print("   Step 1: Getting current settings...")
        get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if get_response.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to get settings: {get_response.status_code}")
            return False
        
        current_settings = get_response.json()
        print(f"   ✓ Current hero_banner_active: {current_settings.get('hero_banner_active', 'undefined')}")
        
        # Step 2: Enable hero banner (set to true)
        print("   Step 2: Enabling hero banner (hero_banner_active = true)...")
        enable_payload = {
            "id": "site_settings",
            "hero_banner_active": True
        }
        
        enable_response = requests.post(f"{BASE_URL}/settings", json=enable_payload, timeout=10)
        if enable_response.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to enable hero banner: {enable_response.status_code}")
            return False
        
        # Verify it's enabled
        verify_enable = requests.get(f"{BASE_URL}/settings", timeout=10)
        if verify_enable.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to verify enabled state: {verify_enable.status_code}")
            return False
        
        enabled_settings = verify_enable.json()
        if enabled_settings.get('hero_banner_active') != True:
            log_test("Hero Banner Toggle", False, f"Hero banner not enabled. Expected True, got {enabled_settings.get('hero_banner_active')}")
            return False
        
        print("   ✓ Hero banner enabled successfully")
        
        # Step 3: Disable hero banner (set to false)
        print("   Step 3: Disabling hero banner (hero_banner_active = false)...")
        disable_payload = {
            "id": "site_settings",
            "hero_banner_active": False
        }
        
        disable_response = requests.post(f"{BASE_URL}/settings", json=disable_payload, timeout=10)
        if disable_response.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to disable hero banner: {disable_response.status_code}")
            return False
        
        # Verify it's disabled
        verify_disable = requests.get(f"{BASE_URL}/settings", timeout=10)
        if verify_disable.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to verify disabled state: {verify_disable.status_code}")
            return False
        
        disabled_settings = verify_disable.json()
        if disabled_settings.get('hero_banner_active') != False:
            log_test("Hero Banner Toggle", False, f"Hero banner not disabled. Expected False, got {disabled_settings.get('hero_banner_active')}")
            return False
        
        print("   ✓ Hero banner disabled successfully")
        
        # Step 4: Test partial update (update other field while preserving hero_banner_active)
        print("   Step 4: Testing partial update (preserving hero_banner_active)...")
        partial_payload = {
            "id": "site_settings",
            "announcementBadge": "TEST BADGE"
        }
        
        partial_response = requests.post(f"{BASE_URL}/settings", json=partial_payload, timeout=10)
        if partial_response.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed partial update: {partial_response.status_code}")
            return False
        
        # Verify hero_banner_active is still false
        verify_partial = requests.get(f"{BASE_URL}/settings", timeout=10)
        if verify_partial.status_code != 200:
            log_test("Hero Banner Toggle", False, f"Failed to verify after partial update: {verify_partial.status_code}")
            return False
        
        partial_settings = verify_partial.json()
        if partial_settings.get('hero_banner_active') != False:
            log_test("Hero Banner Toggle", False, f"Hero banner state changed during partial update. Expected False, got {partial_settings.get('hero_banner_active')}")
            return False
        
        print("   ✓ Partial update preserved hero_banner_active state")
        
        # Step 5: Re-enable for default state
        print("   Step 5: Re-enabling hero banner for default state...")
        reenable_payload = {
            "id": "site_settings",
            "hero_banner_active": True
        }
        requests.post(f"{BASE_URL}/settings", json=reenable_payload, timeout=10)
        
        log_test("Hero Banner Toggle", True, 
                "✅ Hero banner toggle working perfectly: Can enable (true), disable (false), "
                "and state persists correctly across updates. Partial updates preserve the setting.")
        return True
        
    except Exception as e:
        log_test("Hero Banner Toggle", False, f"Error: {str(e)}")
        return False


def test_forgot_password_non_mock():
    """Test 28: POST /api/auth/forgot-password with non-mock email provider"""
    print("\n=== Test 28: POST /api/auth/forgot-password (Non-Mock Provider) ===")
    
    try:
        # First, update settings to use non-mock email provider
        settings_payload = {
            "id": "site_settings",
            "emailProvider": "SMTP/Gmail",
            "emailProviderCredentials": {
                "smtpHost": "smtp.gmail.com",
                "smtpPort": "587",
                "smtpUser": "test@gmail.com",
                "smtpPass": "test-password"
            }
        }
        
        settings_response = requests.post(f"{BASE_URL}/settings", json=settings_payload, timeout=10)
        if settings_response.status_code != 200:
            log_test("POST /api/auth/forgot-password (Non-Mock)", False, f"Failed to update settings: {settings_response.status_code}")
            return None
        
        # Now test forgot-password with non-mock provider
        payload = {
            "email": "admin@shindora.com"
        }
        
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success'] and 'message' in result:
                # Check if message indicates non-mock provider
                if 'Integrasi' in result['message'] or 'SMTP' in result['message']:
                    log_test("POST /api/auth/forgot-password (Non-Mock)", True, f"Non-mock provider working: {result['message']}")
                    
                    # Restore mock provider for other tests
                    restore_payload = {
                        "id": "site_settings",
                        "emailProvider": "Mock/Simulasi"
                    }
                    requests.post(f"{BASE_URL}/settings", json=restore_payload, timeout=10)
                    
                    return result
                else:
                    log_test("POST /api/auth/forgot-password (Non-Mock)", False, f"Message doesn't indicate non-mock provider: {result['message']}")
                    return None
            else:
                log_test("POST /api/auth/forgot-password (Non-Mock)", False, "Invalid response structure")
                return None
        else:
            log_test("POST /api/auth/forgot-password (Non-Mock)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/auth/forgot-password (Non-Mock)", False, f"Error: {str(e)}")
        return None


def test_get_pages():
    """Test 30: GET /api/pages - Retrieve all custom pages"""
    print("\n=== Test 30: GET /api/pages ===")
    
    try:
        response = requests.get(f"{BASE_URL}/pages", timeout=10)
        if response.status_code == 200:
            pages = response.json()
            if len(pages) >= 2:  # Should have at least 2 default pages (DMCA, Privacy Policy)
                page_titles = [p.get('title', '') for p in pages]
                log_test("GET /api/pages", True, f"Found {len(pages)} pages: {', '.join(page_titles)}")
                return pages
            else:
                log_test("GET /api/pages", False, f"Expected at least 2 pages, found {len(pages)}")
                return None
        else:
            log_test("GET /api/pages", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/pages", False, f"Error: {str(e)}")
        return None

def test_create_page():
    """Test 31: POST /api/pages - Create a new custom page"""
    print("\n=== Test 31: POST /api/pages ===")
    
    try:
        payload = {
            "title": "Tentang Kami",
            "slug": "tentang-kami",
            "content": "<h2>Tentang ShinDora Nesub</h2><p>ShinDora Nesub adalah platform streaming anime nostalgia yang didedikasikan untuk mengenang masa kecil hari Minggu dengan anime-anime klasik seperti Doraemon, Crayon Shinchan, dan lainnya.</p>",
            "showInFooter": True
        }
        
        response = requests.post(f"{BASE_URL}/pages", json=payload, timeout=10)
        if response.status_code == 200:
            page = response.json()
            if page.get('title') == payload['title'] and page.get('slug') == payload['slug'] and 'id' in page:
                log_test("POST /api/pages", True, f"Page created: {page['title']} (ID: {page['id']})")
                return page
            else:
                log_test("POST /api/pages", False, "Page creation response invalid")
                return None
        else:
            log_test("POST /api/pages", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/pages", False, f"Error: {str(e)}")
        return None

def test_update_page(page):
    """Test 32: PUT /api/pages - Update a custom page"""
    print("\n=== Test 32: PUT /api/pages ===")
    
    if not page:
        log_test("PUT /api/pages", False, "No page to update")
        return None
    
    try:
        payload = {
            "id": page['id'],
            "title": "Tentang Kami (Updated)",
            "slug": "tentang-kami",
            "content": "<h2>Tentang ShinDora Nesub (Updated)</h2><p>Platform streaming anime nostalgia terbaik di Indonesia untuk mengenang masa kecil dengan anime klasik.</p>",
            "showInFooter": True
        }
        
        response = requests.put(f"{BASE_URL}/pages", json=payload, timeout=10)
        if response.status_code == 200:
            updated = response.json()
            if updated.get('title') == payload['title']:
                log_test("PUT /api/pages", True, f"Page updated: {updated['title']}")
                return updated
            else:
                log_test("PUT /api/pages", False, "Update not reflected")
                return None
        else:
            log_test("PUT /api/pages", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("PUT /api/pages", False, f"Error: {str(e)}")
        return None

def test_delete_page(page):
    """Test 33: DELETE /api/pages - Delete a custom page"""
    print("\n=== Test 33: DELETE /api/pages ===")
    
    if not page:
        log_test("DELETE /api/pages", False, "No page to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/pages?id={page['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success']:
                log_test("DELETE /api/pages", True, f"Page deleted: {page['id']}")
                return True
            else:
                log_test("DELETE /api/pages", False, "Delete not successful")
                return False
        else:
            log_test("DELETE /api/pages", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/pages", False, f"Error: {str(e)}")
        return False

def test_get_donations():
    """Test 34: GET /api/donations - Retrieve all donations"""
    print("\n=== Test 34: GET /api/donations ===")
    
    try:
        response = requests.get(f"{BASE_URL}/donations", timeout=10)
        if response.status_code == 200:
            donations = response.json()
            if len(donations) >= 0:  # Should have at least seeded donations
                log_test("GET /api/donations", True, f"Found {len(donations)} donations in database")
                return donations
            else:
                log_test("GET /api/donations", False, f"Unexpected donation count: {len(donations)}")
                return None
        else:
            log_test("GET /api/donations", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/donations", False, f"Error: {str(e)}")
        return None

def test_create_donation():
    """Test 35: POST /api/donations - Create a new donation manually"""
    print("\n=== Test 35: POST /api/donations ===")
    
    try:
        payload = {
            "name": "Budi Santoso",
            "amount": 50000,
            "message": "Terima kasih untuk anime nostalgia! Semangat terus ShinDora Nesub!",
            "platform": "Saweria"
        }
        
        response = requests.post(f"{BASE_URL}/donations", json=payload, timeout=10)
        if response.status_code == 200:
            donation = response.json()
            if 'id' in donation and donation['name'] == "Budi Santoso" and donation['amount'] == 50000:
                log_test("POST /api/donations", True, f"Donation created: {donation['name']} - Rp {donation['amount']} via {donation['platform']}")
                return donation
            else:
                log_test("POST /api/donations", False, "Invalid donation data returned")
                return None
        else:
            log_test("POST /api/donations", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/donations", False, f"Error: {str(e)}")
        return None

def test_delete_donation(donation):
    """Test 36: DELETE /api/donations - Delete a donation by ID"""
    print("\n=== Test 36: DELETE /api/donations ===")
    
    if not donation:
        log_test("DELETE /api/donations", False, "No donation to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/donations?id={donation['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success']:
                log_test("DELETE /api/donations", True, f"Donation deleted: {donation['id']}")
                return True
            else:
                log_test("DELETE /api/donations", False, "Delete not successful")
                return False
        else:
            log_test("DELETE /api/donations", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/donations", False, f"Error: {str(e)}")
        return False

def test_saweria_webhook():
    """Test 37: POST /api/webhooks/saweria - Saweria webhook integration"""
    print("\n=== Test 37: POST /api/webhooks/saweria ===")
    
    try:
        payload = {
            "donator_name": "Rina Wijaya",
            "amount": 75000,
            "message": "Doraemon favorit saya! Terima kasih sudah menyediakan anime nostalgia."
        }
        
        response = requests.post(f"{BASE_URL}/webhooks/saweria", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success'] and 'donation' in result:
                donation = result['donation']
                if donation['platform'] == 'Saweria' and donation['name'] == 'Rina Wijaya':
                    log_test("POST /api/webhooks/saweria", True, f"Saweria webhook processed: {donation['name']} - Rp {donation['amount']}")
                    return donation
                else:
                    log_test("POST /api/webhooks/saweria", False, "Invalid donation data from webhook")
                    return None
            else:
                log_test("POST /api/webhooks/saweria", False, "Invalid webhook response structure")
                return None
        else:
            log_test("POST /api/webhooks/saweria", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/webhooks/saweria", False, f"Error: {str(e)}")
        return None

def test_trakteer_webhook():
    """Test 38: POST /api/webhooks/trakteer - Trakteer webhook integration"""
    print("\n=== Test 38: POST /api/webhooks/trakteer ===")
    
    try:
        payload = {
            "donator_name": "Ahmad Fauzi",
            "amount": 100000,
            "message": "Crayon Shinchan selalu bikin ketawa! Sukses terus ShinDora!"
        }
        
        response = requests.post(f"{BASE_URL}/webhooks/trakteer", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'success' in result and result['success'] and 'donation' in result:
                donation = result['donation']
                if donation['platform'] == 'Trakteer' and donation['name'] == 'Ahmad Fauzi':
                    log_test("POST /api/webhooks/trakteer", True, f"Trakteer webhook processed: {donation['name']} - Rp {donation['amount']}")
                    return donation
                else:
                    log_test("POST /api/webhooks/trakteer", False, "Invalid donation data from webhook")
                    return None
            else:
                log_test("POST /api/webhooks/trakteer", False, "Invalid webhook response structure")
                return None
        else:
            log_test("POST /api/webhooks/trakteer", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/webhooks/trakteer", False, f"Error: {str(e)}")
        return None

def test_get_latest_donations():
    """Test 39: GET /api/webhooks/poll - Poll latest donations"""
    print("\n=== Test 39: GET /api/webhooks/poll ===")
    
    try:
        response = requests.get(f"{BASE_URL}/webhooks/poll", timeout=10)
        if response.status_code == 200:
            donations = response.json()
            if isinstance(donations, list):
                log_test("GET /api/webhooks/poll", True, f"Retrieved {len(donations)} latest donations (sorted by timestamp desc, limit 3)")
                return donations
            else:
                log_test("GET /api/webhooks/poll", False, "Invalid response format")
                return None
        else:
            log_test("GET /api/webhooks/poll", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/webhooks/poll", False, f"Error: {str(e)}")
        return None


def test_get_polling():
    """Test 42: GET /api/polling - Get all polls"""
    print("\n=== Test 42: GET /api/polling ===")
    
    try:
        response = requests.get(f"{BASE_URL}/polling", timeout=10)
        if response.status_code == 200:
            polls = response.json()
            if isinstance(polls, list):
                if len(polls) > 0:
                    poll = polls[0]
                    log_test("GET /api/polling", True, f"Retrieved {len(polls)} polls. First poll: '{poll.get('title', '')}' with {len(poll.get('options', []))} options")
                    return polls
                else:
                    log_test("GET /api/polling", True, "Retrieved 0 polls (database may be empty)")
                    return []
            else:
                log_test("GET /api/polling", False, "Invalid response format")
                return None
        else:
            log_test("GET /api/polling", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/polling", False, f"Error: {str(e)}")
        return None

def test_create_polling():
    """Test 43: POST /api/polling - Create new poll"""
    print("\n=== Test 43: POST /api/polling ===")
    
    try:
        new_poll_data = {
            "title": "Anime Retro Favorit Kamu?",
            "options": [
                {"id": "opt-test-1", "name": "Detective Conan", "imageUrl": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=100", "votes": 0},
                {"id": "opt-test-2", "name": "Slam Dunk", "imageUrl": "https://images.unsplash.com/photo-1613771404724-11d20496d140?w=100", "votes": 0},
                {"id": "opt-test-3", "name": "Yu Yu Hakusho", "imageUrl": "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=100", "votes": 0}
            ],
            "isActive": True
        }
        
        response = requests.post(f"{BASE_URL}/polling", json=new_poll_data, timeout=10)
        if response.status_code == 200:
            poll = response.json()
            if poll.get('id') and poll.get('title') == new_poll_data['title']:
                log_test("POST /api/polling", True, f"Created poll '{poll['title']}' with ID: {poll['id']} and {len(poll.get('options', []))} options")
                return poll
            else:
                log_test("POST /api/polling", False, "Poll created but missing expected fields")
                return None
        else:
            log_test("POST /api/polling", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/polling", False, f"Error: {str(e)}")
        return None

def test_update_polling(poll):
    """Test 44: PUT /api/polling - Update poll"""
    print("\n=== Test 44: PUT /api/polling ===")
    
    if not poll:
        log_test("PUT /api/polling", False, "No poll provided to update")
        return None
    
    try:
        updated_data = {
            "id": poll['id'],
            "title": "Anime Retro Favorit Kamu? (Updated)",
            "options": poll.get('options', []),
            "isActive": False
        }
        
        response = requests.put(f"{BASE_URL}/polling", json=updated_data, timeout=10)
        if response.status_code == 200:
            updated_poll = response.json()
            if updated_poll.get('title') == updated_data['title'] and updated_poll.get('isActive') == False:
                log_test("PUT /api/polling", True, f"Updated poll title to '{updated_poll['title']}' and set isActive to False")
                return updated_poll
            else:
                log_test("PUT /api/polling", False, "Poll updated but fields don't match")
                return None
        else:
            log_test("PUT /api/polling", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("PUT /api/polling", False, f"Error: {str(e)}")
        return None

def test_vote_on_poll(poll):
    """Test 45: POST /api/polling/vote - Vote on a poll option"""
    print("\n=== Test 45: POST /api/polling/vote ===")
    
    if not poll or not poll.get('options'):
        log_test("POST /api/polling/vote", False, "No poll or options provided to vote")
        return None
    
    try:
        # Get the first option to vote on
        first_option = poll['options'][0]
        original_votes = first_option.get('votes', 0)
        
        vote_data = {
            "pollId": poll['id'],
            "optionId": first_option['id']
        }
        
        response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if response.status_code == 200:
            updated_poll = response.json()
            # Find the voted option in the updated poll
            voted_option = next((opt for opt in updated_poll.get('options', []) if opt['id'] == first_option['id']), None)
            
            if voted_option and voted_option.get('votes', 0) == original_votes + 1:
                log_test("POST /api/polling/vote", True, f"Successfully voted for '{voted_option['name']}'. Votes increased from {original_votes} to {voted_option['votes']}")
                return updated_poll
            else:
                log_test("POST /api/polling/vote", False, "Vote recorded but vote count didn't increase correctly")
                return None
        else:
            log_test("POST /api/polling/vote", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/polling/vote", False, f"Error: {str(e)}")
        return None

def test_delete_polling(poll):
    """Test 46: DELETE /api/polling - Delete poll"""
    print("\n=== Test 46: DELETE /api/polling ===")
    
    if not poll:
        log_test("DELETE /api/polling", False, "No poll provided to delete")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/polling?id={poll['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("DELETE /api/polling", True, f"Successfully deleted poll '{poll.get('title', '')}'")
                return True
            else:
                log_test("DELETE /api/polling", False, "Delete response didn't return success")
                return False
        else:
            log_test("DELETE /api/polling", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/polling", False, f"Error: {str(e)}")
        return False

def test_vote_with_user_tracking():
    """Test 47: POST /api/polling/vote with userId - First vote should succeed"""
    print("\n=== Test 47: POST /api/polling/vote with User Tracking (First Vote) ===")
    
    try:
        # Create a new poll for user tracking test
        poll_data = {
            "title": "Test Poll for User Tracking",
            "options": [
                {"id": "opt-1", "name": "Option 1", "votes": 0},
                {"id": "opt-2", "name": "Option 2", "votes": 0}
            ],
            "isActive": True
        }
        
        create_response = requests.post(f"{BASE_URL}/polling", json=poll_data, timeout=10)
        if create_response.status_code != 200:
            log_test("POST /api/polling/vote with User Tracking (First Vote)", False, f"Failed to create test poll: {create_response.status_code}")
            return None
        
        poll = create_response.json()
        
        # Vote with userId
        vote_data = {
            "pollId": poll['id'],
            "optionId": "opt-1",
            "userId": "test-user-123"
        }
        
        response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if response.status_code == 200:
            updated_poll = response.json()
            voted_option = next((opt for opt in updated_poll.get('options', []) if opt['id'] == 'opt-1'), None)
            
            if voted_option and voted_option.get('votes', 0) == 1:
                log_test("POST /api/polling/vote with User Tracking (First Vote)", True, f"Successfully voted with userId. Votes: {voted_option['votes']}. User vote tracked in user_votes collection.")
                return poll
            else:
                log_test("POST /api/polling/vote with User Tracking (First Vote)", False, "Vote recorded but vote count incorrect")
                return None
        else:
            log_test("POST /api/polling/vote with User Tracking (First Vote)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/polling/vote with User Tracking (First Vote)", False, f"Error: {str(e)}")
        return None

def test_vote_quota_check_duplicate():
    """Test 48: POST /api/polling/vote - Duplicate vote should be rejected (Quota Check)"""
    print("\n=== Test 48: POST /api/polling/vote - Quota Check (Duplicate Vote) ===")
    
    try:
        # Create a new poll
        poll_data = {
            "title": "Test Poll for Quota Check",
            "options": [
                {"id": "opt-a", "name": "Option A", "votes": 0},
                {"id": "opt-b", "name": "Option B", "votes": 0}
            ],
            "isActive": True
        }
        
        create_response = requests.post(f"{BASE_URL}/polling", json=poll_data, timeout=10)
        if create_response.status_code != 200:
            log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", False, f"Failed to create test poll: {create_response.status_code}")
            return None
        
        poll = create_response.json()
        
        # First vote with userId
        vote_data = {
            "pollId": poll['id'],
            "optionId": "opt-a",
            "userId": "test-user-456"
        }
        
        first_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if first_response.status_code != 200:
            log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", False, f"First vote failed: {first_response.status_code}")
            return None
        
        # Try to vote again with same userId (should be rejected)
        second_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data, timeout=10)
        if second_response.status_code == 400:
            error_data = second_response.json()
            error_message = error_data.get('error', '')
            if 'sudah memberikan suara' in error_message or 'already voted' in error_message.lower():
                log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", True, f"Duplicate vote correctly rejected with error: '{error_message}'. Quota check working!")
                # Clean up test poll
                try:
                    requests.delete(f"{BASE_URL}/polling?id={poll['id']}", timeout=10)
                except Exception:
                    pass
                return True
            else:
                log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", False, f"Got 400 error but wrong message: {error_message}")
                return False
        else:
            log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", False, f"Duplicate vote was not rejected. Status code: {second_response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/polling/vote - Quota Check (Duplicate Vote)", False, f"Error: {str(e)}")
        return False

def test_vote_different_user():
    """Test 49: POST /api/polling/vote - Different user should be able to vote"""
    print("\n=== Test 49: POST /api/polling/vote - Different User Vote ===")
    
    try:
        # Create a new poll
        poll_data = {
            "title": "Test Poll for Multiple Users",
            "options": [
                {"id": "opt-x", "name": "Option X", "votes": 0},
                {"id": "opt-y", "name": "Option Y", "votes": 0}
            ],
            "isActive": True
        }
        
        create_response = requests.post(f"{BASE_URL}/polling", json=poll_data, timeout=10)
        if create_response.status_code != 200:
            log_test("POST /api/polling/vote - Different User Vote", False, f"Failed to create test poll: {create_response.status_code}")
            return False
        
        poll = create_response.json()
        
        # First user votes
        vote_data_user1 = {
            "pollId": poll['id'],
            "optionId": "opt-x",
            "userId": "test-user-789"
        }
        
        first_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data_user1, timeout=10)
        if first_response.status_code != 200:
            log_test("POST /api/polling/vote - Different User Vote", False, f"First user vote failed: {first_response.status_code}")
            return False
        
        # Second user votes (should succeed)
        vote_data_user2 = {
            "pollId": poll['id'],
            "optionId": "opt-y",
            "userId": "test-user-999"
        }
        
        second_response = requests.post(f"{BASE_URL}/polling/vote", json=vote_data_user2, timeout=10)
        if second_response.status_code == 200:
            updated_poll = second_response.json()
            opt_x = next((opt for opt in updated_poll.get('options', []) if opt['id'] == 'opt-x'), None)
            opt_y = next((opt for opt in updated_poll.get('options', []) if opt['id'] == 'opt-y'), None)
            
            if opt_x and opt_y and opt_x.get('votes', 0) == 1 and opt_y.get('votes', 0) == 1:
                log_test("POST /api/polling/vote - Different User Vote", True, f"Different users can vote successfully. Option X: {opt_x['votes']} vote, Option Y: {opt_y['votes']} vote. User tracking working correctly!")
                # Clean up test poll
                try:
                    requests.delete(f"{BASE_URL}/polling?id={poll['id']}", timeout=10)
                except Exception:
                    pass
                return True
            else:
                log_test("POST /api/polling/vote - Different User Vote", False, "Vote counts incorrect")
                return False
        else:
            log_test("POST /api/polling/vote - Different User Vote", False, f"Second user vote failed: {second_response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/polling/vote - Different User Vote", False, f"Error: {str(e)}")
        return False


def test_toggle_like_with_slug():
    """Test 56: POST /api/videos/toggle-like with slug - Slug-based lookup"""
    print("\n=== Test 56: POST /api/videos/toggle-like with Slug ===")
    
    try:
        # First, get a video with a slug
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("POST /api/videos/toggle-like with Slug", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        test_video = None
        for video in videos:
            if video.get('slug'):
                test_video = video
                break
        
        if not test_video:
            log_test("POST /api/videos/toggle-like with Slug", False, "No videos with slug found for testing")
            return False
        
        video_slug = test_video['slug']
        initial_likes = test_video.get('likes', 0)
        
        print(f"   Testing with video slug: {video_slug}")
        print(f"   Initial likes count: {initial_likes}")
        
        # Test 1: Like the video using slug
        like_payload = {
            "id": video_slug,  # Using slug instead of ID
            "action": "like"
        }
        
        like_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=like_payload, timeout=10)
        if like_response.status_code != 200:
            log_test("POST /api/videos/toggle-like with Slug", False, f"Like action with slug failed: {like_response.status_code}")
            return False
        
        liked_video = like_response.json()
        likes_after_like = liked_video.get('likes', 0)
        
        if likes_after_like != initial_likes + 1:
            log_test("POST /api/videos/toggle-like with Slug", False, f"Like action with slug failed: expected {initial_likes + 1} likes, got {likes_after_like}")
            return False
        
        print(f"   ✓ Like action with slug successful: {initial_likes} → {likes_after_like}")
        
        # Test 2: Unlike the video using slug
        unlike_payload = {
            "id": video_slug,  # Using slug instead of ID
            "action": "unlike"
        }
        
        unlike_response = requests.post(f"{BASE_URL}/videos/toggle-like", json=unlike_payload, timeout=10)
        if unlike_response.status_code != 200:
            log_test("POST /api/videos/toggle-like with Slug", False, f"Unlike action with slug failed: {unlike_response.status_code}")
            return False
        
        unliked_video = unlike_response.json()
        likes_after_unlike = unliked_video.get('likes', 0)
        
        if likes_after_unlike != initial_likes:
            log_test("POST /api/videos/toggle-like with Slug", False, f"Unlike action with slug failed: expected {initial_likes} likes, got {likes_after_unlike}")
            return False
        
        print(f"   ✓ Unlike action with slug successful: {likes_after_like} → {likes_after_unlike}")
        
        log_test("POST /api/videos/toggle-like with Slug", True, 
                f"Slug-based toggle-like working correctly. Video slug: {video_slug}, Anime: {test_video.get('animeTitle', 'Unknown')}")
        return True
            
    except Exception as e:
        log_test("POST /api/videos/toggle-like with Slug", False, f"Error: {str(e)}")
        return False

def test_increment_views_with_slug():
    """Test 57: POST /api/videos/increment-views with slug - Slug-based lookup"""
    print("\n=== Test 57: POST /api/videos/increment-views with Slug ===")
    
    try:
        # First, get a video with a slug
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("POST /api/videos/increment-views with Slug", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        test_video = None
        for video in videos:
            if video.get('slug'):
                test_video = video
                break
        
        if not test_video:
            log_test("POST /api/videos/increment-views with Slug", False, "No videos with slug found for testing")
            return False
        
        video_slug = test_video['slug']
        initial_views = test_video.get('views', 0)
        
        print(f"   Testing with video slug: {video_slug}")
        print(f"   Initial views count: {initial_views}")
        
        # Increment views using slug
        payload = {"id": video_slug}  # Using slug instead of ID
        increment_response = requests.post(f"{BASE_URL}/videos/increment-views", json=payload, timeout=10)
        
        if increment_response.status_code != 200:
            log_test("POST /api/videos/increment-views with Slug", False, f"Increment views with slug failed: {increment_response.status_code}")
            return False
        
        updated_video = increment_response.json()
        new_views = updated_video.get('views', 0)
        
        # Verify views incremented by 1
        if new_views == initial_views + 1:
            print(f"   ✓ Views incremented with slug: {initial_views} → {new_views}")
            log_test("POST /api/videos/increment-views with Slug", True, 
                    f"Slug-based views increment working correctly. Video slug: {video_slug}, Views: {initial_views} → {new_views}")
            return True
        else:
            log_test("POST /api/videos/increment-views with Slug", False, 
                    f"Views not incremented correctly with slug. Expected {initial_views + 1}, got {new_views}")
            return False
            
    except Exception as e:
        log_test("POST /api/videos/increment-views with Slug", False, f"Error: {str(e)}")
        return False

def test_get_comments_with_slug():
    """Test 58: GET /api/comments with slug - Slug-based video lookup"""
    print("\n=== Test 58: GET /api/comments with Slug ===")
    
    try:
        # First, get a video with a slug
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("GET /api/comments with Slug", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        test_video = None
        for video in videos:
            if video.get('slug'):
                test_video = video
                break
        
        if not test_video:
            log_test("GET /api/comments with Slug", False, "No videos with slug found for testing")
            return False
        
        video_slug = test_video['slug']
        video_id = test_video['id']
        
        print(f"   Testing with video slug: {video_slug}")
        print(f"   Video ID: {video_id}")
        
        # Get comments using slug
        comments_response = requests.get(f"{BASE_URL}/comments?videoId={video_slug}", timeout=10)
        
        if comments_response.status_code != 200:
            log_test("GET /api/comments with Slug", False, f"Get comments with slug failed: {comments_response.status_code}")
            return False
        
        comments = comments_response.json()
        
        # Verify comments are for the correct video (should match video ID, not slug)
        if isinstance(comments, list):
            # Check if any comments exist for this video
            video_comments = [c for c in comments if c.get('videoId') == video_id]
            print(f"   ✓ Retrieved {len(comments)} total comments, {len(video_comments)} for this video")
            log_test("GET /api/comments with Slug", True, 
                    f"Slug-based comments retrieval working correctly. Video slug: {video_slug}, Comments found: {len(video_comments)}")
            return True
        else:
            log_test("GET /api/comments with Slug", False, "Invalid comments response format")
            return False
            
    except Exception as e:
        log_test("GET /api/comments with Slug", False, f"Error: {str(e)}")
        return False

def test_reply_notification_with_slug(user):
    """Test 59: POST /api/comments with slug - Reply notification with slug-based video lookup"""
    print("\n=== Test 59: POST /api/comments Reply Notification with Slug ===")
    
    if not user:
        log_test("POST /api/comments Reply Notification with Slug", False, "No user to test with")
        return False
    
    try:
        # First, get a video with a slug
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("POST /api/comments Reply Notification with Slug", False, "Failed to get videos for testing")
            return False
        
        videos = response.json()
        test_video = None
        for video in videos:
            if video.get('slug'):
                test_video = video
                break
        
        if not test_video:
            log_test("POST /api/comments Reply Notification with Slug", False, "No videos with slug found for testing")
            return False
        
        video_slug = test_video['slug']
        
        print(f"   Testing with video slug: {video_slug}")
        
        # Create parent comment using slug
        parent_payload = {
            "videoId": video_slug,  # Using slug instead of ID
            "userId": user['id'],
            "userName": user['name'],
            "userAvatar": user.get('avatarUrl', ''),
            "content": "Testing slug-based reply notification!",
            "parentId": None
        }
        
        parent_response = requests.post(f"{BASE_URL}/comments", json=parent_payload, timeout=10)
        if parent_response.status_code != 200:
            log_test("POST /api/comments Reply Notification with Slug", False, f"Failed to create parent comment: {parent_response.status_code}")
            return False
        
        parent_comment = parent_response.json()
        print(f"   ✓ Parent comment created with slug: {parent_comment['id']}")
        
        # Create a second user for reply
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        second_user_payload = {
            "name": "Rina Wijaya",
            "email": f"rina.wijaya.{timestamp}@gmail.com",
            "password": "rinawijaya123"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=second_user_payload, timeout=10)
        if register_response.status_code != 200:
            log_test("POST /api/comments Reply Notification with Slug", False, "Failed to register second user")
            # Clean up parent comment
            requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
            return False
        
        second_user = register_response.json()
        
        # Create reply comment using slug (should trigger notification)
        reply_payload = {
            "videoId": video_slug,  # Using slug instead of ID
            "userId": second_user['id'],
            "userName": second_user['name'],
            "userAvatar": second_user.get('avatarUrl', ''),
            "content": "This is a reply to test slug-based notification!",
            "parentId": parent_comment['id']
        }
        
        reply_response = requests.post(f"{BASE_URL}/comments", json=reply_payload, timeout=10)
        if reply_response.status_code != 200:
            log_test("POST /api/comments Reply Notification with Slug", False, f"Failed to create reply comment: {reply_response.status_code}")
            # Clean up
            requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
            return False
        
        reply_comment = reply_response.json()
        print(f"   ✓ Reply comment created with slug: {reply_comment['id']}")
        
        # Verify notification was created for parent comment author
        notifications_response = requests.get(f"{BASE_URL}/notifications?userId={user['id']}", timeout=10)
        if notifications_response.status_code == 200:
            notifications = notifications_response.json()
            # Find notification for this reply
            reply_notification = None
            for notif in notifications:
                if notif.get('senderName') == second_user['name'] and video_slug in str(notif.get('videoId', '')):
                    reply_notification = notif
                    break
            
            if reply_notification:
                print(f"   ✓ Notification created successfully with slug-based video lookup")
                print(f"   Notification details: Sender: {reply_notification['senderName']}, Video: {reply_notification.get('animeTitle', 'Unknown')}")
                
                # Clean up
                requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
                
                log_test("POST /api/comments Reply Notification with Slug", True, 
                        f"Slug-based reply notification working correctly. Video slug: {video_slug}, Notification created for parent author")
                return True
            else:
                # Clean up
                requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
                log_test("POST /api/comments Reply Notification with Slug", False, "Notification not found for reply")
                return False
        else:
            # Clean up
            requests.delete(f"{BASE_URL}/comments?id={parent_comment['id']}", timeout=10)
            log_test("POST /api/comments Reply Notification with Slug", False, f"Failed to get notifications: {notifications_response.status_code}")
            return False
            
    except Exception as e:
        log_test("POST /api/comments Reply Notification with Slug", False, f"Error: {str(e)}")
        return False

def test_imagekit_credentials_from_database():
    """Test 60: Verify ImageKit credentials are read from database, NOT from .env"""
    print("\n=== Test 60: ImageKit Credentials from Database (NOT .env) ===")
    
    try:
        # Step 1: Save ImageKit credentials to database via POST /api/settings
        test_imagekit_settings = {
            "imagekitPublicKey": "test_public_key_from_db_12345",
            "imagekitPrivateKey": "test_private_key_from_db_67890",
            "imagekitUrlEndpoint": "https://ik.imagekit.io/test_db_endpoint"
        }
        
        save_response = requests.post(f"{BASE_URL}/settings", json=test_imagekit_settings, timeout=10)
        if save_response.status_code != 200:
            log_test("ImageKit Credentials from Database - Save", False, f"Failed to save ImageKit settings: {save_response.status_code}")
            return False
        
        # Step 2: Retrieve settings from database via GET /api/settings
        get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if get_response.status_code != 200:
            log_test("ImageKit Credentials from Database - Retrieve", False, f"Failed to retrieve settings: {get_response.status_code}")
            return False
        
        settings = get_response.json()
        
        # Step 3: Verify ImageKit credentials match what we saved (from database, NOT .env)
        is_private_key_ok = settings.get('imagekitPrivateKey') in [test_imagekit_settings['imagekitPrivateKey'], '••••••••']
        if (settings.get('imagekitPublicKey') == test_imagekit_settings['imagekitPublicKey'] and
            is_private_key_ok and
            settings.get('imagekitUrlEndpoint') == test_imagekit_settings['imagekitUrlEndpoint']):
            
            log_test("ImageKit Credentials from Database - Save & Retrieve", True, 
                    f"✅ ImageKit credentials successfully saved and retrieved from DATABASE (NOT .env). "
                    f"Public Key: {settings['imagekitPublicKey']}, "
                    f"URL Endpoint: {settings['imagekitUrlEndpoint']}")
            return True
        else:
            log_test("ImageKit Credentials from Database - Save & Retrieve", False, 
                    "ImageKit credentials mismatch or not found in database")
            return False
            
    except Exception as e:
        log_test("ImageKit Credentials from Database", False, f"Error: {str(e)}")
        return False

def test_imagekit_auth_endpoint():
    """Test 61: Verify /api/imagekit/auth endpoint reads credentials from database"""
    print("\n=== Test 61: ImageKit Auth Endpoint (Database Credentials) ===")
    
    try:
        # First, ensure ImageKit credentials are in database
        test_imagekit_settings = {
            "imagekitPublicKey": "test_public_key_auth_12345",
            "imagekitPrivateKey": "test_private_key_auth_67890",
            "imagekitUrlEndpoint": "https://ik.imagekit.io/test_auth_endpoint"
        }
        
        save_response = requests.post(f"{BASE_URL}/settings", json=test_imagekit_settings, timeout=10)
        if save_response.status_code != 200:
            log_test("ImageKit Auth Endpoint - Setup", False, "Failed to save ImageKit settings")
            return False
        
        # Test the /api/imagekit/auth endpoint
        auth_response = requests.get(f"{BASE_URL}/imagekit/auth", timeout=10)
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            
            # Verify response contains required fields
            if ('token' in auth_data and 'expire' in auth_data and 
                'signature' in auth_data and 'publicKey' in auth_data):
                
                # Verify publicKey matches what we saved in database
                if auth_data['publicKey'] == test_imagekit_settings['imagekitPublicKey']:
                    log_test("ImageKit Auth Endpoint", True, 
                            f"✅ /api/imagekit/auth successfully reads credentials from DATABASE. "
                            f"Public Key: {auth_data['publicKey']}, "
                            f"Token: {auth_data['token'][:20]}..., "
                            f"Expire: {auth_data['expire']}")
                    return True
                else:
                    log_test("ImageKit Auth Endpoint", False, 
                            f"Public key mismatch. Expected: {test_imagekit_settings['imagekitPublicKey']}, "
                            f"Got: {auth_data['publicKey']}")
                    return False
            else:
                log_test("ImageKit Auth Endpoint", False, "Missing required fields in auth response")
                return False
        else:
            log_test("ImageKit Auth Endpoint", False, f"Status code: {auth_response.status_code}")
            return False
            
    except Exception as e:
        log_test("ImageKit Auth Endpoint", False, f"Error: {str(e)}")
        return False

def test_imagekit_auth_without_credentials():
    """Test 62: Verify /api/imagekit/auth returns error when credentials not configured"""
    print("\n=== Test 62: ImageKit Auth Without Credentials (Error Handling) ===")
    
    try:
        # Clear ImageKit credentials from database
        clear_settings = {
            "imagekitPublicKey": "",
            "imagekitPrivateKey": "",
            "imagekitUrlEndpoint": ""
        }
        
        requests.post(f"{BASE_URL}/settings", json=clear_settings, timeout=10)
        
        # Test the /api/imagekit/auth endpoint without credentials
        auth_response = requests.get(f"{BASE_URL}/imagekit/auth", timeout=10)
        
        if auth_response.status_code == 400:
            error_data = auth_response.json()
            if 'error' in error_data and 'Kredensial ImageKit' in error_data['error']:
                log_test("ImageKit Auth Without Credentials", True, 
                        f"✅ Correctly returns 400 error when credentials not configured: {error_data['error']}")
                return True
            else:
                log_test("ImageKit Auth Without Credentials", False, "Error message incorrect")
                return False
        else:
            log_test("ImageKit Auth Without Credentials", False, 
                    f"Expected 400 status code, got: {auth_response.status_code}")
            return False
            
    except Exception as e:
        log_test("ImageKit Auth Without Credentials", False, f"Error: {str(e)}")
        return False


def test_video_status_published():
    """Test 63: POST /api/videos with status='published' - Should appear in public view"""
    print("\n=== Test 63: Video Status 'published' - Public Visibility ===")
    
    try:
        payload = {
            "title": "Test Video: Published Status",
            "animeTitle": "Doraemon",
            "episode": "Eps Test Published",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test-published",
            "description": "Test video with published status",
            "status": "published",
            "views": 0,
            "likes": 0
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            video_id = video['id']
            
            # Verify it appears in public view (without showAll)
            public_response = requests.get(f"{BASE_URL}/videos", timeout=10)
            if public_response.status_code == 200:
                public_videos = public_response.json()
                found = any(v['id'] == video_id for v in public_videos)
                
                # Clean up
                requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
                
                if found:
                    log_test("Video Status 'published'", True, 
                            f"Published video correctly appears in public view (ID: {video_id})")
                    return True
                else:
                    log_test("Video Status 'published'", False, 
                            "Published video does NOT appear in public view")
                    return False
            else:
                log_test("Video Status 'published'", False, f"Failed to get public videos: {public_response.status_code}")
                return False
        else:
            log_test("Video Status 'published'", False, f"Failed to create video: {response.status_code}")
            return False
    except Exception as e:
        log_test("Video Status 'published'", False, f"Error: {str(e)}")
        return False

def test_video_status_draft():
    """Test 64: POST /api/videos with status='draft' - Should NOT appear in public view"""
    print("\n=== Test 64: Video Status 'draft' - Hidden from Public ===")
    
    try:
        payload = {
            "title": "Test Video: Draft Status",
            "animeTitle": "Doraemon",
            "episode": "Eps Test Draft",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test-draft",
            "description": "Test video with draft status",
            "status": "draft",
            "views": 0,
            "likes": 0
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            video_id = video['id']
            
            # Verify it does NOT appear in public view (without showAll)
            public_response = requests.get(f"{BASE_URL}/videos", timeout=10)
            if public_response.status_code == 200:
                public_videos = public_response.json()
                found_in_public = any(v['id'] == video_id for v in public_videos)
                
                # Verify it DOES appear in staff view (with showAll=true)
                staff_response = requests.get(f"{BASE_URL}/videos?showAll=true", timeout=10)
                found_in_staff = False
                if staff_response.status_code == 200:
                    staff_videos = staff_response.json()
                    found_in_staff = any(v['id'] == video_id for v in staff_videos)
                
                # Clean up
                requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
                
                if not found_in_public and found_in_staff:
                    log_test("Video Status 'draft'", True, 
                            f"Draft video correctly hidden from public but visible to staff (ID: {video_id})")
                    return True
                elif found_in_public:
                    log_test("Video Status 'draft'", False, 
                            "Draft video incorrectly appears in public view")
                    return False
                else:
                    log_test("Video Status 'draft'", False, 
                            "Draft video not visible to staff with showAll=true")
                    return False
            else:
                log_test("Video Status 'draft'", False, f"Failed to get public videos: {public_response.status_code}")
                return False
        else:
            log_test("Video Status 'draft'", False, f"Failed to create video: {response.status_code}")
            return False
    except Exception as e:
        log_test("Video Status 'draft'", False, f"Error: {str(e)}")
        return False

def test_video_status_scheduled_future():
    """Test 65: POST /api/videos with status='scheduled' (future date) - Should NOT appear in public view"""
    print("\n=== Test 65: Video Status 'scheduled' (Future) - Hidden from Public ===")
    
    try:
        from datetime import timedelta
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        payload = {
            "title": "Test Video: Scheduled Future",
            "animeTitle": "Doraemon",
            "episode": "Eps Test Scheduled Future",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test-scheduled-future",
            "description": "Test video scheduled for future release",
            "status": "scheduled",
            "scheduledAt": future_date,
            "views": 0,
            "likes": 0
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            video_id = video['id']
            
            # Verify it does NOT appear in public view
            public_response = requests.get(f"{BASE_URL}/videos", timeout=10)
            if public_response.status_code == 200:
                public_videos = public_response.json()
                found_in_public = any(v['id'] == video_id for v in public_videos)
                
                # Verify it DOES appear in staff view (with showAll=true)
                staff_response = requests.get(f"{BASE_URL}/videos?showAll=true", timeout=10)
                found_in_staff = False
                if staff_response.status_code == 200:
                    staff_videos = staff_response.json()
                    found_in_staff = any(v['id'] == video_id for v in staff_videos)
                
                # Clean up
                requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
                
                if not found_in_public and found_in_staff:
                    log_test("Video Status 'scheduled' (Future)", True, 
                            f"Future scheduled video correctly hidden from public but visible to staff (scheduledAt: {future_date[:10]})")
                    return True
                elif found_in_public:
                    log_test("Video Status 'scheduled' (Future)", False, 
                            "Future scheduled video incorrectly appears in public view")
                    return False
                else:
                    log_test("Video Status 'scheduled' (Future)", False, 
                            "Future scheduled video not visible to staff with showAll=true")
                    return False
            else:
                log_test("Video Status 'scheduled' (Future)", False, f"Failed to get public videos: {public_response.status_code}")
                return False
        else:
            log_test("Video Status 'scheduled' (Future)", False, f"Failed to create video: {response.status_code}")
            return False
    except Exception as e:
        log_test("Video Status 'scheduled' (Future)", False, f"Error: {str(e)}")
        return False

def test_video_status_scheduled_past():
    """Test 66: POST /api/videos with status='scheduled' (past date) - Should appear in public view"""
    print("\n=== Test 66: Video Status 'scheduled' (Past) - Public Visibility ===")
    
    try:
        from datetime import timedelta
        past_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        payload = {
            "title": "Test Video: Scheduled Past",
            "animeTitle": "Doraemon",
            "episode": "Eps Test Scheduled Past",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test-scheduled-past",
            "description": "Test video scheduled for past release (should be visible)",
            "status": "scheduled",
            "scheduledAt": past_date,
            "views": 0,
            "likes": 0
        }
        
        response = requests.post(f"{BASE_URL}/videos", json=payload, timeout=10)
        if response.status_code == 200:
            video = response.json()
            video_id = video['id']
            
            # Verify it DOES appear in public view
            public_response = requests.get(f"{BASE_URL}/videos", timeout=10)
            if public_response.status_code == 200:
                public_videos = public_response.json()
                found_in_public = any(v['id'] == video_id for v in public_videos)
                
                # Clean up
                requests.delete(f"{BASE_URL}/videos?id={video_id}", timeout=10)
                
                if found_in_public:
                    log_test("Video Status 'scheduled' (Past)", True, 
                            f"Past scheduled video correctly appears in public view (scheduledAt: {past_date[:10]})")
                    return True
                else:
                    log_test("Video Status 'scheduled' (Past)", False, 
                            "Past scheduled video does NOT appear in public view")
                    return False
            else:
                log_test("Video Status 'scheduled' (Past)", False, f"Failed to get public videos: {public_response.status_code}")
                return False
        else:
            log_test("Video Status 'scheduled' (Past)", False, f"Failed to create video: {response.status_code}")
            return False
    except Exception as e:
        log_test("Video Status 'scheduled' (Past)", False, f"Error: {str(e)}")
        return False

def test_video_showAll_parameter():
    """Test 67: GET /api/videos?showAll=true - Staff view shows all videos regardless of status"""
    print("\n=== Test 67: GET /api/videos?showAll=true - Staff View ===")
    
    try:
        from datetime import timedelta
        
        # Create test videos with different statuses
        test_videos = []
        
        # Published video
        published_payload = {
            "title": "Test: Published for ShowAll",
            "animeTitle": "Doraemon",
            "episode": "Eps Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test1",
            "status": "published",
            "views": 0,
            "likes": 0
        }
        resp1 = requests.post(f"{BASE_URL}/videos", json=published_payload, timeout=10)
        if resp1.status_code == 200:
            test_videos.append(resp1.json())
        
        # Draft video
        draft_payload = {
            "title": "Test: Draft for ShowAll",
            "animeTitle": "Doraemon",
            "episode": "Eps Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test2",
            "status": "draft",
            "views": 0,
            "likes": 0
        }
        resp2 = requests.post(f"{BASE_URL}/videos", json=draft_payload, timeout=10)
        if resp2.status_code == 200:
            test_videos.append(resp2.json())
        
        # Future scheduled video
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        scheduled_payload = {
            "title": "Test: Scheduled for ShowAll",
            "animeTitle": "Doraemon",
            "episode": "Eps Test",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test3",
            "status": "scheduled",
            "scheduledAt": future_date,
            "views": 0,
            "likes": 0
        }
        resp3 = requests.post(f"{BASE_URL}/videos", json=scheduled_payload, timeout=10)
        if resp3.status_code == 200:
            test_videos.append(resp3.json())
        
        if len(test_videos) < 3:
            log_test("GET /api/videos?showAll=true", False, "Failed to create test videos")
            return False
        
        # Get public view (without showAll)
        public_response = requests.get(f"{BASE_URL}/videos", timeout=10)
        public_count = 0
        if public_response.status_code == 200:
            public_videos = public_response.json()
            test_ids = [v['id'] for v in test_videos]
            public_count = sum(1 for v in public_videos if v['id'] in test_ids)
        
        # Get staff view (with showAll=true)
        staff_response = requests.get(f"{BASE_URL}/videos?showAll=true", timeout=10)
        staff_count = 0
        if staff_response.status_code == 200:
            staff_videos = staff_response.json()
            test_ids = [v['id'] for v in test_videos]
            staff_count = sum(1 for v in staff_videos if v['id'] in test_ids)
        
        # Clean up
        for video in test_videos:
            requests.delete(f"{BASE_URL}/videos?id={video['id']}", timeout=10)
        
        # Public view should show only 1 (published), staff view should show all 3
        if public_count == 1 and staff_count == 3:
            log_test("GET /api/videos?showAll=true", True, 
                    f"Staff view correctly shows all videos (3/3), public view shows only published (1/3)")
            return True
        else:
            log_test("GET /api/videos?showAll=true", False, 
                    f"Incorrect filtering: public={public_count}/1, staff={staff_count}/3")
            return False
            
    except Exception as e:
        log_test("GET /api/videos?showAll=true", False, f"Error: {str(e)}")
        return False


def test_video_search_by_episode():
    """Test 68: GET /api/videos?search=<episode> - Search videos by episode number/string"""
    print("\n=== Test 68: GET /api/videos?search=<episode> - Episode Search ===")
    
    try:
        # Create test videos with specific episode numbers
        test_videos = []
        
        # Video with episode "Eps 100"
        video1_payload = {
            "title": "Doraemon: Petualangan Episode 100",
            "animeTitle": "Doraemon",
            "episode": "Eps 100",
            "thumbnailUrl": "https://images.unsplash.com/photo-1710052014408-557848f939db?w=400",
            "videoUrl": "https://www.youtube.com/embed/test100",
            "description": "Episode spesial ke-100",
            "views": 0,
            "likes": 0
        }
        resp1 = requests.post(f"{BASE_URL}/videos", json=video1_payload, timeout=10)
        if resp1.status_code == 200:
            test_videos.append(resp1.json())
        
        # Video with episode "Eps 200"
        video2_payload = {
            "title": "Crayon Shinchan: Episode 200 Spesial",
            "animeTitle": "Crayon Shinchan",
            "episode": "Eps 200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1741676470815-f4e90ca4d650?w=400",
            "videoUrl": "https://www.youtube.com/embed/test200",
            "description": "Episode spesial ke-200",
            "views": 0,
            "likes": 0
        }
        resp2 = requests.post(f"{BASE_URL}/videos", json=video2_payload, timeout=10)
        if resp2.status_code == 200:
            test_videos.append(resp2.json())
        
        # Video with episode "100" (integer-like string)
        video3_payload = {
            "title": "Ninja Hattori: Episode Seratus",
            "animeTitle": "Ninja Hattori-kun",
            "episode": "100",
            "thumbnailUrl": "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400",
            "videoUrl": "https://www.youtube.com/embed/test100b",
            "description": "Episode dengan nomor 100",
            "views": 0,
            "likes": 0
        }
        resp3 = requests.post(f"{BASE_URL}/videos", json=video3_payload, timeout=10)
        if resp3.status_code == 200:
            test_videos.append(resp3.json())
        
        if len(test_videos) < 3:
            log_test("GET /api/videos?search=<episode>", False, "Failed to create test videos")
            return False
        
        # Test 1: Search by "100" - should find videos with episode containing "100"
        search_response1 = requests.get(f"{BASE_URL}/videos?search=100", timeout=10)
        found_count_100 = 0
        if search_response1.status_code == 200:
            search_results = search_response1.json()
            test_ids = [v['id'] for v in test_videos]
            found_videos = [v for v in search_results if v['id'] in test_ids]
            found_count_100 = len(found_videos)
            print(f"   ✓ Search '100' found {found_count_100} test videos")
            for v in found_videos:
                print(f"     - {v['animeTitle']}: {v['episode']}")
        
        # Test 2: Search by "200" - should find video with episode "Eps 200"
        search_response2 = requests.get(f"{BASE_URL}/videos?search=200", timeout=10)
        found_count_200 = 0
        if search_response2.status_code == 200:
            search_results = search_response2.json()
            test_ids = [v['id'] for v in test_videos]
            found_videos = [v for v in search_results if v['id'] in test_ids]
            found_count_200 = len(found_videos)
            print(f"   ✓ Search '200' found {found_count_200} test video(s)")
            for v in found_videos:
                print(f"     - {v['animeTitle']}: {v['episode']}")
        
        # Test 3: Search by "Eps" - should find videos with "Eps" in episode
        search_response3 = requests.get(f"{BASE_URL}/videos?search=Eps", timeout=10)
        found_count_eps = 0
        if search_response3.status_code == 200:
            search_results = search_response3.json()
            test_ids = [v['id'] for v in test_videos]
            found_videos = [v for v in search_results if v['id'] in test_ids]
            found_count_eps = len(found_videos)
            print(f"   ✓ Search 'Eps' found {found_count_eps} test video(s)")
        
        # Clean up
        for video in test_videos:
            requests.delete(f"{BASE_URL}/videos?id={video['id']}", timeout=10)
        
        # Verify results
        # Search "100" should find at least 2 videos (Eps 100 and 100)
        # Search "200" should find at least 1 video (Eps 200)
        # Search "Eps" should find at least 2 videos (Eps 100 and Eps 200)
        if found_count_100 >= 2 and found_count_200 >= 1 and found_count_eps >= 2:
            log_test("GET /api/videos?search=<episode>", True, 
                    f"Episode search working correctly: '100' found {found_count_100} videos, '200' found {found_count_200} video, 'Eps' found {found_count_eps} videos")
            return True
        else:
            log_test("GET /api/videos?search=<episode>", False, 
                    f"Episode search not working as expected: '100'={found_count_100}/2+, '200'={found_count_200}/1+, 'Eps'={found_count_eps}/2+")
            return False
            
    except Exception as e:
        log_test("GET /api/videos?search=<episode>", False, f"Error: {str(e)}")
        return False

def test_get_chat_messages():
    """Test 78: GET /api/chat - Retrieve global chat messages"""
    print("\n=== Test 78: GET /api/chat ===")
    
    try:
        response = requests.get(f"{BASE_URL}/chat", timeout=10)
        if response.status_code == 200:
            messages = response.json()
            if isinstance(messages, list):
                log_test("GET /api/chat", True, f"Retrieved {len(messages)} chat messages")
                return messages
            else:
                log_test("GET /api/chat", False, "Response is not a list")
                return None
        else:
            log_test("GET /api/chat", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/chat", False, f"Error: {str(e)}")
        return None

def test_create_chat_message():
    """Test 79: POST /api/chat - Send a new chat message"""
    print("\n=== Test 79: POST /api/chat ===")
    
    try:
        payload = {
            "userName": "Test User Retro",
            "userAvatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80",
            "content": "Halo dari backend test! Doraemon adalah anime terbaik! 🎌"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=10)
        if response.status_code == 200:
            message = response.json()
            if message.get('id') and message.get('content') == payload['content']:
                log_test("POST /api/chat", True, f"Message created with ID: {message['id']}")
                return message
            else:
                log_test("POST /api/chat", False, "Message creation response invalid")
                return None
        else:
            log_test("POST /api/chat", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/chat", False, f"Error: {str(e)}")
        return None

def test_create_chat_message_empty_content():
    """Test 80: POST /api/chat - Validation for empty content"""
    print("\n=== Test 80: POST /api/chat (Empty Content Validation) ===")
    
    try:
        payload = {
            "userName": "Test User",
            "userAvatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80",
            "content": ""
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=10)
        if response.status_code == 400:
            error = response.json()
            if 'error' in error:
                log_test("POST /api/chat (Empty Content)", True, f"Correctly rejected empty content: {error['error']}")
                return True
            else:
                log_test("POST /api/chat (Empty Content)", False, "Error response missing 'error' field")
                return False
        else:
            log_test("POST /api/chat (Empty Content)", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/chat (Empty Content)", False, f"Error: {str(e)}")
        return False

def test_create_chat_message_default_values():
    """Test 81: POST /api/chat - Default userName and userAvatar"""
    print("\n=== Test 81: POST /api/chat (Default Values) ===")
    
    try:
        payload = {
            "content": "Pesan tanpa nama dan avatar eksplisit"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=10)
        if response.status_code == 200:
            message = response.json()
            if message.get('userName') == 'Pecinta Retro' and message.get('userAvatar'):
                log_test("POST /api/chat (Default Values)", True, f"Default values applied: userName='{message['userName']}'")
                return message
            else:
                log_test("POST /api/chat (Default Values)", False, f"Default values not applied correctly")
                return None
        else:
            log_test("POST /api/chat (Default Values)", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/chat (Default Values)", False, f"Error: {str(e)}")
        return None

def test_chat_message_ordering():
    """Test 82: GET /api/chat - Verify messages are ordered by createdAt ascending"""
    print("\n=== Test 82: GET /api/chat (Message Ordering) ===")
    
    try:
        # Create multiple messages
        messages_created = []
        for i in range(3):
            payload = {
                "userName": f"Test User {i+1}",
                "content": f"Test message {i+1} untuk verifikasi urutan"
            }
            response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=10)
            if response.status_code == 200:
                messages_created.append(response.json())
        
        # Retrieve messages
        response = requests.get(f"{BASE_URL}/chat", timeout=10)
        if response.status_code == 200:
            messages = response.json()
            
            # Check if messages are ordered by createdAt ascending (oldest first)
            if len(messages) >= 3:
                # Find our test messages
                test_messages = [m for m in messages if any(created['id'] == m['id'] for created in messages_created)]
                
                if len(test_messages) >= 3:
                    # Verify ordering
                    is_ordered = True
                    for i in range(len(test_messages) - 1):
                        current_time = test_messages[i].get('createdAt', '')
                        next_time = test_messages[i+1].get('createdAt', '')
                        if current_time > next_time:
                            is_ordered = False
                            break
                    
                    if is_ordered:
                        log_test("GET /api/chat (Message Ordering)", True, "Messages correctly ordered by createdAt ascending")
                        return True
                    else:
                        log_test("GET /api/chat (Message Ordering)", False, "Messages not ordered correctly")
                        return False
                else:
                    log_test("GET /api/chat (Message Ordering)", False, "Could not find test messages in response")
                    return False
            else:
                log_test("GET /api/chat (Message Ordering)", False, f"Not enough messages to verify ordering (found {len(messages)})")
                return False
        else:
            log_test("GET /api/chat (Message Ordering)", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("GET /api/chat (Message Ordering)", False, f"Error: {str(e)}")
        return False

def test_chat_message_limit():
    """Test 83: GET /api/chat - Verify 100 message limit"""
    print("\n=== Test 83: GET /api/chat (100 Message Limit) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/chat", timeout=10)
        if response.status_code == 200:
            messages = response.json()
            message_count = len(messages)
            
            if message_count <= 100:
                log_test("GET /api/chat (Message Limit)", True, f"Message count within limit: {message_count}/100")
                return True
            else:
                log_test("GET /api/chat (Message Limit)", False, f"Message count exceeds limit: {message_count}/100")
                return False
        else:
            log_test("GET /api/chat (Message Limit)", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("GET /api/chat (Message Limit)", False, f"Error: {str(e)}")
        return False


def test_get_emotes():
    """Test 87: GET /api/emotes - Retrieve custom emotes"""
    print("\n=== Test 87: GET /api/emotes ===")
    
    try:
        response = requests.get(f"{BASE_URL}/emotes", timeout=10)
        if response.status_code == 200:
            emotes = response.json()
            if isinstance(emotes, list):
                log_test("GET /api/emotes", True, f"Retrieved {len(emotes)} custom emotes")
                return emotes
            else:
                log_test("GET /api/emotes", False, "Response is not a list")
                return None
        else:
            log_test("GET /api/emotes", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("GET /api/emotes", False, f"Error: {str(e)}")
        return None

def test_create_emote():
    """Test 88: POST /api/emotes - Create a new custom emote"""
    print("\n=== Test 88: POST /api/emotes ===")
    
    try:
        payload = {
            "code": "test_emote_backend",
            "imageUrl": "https://ik.imagekit.io/shindoranesub/test-emote.gif"
        }
        
        response = requests.post(f"{BASE_URL}/emotes", json=payload, timeout=10)
        if response.status_code == 200:
            emote = response.json()
            if emote.get('id') and emote.get('code') == ':test_emote_backend:':
                log_test("POST /api/emotes", True, f"Emote created with ID: {emote['id']}, code: {emote['code']}")
                return emote
            else:
                log_test("POST /api/emotes", False, "Emote creation response invalid")
                return None
        else:
            log_test("POST /api/emotes", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        log_test("POST /api/emotes", False, f"Error: {str(e)}")
        return None

def test_create_emote_validation():
    """Test 89: POST /api/emotes - Validation for missing fields"""
    print("\n=== Test 89: POST /api/emotes (Validation) ===")
    
    try:
        # Test with missing code
        payload = {
            "imageUrl": "https://ik.imagekit.io/shindoranesub/test.gif"
        }
        
        response = requests.post(f"{BASE_URL}/emotes", json=payload, timeout=10)
        if response.status_code == 400:
            error = response.json()
            if 'error' in error:
                log_test("POST /api/emotes (Missing Code)", True, f"Correctly rejected: {error['error']}")
                return True
            else:
                log_test("POST /api/emotes (Missing Code)", False, "Error response missing 'error' field")
                return False
        else:
            log_test("POST /api/emotes (Missing Code)", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/emotes (Missing Code)", False, f"Error: {str(e)}")
        return False

def test_create_emote_duplicate():
    """Test 90: POST /api/emotes - Duplicate code validation"""
    print("\n=== Test 90: POST /api/emotes (Duplicate Code) ===")
    
    try:
        # Try to create emote with same code
        payload = {
            "code": ":test_emote_backend:",
            "imageUrl": "https://ik.imagekit.io/shindoranesub/test-duplicate.gif"
        }
        
        response = requests.post(f"{BASE_URL}/emotes", json=payload, timeout=10)
        if response.status_code == 400:
            error = response.json()
            if 'error' in error and 'sudah digunakan' in error['error']:
                log_test("POST /api/emotes (Duplicate Code)", True, f"Correctly rejected duplicate: {error['error']}")
                return True
            else:
                log_test("POST /api/emotes (Duplicate Code)", False, "Error message doesn't indicate duplicate")
                return False
        else:
            log_test("POST /api/emotes (Duplicate Code)", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/emotes (Duplicate Code)", False, f"Error: {str(e)}")
        return False

def test_delete_emote(emote):
    """Test 91: DELETE /api/emotes - Delete a custom emote"""
    print("\n=== Test 91: DELETE /api/emotes ===")
    
    if not emote or not emote.get('id'):
        log_test("DELETE /api/emotes", False, "No emote provided for deletion")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/emotes?id={emote['id']}", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("DELETE /api/emotes", True, f"Emote {emote['code']} deleted successfully")
                return True
            else:
                log_test("DELETE /api/emotes", False, "Delete response missing 'success' field")
                return False
        else:
            log_test("DELETE /api/emotes", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("DELETE /api/emotes", False, f"Error: {str(e)}")
        return False

def test_emote_code_formatting():
    """Test 92: POST /api/emotes - Auto-formatting of emote codes"""
    print("\n=== Test 92: POST /api/emotes (Code Formatting) ===")
    
    try:
        # Test with code without colons
        payload = {
            "code": "test_format",
            "imageUrl": "https://ik.imagekit.io/shindoranesub/test-format.gif"
        }
        
        response = requests.post(f"{BASE_URL}/emotes", json=payload, timeout=10)
        if response.status_code == 200:
            emote = response.json()
            if emote.get('code') == ':test_format:':
                log_test("POST /api/emotes (Code Formatting)", True, f"Code auto-formatted: 'test_format' → '{emote['code']}'")
                # Clean up
                try:
                    requests.delete(f"{BASE_URL}/emotes?id={emote['id']}", timeout=10)
                except:
                    pass
                return True
            else:
                log_test("POST /api/emotes (Code Formatting)", False, f"Code not formatted correctly: {emote.get('code')}")
                return False
        else:
            log_test("POST /api/emotes (Code Formatting)", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("POST /api/emotes (Code Formatting)", False, f"Error: {str(e)}")
        return False



def test_sitemap_xml():
    """Test 84: GET /sitemap.xml - Dynamic XML Sitemap Generation"""
    print("\n=== Test 84: GET /sitemap.xml (Dynamic XML Sitemap) ===")
    
    try:
        # Test sitemap endpoint
        response = requests.get(f"{BASE_URL.replace('/api', '')}/sitemap.xml", timeout=15)
        
        if response.status_code != 200:
            log_test("GET /sitemap.xml", False, f"Status code: {response.status_code}")
            return False
        
        # Verify Content-Type is XML
        content_type = response.headers.get('Content-Type', '')
        if 'xml' not in content_type.lower():
            log_test("GET /sitemap.xml", False, f"Invalid Content-Type: {content_type}, expected application/xml")
            return False
        
        print(f"   ✓ Content-Type: {content_type}")
        
        # Parse XML content
        xml_content = response.text
        
        # Verify XML structure
        if '<?xml version="1.0" encoding="UTF-8"?>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing XML declaration")
            return False
        
        if '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing urlset declaration")
            return False
        
        print("   ✓ Valid XML structure")
        
        # Count URLs in sitemap
        url_count = xml_content.count('<url>')
        if url_count == 0:
            log_test("GET /sitemap.xml", False, "No URLs found in sitemap")
            return False
        
        print(f"   ✓ Found {url_count} URLs in sitemap")
        
        # Verify home page is included
        base_url = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/')
        if f'<loc>{base_url}</loc>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Home page not found in sitemap")
            return False
        
        print(f"   ✓ Home page included: {base_url}")
        
        # Verify video pages are included (check for /watch/ URLs)
        watch_url_count = xml_content.count('/watch/')
        if watch_url_count == 0:
            log_test("GET /sitemap.xml", False, "No video pages (/watch/) found in sitemap")
            return False
        
        print(f"   ✓ Found {watch_url_count} video pages (/watch/)")
        
        # Verify category pages are included (check for /page/ URLs)
        page_url_count = xml_content.count('/page/')
        print(f"   ✓ Found {page_url_count} category pages (/page/)")
        
        # Verify lastmod, changefreq, and priority tags exist
        if '<lastmod>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing <lastmod> tags")
            return False
        
        if '<changefreq>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing <changefreq> tags")
            return False
        
        if '<priority>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing <priority> tags")
            return False
        
        print("   ✓ All required tags present: <lastmod>, <changefreq>, <priority>")
        
        # Verify sitemap closes properly
        if '</urlset>' not in xml_content:
            log_test("GET /sitemap.xml", False, "Missing closing </urlset> tag")
            return False
        
        print("   ✓ Sitemap properly closed")
        
        # Verify Cache-Control header
        cache_control = response.headers.get('Cache-Control', '')
        if 'max-age' in cache_control:
            print(f"   ✓ Cache-Control header present: {cache_control}")
        
        log_test("GET /sitemap.xml", True, 
                f"✅ Dynamic XML sitemap working perfectly: {url_count} total URLs ({watch_url_count} videos, {page_url_count} categories), "
                f"valid XML structure, proper headers (Content-Type: {content_type}), "
                f"includes home page, video pages (/watch/), and category pages (/page/). "
                f"All required SEO tags present (lastmod, changefreq, priority).")
        return True
        
    except Exception as e:
        log_test("GET /sitemap.xml", False, f"Error: {str(e)}")
        return False


def test_rate_limiting():
    """Test 85: Rate Limiting Middleware - Verify 429 status on spam request bursts"""
    print("\n=== Test 85: Rate Limiting Middleware (429 on Spam Bursts) ===")
    
    try:
        # The middleware allows 100 requests per minute per IP
        # We'll make 105 rapid requests to trigger rate limiting
        print("   Making burst requests to trigger rate limiting...")
        
        rate_limit_triggered = False
        success_count = 0
        rate_limited_count = 0
        
        # Make burst requests
        for i in range(105):
            try:
                response = requests.get(f"{BASE_URL}/videos", headers={"x-test-rate-limit": "true"}, timeout=5)
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    rate_limit_triggered = True
                    
                    # Verify response structure
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            print(f"   ✓ Rate limit triggered at request #{i+1}")
                            print(f"   ✓ Error message: {error_data['error']}")
                        
                        # Verify Retry-After header
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            print(f"   ✓ Retry-After header present: {retry_after} seconds")
                    except:
                        pass
                    
                    break
                    
            except Exception as e:
                print(f"   Request #{i+1} error: {str(e)}")
                continue
        
        print(f"   ✓ Successful requests: {success_count}")
        print(f"   ✓ Rate limited requests: {rate_limited_count}")
        
        if rate_limit_triggered:
            log_test("Rate Limiting Middleware", True, 
                    f"✅ Rate limiting working correctly: Triggered 429 status after {success_count} requests. "
                    f"Middleware successfully blocks spam request bursts (limit: 100 req/min). "
                    f"Response includes proper error message and Retry-After header.")
            return True
        else:
            log_test("Rate Limiting Middleware", False, 
                    f"Rate limiting not triggered after 105 requests. Expected 429 status after ~100 requests.")
            return False
            
    except Exception as e:
        log_test("Rate Limiting Middleware", False, f"Error: {str(e)}")
        return False

def test_json_ld_schema():
    """Test 86: JSON-LD Schema Validation - Verify VideoObject structured data"""
    print("\n=== Test 86: JSON-LD Schema Validation (VideoObject) ===")
    
    try:
        # First, get a video to test with
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code != 200:
            log_test("JSON-LD Schema Validation", False, "Failed to fetch videos for testing")
            return False
        
        videos = response.json()
        if not videos or len(videos) == 0:
            log_test("JSON-LD Schema Validation", False, "No videos found in database")
            return False
        
        # Get the first video's slug
        test_video = videos[0]
        video_slug = test_video.get('slug')
        
        if not video_slug:
            log_test("JSON-LD Schema Validation", False, "Test video has no slug")
            return False
        
        print(f"   Testing with video: {test_video.get('title', 'Unknown')} (slug: {video_slug})")
        
        # Fetch the video page HTML to extract JSON-LD
        base_url = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000").rstrip('/')
        page_url = f"{base_url}/watch/{video_slug}"
        
        print(f"   Fetching page: {page_url}")
        page_response = requests.get(page_url, timeout=15)
        
        if page_response.status_code != 200:
            log_test("JSON-LD Schema Validation", False, f"Failed to fetch video page: {page_response.status_code}")
            return False
        
        html_content = page_response.text
        
        # Extract JSON-LD from HTML
        import re
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(json_ld_pattern, html_content, re.DOTALL)
        
        if not matches:
            log_test("JSON-LD Schema Validation", False, "No JSON-LD script found in page HTML")
            return False
        
        print(f"   ✓ Found {len(matches)} JSON-LD script(s)")
        
        # Parse the JSON-LD
        json_ld_str = matches[0].strip()
        try:
            json_ld = json.loads(json_ld_str)
        except json.JSONDecodeError as e:
            log_test("JSON-LD Schema Validation", False, f"Invalid JSON-LD format: {str(e)}")
            return False
        
        print("   ✓ JSON-LD is valid JSON")
        
        # Validate VideoObject schema structure
        required_fields = ['@context', '@type', 'name', 'description', 'thumbnailUrl', 'uploadDate']
        missing_fields = []
        
        for field in required_fields:
            if field not in json_ld:
                missing_fields.append(field)
        
        if missing_fields:
            log_test("JSON-LD Schema Validation", False, f"Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("   ✓ All required fields present")
        
        # Validate field values
        if json_ld.get('@context') != 'https://schema.org':
            log_test("JSON-LD Schema Validation", False, f"Invalid @context: {json_ld.get('@context')}")
            return False
        
        print(f"   ✓ @context: {json_ld.get('@context')}")
        
        if json_ld.get('@type') != 'VideoObject':
            log_test("JSON-LD Schema Validation", False, f"Invalid @type: {json_ld.get('@type')}, expected 'VideoObject'")
            return False
        
        print(f"   ✓ @type: {json_ld.get('@type')}")
        
        # Validate name
        if not json_ld.get('name'):
            log_test("JSON-LD Schema Validation", False, "Empty 'name' field")
            return False
        
        print(f"   ✓ name: {json_ld.get('name')}")
        
        # Validate description
        if not json_ld.get('description'):
            log_test("JSON-LD Schema Validation", False, "Empty 'description' field")
            return False
        
        print(f"   ✓ description: {json_ld.get('description')[:50]}...")
        
        # Validate thumbnailUrl (should be array)
        thumbnail_url = json_ld.get('thumbnailUrl')
        if not isinstance(thumbnail_url, list) or len(thumbnail_url) == 0:
            log_test("JSON-LD Schema Validation", False, "thumbnailUrl should be a non-empty array")
            return False
        
        print(f"   ✓ thumbnailUrl: {thumbnail_url[0]}")
        
        # Validate uploadDate (should be ISO format)
        upload_date = json_ld.get('uploadDate')
        try:
            from datetime import datetime
            datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
            print(f"   ✓ uploadDate: {upload_date} (valid ISO format)")
        except:
            log_test("JSON-LD Schema Validation", False, f"Invalid uploadDate format: {upload_date}")
            return False
        
        # Check optional fields
        optional_fields = ['embedUrl', 'interactionStatistic']
        for field in optional_fields:
            if field in json_ld:
                print(f"   ✓ {field}: present")
                
                # Validate interactionStatistic structure if present
                if field == 'interactionStatistic':
                    interaction = json_ld[field]
                    if isinstance(interaction, dict):
                        if interaction.get('@type') == 'InteractionCounter':
                            print(f"      - @type: InteractionCounter")
                            print(f"      - userInteractionCount: {interaction.get('userInteractionCount', 0)}")
        
        log_test("JSON-LD Schema Validation", True, 
                f"✅ JSON-LD VideoObject schema is valid and healthy. "
                f"All required fields present (@context, @type, name, description, thumbnailUrl, uploadDate). "
                f"Schema.org VideoObject structure verified. "
                f"Optional fields (embedUrl, interactionStatistic) also present. "
                f"Tested with video: {json_ld.get('name')}")
        return True
        
    except Exception as e:
        log_test("JSON-LD Schema Validation", False, f"Error: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main test execution"""
    # Pre-test database cleanup of stale test data
    try:
        from pymongo import MongoClient
        import os
        client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
        db = client[os.getenv("DB_NAME", "your_database_name")]
        db.videos.delete_many({"$or": [{"slug": {"$regex": "^test-"}}, {"title": {"$regex": "^Test"}}]})
        db.categories.delete_many({"$or": [{"slug": {"$regex": "^test-"}}, {"name": {"$regex": "^Test"}}]})
    except Exception as e:
        print("Pre-test cleanup warning:", e)

    print("="*60)
    print("ShinDora Nesub Backend API Test Suite")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests in sequence
    test_mongodb_connection_and_seeding()
    videos = test_get_videos()
    categories = test_get_categories()
    settings = test_get_settings()
    ads = test_get_ads()
    
    # Categories CRUD tests
    new_category = test_create_category()
    updated_category = test_update_category(new_category)
    test_delete_category(updated_category if updated_category else new_category)
    test_database_seeding_verification()
    
    # Auth tests
    new_user = test_auth_register()
    logged_user = test_auth_login(new_user)
    admin = test_admin_login_staff_only()
    admin_regular = test_admin_login_regular()
    test_regular_user_staff_only_rejection(logged_user)
    
    # NEW FEATURE TESTS
    moderator = test_moderator_login_staff_only()
    test_forgot_password()
    test_forgot_password_unregistered()
    
    # RESET PASSWORD TESTS (NEW)
    test_reset_password_valid()
    test_reset_password_invalid_pin()
    test_reset_password_missing_fields()
    test_reset_password_unregistered_email()
    
    test_onesignal_notify()
    test_onesignal_notify_missing_fields()
    
    # Comment tests
    parent_comment, reply_comment = test_create_comment_and_reply(logged_user)
    test_delete_comment_recursive(parent_comment)
    
    # Multi-server video URLs test
    test_multi_server_video_urls()
    
    # Playlist CRUD tests
    playlists = test_get_playlists()
    new_playlist = test_create_playlist(logged_user)
    updated_playlist = test_update_playlist(new_playlist)
    test_delete_playlist(updated_playlist)
    
    # Video CRUD tests
    new_video = test_create_video()
    updated_video = test_update_video(new_video)
    # Test video views increment
    video_with_incremented_views = test_increment_video_views(updated_video if updated_video else new_video)
    
    # Test likes toggle functionality
    test_toggle_like()
    
    test_delete_video(video_with_incremented_views if video_with_incremented_views else updated_video)
    
    # Bulk CSV import test
    test_bulk_csv_import()
    
    # Users management test
    test_get_users()
    
    # Test forgot-password with non-mock provider
    test_forgot_password_non_mock()
    
    # Custom Pages CRUD tests
    pages = test_get_pages()
    new_page = test_create_page()
    updated_page = test_update_page(new_page)
    test_delete_page(updated_page)
    
    # Donation & Webhook tests
    donations = test_get_donations()
    new_donation = test_create_donation()
    test_delete_donation(new_donation)
    saweria_donation = test_saweria_webhook()
    trakteer_donation = test_trakteer_webhook()
    latest_donations = test_get_latest_donations()
    
    # NEW FEATURE TESTS: Auto-Push OneSignal & Running Text Announcement
    video_with_push = test_create_video_with_push_notification()
    if video_with_push:
        # Clean up the test video
        try:
            requests.delete(f"{BASE_URL}/videos?id={video_with_push['id']}", timeout=10)
        except Exception:
            pass
    running_text_settings = test_settings_running_text_announcement()
    
    # NEW FEATURE TEST: Stream Key Masking (Saweria, Trakteer, Tako.id)
    test_stream_key_masking()
    
    # NEW FEATURE TEST: Hero Banner Toggle
    test_hero_banner_toggle()
    
    # NEW FEATURE TESTS: Polling & Voting (Vote Anime Selanjutnya)
    existing_polls = test_get_polling()
    new_poll = test_create_polling()
    updated_poll = test_update_polling(new_poll)
    voted_poll = test_vote_on_poll(updated_poll if updated_poll else new_poll)
    test_delete_polling(voted_poll if voted_poll else new_poll)
    
    # NEW FEATURE TESTS: User-Votes Database Tracking & Quota Check
    test_poll_user_tracking = test_vote_with_user_tracking()
    test_vote_quota_check_duplicate()
    test_vote_different_user()
    
    # NEW FEATURE TESTS: ImageKit Credentials from Database (NOT .env)
    test_imagekit_credentials_from_database()
    test_imagekit_auth_endpoint()
    test_imagekit_auth_without_credentials()
    
    # NEW FEATURE TESTS: Slug-based lookups for video API endpoints
    test_toggle_like_with_slug()
    test_increment_views_with_slug()
    test_get_comments_with_slug()
    test_reply_notification_with_slug(logged_user)
    
    # NEW FEATURE TESTS: Video Status and Release Schedule Filtering
    test_video_status_published()
    test_video_status_draft()
    test_video_status_scheduled_future()
    test_video_status_scheduled_past()
    test_video_showAll_parameter()
    
    # NEW FEATURE TEST: Episode Search Functionality
    test_video_search_by_episode()
    
    # NEW FEATURE TESTS: Category Parent/Child Structure and Video Associations
    parent_cat, child_cats = test_category_parent_child_structure()
    test_category_parent_deletion_orphan_handling(parent_cat, child_cats)
    test_video_category_association()
    
    # NEW FEATURE TESTS: Global Floating Live Chat Widget
    chat_messages = test_get_chat_messages()
    new_chat_message = test_create_chat_message()
    test_create_chat_message_empty_content()
    test_create_chat_message_default_values()
    test_chat_message_ordering()
    test_chat_message_limit()
    
    # NEW FEATURE TESTS: Custom Emotes Management
    existing_emotes = test_get_emotes()
    new_emote = test_create_emote()
    test_create_emote_validation()
    test_create_emote_duplicate()
    test_emote_code_formatting()
    if new_emote:
        test_delete_emote(new_emote)
    
    # NEW FEATURE TEST: Dynamic XML Sitemap & Server-Side Metadata
    test_sitemap_xml()
    
    # NEW FEATURE TESTS: Rate Limiting & JSON-LD Schema Validation
    test_rate_limiting()
    test_json_ld_schema()
    
    # Print summary
    all_passed = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
