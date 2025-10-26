#!/usr/bin/env python3
"""
Quick API test script to verify backend endpoints work before building frontend.
Run this to make sure your API is ready for frontend development.
"""
import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.world_id = None
        
    def register_user(self):
        """Register a test user"""
        print("🔐 Registering test user...")
        response = self.session.post(f"{BASE_URL}/auth/register/", json=TEST_USER)
        if response.status_code in [201, 400]:  # 400 if user already exists
            print("✅ User registration OK")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    
    def login(self):
        """Login and get JWT token"""
        print("🔑 Logging in...")
        response = self.session.post(f"{BASE_URL}/auth/login/", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def create_world(self):
        """Create a test world"""
        print("🌍 Creating test world...")
        world_data = {
            "title": f"Test World {datetime.now().strftime('%H:%M:%S')}",
            "description": "A test world for API validation",
            "is_public": True
        }
        
        response = self.session.post(f"{BASE_URL}/worlds/", json=world_data)
        if response.status_code == 201:
            data = response.json()
            self.world_id = data["id"]
            print(f"✅ World created with ID: {self.world_id}")
            return True
        else:
            print(f"❌ World creation failed: {response.status_code} - {response.text}")
            return False
    
    def create_page(self):
        """Create a test page"""
        print("📄 Creating test page...")
        page_data = {
            "title": "Test Page",
            "content": "This is a test page to verify the API works correctly.",
            "summary": "A simple test page"
        }
        
        response = self.session.post(f"{BASE_URL}/worlds/{self.world_id}/pages/", json=page_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Page created with ID: {data['id']}")
            return data["id"]
        else:
            print(f"❌ Page creation failed: {response.status_code} - {response.text}")
            return None
    
    def create_character(self):
        """Create a test character"""
        print("👤 Creating test character...")
        character_data = {
            "title": "Test Character Profile",
            "content": "A brave adventurer from the northern lands.",
            "full_name": "Aria Stormwind",
            "age": "25",
            "species": "Human",
            "occupation": "Warrior",
            "location": "Northern Kingdoms",
            "personality_traits": ["brave", "loyal", "quick-tempered"],
            "physical_description": "Tall with auburn hair and green eyes",
            "background": "Born in a small village, trained as a warrior",
            "relationships": {"mentor": "Master Gareth", "friend": "Finn the Bard"}
        }
        
        response = self.session.post(f"{BASE_URL}/worlds/{self.world_id}/characters/", json=character_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Character created with ID: {data['id']}")
            return data["id"]
        else:
            print(f"❌ Character creation failed: {response.status_code} - {response.text}")
            return None
    
    def add_tags(self, content_type, content_id):
        """Add tags to content"""
        print(f"🏷️  Adding tags to {content_type}...")
        tag_data = {"tag_names": ["fantasy", "adventure", "test"]}
        
        response = self.session.post(
            f"{BASE_URL}/worlds/{self.world_id}/{content_type}/{content_id}/add-tags/", 
            json=tag_data
        )
        if response.status_code == 200:
            print("✅ Tags added successfully")
            return True
        else:
            print(f"❌ Tag addition failed: {response.status_code} - {response.text}")
            return False
    
    def get_world_timeline(self):
        """Get world timeline"""
        print("📅 Getting world timeline...")
        response = self.session.get(f"{BASE_URL}/worlds/{self.world_id}/timeline/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Timeline retrieved with {len(data.get('timeline', []))} entries")
            return True
        else:
            print(f"❌ Timeline retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def run_full_test(self):
        """Run complete API test suite"""
        print("🚀 Starting API Test Suite")
        print("=" * 50)
        
        # Test authentication flow
        if not self.register_user():
            return False
        if not self.login():
            return False
            
        # Test world creation
        if not self.create_world():
            return False
            
        # Test content creation
        page_id = self.create_page()
        if not page_id:
            return False
            
        character_id = self.create_character()
        if not character_id:
            return False
            
        # Test tagging
        if not self.add_tags("pages", page_id):
            return False
        if not self.add_tags("characters", character_id):
            return False
            
        # Test timeline
        if not self.get_world_timeline():
            return False
            
        print("=" * 50)
        print("🎉 All API tests passed! Your backend is ready for frontend development.")
        print(f"📝 Test world ID: {self.world_id}")
        print(f"🔗 API Base URL: {BASE_URL}")
        return True

def main():
    print("🧪 Collaborative Worldbuilding API Tester")
    print("This script will test your API endpoints before frontend development.\n")
    
    # Check if Django server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/")
        print("✅ Django server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running!")
        print("Please start it with: python manage.py runserver")
        return
    
    tester = APITester()
    success = tester.run_full_test()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Your API is working correctly")
        print("2. You can now start building your frontend")
        print("3. Use the test world created above for initial development")
        print("4. Key endpoints to implement in frontend:")
        print("   - POST /api/v1/register/ (user registration)")
        print("   - POST /api/v1/token/ (login)")
        print("   - GET/POST /api/v1/worlds/ (world management)")
        print("   - POST /api/v1/worlds/{id}/pages/ (content creation)")
        print("   - GET /api/v1/worlds/{id}/timeline/ (content viewing)")

if __name__ == "__main__":
    main()