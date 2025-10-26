#!/usr/bin/env python3
"""
Create the complete documentation folder structure
"""

import os

# Define the complete folder structure
folders = [
    # Getting Started
    "docs/01-getting-started",
    
    # Frontend
    "docs/02-frontend/components",
    "docs/02-frontend/implementation", 
    "docs/02-frontend/troubleshooting",
    
    # Backend
    "docs/03-backend/api",
    "docs/03-backend/models",
    "docs/03-backend/testing",
    
    # Database
    "docs/04-database/schema",
    "docs/04-database/operations",
    "docs/04-database/postgres-migration",
    
    # Deployment
    "docs/05-deployment/local",
    "docs/05-deployment/cloud",
    "docs/05-deployment/production",
    
    # Testing
    "docs/06-testing/frontend",
    "docs/06-testing/backend",
    "docs/06-testing/end-to-end",
    
    # Development
    "docs/07-development/planning",
    "docs/07-development/guides",
    "docs/07-development/features",
    "docs/07-development/troubleshooting",
    
    # Specs
    "docs/08-specs/requirements",
    "docs/08-specs/design", 
    "docs/08-specs/implementation",
    
    # Archive
    "docs/09-archive/old-implementations",
    "docs/09-archive/experiment-logs",
    "docs/09-archive/session-summaries"
]

def create_folders():
    """Create all documentation folders"""
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Created: {folder}")
        except Exception as e:
            print(f"❌ Failed to create {folder}: {e}")

def create_readme_files():
    """Create README.md files for main sections"""
    readme_files = {
        "docs/05-deployment/README.md": "# 🚀 Deployment Documentation\n\nDeployment guides for local, cloud, and production environments.",
        "docs/06-testing/README.md": "# 🧪 Testing Documentation\n\nComprehensive testing guides for frontend, backend, and end-to-end testing.",
        "docs/07-development/README.md": "# 👨‍💻 Development Documentation\n\nDevelopment guides, planning documents, and troubleshooting resources.",
        "docs/08-specs/README.md": "# 📋 Specifications\n\nProject specifications including requirements, design, and implementation details.",
        "docs/09-archive/README.md": "# 📦 Archive\n\nArchived documentation, old implementations, and historical development logs."
    }
    
    for file_path, content in readme_files.items():
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created README: {file_path}")
        except Exception as e:
            print(f"❌ Failed to create README {file_path}: {e}")

if __name__ == "__main__":
    print("📁 Creating documentation folder structure...")
    create_folders()
    print("\n📝 Creating README files...")
    create_readme_files()
    print("\n🎉 Documentation structure created successfully!")