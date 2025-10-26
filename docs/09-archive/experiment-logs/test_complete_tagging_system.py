#!/usr/bin/env python3
"""
Test the complete tagging system - both TagsPage and TagPage
"""

import requests
import webbrowser
import time

def test_backend_endpoints():
    """Test the backend endpoints"""
    print("🔧 Testing Backend Endpoints...")
    
    # Get token
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login/",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test tags list
    print("  Testing tags list...")
    response = requests.get("http://localhost:8000/api/v1/worlds/9/tags/", headers=headers)
    if response.status_code == 200:
        tags_data = response.json()
        tags = tags_data.get('results', tags_data)
        print(f"  ✅ Tags list: {len(tags)} tags found")
        
        # Test individual tag by name
        if tags:
            test_tag = tags[0]
            tag_name = test_tag['name']
            print(f"  Testing tag detail for: {tag_name}")
            
            response = requests.get(
                f"http://localhost:8000/api/v1/worlds/9/tags/by-name/{tag_name}/", 
                headers=headers
            )
            if response.status_code == 200:
                tag_detail = response.json()
                tagged_content = tag_detail.get('tagged_content', [])
                print(f"  ✅ Tag detail: {len(tagged_content)} tagged items")
                return True
            else:
                print(f"  ❌ Tag detail failed: {response.status_code}")
                return False
    else:
        print(f"  ❌ Tags list failed: {response.status_code}")
        return False

def main():
    print("🏷️ Complete Tagging System Test")
    print("=" * 50)
    
    # Test backend first
    if not test_backend_endpoints():
        print("❌ Backend tests failed - fix backend issues first")
        return
    
    print("\n✅ Backend tests passed!")
    
    print("\n📋 Frontend Testing Steps:")
    print("1. TagsPage Test:")
    print("   - Navigate to: http://localhost:3000/worlds/9/tags")
    print("   - Should see grid of 14 tags")
    print("   - Tags should include: alejandro, alt-history, buddhism, etc.")
    
    print("\n2. TagPage Test:")
    print("   - Click on any tag from the grid")
    print("   - Should navigate to individual tag page")
    print("   - Should show tagged content")
    print("   - Should show content count")
    
    print("\n3. Navigation Test:")
    print("   - Click on tagged content items")
    print("   - Should navigate to content detail pages")
    print("   - Should see tags in content pages")
    
    # Open TagsPage
    tags_url = "http://localhost:3000/worlds/9/tags"
    
    try:
        print(f"\n🌐 Opening TagsPage: {tags_url}")
        webbrowser.open(tags_url)
        
        print("\n✅ Expected Results:")
        print("- Grid layout with 14 tag cards")
        print("- Each tag shows name and creation date")
        print("- Clicking tag navigates to /worlds/9/tags/{tag-name}")
        print("- Individual tag pages show tagged content")
        print("- No 'No tags yet' message")
        print("- No JavaScript errors in console")
        
        print("\n🐛 If Issues Persist:")
        print("- Check browser console for errors")
        print("- Check Network tab for failed API calls")
        print("- Verify frontend server reloaded after changes")
        print("- Check if you're logged in")
        
        print("\n🎯 Success Criteria:")
        print("- TagsPage displays all world tags")
        print("- TagPage shows tagged content for each tag")
        print("- Navigation between pages works smoothly")
        print("- Users can discover content through tags")
        
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print(f"Please manually navigate to: {tags_url}")

if __name__ == "__main__":
    main()