#!/usr/bin/env python3
"""
Test if the TagsPage fix works
"""

import webbrowser
import time

def main():
    print("🏷️ Testing TagsPage Fix")
    print("=" * 40)
    
    print("✅ Fixed tagsAPI.list to handle paginated responses")
    print("✅ Fixed worldsAPI.list to handle paginated responses") 
    print("✅ Fixed contentAPI.list to handle paginated responses")
    print("✅ Fixed linksAPI.list to handle paginated responses")
    
    print("\n📋 Manual Test Steps:")
    print("1. Make sure frontend server is running (npm run dev)")
    print("2. Navigate to: http://localhost:3000/worlds/9/tags")
    print("3. You should now see 14 tags displayed in a grid")
    print("4. Click on any tag to see tagged content")
    
    tags_url = "http://localhost:3000/worlds/9/tags"
    
    try:
        print(f"\n🌐 Opening: {tags_url}")
        webbrowser.open(tags_url)
        
        print("\n✅ Expected Results:")
        print("- Tags grid with 14 tags should display")
        print("- Tags include: alejandro, alt-history, buddhism, cuneiform, etc.")
        print("- Each tag shows creation date")
        print("- Clicking tag navigates to individual tag page")
        print("- No 'No tags yet' message should appear")
        
        print("\n🐛 If still blank:")
        print("- Check browser console for errors")
        print("- Check Network tab for failed API calls")
        print("- Verify you're logged in")
        print("- Check if frontend server reloaded after API changes")
        
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print(f"Please manually navigate to: {tags_url}")

if __name__ == "__main__":
    main()