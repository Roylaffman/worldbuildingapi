// Frontend Tagging & Linking Test Script
// Run this in browser console on http://localhost:3000

console.log('🏷️ Starting Frontend Tagging & Linking Tests...');

// Test configuration
const TEST_CONFIG = {
  baseURL: 'http://localhost:8000/api/v1',
  frontendURL: 'http://localhost:3000',
  testUser: {
    username: 'admin',
    password: 'admin123'
  },
  testWorldId: 9, // Adjust based on available worlds
};

// Helper function to make authenticated API calls
async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };
  
  const response = await fetch(`${TEST_CONFIG.baseURL}${endpoint}`, {
    ...defaultOptions,
    ...options,
    headers: { ...defaultOptions.headers, ...options.headers }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.message || response.statusText}`);
  }
  
  return response.json();
}

// Test Phase 1: Authentication and Setup
async function testAuthentication() {
  console.log('📋 Phase 1: Testing Authentication...');
  
  try {
    // Check if already logged in
    const token = localStorage.getItem('token');
    if (token) {
      console.log('✅ Already authenticated with token');
      return true;
    }
    
    // Login
    const loginResponse = await fetch(`${TEST_CONFIG.baseURL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(TEST_CONFIG.testUser)
    });
    
    if (loginResponse.ok) {
      const data = await loginResponse.json();
      localStorage.setItem('token', data.access);
      console.log('✅ Login successful');
      return true;
    } else {
      console.error('❌ Login failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Authentication error:', error);
    return false;
  }
}

// Test Phase 2: Check Available Data
async function testDataAvailability() {
  console.log('📋 Phase 2: Checking Available Data...');
  
  try {
    // Check worlds
    const worlds = await apiCall('/worlds/');
    console.log(`✅ Found ${worlds.length} worlds:`, worlds.map(w => `${w.id}: ${w.title}`));
    
    if (worlds.length === 0) {
      console.warn('⚠️ No worlds found - create a world first');
      return false;
    }
    
    // Use first available world or specified test world
    const testWorld = worlds.find(w => w.id === TEST_CONFIG.testWorldId) || worlds[0];
    TEST_CONFIG.testWorldId = testWorld.id;
    console.log(`🌍 Using world: ${testWorld.id} - ${testWorld.title}`);
    
    // Check content in world
    const contentTypes = ['pages', 'essays', 'characters', 'stories', 'images'];
    const contentCounts = {};
    
    for (const type of contentTypes) {
      try {
        const content = await apiCall(`/worlds/${testWorld.id}/${type}/`);
        contentCounts[type] = content.length;
        console.log(`📄 ${type}: ${content.length} items`);
      } catch (error) {
        console.warn(`⚠️ Could not fetch ${type}:`, error.message);
        contentCounts[type] = 0;
      }
    }
    
    // Check if we have any content to work with
    const totalContent = Object.values(contentCounts).reduce((sum, count) => sum + count, 0);
    if (totalContent === 0) {
      console.warn('⚠️ No content found - create some content first');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('❌ Data availability check failed:', error);
    return false;
  }
}

// Test Phase 3: TagManager Component Test
async function testTagManagerComponent() {
  console.log('📋 Phase 3: Testing TagManager Component...');
  
  try {
    // Check if we're on a content page
    const currentPath = window.location.pathname;
    const contentPageMatch = currentPath.match(/\/worlds\/(\d+)\/content\/(\w+)\/(\d+)/);
    
    if (!contentPageMatch) {
      console.log('ℹ️ Not on content page - navigate to content page first');
      console.log('📍 Example: /worlds/9/content/essay/1');
      return false;
    }
    
    const [, worldId, contentType, contentId] = contentPageMatch;
    console.log(`📄 Testing on ${contentType} ${contentId} in world ${worldId}`);
    
    // Check if TagManager is present
    const manageTagsButton = document.querySelector('button:contains("Manage Tags")') || 
                            Array.from(document.querySelectorAll('button')).find(btn => 
                              btn.textContent.includes('Manage Tags'));
    
    if (!manageTagsButton) {
      console.error('❌ "Manage Tags" button not found');
      return false;
    }
    
    console.log('✅ "Manage Tags" button found');
    
    // Click to open TagManager
    manageTagsButton.click();
    
    // Wait a bit for component to load
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Check if TagManager opened
    const addTagButton = Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.includes('Add Tag'));
    
    if (addTagButton) {
      console.log('✅ TagManager component loaded successfully');
      return true;
    } else {
      console.error('❌ TagManager component did not load');
      return false;
    }
    
  } catch (error) {
    console.error('❌ TagManager component test failed:', error);
    return false;
  }
}

