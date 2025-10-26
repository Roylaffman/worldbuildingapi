#!/usr/bin/env python3
"""
Debug tags API in detail
"""

import requests
import json

# Get token first
response = requests.post(
    "http://localhost:8000/api/v1/auth/login/",
    json={"username": "admin", "password": "admin123"}
)

if response.status_code == 200:
    token = response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check tags for world 9
    print("=== WORLD 9 TAGS DETAILED ===")
    response = requests.get("http://localhost:8000/api/v1/worlds/9/tags/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        tags_data = response.json()
        print(f"Raw response: {json.dumps(tags_data, indent=2)}")
        
        # Handle paginated response
        if isinstance(tags_data, dict) and 'results' in tags_data:
            tags = tags_data['results']
            print(f"\nPaginated response - found {len(tags)} tags in results:")
        else:
            tags = tags_data
            print(f"\nDirect response - found {len(tags)} tags:")
        
        for i, tag in enumerate(tags):
            print(f"\nTag {i+1}:")
            print(f"  ID: {tag.get('id')}")
            print(f"  Name: {tag.get('name')}")
            print(f"  Created: {tag.get('created_at')}")
            
            # Test individual tag detail
            tag_name = tag.get('name')
            if tag_name:
                detail_response = requests.get(
                    f"http://localhost:8000/api/v1/worlds/9/tags/{tag_name}/", 
                    headers=headers
                )
                print(f"  Detail API Status: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    tagged_content = detail_data.get('tagged_content', [])
                    print(f"  Tagged content count: {len(tagged_content)}")
    else:
        print(f"Error: {response.text}")
        
    # Also test the frontend API format
    print("\n=== TESTING FRONTEND API CALL ===")
    print("This simulates what the frontend TagsPage component does:")
    
    try:
        import urllib.parse
        # Test the exact same call the frontend makes
        world_id = 9
        url = f"http://localhost:8000/api/v1/worlds/{world_id}/tags/"
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, list):
                print(f"Direct list with {len(data)} tags")
            elif isinstance(data, dict) and 'results' in data:
                print(f"Paginated response with {len(data['results'])} tags")
            else:
                print("Unexpected response format")
                
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error testing frontend API call: {e}")
        
else:
    print(f"Login failed: {response.status_code} - {response.text}")