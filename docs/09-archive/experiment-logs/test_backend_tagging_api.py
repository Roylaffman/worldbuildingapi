#!/usr/bin/env python3
"""
Backend API Test Script for Tagging & Linking System
Tests the Django REST API endpoints directly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

class TaggingAPITester:
    def __init__(self):
        self.token = None
        self.test_world_id = None
        self.test_content = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Test authentication and get token"""
        self.log("Testing authentication...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access")
                self.log("✅ Authentication successful")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", "ERROR")
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_worlds_list(self):
        """Test worlds list endpoint"""
        self.log("Testing worlds list...")
        
        try:
            response = requests.get(f"{BASE_URL}/worlds/", headers=self.get_headers())
            
            if response.status_code == 200:
                worlds_data = response.json()
                # Handle paginated response
                if isinstance(worlds_data, dict) and 'results' in worlds_data:
                    worlds = worlds_data['results']
                else:
                    worlds = worlds_data
                    
                self.log(f"✅ Found {len(worlds)} worlds")
                
                if worlds:
                    # Use world 9 which has content
                    target_world = next((w for w in worlds if w["id"] == 9), worlds[0])
                    self.test_world_id = target_world["id"]
                    self.log(f"📍 Using world {self.test_world_id}: {target_world['title']}")
                    return True
                else:
                    self.log("⚠️ No worlds found - create a world first", "WARN")
                    return False
            else:
                self.log(f"❌ Worlds list failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Worlds list error: {e}", "ERROR")
            return False
    
    def test_content_availability(self):
        """Test available content in the world"""
        self.log("Testing content availability...")
        
        content_types = ["pages", "essays", "characters", "stories", "images"]
        
        for content_type in content_types:
            try:
                response = requests.get(
                    f"{BASE_URL}/worlds/{self.test_world_id}/{content_type}/",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    content_data = response.json()
                    # Handle paginated response
                    if isinstance(content_data, dict) and 'results' in content_data:
                        content = content_data['results']
                    else:
                        content = content_data
                        
                    self.log(f"📄 {content_type}: {len(content)} items")
                    
                    if content:
                        self.test_content[content_type] = content[0]
                        
                else:
                    self.log(f"⚠️ Could not fetch {content_type}: {response.status_code}", "WARN")
                    
            except Exception as e:
                self.log(f"❌ Error fetching {content_type}: {e}", "ERROR")
        
        total_content = len(self.test_content)
        if total_content > 0:
            self.log(f"✅ Found content in {total_content} content types")
            return True
        else:
            self.log("⚠️ No content found - create some content first", "WARN")
            return False
    
    def test_tags_api(self):
        """Test tags API endpoints"""
        self.log("Testing tags API...")
        
        try:
            # Test tags list
            response = requests.get(
                f"{BASE_URL}/worlds/{self.test_world_id}/tags/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                tags_data = response.json()
                # Handle paginated response
                if isinstance(tags_data, dict) and 'results' in tags_data:
                    tags = tags_data['results']
                else:
                    tags = tags_data
                    
                self.log(f"✅ Tags list: {len(tags)} tags found")
                
                # Test individual tag if any exist
                if tags:
                    tag_name = tags[0]["name"]
                    response = requests.get(
                        f"{BASE_URL}/worlds/{self.test_world_id}/tags/{tag_name}/",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        tag_detail = response.json()
                        self.log(f"✅ Tag detail for '{tag_name}': {len(tag_detail.get('tagged_content', []))} tagged items")
                    else:
                        self.log(f"⚠️ Tag detail failed: {response.status_code}", "WARN")
                
                return True
            else:
                self.log(f"❌ Tags list failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Tags API error: {e}", "ERROR")
            return False
    
    def test_links_api(self):
        """Test links API endpoints"""
        self.log("Testing links API...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/worlds/{self.test_world_id}/links/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                links_data = response.json()
                # Handle paginated response
                if isinstance(links_data, dict) and 'results' in links_data:
                    links = links_data['results']
                else:
                    links = links_data
                    
                self.log(f"✅ Links list: {len(links)} links found")
                return True
            else:
                self.log(f"❌ Links list failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Links API error: {e}", "ERROR")
            return False
    
    def test_add_tags(self):
        """Test adding tags to content"""
        self.log("Testing tag addition...")
        
        if not self.test_content:
            self.log("⚠️ No content available for tag testing", "WARN")
            return False
        
        # Use first available content type
        content_type, content_item = next(iter(self.test_content.items()))
        content_id = content_item["id"]
        
        test_tag = f"api-test-tag-{datetime.now().strftime('%H%M%S')}"
        
        try:
            response = requests.post(
                f"{BASE_URL}/worlds/{self.test_world_id}/{content_type}/{content_id}/add-tags/",
                json={"tags": [test_tag]},
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                self.log(f"✅ Tag '{test_tag}' added to {content_type} {content_id}")
                return True
            else:
                self.log(f"❌ Tag addition failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Tag addition error: {e}", "ERROR")
            return False
    
    def test_add_links(self):
        """Test adding links between content"""
        self.log("Testing link creation...")
        
        if len(self.test_content) < 2:
            self.log("⚠️ Need at least 2 content types for link testing", "WARN")
            return False
        
        # Get two different content items
        content_items = list(self.test_content.items())
        from_type, from_item = content_items[0]
        to_type, to_item = content_items[1]
        
        try:
            response = requests.post(
                f"{BASE_URL}/worlds/{self.test_world_id}/{from_type}/{from_item['id']}/add-links/",
                json={"links": [{"content_type": to_type.rstrip('s'), "content_id": to_item["id"]}]},
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                self.log(f"✅ Link created: {from_type} {from_item['id']} → {to_type} {to_item['id']}")
                return True
            else:
                self.log(f"❌ Link creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Link creation error: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("🚀 Starting Backend API Tests for Tagging & Linking System")
        self.log("=" * 60)
        
        results = {}
        
        # Authentication test
        results["authentication"] = self.authenticate()
        if not results["authentication"]:
            self.log("🛑 Authentication failed - stopping tests", "ERROR")
            return results
        
        # Basic API tests
        results["worlds_list"] = self.test_worlds_list()
        results["content_availability"] = self.test_content_availability()
        results["tags_api"] = self.test_tags_api()
        results["links_api"] = self.test_links_api()
        
        # Functional tests (only if we have content)
        if self.test_content:
            results["add_tags"] = self.test_add_tags()
            results["add_links"] = self.test_add_links()
        else:
            results["add_tags"] = False
            results["add_links"] = False
        
        # Summary
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY:")
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"{status}: {test_name}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        self.log(f"\n🎯 Overall: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            self.log("🎉 All tests passed! Backend API is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Check the issues above.")
        
        return results

def main():
    """Main function"""
    tester = TaggingAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()