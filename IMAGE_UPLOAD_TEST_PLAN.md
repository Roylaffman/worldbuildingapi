# Image Upload System Testing Plan

## 🎯 **Priority 1: Test Image Upload System**

### **Prerequisites**
1. **Start Backend Server**: `python manage.py runserver` (port 8000)
2. **Start Frontend Server**: `cd frontend && npm run dev` (port 3000)
3. **Login**: Use `admin` / `admin123` credentials

### **Test Cases to Execute**

#### **1. Basic Image Upload Flow** ⭐⭐⭐
- [ ] Navigate to: `http://localhost:3000/worlds/9/create/image`
- [ ] Test form validation (empty fields)
- [ ] Upload a PNG image (< 10MB)
- [ ] Verify image preview appears
- [ ] Fill in title, description, alt text
- [ ] Submit form and verify success
- [ ] Check image appears in: `http://localhost:3000/worlds/9/images`

#### **2. File Type Validation** ⭐⭐⭐
- [ ] Test PNG upload ✅
- [ ] Test JPG upload ✅
- [ ] Test GIF upload ✅
- [ ] Test invalid file type (PDF, TXT) ❌ (should reject)
- [ ] Verify error messages for invalid types

#### **3. File Size Validation** ⭐⭐⭐
- [ ] Test small image (< 1MB) ✅
- [ ] Test medium image (5MB) ✅
- [ ] Test large image (> 10MB) ❌ (should reject)
- [ ] Verify file size error message

#### **4. Image Preview Functionality** ⭐⭐
- [ ] Verify preview appears after file selection
- [ ] Test preview with different image sizes
- [ ] Test removing selected image
- [ ] Verify preview updates correctly

#### **5. Form Validation** ⭐⭐
- [ ] Test empty title (should show error)
- [ ] Test empty description (should show error)
- [ ] Test empty alt text (should show error)
- [ ] Test no image selected (should show error)
- [ ] Verify all error messages are clear

#### **6. Image Display in Lists** ⭐⭐⭐
- [ ] Upload test image successfully
- [ ] Navigate to: `http://localhost:3000/worlds/9/images`
- [ ] Verify image appears in content list
- [ ] Check image thumbnail displays correctly
- [ ] Verify image metadata (title, author, date)

#### **7. Image Detail Page** ⭐⭐⭐
- [ ] Click on image from list page
- [ ] Verify full-size image displays
- [ ] Check alt text is shown
- [ ] Verify description and metadata
- [ ] Test image responsiveness on mobile

#### **8. Integration with World Dashboard** ⭐⭐
- [ ] Upload image successfully
- [ ] Navigate to: `http://localhost:3000/worlds/9`
- [ ] Verify image count updates in dashboard
- [ ] Check image appears in "Recent Content"
- [ ] Test clicking from recent content to detail

### **Test Images to Use**

#### **Valid Test Images**
1. **Small PNG** (< 1MB): Character sketch
2. **Medium JPG** (2-5MB): Storyboard panel
3. **Small GIF** (< 1MB): Simple animation
4. **Large JPG** (5-9MB): Detailed concept art

#### **Invalid Test Files**
1. **Oversized Image** (> 10MB): Should be rejected
2. **PDF File**: Should be rejected
3. **Text File**: Should be rejected

### **Expected Results**

#### **Successful Upload Should:**
- ✅ Show image preview during upload
- ✅ Display success message after upload
- ✅ Redirect to world dashboard
- ✅ Update world content counts
- ✅ Show image in content lists
- ✅ Display properly in detail view
- ✅ Include in recent content

#### **Failed Upload Should:**
- ❌ Show clear error message
- ❌ Not submit the form
- ❌ Highlight problematic fields
- ❌ Allow user to fix and retry

### **Performance Tests**
- [ ] Upload multiple images in sequence
- [ ] Test upload speed with different file sizes
- [ ] Verify memory usage during upload
- [ ] Test concurrent uploads (if possible)

### **Mobile Responsiveness**
- [ ] Test upload form on mobile
- [ ] Verify image preview on small screens
- [ ] Check image display in lists on mobile
- [ ] Test detail page responsiveness

### **Accessibility Tests**
- [ ] Verify alt text is required and used
- [ ] Test with screen reader (if available)
- [ ] Check keyboard navigation
- [ ] Verify color contrast and readability

## 🔧 **Debugging Tools**

### **If Upload Fails:**
1. **Check Browser Console** (F12) for JavaScript errors
2. **Check Network Tab** for failed API requests
3. **Check Backend Logs** for server errors
4. **Verify File Permissions** on upload directory

### **Common Issues:**
- **CORS Errors**: Check backend CORS settings
- **File Size**: Verify backend accepts large files
- **Authentication**: Ensure user is logged in
- **API Endpoints**: Verify image API is working

## 🎯 **Success Criteria**

### **Must Pass:**
- [ ] All valid image types upload successfully
- [ ] Invalid files are properly rejected
- [ ] Images display correctly in all views
- [ ] Form validation works properly
- [ ] No JavaScript errors in console

### **Should Pass:**
- [ ] Upload performance is acceptable
- [ ] Mobile experience is good
- [ ] Accessibility features work
- [ ] Error messages are helpful

## 📝 **Test Results Template**

```
## Image Upload Test Results - [Date]

### ✅ Passed Tests:
- Basic PNG upload: ✅
- File size validation: ✅
- Image preview: ✅
- [etc...]

### ❌ Failed Tests:
- [List any failures with details]

### 🐛 Issues Found:
- [List any bugs or problems]

### 📊 Performance:
- Upload speed: [X] seconds for [Y] MB file
- Memory usage: [Normal/High]
- Mobile experience: [Good/Needs work]

### 🎯 Next Steps:
- [List what needs to be fixed or improved]
```

## 🚀 **Ready to Start Testing!**

Once both servers are running, we'll systematically go through each test case and verify the image upload system is working perfectly for storyboards and concept art!