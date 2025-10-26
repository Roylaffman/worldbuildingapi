# 🔍 Database Inspection Guide

Complete guide to inspecting and analyzing your worldbuilding database.

## 🎯 **Quick Start Commands**

```bash
# Get a complete overview of your database
python manage.py inspect_db overview

# List all worlds
python manage.py inspect_db worlds

# List all content
python manage.py inspect_db content

# Show database statistics
python manage.py inspect_db stats
```

## 📋 **All Available Commands**

### **1. Database Overview**
```bash
# Complete database summary
python manage.py inspect_db overview
```
Shows: Users, worlds, content counts, recent activity

### **2. World Inspection**
```bash
# List all worlds
python manage.py inspect_db worlds

# Search worlds by name
python manage.py inspect_db worlds --search "static"

# Limit results
python manage.py inspect_db worlds --limit 10

# Detailed world information
python manage.py inspect_db world-detail --id 9
```

### **3. Content Inspection**
```bash
# List all content
python manage.py inspect_db content

# List specific content type
python manage.py inspect_db content --content-type character

# Content in specific world
python manage.py inspect_db content --world 9

# Include soft-deleted content
python manage.py inspect_db content --include-deleted

# Search content
python manage.py inspect_db content --search "john"
```

### **4. User Analysis**
```bash
# List all users
python manage.py inspect_db users

# Detailed user information
python manage.py inspect_db user-detail --user admin
```

### **5. Database Statistics**
```bash
# Comprehensive statistics
python manage.py inspect_db stats
```
Shows: User stats, world stats, content stats, activity stats, top creators

### **6. Search Everything**
```bash
# Search across all content and worlds
python manage.py inspect_db search --search "magic"
```

### **7. Recent Activity**
```bash
# Show recent activity (last 7 days)
python manage.py inspect_db recent
```

### **8. Data Quality Analysis**
```bash
# Find empty worlds
python manage.py inspect_db empty-worlds

# Find orphaned content
python manage.py inspect_db orphaned-content
```

### **9. Tags and Links** (if implemented)
```bash
# Show tag usage
python manage.py inspect_db tags

# Show content links
python manage.py inspect_db links
```

## 🎯 **Common Use Cases**

### **After Database Reset**
```bash
# Check if database is truly empty
python manage.py inspect_db overview

# Verify no content remains
python manage.py inspect_db content --include-deleted
```

### **Finding Specific Content**
```bash
# Find a character you created
python manage.py inspect_db search --search "john moreau"

# Find all content in a specific world
python manage.py inspect_db content --world 9

# Find content by specific user
python manage.py inspect_db content --search "admin"
```

### **Database Health Check**
```bash
# Overall health
python manage.py inspect_db stats

# Find problems
python manage.py inspect_db empty-worlds
python manage.py inspect_db orphaned-content

# Recent activity
python manage.py inspect_db recent
```

### **Content Management**
```bash
# List all worlds to find duplicates
python manage.py inspect_db worlds

# Find test content
python manage.py inspect_db search --search "test"

# Check specific world details
python manage.py inspect_db world-detail --id 10
```

## 🔧 **Advanced Options**

### **Output Formats**
```bash
# Table format (default)
python manage.py inspect_db worlds --format table

# JSON format for scripting
python manage.py inspect_db worlds --format json

# Detailed format
python manage.py inspect_db worlds --format detailed
```

### **Filtering Options**
```bash
# Limit results
python manage.py inspect_db content --limit 50

# Include deleted content
python manage.py inspect_db content --include-deleted

# Filter by world
python manage.py inspect_db content --world 9

# Filter by content type
python manage.py inspect_db content --content-type page
```

## 📊 **Understanding the Output**

### **World Listing**
```
ID: 10  | 🌐 Public | "My Fantasy World" | Creator: admin | Content: 15 | Created: 2024-10-03 14:30
```
- **ID**: Database ID for the world
- **Visibility**: 🌐 Public or 🔒 Private
- **Title**: World name (truncated if long)
- **Creator**: Username who created it
- **Content**: Total number of content items
- **Created**: When the world was created

### **Content Listing**
```
ID: 25  | "Gandalf the Wizard" | Author: admin | World: Middle Earth | Created: 2024-10-03 15:45 [DELETED]
```
- **ID**: Database ID for the content
- **Title**: Content title (truncated if long)
- **Author**: Username who created it
- **World**: Which world it belongs to
- **Created**: When it was created
- **[DELETED]**: Shows if soft-deleted (only with --include-deleted)

## 🚀 **Your Current Situation**

Since you mentioned the database might be empty now, try these:

```bash
# Check if truly empty
python manage.py inspect_db overview

# Look for any remaining content
python manage.py inspect_db content --include-deleted

# Check user accounts
python manage.py inspect_db users

# See if any worlds remain
python manage.py inspect_db worlds
```

## 💡 **Pro Tips**

### **Regular Health Checks**
```bash
# Weekly database review
python manage.py inspect_db stats
python manage.py inspect_db recent
python manage.py inspect_db empty-worlds
```

### **Before Major Changes**
```bash
# Document current state
python manage.py inspect_db overview > db_state_before.txt
python manage.py inspect_db worlds >> db_state_before.txt
```

### **Finding Lost Content**
```bash
# Search by partial title
python manage.py inspect_db search --search "partial_name"

# Check specific world
python manage.py inspect_db world-detail --id WORLD_ID

# Look in deleted content
python manage.py inspect_db content --include-deleted --search "lost_content"
```

This gives you **complete visibility** into your database! 🔍✨