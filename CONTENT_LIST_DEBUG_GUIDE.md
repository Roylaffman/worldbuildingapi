# Content List Pages Debug Guide

## Issue
Content list pages (`http://localhost:3000/worlds/9/essays`, `/characters`, etc.) are not showing the summaries/lists of content items from the database.

## Debugging Steps

### 1. Check Authentication Status
**Most Common Issue**: User is not logged in

**Steps to Fix**:
1. Go to `http://localhost:3000/login`
2. Login with: `admin` / `admin123`
3. Should redirect to worlds page
4. Then navigate to content list pages

### 2. Use Debug Tools

#### Option A: Frontend Debug Info
1. Navigate to any content list page (e.g., `http://localhost:3000/worlds/9/essays`)
2. Look for yellow debug box showing:
   - Auth status (should be ✅ Authenticated)
   - User (should show "admin")
   - Content Items (should show number > 0 for essays/characters)
   - Tokens (should be ✅ Present)

#### Option B: Debug HTML Page
1. Go to `http://localhost:3000/debug-content.html`
2. Click "Check Auth" - should show valid tokens
3. If no tokens, click "Login" first
4. Click "Test Content API" - should show content data

### 3. Check Browser Console
Open browser developer tools (F12) and look for:
- `ContentListPage: Fetching essays for world 9`
- `ContentListPage: API call successful, received X items`
- Any error messages

### 4. Expected Results

#### Essays Page (`/worlds/9/essays`)
**Should Show**:
- Debug info: "Content Items: 1"
- One essay card: "Static on the Wire"
- Word count: "991 words"
- Author: "by RYAN"

#### Characters Page (`/worlds/9/characters`)
**Should Show**:
- Debug info: "Content Items: 1"
- One character card: "John Moreau"
- Full name: "John Baptiste Moreau"
- Author: "by RYAN"

#### Other Pages (`/pages`, `/stories`, `/images`)
**Should Show**:
- Debug info: "Content Items: 0"
- Empty state: "No [content type] yet"
- Create button

## Common Issues & Solutions

### Issue: "Content Items: 0" for essays/characters
**Cause**: API call failing or authentication issue
**Solution**:
1. Check debug info for authentication status
2. Login if not authenticated
3. Check browser console for API errors

### Issue: "❌ Not authenticated" in debug info
**Cause**: User not logged in or tokens expired
**Solution**:
1. Go to login page: `http://localhost:3000/login`
2. Login with admin/admin123
3. Return to content list page

### Issue: "❌ Missing" tokens in debug info
**Cause**: Tokens not stored or cleared
**Solution**:
1. Login again to get fresh tokens
2. Check if localStorage is working in browser

### Issue: API errors in console
**Cause**: Backend not running or API endpoints changed
**Solution**:
1. Verify backend is running on port 8000
2. Test API directly using debug HTML page
3. Check network tab for failed requests

## Quick Fix Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] User logged in with admin/admin123
- [ ] Navigate to `/worlds/9/essays` or `/worlds/9/characters`
- [ ] Check debug info shows authentication ✅
- [ ] Check debug info shows content items > 0
- [ ] Look for content cards on the page

## API Verification

The backend APIs are confirmed working:
- ✅ `GET /api/v1/worlds/9/essays/` returns 1 essay
- ✅ `GET /api/v1/worlds/9/characters/` returns 1 character
- ✅ Both return proper paginated responses with `results` arrays

## Next Steps

If content still doesn't show after following these steps:
1. Check the debug HTML page results
2. Look at browser console for specific errors
3. Verify the debug info on the content list pages
4. Check if the issue is authentication or API-related

The most likely issue is that you need to be logged in first before accessing the content list pages.