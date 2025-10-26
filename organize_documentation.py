#!/usr/bin/env python3
"""
Organize documentation files into the new folder structure
"""

import os
import shutil
from pathlib import Path

# Define file mappings: source -> destination
file_mappings = {
    # Frontend Documentation
    "frontend_setup.md": "docs/02-frontend/setup.md",
    "FRONTEND_CONTENT_FIXES.md": "docs/02-frontend/implementation/content-pages.md",
    "CONTENT_DETAIL_PAGE_IMPLEMENTATION.md": "docs/02-frontend/implementation/content-detail-pages.md",
    "FRONTEND_IMPROVEMENT_ROADMAP.md": "docs/02-frontend/roadmap.md",
    "AUTHENTICATION_INTEGRATION_SUMMARY.md": "docs/02-frontend/implementation/authentication.md",
    "CONTENT_LIST_DEBUG_GUIDE.md": "docs/02-frontend/troubleshooting/content-list-issues.md",
    "CONTENT_LIST_IMPLEMENTATION_SUMMARY.md": "docs/02-frontend/components/content-management.md",
    "CONTENT_LIST_TROUBLESHOOTING.md": "docs/02-frontend/troubleshooting/content-list-troubleshooting.md",
    
    # Tagging System Documentation
    "TAGGING_LINKING_IMPLEMENTATION_COMPLETE.md": "docs/02-frontend/components/tagging-system.md",
    "TAGGING_SYSTEM_IMPLEMENTATION_COMPLETE.md": "docs/07-development/features/tagging-system-complete.md",
    "TAGGING_LINKING_FRONTEND_TEST_PLAN.md": "docs/06-testing/frontend/tagging-system-tests.md",
    "TAGGING_LINKING_TEST_SUMMARY.md": "docs/06-testing/frontend/tagging-test-summary.md",
    
    # Backend Documentation  
    "docs/api_documentation.md": "docs/03-backend/api/endpoints-reference.md",
    "docs/test_report.md": "docs/03-backend/testing/test-reports.md",
    
    # Database Documentation
    "DATABASE_ANALYSIS_REPORT.md": "docs/04-database/analysis-reports.md",
    "docs/database_inspection_guide.md": "docs/04-database/operations/inspection.md",
    "docs/soft_delete_guide.md": "docs/04-database/operations/soft-delete.md",
    "docs/hard_delete_guide.md": "docs/04-database/operations/hard-delete.md",
    
    # Deployment Documentation
    "docs/docker_deployment_guide.md": "docs/05-deployment/local/docker.md",
    "docs/aws_deployment_guide.md": "docs/05-deployment/cloud/aws.md", 
    "docs/gcp_deployment_guide.md": "docs/05-deployment/cloud/gcp.md",
    "deployment/google-cloud-setup.md": "docs/05-deployment/cloud/gcp-setup.md",
    "docs/deployment_comparison.md": "docs/05-deployment/cloud/comparison.md",
    "docs/project_status_and_deployment.md": "docs/05-deployment/production/checklist.md",
    "nginx.conf": "docs/05-deployment/production/nginx-config.md",
    
    # Testing Documentation
    "IMAGE_UPLOAD_TEST_PLAN.md": "docs/06-testing/backend/image-upload-tests.md",
    "docs/integration_test_summary.md": "docs/06-testing/backend/integration-test-summary.md",
    
    # Development Documentation
    "CURRENT_STATUS.md": "docs/07-development/planning/project-status.md",
    "PROGRESS_SUMMARY.md": "docs/07-development/planning/progress-summary.md",
    "SESSION_SUMMARY.md": "docs/07-development/planning/session-summary.md",
    "GIT_COMMIT_SUMMARY.md": "docs/07-development/planning/git-commit-summary.md",
    "TODAY_ACCOMPLISHMENTS.md": "docs/07-development/planning/today-accomplishments.md",
    "TOMORROW_TASKS.md": "docs/07-development/planning/tomorrow-tasks.md",
    "docs/frontend_implementation_roadmap.md": "docs/07-development/planning/frontend-roadmap.md",
    
    # Specifications
    ".kiro/specs/collaborative-worldbuilding/requirements.md": "docs/08-specs/requirements/functional-requirements.md",
    ".kiro/specs/collaborative-worldbuilding/design.md": "docs/08-specs/design/system-design.md",
    ".kiro/specs/collaborative-worldbuilding/tasks.md": "docs/08-specs/implementation/task-breakdown.md",
    ".kiro/specs/collaborative-worldbuilding/finalization-tasks.md": "docs/08-specs/implementation/finalization-tasks.md",
}

# Test files to move to archive
test_files = [
    "test_auth_integration.js",
    "test_frontend_tagging.js", 
    "test_multi_user_collaboration.js",
    "test_api_endpoints.py",
    "test_tagging_linking.py",
    "test_urls.py",
    "test_backend_tagging_api.py",
    "test_frontend_components_direct.py",
    "test_complete_tagging_system.py",
    "test_tags_page_fix.py",
    "debug_api.py",
    "debug_tags_detailed.py",
    "simple_frontend_test.html",
    "frontend/public/test-auth.html",
    "frontend/public/debug-content.html",
    "frontend/public/test-tagging.html",
    "frontend/public/test-components.js"
]

def move_file(source, destination):
    """Move a file from source to destination, creating directories if needed"""
    try:
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Move the file
            shutil.move(source, destination)
            print(f"✅ Moved: {source} -> {destination}")
            return True
        else:
            print(f"⚠️ Source not found: {source}")
            return False
    except Exception as e:
        print(f"❌ Failed to move {source}: {e}")
        return False

def copy_file(source, destination):
    """Copy a file from source to destination (for files we want to keep in both places)"""
    try:
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, destination)
            print(f"✅ Copied: {source} -> {destination}")
            return True
        else:
            print(f"⚠️ Source not found: {source}")
            return False
    except Exception as e:
        print(f"❌ Failed to copy {source}: {e}")
        return False

def organize_files():
    """Organize all documentation files"""
    print("📁 Organizing documentation files...")
    
    moved_count = 0
    
    # Move mapped files
    for source, destination in file_mappings.items():
        if move_file(source, destination):
            moved_count += 1
    
    # Move test files to archive
    print("\n📦 Moving test files to archive...")
    for test_file in test_files:
        archive_path = f"docs/09-archive/experiment-logs/{os.path.basename(test_file)}"
        if move_file(test_file, archive_path):
            moved_count += 1
    
    # Copy important files that should stay in root
    print("\n📋 Copying important files...")
    important_files = {
        "README.md": "docs/01-getting-started/project-overview.md",
        ".env.example": "docs/01-getting-started/environment-setup.md"
    }
    
    for source, destination in important_files.items():
        copy_file(source, destination)
    
    print(f"\n🎉 Organization complete! Moved {moved_count} files.")
    
    # List remaining files in root that might need attention
    print("\n📋 Remaining files in root directory:")
    root_files = [f for f in os.listdir('.') if f.endswith('.md') and os.path.isfile(f)]
    for file in root_files:
        print(f"  - {file}")

if __name__ == "__main__":
    organize_files()