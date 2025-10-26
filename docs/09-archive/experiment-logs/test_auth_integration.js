// Comprehensive authentication integration test
const API_BASE_URL = 'http://localhost:8000/api/v1';

async function runAuthIntegrationTests() {
  console.log('🚀 Starting comprehensive authentication integration tests...\n');

  let testResults = {
    passed: 0,
    failed: 0,
    tests: []
  };

  // Test 1: User Registration
  try {
    console.log('📝 Test 1: User Registration');
    const testUser = {
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'testpassword123',
      password_confirm: 'testpassword123',
      first_name: 'Test',
      last_name: 'User',
      bio: 'This is a test user account'
    };

    const regResponse = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testUser)
    });

    const regData = await regResponse.json();

    if (regResponse.ok && regData.tokens && regData.user) {
      console.log('✅ Registration successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Registration', status: 'PASS' });

      // Store for later tests
      global.testUser = testUser;
      global.testTokens = regData.tokens;
    } else {
      throw new Error('Registration failed');
    }
  } catch (error) {
    console.log('❌ Registration failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Registration', status: 'FAIL', error: error.message });
  }

  // Test 2: Login with new user
  try {
    console.log('\n🔐 Test 2: Login');
    const loginResponse = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: global.testUser.username,
        password: global.testUser.password
      })
    });

    const loginData = await loginResponse.json();

    if (loginResponse.ok && loginData.access && loginData.refresh && loginData.user) {
      console.log('✅ Login successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Login', status: 'PASS' });
      global.loginTokens = loginData;
    } else {
      throw new Error('Login failed');
    }
  } catch (error) {
    console.log('❌ Login failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Login', status: 'FAIL', error: error.message });
  }

  // Test 3: Token verification
  try {
    console.log('\n🔍 Test 3: Token Verification');
    const verifyResponse = await fetch(`${API_BASE_URL}/auth/verify/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${global.loginTokens.access}`
      }
    });

    const verifyData = await verifyResponse.json();

    if (verifyResponse.ok && verifyData.valid === true) {
      console.log('✅ Token verification successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Token Verification', status: 'PASS' });
    } else {
      throw new Error('Token verification failed');
    }
  } catch (error) {
    console.log('❌ Token verification failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Token Verification', status: 'FAIL', error: error.message });
  }

  // Test 4: User info retrieval
  try {
    console.log('\n👤 Test 4: User Info Retrieval');
    const userResponse = await fetch(`${API_BASE_URL}/auth/user/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${global.loginTokens.access}`
      }
    });

    const userData = await userResponse.json();

    if (userResponse.ok && userData.user && userData.user.profile) {
      console.log('✅ User info retrieval successful');
      testResults.passed++;
      testResults.tests.push({ name: 'User Info Retrieval', status: 'PASS' });
    } else {
      throw new Error('User info retrieval failed');
    }
  } catch (error) {
    console.log('❌ User info retrieval failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'User Info Retrieval', status: 'FAIL', error: error.message });
  }

  // Test 5: Token refresh
  try {
    console.log('\n🔄 Test 5: Token Refresh');
    const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: global.loginTokens.refresh })
    });

    const refreshData = await refreshResponse.json();

    if (refreshResponse.ok && refreshData.access) {
      console.log('✅ Token refresh successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Token Refresh', status: 'PASS' });
      global.newAccessToken = refreshData.access;
    } else {
      throw new Error('Token refresh failed');
    }
  } catch (error) {
    console.log('❌ Token refresh failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Token Refresh', status: 'FAIL', error: error.message });
  }

  // Test 6: Using refreshed token
  try {
    console.log('\n🔑 Test 6: Using Refreshed Token');
    const testResponse = await fetch(`${API_BASE_URL}/auth/user/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${global.newAccessToken}`
      }
    });

    if (testResponse.ok) {
      console.log('✅ Refreshed token works correctly');
      testResults.passed++;
      testResults.tests.push({ name: 'Refreshed Token Usage', status: 'PASS' });
    } else {
      throw new Error('Refreshed token failed');
    }
  } catch (error) {
    console.log('❌ Refreshed token failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Refreshed Token Usage', status: 'FAIL', error: error.message });
  }

  // Test 7: Protected endpoint access
  try {
    console.log('\n🌍 Test 7: Protected Endpoint Access (Worlds List)');
    const worldsResponse = await fetch(`${API_BASE_URL}/worlds/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${global.loginTokens.access}`
      }
    });

    const worldsData = await worldsResponse.json();

    if (worldsResponse.ok && worldsData.results) {
      console.log('✅ Protected endpoint access successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Protected Endpoint Access', status: 'PASS' });
    } else {
      throw new Error('Protected endpoint access failed');
    }
  } catch (error) {
    console.log('❌ Protected endpoint access failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Protected Endpoint Access', status: 'FAIL', error: error.message });
  }

  // Test 8: Logout
  try {
    console.log('\n🚪 Test 8: Logout');
    const logoutResponse = await fetch(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${global.loginTokens.access}`
      },
      body: JSON.stringify({ refresh_token: global.loginTokens.refresh })
    });

    if (logoutResponse.ok) {
      console.log('✅ Logout successful');
      testResults.passed++;
      testResults.tests.push({ name: 'Logout', status: 'PASS' });
    } else {
      throw new Error('Logout failed');
    }
  } catch (error) {
    console.log('❌ Logout failed:', error.message);
    testResults.failed++;
    testResults.tests.push({ name: 'Logout', status: 'FAIL', error: error.message });
  }

  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${testResults.passed + testResults.failed}`);
  console.log(`Passed: ${testResults.passed}`);
  console.log(`Failed: ${testResults.failed}`);
  console.log(`Success Rate: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);

  console.log('\n📋 DETAILED RESULTS:');
  testResults.tests.forEach((test, index) => {
    const status = test.status === 'PASS' ? '✅' : '❌';
    console.log(`${index + 1}. ${status} ${test.name}`);
    if (test.error) {
      console.log(`   Error: ${test.error}`);
    }
  });

  if (testResults.failed === 0) {
    console.log('\n🎉 All authentication tests passed! API integration is working correctly.');
  } else {
    console.log(`\n⚠️  ${testResults.failed} test(s) failed. Please check the errors above.`);
  }
}

runAuthIntegrationTests();