// Test Phase 4: Tag Addition Test
async function testTagAddition() {
  console.log('📋 Phase 4: Testing Tag Addition...');
  
  try {
    // Find and click "Add Tag" button
    const addTagButton = Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.includes('Add Tag'));
    
    if (!addTagButton) {
      console.error('❌ "Add Tag" button not found - open TagManager first');
      return false;
    }
    
    addTagButton.click();
    
    // Wait for input to appear
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Find tag input field
    const tagInput = document.querySelector('input[placeholder*="tag"]') || 
                    document.querySelector('input[placeholder*="Tag"]');
    
    if (!tagInput) {
      console.error('❌ Tag input field not found');
      return false;
    }
    
    console.log('✅ Tag input field found');
    
    // Add a test tag
    const testTagName = `frontend-test-${Date.now()}`;
    tagInput.value = testTagName;
    tagInput.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Find and click Add button
    const addButton = Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.trim() === 'Add');
    
    if (!addButton) {
      console.error('❌ "Add" button not found');
      return false;
    }
    
    console.log(`🏷️ Adding test tag: ${testTagName}`);
    addButton.click();
    
    // Wait for API call to complete
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check if tag was added (look for tag in the page)
    const tagElements = document.querySelectorAll('[class*="tag"], [class*="Tag"]');
    const tagAdded = Array.from(tagElements).some(el => 
      el.textContent.includes(testTagName));
    
    if (tagAdded) {
      console.log('✅ Tag added successfully');
      return true;
    } else {
      console.warn('⚠️ Tag may not have been added - check manually');
      return false;
    }
    
  } catch (error) {
    console.error('❌ Tag addition test failed:', error);
    return false;
  }
}

// Test Phase 5: ContentLinker Component Test
async function testContentLinkerComponent() {
  console.log('📋 Phase 5: Testing ContentLinker Component...');
  
  try {
    // Find "Manage Links" button
    const manageLinksButton = Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.includes('Manage Links'));
    
    if (!manageLinksButton) {
      console.error('❌ "Manage Links" button not found');
      return false;
    }
    
    console.log('✅ "Manage Links" button found');
    
    // Click to open ContentLinker
    manageLinksButton.click();
    
    // Wait for component to load
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Check if ContentLinker opened
    const linkButton = Array.from(document.querySelectorAll('button')).find(btn => 
      btn.textContent.includes('Link to Other Content'));
    
    if (linkButton) {
      console.log('✅ ContentLinker component loaded successfully');
      return true;
    } else {
      console.error('❌ ContentLinker component did not load');
      return false;
    }
    
  } catch (error) {
    console.error('❌ ContentLinker component test failed:', error);
    return false;
  }
}

// Test Phase 6: Navigation Tests
async function testTagsPageNavigation() {
  console.log('📋 Phase 6: Testing TagsPage Navigation...');
  
  try {
    const currentPath = window.location.pathname;
    const worldMatch = currentPath.match(/\/worlds\/(\d+)/);
    
    if (!worldMatch) {
      console.error('❌ Not in a world context');
      return false;
    }
    
    const worldId = worldMatch[1];
    const tagsPageUrl = `/worlds/${worldId}/tags`;
    
    console.log(`🔗 Navigating to: ${tagsPageUrl}`);
    
    // Navigate to tags page
    window.location.href = tagsPageUrl;
    
    // Wait for navigation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check if we're on tags page
    if (window.location.pathname.includes('/tags')) {
      console.log('✅ Successfully navigated to TagsPage');
      return true;
    } else {
      console.error('❌ Navigation to TagsPage failed');
      return false;
    }
    
  } catch (error) {
    console.error('❌ TagsPage navigation test failed:', error);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting Comprehensive Frontend Tagging & Linking Tests');
  console.log('=' .repeat(60));
  
  const results = {
    authentication: false,
    dataAvailability: false,
    tagManagerComponent: false,
    tagAddition: false,
    contentLinkerComponent: false,
    tagsPageNavigation: false
  };
  
  // Run tests sequentially
  results.authentication = await testAuthentication();
  if (!results.authentication) {
    console.error('🛑 Authentication failed - stopping tests');
    return results;
  }
  
  results.dataAvailability = await testDataAvailability();
  if (!results.dataAvailability) {
    console.warn('⚠️ Limited data available - some tests may fail');
  }
  
  // Component tests (only if on content page)
  if (window.location.pathname.includes('/content/')) {
    results.tagManagerComponent = await testTagManagerComponent();
    if (results.tagManagerComponent) {
      results.tagAddition = await testTagAddition();
    }
    results.contentLinkerComponent = await testContentLinkerComponent();
  } else {
    console.log('ℹ️ Skipping component tests - navigate to content page first');
  }
  
  // Navigation test
  results.tagsPageNavigation = await testTagsPageNavigation();
  
  // Summary
  console.log('=' .repeat(60));
  console.log('📊 TEST RESULTS SUMMARY:');
  Object.entries(results).forEach(([test, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
  });
  
  const passedCount = Object.values(results).filter(Boolean).length;
  const totalCount = Object.keys(results).length;
  console.log(`\n🎯 Overall: ${passedCount}/${totalCount} tests passed`);
  
  if (passedCount === totalCount) {
    console.log('🎉 All tests passed! Tagging & Linking system is working correctly.');
  } else {
    console.log('⚠️ Some tests failed. Check the issues above.');
  }
  
  return results;
}

// Instructions for manual testing
console.log('📋 MANUAL TESTING INSTRUCTIONS:');
console.log('1. Make sure you are logged in to the application');
console.log('2. Navigate to a content page (e.g., /worlds/9/content/essay/1)');
console.log('3. Run: runAllTests()');
console.log('4. For TagsPage testing, the script will navigate automatically');
console.log('');
console.log('🚀 Ready to test! Run: runAllTests()');

// Export functions for manual testing
window.testTaggingSystem = {
  runAllTests,
  testAuthentication,
  testDataAvailability,
  testTagManagerComponent,
  testTagAddition,
  testContentLinkerComponent,
  testTagsPageNavigation
};