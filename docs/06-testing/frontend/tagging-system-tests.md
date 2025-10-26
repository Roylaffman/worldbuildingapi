# 🏷️ Tagging & Linking Frontend Test Plan

## 🎯 **OBJECTIVE**
Test the frontend integration of the tagging and linking system to ensure:
1. TagManager component works correctly
2. ContentLinker component works correctly  
3. TagsPage and TagPage display properly
4. API integration functions correctly
5. User workflows are smooth and intuitive

## 🔧 **SETUP VERIFICATION**
- ✅ Backend server running on http://127.0.0.1:8000/
- ✅ Frontend server running on http://localhost:3000/
- ✅ Components exist: TagManager, ContentLinker, TagsPage, TagPage
- ✅ API functions exist: tagsAPI, contentAPI.addTags, contentAPI.addLinks

## 📋 **TEST PLAN**

### **PHASE 1: Basic Component Loading**

#### **Test 1.1: TagManager Component Loading**
**Objective**: Verify TagManager loads without errors
**Steps**:
1. Navigate to any content detail page (e.g., `/worlds/9/content/essay/1`)
2. Click "Manage Tags" button
3. Verify TagManager component appears
4. Check browser console for errors

**Expected Results**:
- TagManager component loads
- "Add Tag" button appears
- No JavaScript errors in console
- Existing tags display (if any)

#### **Test 1.2: ContentLinker Component Loading**
**Objective**: Verify ContentLinker loads without errors
**Steps**:
1. Navigate to any content detail page
2. Click "Manage Links" button  
3. Verify ContentLinker component appears
4. Check browser console for errors

**Expected Results**:
- ContentLinker component loads
- "Link to Other Content" button appears
- No JavaScript errors in console
- Existing links display (if any)

### **PHASE 2: TagManager Functionality**

#### **Test 2.1: Tag Addition**
**Objective**: Test adding new tags to content
**Steps**:
1. Open TagManager on content page
2. Click "Add Tag" button
3. Type a new tag name (e.g., "test-tag-frontend")
4. Press Enter or click "Add"
5. Verify tag appears in existing tags list
6. Check network tab for API call

**Expected Results**:
- Tag input field appears
- Tag is added successfully
- API call to `/add-tags/` endpoint succeeds
- Tag appears in existing tags list
- Success toast notification appears

#### **Test 2.2: Tag Autocomplete**
**Objective**: Test tag suggestion functionality
**Steps**:
1. Create some tags first (if none exist)
2. Open TagManager
3. Click "Add Tag"
4. Start typing partial tag name
5. Verify suggestions appear
6. Click on a suggestion

**Expected Results**:
- Suggestions dropdown appears
- Existing tags are suggested
- Clicking suggestion adds the tag
- No duplicate tags are created

#### **Test 2.3: Tag Limits**
**Objective**: Test maximum tag limit enforcement
**Steps**:
1. Add tags until reaching the limit (10 tags)
2. Verify "Add Tag" button becomes disabled
3. Check helper text shows "0 tags remaining"

**Expected Results**:
- Cannot add more than 10 tags
- UI clearly indicates limit reached
- Add button is disabled when limit reached

### **PHASE 3: ContentLinker Functionality**

#### **Test 3.1: Content Type Selection**
**Objective**: Test content type dropdown
**Steps**:
1. Open ContentLinker
2. Click "Link to Other Content"
3. Test each content type in dropdown
4. Verify content loads for each type

**Expected Results**:
- All content types available (pages, essays, characters, stories, images)
- Content loads when type is selected
- Search works for each content type

#### **Test 3.2: Content Search**
**Objective**: Test content search functionality
**Steps**:
1. Open ContentLinker
2. Select a content type
3. Type in search field
4. Verify results filter correctly

**Expected Results**:
- Search filters content by title
- Results update as user types
- "No content found" message when no matches

#### **Test 3.3: Link Creation**
**Objective**: Test creating links between content
**Steps**:
1. Open ContentLinker
2. Select content type and find content to link
3. Click on content item to create link
4. Verify link appears in "Existing Links" section
5. Check network tab for API call

**Expected Results**:
- Link is created successfully
- API call to `/add-links/` endpoint succeeds
- Link appears in existing links list
- Success toast notification appears

#### **Test 3.4: Duplicate Link Prevention**
**Objective**: Test that duplicate links are prevented
**Steps**:
1. Create a link between two pieces of content
2. Try to create the same link again
3. Verify "Already linked" message appears

**Expected Results**:
- Cannot create duplicate links
- "Already linked" message shows
- Link button is disabled for already linked content

### **PHASE 4: TagsPage and TagPage**

#### **Test 4.1: TagsPage Display**
**Objective**: Test tags overview page
**Steps**:
1. Navigate to `/worlds/9/tags`
2. Verify all world tags display
3. Check tag grid layout
4. Test clicking on individual tags

**Expected Results**:
- All world tags display in grid
- Tag creation dates show
- Clicking tag navigates to TagPage
- "No tags yet" message if no tags exist

#### **Test 4.2: TagPage Content Display**
**Objective**: Test individual tag page
**Steps**:
1. Navigate to specific tag page (e.g., `/worlds/9/tags/test-tag`)
2. Verify tagged content displays
3. Test content type filtering
4. Click on tagged content items

**Expected Results**:
- Tagged content displays correctly
- Content shows proper icons and metadata
- Clicking content navigates to content page
- "No content with this tag" message if empty

### **PHASE 5: End-to-End Workflows**

