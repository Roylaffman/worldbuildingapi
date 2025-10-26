#!/usr/bin/env python3
"""
Direct Frontend Component Testing
Tests the TagManager and ContentLinker components in the main application
"""

import requests
import json
import webbrowser
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json=TEST_USER
    )
    if response.status_code == 200:
        return response.json()["access"]
    return None

def get_test_content():
    """Get available content for testing"""
    token = get_auth_token()
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get world 9 content
    world_id = 9
    content_types = ["pages", "essays", "characters", "images"]
    
    test_content = {}
    
    for content_type in content_types:
        try:
            response = requests.get(
                f"{BASE_URL}/worlds/{world_id}/{content_type}/",
                headers=headers
            )
            if response.status_code == 200:
                content_data = response.json()
                if isinstance(content_data, dict) and 'results' in content_data:
                    content = content_data['results']
                else:
                    content = content_data
                
                if content:
                    test_content[content_type] = content[0]
                    
        except Exception as e:
            print(f"Error fetching {content_type}: {e}")
    
    return test_content, world_id

def main():
    print("🎯 Frontend Component Testing - Direct Approach")
    print("=" * 60)
    
    # Get test content
    test_content, world_id = get_test_content()
    
    if not test_content:
        print("❌ No test content available")
        return
    
    print(f"✅ Found test content in world {world_id}:")
    for content_type, content in test_content.items():
        print(f"  - {content_type}: {content['title']} (ID: {content['id']})")
    
    print("\n📋 MANUAL TESTING INSTRUCTIONS:")
    print("=" * 60)
    
    # Pick the first available content for testing
    test_type, test_item = next(iter(test_content.items()))
    content_url = f"{FRONTEND_URL}/worlds/{world_id}/content/{test_type.rstrip('s')}/{test_item['id']}"
    
    print(f"1. 🌐 Opening content page: {content_url}")
    print(f"   Content: {test_item['title']}")
    print()
    
    print("2. 🏷️ TAGMANAGER TESTING:")
    print("   a. Look for 'Manage Tags' button in the Tags section")
    print("   b. Click 'Manage Tags' to open TagManager component")
    print("   c. Click 'Add Tag' button")
    print("   d. Type a test tag name (e.g., 'frontend-test-tag')")
    print("   e. Press Enter or click 'Add' button")
    print("   f. Verify tag appears in the existing tags list")
    print("   g. Check browser console for any errors")
    print()
    
    print("3. 🔗 CONTENTLINKER TESTING:")
    print("   a. Look for 'Manage Links' button in the Linked Content section")
    print("   b. Click 'Manage Links' to open ContentLinker component")
    print("   c. Click 'Link to Other Content' button")
    print("   d. Select different content types from dropdown")
    print("   e. Use search field to find content")
    print("   f. Click on content item to create link")
    print("   g. Verify link appears in 'Existing Links' section")
    print("   h. Check browser console for any errors")
    print()
    
    print("4. 📄 TAGSPAGE TESTING:")
    tags_url = f"{FRONTEND_URL}/worlds/{world_id}/tags"
    print(f"   a. Navigate to: {tags_url}")
    print("   b. Verify all world tags display in grid")
    print("   c. Click on individual tags")
    print("   d. Verify tagged content displays on TagPage")
    print()
    
    print("5. ✅ SUCCESS CRITERIA:")
    print("   - TagManager loads without errors")
    print("   - Tags can be added successfully")
    print("   - ContentLinker loads without errors")
    print("   - Links can be created successfully")
    print("   - TagsPage displays all tags")
    print("   - TagPage shows tagged content")
    print("   - No JavaScript errors in browser console")
    print()
    
    print("6. 🐛 COMMON ISSUES TO WATCH FOR:")
    print("   - Components not loading (check React errors)")
    print("   - API calls failing (check Network tab)")
    print("   - Authentication issues (check token in localStorage)")
    print("   - Missing data (check if content exists)")
    print("   - UI not updating after actions (check state management)")
    print()
    
    # Open the browser
    try:
        webbrowser.open(content_url)
        print(f"🌐 Opened browser to: {content_url}")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"   Please manually navigate to: {content_url}")
    
    print("\n🚀 Ready for manual testing!")
    print("   Follow the instructions above and report any issues.")

if __name__ == "__main__":
    main()