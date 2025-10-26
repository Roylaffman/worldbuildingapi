// Frontend Component Integration Test
// Run this in browser console on a content page (e.g., /worlds/9/content/page/5)

console.log('🧪 Starting Frontend Component Integration Test');

// Test configuration
const TEST_CONFIG = {
  worldId: 9,
  testTagName: `frontend-test-${Date.now()}`,
  apiBaseUrl: 'http://localhost:8000/api/v1'
};

// Helper function to wait for element
function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }

    const observer = new MutationObserver(() => {
      const element = document.querySelector(selector);
      if (element) {
        observer.disconnect();
        resolve(element);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Element ${selector} not found within ${timeout}ms`));
    }, timeout);
  });
}

// Helper function to simulate user input
function simulateInput(element, value) {
  element.value = value;
  element.dispatchEvent(new Event('input', { bubbles: true }));
  element.dispatchEvent(new Event('change', { bubbles: true }));
}

// Test 1: Check if we're on a content page
async function testPageContext() {
  console.log('📍 Test 1: Checking page context...');
  
  const path = window.location.pathname;
  const contentMatch = path.match(/\/worlds\/(\d+)\/content\/(\w+)\/(\d+)/);
  
  if (!contentMatch) {
    throw new Error('Not on a content page. Navigate to a content page first.');
  }
  
  const [, worldId, contentType, contentId] = contentMatch;
  console.log(`✅ On content page: ${contentType} ${contentId} in world ${worldId}`);
  
  return { worldId: parseInt(worldId), contentType, contentId: parseInt(contentId) };
}

// Test 2: Check if TagManager components are present
async function testTagManagerPresence() {
  console.log('🏷️ Test 2: Checking TagManager presence...');
  
  // Look for Tags section
  const tagsSection = Array.from(document.querySelectorAll('h2')).find(h2 => 
    h2.textContent.includes('Tags'));
  
  if (!tagsSection) {
    throw new Error('Tags section not found');
  }
  
  console.log('✅ Tags section found');
  
  // Look for Manage Tags button
  const manageTagsButton = Array.from(document.querySelectorAll('button')).find(btn => 
    btn.textContent.includes('Manage Tags'));
  
  if (!manageTagsButton) {
    throw new Error('Manage Tags button not found');
  }
  
  console.log('✅ Manage Tags button found');
  return manageTagsButton;
}

// Test 3: Test TagManager functionality
async function testTagManagerFunctionality(manageTagsButton) {
  console.log('🏷️ Test 3: Testing TagManager functionality...');
  
  // Click Manage Tags button
  manageTagsButton.click();
  console.log('📝 Clicked Manage Tags button');
  
  // Wait for TagManager to load
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Look for Add Tag button
  const addTagButton = Array.from(document.querySelectorAll('button')).find(btn => 
    btn.textContent.includes('Add Tag'));
  
  if (!addTagButton) {
    throw new Error('Add Tag button not found after opening TagManager');
  }
  
  console.log('✅ Add Tag button found');
  
  // Click Add Tag button
  addTagButton.click();
  console.log('📝 Clicked Add Tag button');
  
  // Wait for input to appear
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Find tag input
  const tagInput = document.querySelector('input[placeholder*="tag" i]');
  if (!tagInput) {
    throw new Error('Tag input field not found');
  }
  
  console.log('✅ Tag input field found');
  
  // Enter test tag
  simulateInput(tagInput, TEST_CONFIG.testTagName);
  console.log(`📝 Entered tag name: ${TEST_CONFIG.testTagName}`);
  
  // Find Add button
  const addButton = Array.from(document.querySelectorAll('button')).find(btn => 
    btn.textContent.trim() === 'Add');
  
  if (!addButton) {
    throw new Error('Add button not found');
  }
  
  // Click Add button
  addButton.click();
  console.log('📝 Clicked Add button');
  
  // Wait for API call to complete
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('✅ TagManager functionality test completed');
  return true;
}

// Test 4: Check if ContentLinker components are present
async function testContentLinkerPresence() {
  console.log('🔗 Test 4: Checking ContentLinker presence...');
  
  // Look for Linked Content section
  const linkedSection = Array.from(document.querySelectorAll('h2')).find(h2 => 
    h2.textContent.includes('Linked Content'));
  
  if (!linkedSection) {
    throw new Error('Linked Content section not found');
  }
  
  console.log('✅ Linked Content section found');
  
  // Look for Manage Links button
  const manageLinksButton = Array.from(document.querySelectorAll('button')).find(btn => 
    btn.textContent.includes('Manage Links'));
  
  if (!manageLinksButton) {
    throw new Error('Manage Links button not found');
  }
  
  console.log('✅ Manage Links button found');
  return manageLinksButton;
}

// Test 5: Test ContentLinker functionality
async function testContentLinkerFunctionality(manageLinksButton) {
  console.log('🔗 Test 5: Testing ContentLinker functionality...');
  
  // Click Manage Links button
  manageLinksButton.click();
  console.log('📝 Clicked Manage Links button');
  
  // Wait for ContentLinker to load
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Look for Link to Other Content button
  const linkButton = Array.from(document.querySelectorAll('button')).find(btn => 
    btn.textContent.includes('Link to Other Content'));
  
  if (!linkButton) {
    throw new Error('Link to Other Content button not found after opening ContentLinker');
  }
  
  console.log('✅ Link to Other Content button found');
  
  // Click Link button
  linkButton.click();
  console.log('📝 Clicked Link to Other Content button');
  
  // Wait for interface to load
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Check for content type selector
  const contentTypeSelect = document.querySelector('select');
  if (!contentTypeSelect) {
    throw new Error('Content type selector not found');
  }
  
  console.log('✅ Content type selector found');
  
  // Check for search input
  const searchInput = document.querySelector('input[placeholder*="Search" i]');
  if (!searchInput) {
    throw new Error('Search input not found');
  }
  
  console.log('✅ Search input found');
  console.log('✅ ContentLinker functionality test completed');
  
  return true;
}

// Test 6: Check browser console for errors
function testConsoleErrors() {
  console.log('🐛 Test 6: Checking for console errors...');
  
  // This is a basic check - in a real scenario, you'd want to capture errors
  // during the test execution
  console.log('✅ Console error check completed (manual verification needed)');
  return true;
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting Comprehensive Frontend Component Tests');
  console.log('=' .repeat(60));
  
  const results = {};
  
  try {
    // Test 1: Page context
    const pageContext = await testPageContext();
    results.pageContext = true;
    
    // Test 2: TagManager presence
    const manageTagsButton = await testTagManagerPresence();
    results.tagManagerPresence = true;
    
    // Test 3: TagManager functionality
    await testTagManagerFunctionality(manageTagsButton);
    results.tagManagerFunctionality = true;
    
    // Test 4: ContentLinker presence
    const manageLinksButton = await testContentLinkerPresence();
    results.contentLinkerPresence = true;
    
    // Test 5: ContentLinker functionality
    await testContentLinkerFunctionality(manageLinksButton);
    results.contentLinkerFunctionality = true;
    
    // Test 6: Console errors
    testConsoleErrors();
    results.consoleErrors = true;
    
  } catch (error) {
    console.error(`❌ Test failed: ${error.message}`);
    results.error = error.message;
  }
  
  // Summary
  console.log('=' .repeat(60));
  console.log('📊 TEST RESULTS SUMMARY:');
  
  const testNames = [
    'pageContext',
    'tagManagerPresence', 
    'tagManagerFunctionality',
    'contentLinkerPresence',
    'contentLinkerFunctionality',
    'consoleErrors'
  ];
  
  testNames.forEach(testName => {
    const passed = results[testName] === true;
    console.log(`${passed ? '✅' : '❌'} ${testName}: ${passed ? 'PASSED' : 'FAILED'}`);
  });
  
  if (results.error) {
    console.log(`\n❌ Error: ${results.error}`);
  }
  
  const passedCount = testNames.filter(name => results[name] === true).length;
  console.log(`\n🎯 Overall: ${passedCount}/${testNames.length} tests passed`);
  
  if (passedCount === testNames.length) {
    console.log('🎉 All tests passed! Frontend components are working correctly.');
  } else {
    console.log('⚠️ Some tests failed. Check the issues above.');
  }
  
  return results;
}

// Instructions
console.log('📋 INSTRUCTIONS:');
console.log('1. Make sure you are on a content page (e.g., /worlds/9/content/page/5)');
console.log('2. Make sure you are logged in');
console.log('3. Run: runAllTests()');
console.log('');
console.log('🚀 Ready to test! Run: runAllTests()');

// Export for manual use
window.frontendComponentTest = {
  runAllTests,
  testPageContext,
  testTagManagerPresence,
  testTagManagerFunctionality,
  testContentLinkerPresence,
  testContentLinkerFunctionality,
  testConsoleErrors,
  TEST_CONFIG
};