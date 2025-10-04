# 🔥 Hard Delete Management Guide

This guide covers **hard deletion** commands that bypass immutability for testing and administrative purposes.

## ⚠️ **DANGER ZONE - Use with Caution!**

These commands **permanently delete** data and **cannot be undone**. Always use `--dry-run` first!

## 📋 **Available Commands**

### **1. List All Content**
```bash
# See what's in your database
python manage.py hard_delete_content list
```

### **2. Delete Specific Worlds**
```bash
# Delete a specific world by ID (dry run first)
python manage.py hard_delete_content delete-world --world-id 9 --dry-run
python manage.py hard_delete_content delete-world --world-id 9 --force

# Delete all worlds matching a pattern
python manage.py hard_delete_content delete-world --pattern "static" --dry-run
python manage.py hard_delete_content delete-world --pattern "static" --force

# Delete multiple test worlds
python manage.py hard_delete_content delete-world --pattern "test" --force
```

### **3. Delete Specific Content**
```bash
# Delete a specific character
python manage.py hard_delete_content delete-content --content-type character --content-id 1 --force

# Delete all characters matching a pattern
python manage.py hard_delete_content delete-content --content-type character --pattern "test" --force

# Delete all pages in test worlds
python manage.py hard_delete_content delete-content --content-type page --pattern "test" --force
```

### **4. Delete User Data**
```bash
# Delete all data for a specific user (dry run first)
python manage.py hard_delete_content delete-user-data --user testuser --dry-run
python manage.py hard_delete_content delete-user-data --user testuser --force
```

### **5. Reset All Test Data**
```bash
# Delete all test/demo worlds and content (dry run first)
python manage.py hard_delete_content reset-test-data --dry-run
python manage.py hard_delete_content reset-test-data --force
```

## 🎯 **Common Use Cases**

### **During Development/Testing**
```bash
# Clean up all your test worlds
python manage.py hard_delete_content reset-test-data --force

# Remove duplicate worlds
python manage.py hard_delete_content delete-world --pattern "static on the" --dry-run
python manage.py hard_delete_content delete-world --pattern "static on the" --force

# Clean up test characters
python manage.py hard_delete_content delete-content --content-type character --pattern "test" --force
```

### **Production Maintenance**
```bash
# Remove abandoned worlds
python manage.py hard_delete_content delete-world --pattern "untitled" --dry-run
python manage.py hard_delete_content delete-world --pattern "untitled" --force

# Clean up spam content
python manage.py hard_delete_content delete-user-data --user spammer123 --force
```

### **Database Reset**
```bash
# Nuclear option: reset all test data
python manage.py hard_delete_content reset-test-data --force

# List what's left
python manage.py hard_delete_content list
```

## 🛡️ **Safety Features**

### **Dry Run Protection**
- Always use `--dry-run` first to see what would be deleted
- Shows exactly what will be affected before you commit

### **Confirmation Prompts**
- Bulk operations require typing "yes" to confirm
- Prevents accidental mass deletion

### **Transaction Safety**
- All operations are wrapped in database transactions
- If something fails, changes are rolled back

## 📊 **What Gets Deleted**

### **World Deletion**
- ✅ The world itself
- ✅ All pages in that world
- ✅ All characters in that world  
- ✅ All stories in that world
- ✅ All essays in that world
- ✅ All images in that world
- ✅ All tags and links related to that content

### **User Data Deletion**
- ✅ All worlds created by the user
- ✅ All content authored by the user
- ✅ All soft-deleted content by the user
- ❌ The user account itself (preserved)

### **Content Deletion**
- ✅ The specific content item
- ✅ All tags associated with it
- ✅ All links to/from other content
- ✅ Soft-deleted versions

## 🚨 **Important Notes**

### **Immutability Bypass**
- These commands **bypass all immutability protections**
- Use only for administrative purposes
- Not available through the regular API

### **Cascade Effects**
- Deleting a world deletes ALL its content
- Deleting content breaks links from other content
- Consider the impact on collaborators

### **No Undo**
- Hard deletion is **permanent**
- No way to recover deleted data
- Always backup before major operations

## 🔄 **Recommended Workflow**

### **1. Investigate**
```bash
python manage.py hard_delete_content list
```

### **2. Plan**
```bash
python manage.py hard_delete_content delete-world --pattern "test" --dry-run
```

### **3. Execute**
```bash
python manage.py hard_delete_content delete-world --pattern "test" --force
```

### **4. Verify**
```bash
python manage.py hard_delete_content list
```

## 🎯 **Quick Cleanup for Your Current Situation**

Based on your test worlds, here's what you can run:

```bash
# See all your test worlds
python manage.py hard_delete_content list

# Clean up the duplicate "Static" worlds (dry run first)
python manage.py hard_delete_content delete-world --pattern "static" --dry-run

# If it looks good, execute
python manage.py hard_delete_content delete-world --pattern "static" --force

# Keep only the world you want to work with
```

This gives you **complete control** over your database while maintaining safety through dry-run and confirmation prompts! 🎯