#### **Test 5.1: Complete Tagging Workflow**
**Objective**: Test full tagging user journey
**Steps**:
1. Create new content (essay, character, etc.)
2. Add tags using TagManager
3. Navigate to TagsPage and find new tags
4. Click tag to see tagged content
5. Verify content appears on TagPage

**Expected Results**:
- Complete workflow works smoothly
- Tags persist across page refreshes
- Navigation between pages works
- Content discovery via tags works

#### **Test 5.2: Complete Linking Workflow**
**Objective**: Test full linking user journey
**Steps**:
1. Create multiple pieces of content
2. Use ContentLinker to link them together
3. Navigate between linked content
4. Verify bidirectional relationships

**Expected Results**:
- Links are created successfully
- Bidirectional navigation works
- Linked content displays properly
- Link relationships persist

#### **Test 5.3: Cross-Content Type Workflow**
**Objective**: Test linking different content types
**Steps**:
1. Create one of each content type (page, essay, character, story, image)
2. Tag all with same tag
3. Link them in a chain (essay→character→image→story→page)
4. Test navigation through entire network

**Expected Results**:
- All content types can be tagged and linked
- Cross-type relationships work correctly
- Navigation through link network works
- Tag-based discovery includes all types

### **PHASE 6: Error Handling and Edge Cases**

#### **Test 6.1: Network Error Handling**
**Objective**: Test behavior when API calls fail
**Steps**:
1. Disconnect from internet or stop backend server
2. Try to add tags and links
3. Verify error messages appear
4. Reconnect and verify retry works

**Expected Results**:
- Clear error messages for users
- No application crashes
- Graceful degradation
- Retry functionality works

#### **Test 6.2: Edge Case Testing**
**Objective**: Test unusual scenarios
**Steps**:
1. Try very long tag names
2. Try special characters in tags
3. Try linking content to itself
4. Test with empty content lists

**Expected Results**:
- Proper validation and error handling
- No crashes or unexpected behavior
- Clear feedback for invalid operations

## 🧪 **TESTING SCRIPT**

### **Quick Manual Test Checklist**
```
□ 1. Login to application (http://localhost:3000)
□ 2. Navigate to world (e.g., /worlds/9)
□ 3. Click on existing content or create new content
□ 4. Test TagManager:
   □ Click "Manage Tags"
   □ Add a new tag
   □ Verify tag appears
□ 5. Test ContentLinker:
   □ Click "Manage Links"
   □ Select content type
   □ Search for content
   □ Create a link
   □ Verify link appears
□ 6. Test TagsPage:
   □ Navigate to /worlds/9/tags
   □ Verify tags display
   □ Click on a tag
□ 7. Test TagPage:
   □ Verify tagged content displays
   □ Click on content item
□ 8. Verify no console errors throughout
```

### **API Test Commands**
```bash
# Test tag creation
curl -X POST http://localhost:8000/api/v1/worlds/9/essays/1/add-tags/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["frontend-test-tag"]}'

# Test link creation  
curl -X POST http://localhost:8000/api/v1/worlds/9/essays/1/add-links/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"links": [{"content_type": "character", "content_id": 1}]}'

# Test tag retrieval
curl -X GET http://localhost:8000/api/v1/worlds/9/tags/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 **SUCCESS CRITERIA**

### **Must Pass (Deployment Blockers)**
- [ ] TagManager loads and functions without errors
- [ ] ContentLinker loads and functions without errors
- [ ] Tags can be added to content successfully
- [ ] Links can be created between content successfully
- [ ] TagsPage displays world tags correctly
- [ ] TagPage shows tagged content correctly
- [ ] No critical JavaScript errors in console
- [ ] API calls succeed and return expected data

### **Should Pass (High Priority)**
- [ ] Tag autocomplete works with existing tags
- [ ] Content search and filtering works in ContentLinker
- [ ] Duplicate prevention works for tags and links
- [ ] Error handling provides good user feedback
- [ ] Loading states are shown during API calls
- [ ] Success notifications appear for user actions

### **Nice to Have (Post-Deployment)**
- [ ] Advanced tag search and filtering
- [ ] Bulk tag operations
- [ ] Link visualization
- [ ] Tag analytics and statistics
- [ ] Performance optimizations

## 🚨 **KNOWN ISSUES TO WATCH FOR**

1. **API Integration**: Ensure frontend API calls match backend endpoints
2. **Content Type Handling**: Verify singular/plural content type handling
3. **Authentication**: Ensure auth tokens are included in API calls
4. **Error Boundaries**: Check that component errors don't crash the app
5. **Loading States**: Verify loading indicators during API operations
6. **Data Persistence**: Ensure tags/links persist after page refresh

## 📊 **TEST RESULTS TRACKING**

### **Test Execution Log**
```
Date: [DATE]
Tester: [NAME]
Environment: Frontend (localhost:3000) + Backend (localhost:8000)

Phase 1 - Component Loading:
□ Test 1.1: TagManager Loading - [PASS/FAIL] - Notes: ___
□ Test 1.2: ContentLinker Loading - [PASS/FAIL] - Notes: ___

Phase 2 - TagManager Functionality:
□ Test 2.1: Tag Addition - [PASS/FAIL] - Notes: ___
□ Test 2.2: Tag Autocomplete - [PASS/FAIL] - Notes: ___
□ Test 2.3: Tag Limits - [PASS/FAIL] - Notes: ___

[Continue for all phases...]
```

**🎉 Ready to start testing! The tagging and linking system is the core of collaborative worldbuilding - let's make sure it works perfectly!**