# 🗑️ Soft Delete System Guide

The collaborative worldbuilding platform now supports **soft deletion** as a compromise between immutability and database management.

## 🎯 **What is Soft Delete?**

- Content is marked as "deleted" but **not actually removed** from the database
- Deleted content is **hidden from normal views** but can be **restored**
- Provides **undo functionality** while maintaining data integrity
- Allows **eventual cleanup** of truly unwanted content

## 🔧 **How It Works**

### **For Users:**
- When you "delete" content, it's soft-deleted (hidden, not destroyed)
- Content can be restored if deleted by mistake
- Only content authors and admins can delete content

### **For Administrators:**
- View all soft-deleted content
- Restore accidentally deleted content
- Permanently delete content when appropriate
- Automated cleanup of old deleted content

## 📋 **Management Commands**

### **View Deleted Content**
```bash
# List all soft-deleted content
python manage.py manage_deleted_content list

# List only deleted pages
python manage.py manage_deleted_content list --content-type page

# List deleted content by specific type
python manage.py manage_deleted_content list --content-type character
```

### **Restore Content**
```bash
# Restore specific content by ID
python manage.py manage_deleted_content restore --content-type page --id 123 --force

# Restore all deleted pages
python manage.py manage_deleted_content restore --content-type page --force

# Restore all deleted content
python manage.py manage_deleted_content restore --force
```

### **Permanent Deletion (Purge)**
```bash
# Permanently delete specific content
python manage.py manage_deleted_content purge --content-type page --id 123 --force

# Permanently delete content soft-deleted more than 30 days ago
python manage.py manage_deleted_content purge --days 30 --force

# Permanently delete old deleted pages only
python manage.py manage_deleted_content purge --content-type page --days 60 --force
```

### **Automated Cleanup**
```bash
# Clean up old unused content (dry run first)
python manage.py cleanup_old_content --dry-run

# Actually clean up content older than 90 days
python manage.py cleanup_old_content --force

# Clean up content older than 30 days
python manage.py cleanup_old_content --days 30 --force
```

## 🛡️ **Safety Features**

### **Immutability Preserved**
- Content remains immutable during normal use
- Only soft delete operations are allowed
- Original content integrity is maintained

### **Restore Protection**
- Content with links from other content is preserved during cleanup
- Only truly orphaned content is permanently deleted
- Multiple confirmation steps for permanent deletion

### **User Permissions**
- Only content authors can soft-delete their own content
- Admins can manage all deleted content
- Regular users cannot see deleted content

## 📊 **Database Impact**

### **Storage Efficiency**
- Soft-deleted content uses minimal additional storage (3 extra fields)
- Automated cleanup prevents infinite growth
- Smart cleanup preserves referenced content

### **Performance**
- Default queries exclude soft-deleted content (no performance impact)
- Special managers available for including deleted content when needed
- Indexes on deletion fields for efficient queries

## 🔄 **Recommended Workflow**

### **Daily Operations**
1. Users create and collaborate on content normally
2. Accidental deletions can be easily restored
3. Content remains immutable and trustworthy

### **Weekly Maintenance**
```bash
# Check what's been deleted recently
python manage.py manage_deleted_content list
```

### **Monthly Cleanup**
```bash
# See what would be cleaned up
python manage.py cleanup_old_content --dry-run

# Clean up old unused content
python manage.py cleanup_old_content --force

# Permanently delete content soft-deleted more than 30 days ago
python manage.py manage_deleted_content purge --days 30 --force
```

## 🎛️ **Configuration Options**

### **Default Retention Periods**
- **Soft Delete**: Indefinite (until manually purged)
- **Cleanup**: 90 days for unused content
- **Purge**: 30 days for soft-deleted content

### **Customization**
You can adjust these periods based on your needs:
- More conservative: Increase retention periods
- More aggressive: Decrease retention periods
- Content-specific: Different periods for different content types

## 🚨 **Important Notes**

### **What Gets Preserved**
- ✅ Content referenced by other content
- ✅ Content in active worlds
- ✅ Recently created content
- ✅ Content with collaboration links

### **What Gets Cleaned Up**
- ❌ Truly orphaned content (no references)
- ❌ Content in empty, inactive worlds
- ❌ Old soft-deleted content
- ❌ Content explicitly marked for purging

### **Best Practices**
1. **Always use --dry-run first** to see what would be affected
2. **Regular backups** before major cleanup operations
3. **Monitor deletion patterns** to adjust retention policies
4. **Communicate with users** about deletion policies

This system gives you the **best of both worlds**: content integrity during active use, with smart cleanup to prevent database bloat! 🎉