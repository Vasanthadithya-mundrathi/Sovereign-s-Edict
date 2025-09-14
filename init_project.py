#!/usr/bin/env python3
"""
Project initialization and organization script for Sovereign's Edict
This script helps organize the project structure and ensures all components are properly set up.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create a clean directory structure for the project"""
    # Define the desired directory structure
    directories = [
        "backend/api",
        "backend/models",
        "backend/ingestion",
        "backend/mining",
        "backend/citation",
        "backend/fusion",
        "backend/amendment",
        "backend/compute",
        "backend/plugins",
        "backend/utils",
        "backend/tests",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/src/utils",
        "frontend/src/assets",
        "data/raw",
        "data/processed",
        "data/sample",
        "models/llm",
        "models/embeddings",
        "docs/api",
        "docs/plugins",
        "docs/user_guides",
        "docs/architecture",
        "docs/specifications",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "phases",
        "social_media_analysis"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def organize_phases():
    """Organize phase documentation files"""
    print("Organizing phase documentation...")
    
    # Move phase files to phases directory
    phase_files = [
        "PHASE_1_SECURITY_FIXES.md",
        "PHASE_2_DATA_INGESTION.md",
        "PHASE_3_AUTOMATED_PROCESSING.md",
        "PHASE_4_USER_DASHBOARD.md",
        "PHASE_5_EXPLAIN_MODE.md",
        "PHASE_6_NO_SETUP_DEPLOYMENT.md",
        "PHASE_7_OFFLINE_FIRST.md",
        "PHASE_8_COMMUNITY_MODE.md",
        "PHASE_9_PRIVACY_TRANSPARENCY.md",
        "PHASE_10_POLISH_USER_TRUST.md",
        "PHASE_11_COMMUNITY_PLUGIN.md"
    ]
    
    for phase_file in phase_files:
        if os.path.exists(phase_file):
            shutil.move(phase_file, f"phases/{phase_file}")
            print(f"Moved {phase_file} to phases/")

def organize_tests():
    """Organize test files"""
    print("Organizing test files...")
    
    # Move test files to appropriate locations
    test_files = [
        ("test_api_plugins.py", "tests/unit/test_api_plugins.py"),
        ("test_indian_policy_analysis.py", "tests/integration/test_indian_policy_analysis.py"),
        ("test_plugins.py", "tests/unit/test_plugins.py"),
        ("test_scraped_data_ingestion.py", "tests/integration/test_scraped_data_ingestion.py"),
        ("test_social_media_analysis.py", "tests/integration/test_social_media_analysis.py"),
        ("backend/tests/test_models.py", "tests/unit/test_models.py")
    ]
    
    for src, dst in test_files:
        if os.path.exists(src):
            # Ensure destination directory exists
            dst_dir = os.path.dirname(dst)
            Path(dst_dir).mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            print(f"Moved {src} to {dst}")

def organize_social_media_analysis():
    """Organize social media analysis files"""
    print("Organizing social media analysis files...")
    
    # Move social media analysis files to social_media_analysis directory
    sm_files = [
        "SOCIAL_MEDIA_ANALYSIS_FEATURES.md",
        "SOCIAL_MEDIA_ANALYSIS_TEST_RESULTS.md",
        "HIGH_SCRAPING_TOOLS_INTEGRATION.md"
    ]
    
    for sm_file in sm_files:
        if os.path.exists(sm_file):
            shutil.move(sm_file, f"social_media_analysis/{sm_file}")
            print(f"Moved {sm_file} to social_media_analysis/")

def organize_summaries():
    """Organize summary files"""
    print("Organizing summary files...")
    
    # Move summary files to docs directory
    summary_files = [
        "FINAL_SUMMARY.md",
        "IMPLEMENTATION_SUMMARY.md",
        "PLUGIN_IMPLEMENTATION_SUMMARY.md",
        "SUMMARY.md"
    ]
    
    for summary_file in summary_files:
        if os.path.exists(summary_file):
            shutil.move(summary_file, f"docs/{summary_file.lower()}")
            print(f"Moved {summary_file} to docs/")

def organize_docs():
    """Organize documentation files"""
    print("Organizing documentation files...")
    
    # Move documentation files to docs directory
    doc_files = [
        "ACTION_PLAN.md",
        "ENHANCEMENTS.md",
        "NEXT_STEPS.md",
        "PRODUCT_ROADMAP.md",
        "PROJECT_PLAN.md",
        "TECHNICAL_SPEC.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            # Determine appropriate subdirectory based on content
            if "SPEC" in doc_file or "PLAN" in doc_file:
                target_dir = "docs/specifications"
            elif "ROADMAP" in doc_file:
                target_dir = "docs/planning"
            else:
                target_dir = "docs"
                
            # Create target directory if needed
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            shutil.move(doc_file, f"{target_dir}/{doc_file}")
            print(f"Moved {doc_file} to {target_dir}/")

def organize_data():
    """Organize data files"""
    print("Organizing data files...")
    
    # Create data directory structure
    data_dirs = [
        "data/raw",
        "data/processed"
    ]
    
    for data_dir in data_dirs:
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {data_dir}")

def create_readme_files():
    """Create README files for each major directory"""
    readme_contents = {
        "backend/README.md": "# Backend\n\nThis directory contains all backend logic for Sovereign's Edict.",
        "frontend/README.md": "# Frontend\n\nThis directory contains the React frontend application.",
        "backend/plugins/README.md": "# Plugins\n\nThis directory contains modular plugins for data ingestion.",
        "data/README.md": "# Data\n\nThis directory contains real policy data and datasets for analysis.",
        "models/README.md": "# Models\n\nThis directory contains AI/ML models used in the application.",
        "docs/README.md": "# Documentation\n\nThis directory contains project documentation.",
        "tests/README.md": "# Tests\n\nThis directory contains all test files for the project.",
        "phases/README.md": "# Development Phases\n\nThis directory contains documentation for each development phase.",
        "social_media_analysis/README.md": "# Social Media Analysis\n\nThis directory contains documentation and resources for social media analysis features."
    }
    
    # Create docs subdirectory READMEs
    Path("docs/specifications").mkdir(parents=True, exist_ok=True)
    Path("docs/planning").mkdir(parents=True, exist_ok=True)
    
    readme_contents.update({
        "docs/specifications/README.md": "# Specifications\n\nThis directory contains technical specifications and project plans.",
        "docs/planning/README.md": "# Planning\n\nThis directory contains project planning documents.",
        "docs/architecture/README.md": "# Architecture\n\nThis directory contains architecture documentation."
    })
    
    for file_path, content in readme_contents.items():
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Created {file_path}")

def main():
    """Main function to organize the project"""
    print("🏛️  Organizing Sovereign's Edict Project Structure")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    # Organize components
    organize_phases()
    organize_tests()
    organize_social_media_analysis()
    organize_summaries()
    organize_docs()
    organize_data()
    
    # Create README files
    create_readme_files()
    
    print("=" * 50)
    print("✅ Project organization completed successfully!")
    print("\nDirectory structure:")
    print("""
Sovereign's Edict/
├── backend/
│   ├── api/          # API endpoints
│   ├── ingestion/    # Data ingestion modules
│   ├── mining/       # Argument mining core
│   ├── citation/     # Citation oracle
│   ├── fusion/       # Multi-source fusion engine
│   ├── amendment/    # Amendment generator
│   ├── compute/      # Compute management
│   ├── models/       # Data models
│   ├── plugins/      # Community plugins
│   ├── utils/        # Utility functions
│   └── tests/        # Unit tests
├── frontend/
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── tests/        # Frontend tests
├── data/             # Data files
│   ├── raw/          # Raw data files
│   ├── processed/    # Processed data files
│   └── sample/       # Sample data for testing
├── models/           # AI/ML models
├── docs/             # Documentation
│   ├── api/          # API documentation
│   ├── plugins/      # Plugin documentation
│   ├── specifications/ # Technical specifications
│   ├── planning/     # Planning documents
│   ├── architecture/  # Architecture documentation
│   └── user_guides/  # User guides
├── tests/            # Integration tests
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── e2e/          # End-to-end tests
├── phases/           # Development phases documentation
├── social_media_analysis/ # Social media analysis resources
└── README.md         # Project overview
    """)

if __name__ == "__main__":
    main()