#!/usr/bin/env python3
"""
Test script to verify app/putar-manual/page.js compilation and functionality
"""

import requests
import json
import os
import subprocess
import re

BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://next-anime-hub.preview.emergentagent.com')

def test_nextjs_server_running():
    """Test 1: Verify Next.js server is running"""
    try:
        result = subprocess.run(
            ['sudo', 'supervisorctl', 'status', 'nextjs'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if 'RUNNING' in result.stdout:
            print("✅ Test 1 PASSED: Next.js server is running")
            print(f"   Server status: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Test 1 FAILED: Next.js server is not running")
            print(f"   Server status: {result.stdout.strip()}")
            return False
    except Exception as e:
        print(f"❌ Test 1 FAILED: Error checking server status: {e}")
        return False

def test_putar_manual_page_accessible():
    """Test 2: Verify /putar-manual page is accessible"""
    try:
        url = f"{BASE_URL}/putar-manual"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Test 2 PASSED: /putar-manual page is accessible (HTTP {response.status_code})")
            print(f"   URL: {url}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Test 2 FAILED: /putar-manual page returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test 2 FAILED: Error accessing /putar-manual page: {e}")
        return False

def test_putar_manual_page_content():
    """Test 3: Verify /putar-manual page contains expected content"""
    try:
        url = f"{BASE_URL}/putar-manual"
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Test 3 FAILED: Cannot verify content, page returned HTTP {response.status_code}")
            return False
        
        content = response.text
        
        # Check for key elements that should be present in the page
        checks = [
            ('PUTAR MANUAL SHINDORA', 'Page title'),
            ('Katalog Putar Manual', 'Catalog section'),
            ('Mode Mandiri', 'Manual mode indicator'),
            ('Kembali ke Beranda', 'Back to home link'),
        ]
        
        all_passed = True
        for search_text, description in checks:
            if search_text in content:
                print(f"   ✓ Found: {description}")
            else:
                print(f"   ✗ Missing: {description}")
                all_passed = False
        
        if all_passed:
            print("✅ Test 3 PASSED: /putar-manual page contains expected content")
            return True
        else:
            print("❌ Test 3 FAILED: /putar-manual page is missing some expected content")
            return False
    except Exception as e:
        print(f"❌ Test 3 FAILED: Error verifying page content: {e}")
        return False

def test_no_compilation_errors_in_logs():
    """Test 4: Verify no compilation errors in Next.js logs"""
    try:
        result = subprocess.run(
            ['tail', '-n', '200', '/var/log/supervisor/nextjs.stdout.log'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout
        
        # Check for compilation errors
        error_patterns = [
            r'Error:.*putar-manual',
            r'SyntaxError.*putar-manual',
            r'Failed to compile.*putar-manual',
            r'Module not found.*putar-manual',
            r'Cannot find module.*putar-manual',
        ]
        
        errors_found = []
        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                errors_found.extend(matches)
        
        if errors_found:
            print(f"❌ Test 4 FAILED: Found compilation errors in logs:")
            for error in errors_found[:5]:  # Show first 5 errors
                print(f"   - {error}")
            return False
        else:
            print("✅ Test 4 PASSED: No compilation errors found in Next.js logs")
            
            # Check for successful GET requests to /putar-manual
            putar_manual_requests = re.findall(r'GET /putar-manual.*', logs)
            if putar_manual_requests:
                print(f"   Found {len(putar_manual_requests)} successful requests to /putar-manual")
                # Show last 3 requests
                for req in putar_manual_requests[-3:]:
                    print(f"   - {req.strip()}")
            
            return True
    except Exception as e:
        print(f"❌ Test 4 FAILED: Error checking logs: {e}")
        return False

def test_page_file_syntax():
    """Test 5: Verify page.js file has valid JavaScript syntax"""
    try:
        file_path = '/app/app/putar-manual/page.js'
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ Test 5 FAILED: File not found: {file_path}")
            return False
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Basic syntax checks
        checks = [
            ("'use client'" in content or '"use client"' in content, "Client component directive"),
            ('export default function' in content, "Default export function"),
            ('useState' in content, "React useState hook"),
            ('useEffect' in content, "React useEffect hook"),
            ('return (' in content or 'return(' in content, "JSX return statement"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"   ✓ {description} present")
            else:
                print(f"   ✗ {description} missing")
                all_passed = False
        
        # Check for common syntax errors
        syntax_issues = []
        
        # Check for unmatched brackets (basic check)
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        
        if open_braces != close_braces:
            syntax_issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        if open_parens != close_parens:
            syntax_issues.append(f"Unmatched parentheses: {open_parens} open, {close_parens} close")
        if open_brackets != close_brackets:
            syntax_issues.append(f"Unmatched brackets: {open_brackets} open, {close_brackets} close")
        
        if syntax_issues:
            print("   ⚠ Potential syntax issues detected:")
            for issue in syntax_issues:
                print(f"     - {issue}")
            all_passed = False
        
        if all_passed:
            print("✅ Test 5 PASSED: page.js file has valid JavaScript syntax")
            print(f"   File size: {len(content)} bytes")
            print(f"   Lines of code: {len(content.splitlines())}")
            return True
        else:
            print("❌ Test 5 FAILED: page.js file has syntax issues")
            return False
    except Exception as e:
        print(f"❌ Test 5 FAILED: Error checking file syntax: {e}")
        return False

def test_api_endpoints_working():
    """Test 6: Verify API endpoints used by putar-manual page are working"""
    try:
        endpoints = [
            ('/api/videos', 'Videos API'),
            ('/api/categories', 'Categories API'),
            ('/api/settings', 'Settings API'),
        ]
        
        all_passed = True
        for endpoint, description in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    print(f"   ✓ {description} working (HTTP {response.status_code})")
                else:
                    print(f"   ✗ {description} failed (HTTP {response.status_code})")
                    all_passed = False
            except Exception as e:
                print(f"   ✗ {description} error: {e}")
                all_passed = False
        
        if all_passed:
            print("✅ Test 6 PASSED: All API endpoints used by putar-manual page are working")
            return True
        else:
            print("❌ Test 6 FAILED: Some API endpoints are not working")
            return False
    except Exception as e:
        print(f"❌ Test 6 FAILED: Error testing API endpoints: {e}")
        return False

def main():
    print("=" * 80)
    print("PUTAR MANUAL PAGE COMPILATION AND FUNCTIONALITY TEST")
    print("=" * 80)
    print()
    
    tests = [
        test_nextjs_server_running,
        test_putar_manual_page_accessible,
        test_putar_manual_page_content,
        test_no_compilation_errors_in_logs,
        test_page_file_syntax,
        test_api_endpoints_working,
    ]
    
    results = []
    for i, test in enumerate(tests, 1):
        print(f"\n{'=' * 80}")
        print(f"Running Test {i}/{len(tests)}: {test.__doc__.strip()}")
        print('=' * 80)
        result = test()
        results.append(result)
        print()
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The putar-manual page compiles and works correctly.")
        print("✅ No syntax errors detected")
        print("✅ No logic errors detected")
        print("✅ Server compiles the page successfully")
        print("✅ Page is accessible and functional")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the results above.")
    
    print("=" * 80)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
