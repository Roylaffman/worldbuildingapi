#!/usr/bin/env python3
"""
Debug API endpoints
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
    
    # Check worlds
    print("=== WORLDS ===")
    response = requests.get("http://localhost:8000/api/v1/worlds/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        worlds_data = response.json()
        print(f"Type: {type(worlds_data)}")
        
        # Handle paginated response
        if isinstance(worlds_data, dict) and 'results' in worlds_data:
            worlds = worlds_data['results']
        else:
            worlds = worlds_data
            
        print(f"Found {len(worlds)} worlds:")
        
        # Test with world 9 specifically (has content according to the data)
        test_world = None
        for world in worlds:
            print(f"  - ID: {world['id']}, Title: {world['title']}")
            if world['id'] == 9:
                test_world = world
        
        if test_world:
            world_id = test_world['id']
            print(f"\n  Testing world {world_id} content:")
            
            content_types = ["pages", "essays", "characters", "stories", "images"]
            for content_type in content_types:
                url = f"http://localhost:8000/api/v1/worlds/{world_id}/{content_type}/"
                resp = requests.get(url, headers=headers)
                print(f"    {content_type}: {resp.status_code}")
                if resp.status_code == 200:
                    content_data = resp.json()
                    # Handle paginated response
                    if isinstance(content_data, dict) and 'results' in content_data:
                        content = content_data['results']
                    else:
                        content = content_data
                    print(f"      Found {len(content)} items")
                    if content:
                        print(f"      First item: {content[0].get('title', 'No title')}")
            
            # Test tags for this world
            url = f"http://localhost:8000/api/v1/worlds/{world_id}/tags/"
            resp = requests.get(url, headers=headers)
            print(f"    tags: {resp.status_code}")
            if resp.status_code == 200:
                tags = resp.json()
                print(f"      Found {len(tags)} tags")
            
            # Test links for this world
            url = f"http://localhost:8000/api/v1/worlds/{world_id}/links/"
            resp = requests.get(url, headers=headers)
            print(f"    links: {resp.status_code}")
            if resp.status_code == 200:
                links = resp.json()
                print(f"      Found {len(links)} links")
            
            print()
    else:
        print(f"Error: {response.text}")
else:
    print(f"Login failed: {response.status_code} - {response.text}")