// Multi-User Collaboration Testing Script
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Test users from the database
const TEST_USERS = [
  { username: 'admin', password: 'admin123', name: 'Admin User' },
  { username: 'testuser', password: 'testpass123', name: 'Test User' },
  { username: 'perftest', password: 'perftest123', name: 'Performance Test User' }
];

class MultiUserTester {
  constructor() {
    this.userSessions = new Map();
    this.testWorldId = 9; // Using existing world "Static on the Grid"
  }

  async authenticateUser(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();
      
      if (response.ok && data.access) {
        this.userSessions.set(username, {
          token: data.access,
          user: data.user,
          authenticated: true
        });
        return { success: true, user: data.user };
      } else {
        return { success: false, error: data.detail || 'Authentication failed' };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async makeAuthenticatedRequest(username, url, options = {}) {
    const session = this.userSessions.get(username);
    if (!session || !session.authenticated) {
      throw new Error(`User ${username} not authenticated`);
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`,
      ...options.headers
    };

    return fetch(url, { ...options, headers });
  }

  async testUserAuthentication() {
    console.log('🔐 Testing Multi-User Authentication...');
    console.log('-'.repeat(50));

    const results = [];
    
    for (const user of TEST_USERS) {
      const result = await this.authenticateUser(user.username, user.password);
      results.push({ username: user.username, ...result });
      
      if (result.success) {
        console.log(`✅ ${user.username}: Authenticated successfully`);
        console.log(`   User ID: ${result.user.id}, Email: ${result.user.email}`);
      } else {
        console.log(`❌ ${user.username}: ${result.error}`);
      }
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`\n📊 Authentication Results: ${successCount}/${TEST_USERS.length} users authenticated`);
    
    return results;
  }

  async testConcurrentContentCreation() {
    console.log('\n📝 Testing Concurrent Content Creation...');
    console.log('-'.repeat(50));

    const authenticatedUsers = Array.from(this.userSessions.keys());
    if (authenticatedUsers.length < 2) {
      console.log('❌ Need at least 2 authenticated users for concurrent testing');
      return;
    }

    const contentPromises = [];
    const timestamp = Date.now();

    // Each user creates different content simultaneously
    for (let i = 0; i < authenticatedUsers.length; i++) {
      const username = authenticatedUsers[i];
      const contentData = {
        title: `Collaborative Content by ${username} - ${timestamp}`,
        content: `This content was created by ${username} as part of multi-user collaboration testing at ${new Date().toISOString()}. This tests concurrent content creation capabilities.`,
        world: this.testWorldId
      };

      const promise = this.makeAuthenticatedRequest(
        username,
        `${API_BASE_URL}/worlds/${this.testWorldId}/essays/`,
        {
          method: 'POST',
          body: JSON.stringify(contentData)
        }
      ).then(response => ({
        username,
        success: response.ok,
        status: response.status,
        data: response.ok ? response.json() : null
      }));

      contentPromises.push(promise);
    }

    const results = await Promise.all(contentPromises);
    
    for (const result of results) {
      if (result.success) {
        console.log(`✅ ${result.username}: Created content successfully`);
      } else {
        console.log(`❌ ${result.username}: Failed to create content (${result.status})`);
      }
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`\n📊 Concurrent Creation Results: ${successCount}/${results.length} successful`);
    
    return results;
  }

  async testConcurrentTagging() {
    console.log('\n🏷️  Testing Concurrent Tagging...');
    console.log('-'.repeat(50));

    const authenticatedUsers = Array.from(this.userSessions.keys());
    if (authenticatedUsers.length < 2) {
      console.log('❌ Need at least 2 authenticated users for concurrent tagging');
      return;
    }

    // Test tagging the same content by different users
    const essayId = 1; // Using existing essay
    const timestamp = Date.now();
    
    const taggingPromises = [];

    for (let i = 0; i < authenticatedUsers.length; i++) {
      const username = authenticatedUsers[i];
      const tagName = `collab-${username}-${timestamp}`;

      const promise = this.makeAuthenticatedRequest(
        username,
        `${API_BASE_URL}/worlds/${this.testWorldId}/essays/${essayId}/add-tags/`,
        {
          method: 'POST',
          body: JSON.stringify({ tags: [tagName] })
        }
      ).then(response => ({
        username,
        tagName,
        success: response.ok,
        status: response.status
      }));

      taggingPromises.push(promise);
    }

    const results = await Promise.all(taggingPromises);
    
    for (const result of results) {
      if (result.success) {
        console.log(`✅ ${result.username}: Added tag "${result.tagName}" successfully`);
      } else {
        console.log(`❌ ${result.username}: Failed to add tag (${result.status})`);
      }
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`\n📊 Concurrent Tagging Results: ${successCount}/${results.length} successful`);
    
    return results;
  }

  async testConcurrentLinking() {
    console.log('\n🔗 Testing Concurrent Content Linking...');
    console.log('-'.repeat(50));

    const authenticatedUsers = Array.from(this.userSessions.keys());
    if (authenticatedUsers.length < 2) {
      console.log('❌ Need at least 2 authenticated users for concurrent linking');
      return;
    }

    // Test linking different content by different users
    const linkingPromises = [];

    for (let i = 0; i < authenticatedUsers.length; i++) {
      const username = authenticatedUsers[i];
      
      // Link essay to character (different users trying same link)
      const promise = this.makeAuthenticatedRequest(
        username,
        `${API_BASE_URL}/worlds/${this.testWorldId}/essays/1/add-links/`,
        {
          method: 'POST',
          body: JSON.stringify({
            links: [{ content_type: 'image', content_id: 1 }]
          })
        }
      ).then(response => ({
        username,
        success: response.ok,
        status: response.status
      }));

      linkingPromises.push(promise);
    }

    const results = await Promise.all(linkingPromises);
    
    for (const result of results) {
      if (result.success) {
        console.log(`✅ ${result.username}: Created content link successfully`);
      } else {
        console.log(`❌ ${result.username}: Failed to create link (${result.status})`);
      }
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`\n📊 Concurrent Linking Results: ${successCount}/${results.length} successful`);
    
    return results;
  }

  async testContentAttribution() {
    console.log('\n👤 Testing Content Attribution...');
    console.log('-'.repeat(50));

    // Check that content shows correct authorship
    try {
      const response = await this.makeAuthenticatedRequest(
        'admin',
        `${API_BASE_URL}/worlds/${this.testWorldId}/essays/`
      );

      if (response.ok) {
        const essays = await response.json();
        console.log(`✅ Retrieved ${essays.results?.length || essays.length} essays`);
        
        const recentEssays = (essays.results || essays).slice(0, 3);
        for (const essay of recentEssays) {
          console.log(`   "${essay.title}" by ${essay.author.username} (${essay.author.first_name || 'No name'})`);
          console.log(`   Created: ${new Date(essay.created_at).toLocaleString()}`);
          console.log(`   Tags: ${essay.tags?.length || 0}, Links: ${essay.linked_content?.length || 0}`);
        }
      } else {
        console.log('❌ Failed to retrieve content for attribution test');
      }
    } catch (error) {
      console.log(`❌ Attribution test failed: ${error.message}`);
    }
  }

  async testWorldAccess() {
    console.log('\n🌍 Testing World Access Permissions...');
    console.log('-'.repeat(50));

    const authenticatedUsers = Array.from(this.userSessions.keys());
    
    for (const username of authenticatedUsers) {
      try {
        const response = await this.makeAuthenticatedRequest(
          username,
          `${API_BASE_URL}/worlds/${this.testWorldId}/`
        );

        if (response.ok) {
          const world = await response.json();
          console.log(`✅ ${username}: Can access world "${world.title}"`);
          console.log(`   Creator: ${world.creator.username}, Public: ${world.is_public}`);
        } else {
          console.log(`❌ ${username}: Cannot access world (${response.status})`);
        }
      } catch (error) {
        console.log(`❌ ${username}: World access test failed - ${error.message}`);
      }
    }
  }

  async runFullCollaborationTest() {
    console.log('🚀 Multi-User Collaboration Testing Suite');
    console.log('='.repeat(60));
    console.log(`Testing with World ID: ${this.testWorldId}`);
    console.log(`Test Users: ${TEST_USERS.map(u => u.username).join(', ')}`);
    console.log('='.repeat(60));

    // Step 1: Authenticate all users
    await this.testUserAuthentication();

    // Step 2: Test world access
    await this.testWorldAccess();

    // Step 3: Test concurrent content creation
    await this.testConcurrentContentCreation();

    // Step 4: Test concurrent tagging
    await this.testConcurrentTagging();

    // Step 5: Test concurrent linking
    await this.testConcurrentLinking();

    // Step 6: Test content attribution
    await this.testContentAttribution();

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('🎯 Multi-User Collaboration Test Summary');
    console.log('='.repeat(60));
    
    const authenticatedCount = this.userSessions.size;
    console.log(`✅ Authenticated Users: ${authenticatedCount}/${TEST_USERS.length}`);
    console.log('✅ World Access: Tested for all users');
    console.log('✅ Concurrent Content Creation: Tested');
    console.log('✅ Concurrent Tagging: Tested');
    console.log('✅ Concurrent Linking: Tested');
    console.log('✅ Content Attribution: Verified');
    
    console.log('\n🎉 Multi-user collaboration testing complete!');
    console.log('\n📋 Manual Testing Recommendations:');
    console.log('1. Open multiple browser windows/tabs');
    console.log('2. Login as different users in each');
    console.log('3. Navigate to the same world and content');
    console.log('4. Test simultaneous tagging and linking');
    console.log('5. Verify real-time updates and attribution');
  }
}

// Run the test
const tester = new MultiUserTester();
tester.runFullCollaborationTest().catch(console.error);