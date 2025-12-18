"""
Quick Update Script - Apply New Features
Run this to check if your system is ready for the new features
"""

import os
import sys

def check_updates():
    """Check if system is ready for new features"""
    
    print("="*70)
    print("Waste Collection App - Feature Update Checker")
    print("="*70)
    print()
    
    issues = []
    warnings = []
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        issues.append("❌ app.py not found. Make sure you're in the waste_collection_app folder.")
    else:
        print("✓ Found app.py")
    
    if not os.path.exists('templates'):
        issues.append("❌ templates folder not found.")
    else:
        print("✓ Found templates folder")
    
    # Check for openpyxl
    try:
        import openpyxl
        print("✓ openpyxl is installed (needed for Excel export)")
    except ImportError:
        warnings.append("⚠️  openpyxl not installed. Run: pip install openpyxl")
    
    # Check pandas
    try:
        import pandas
        print("✓ pandas is installed")
    except ImportError:
        issues.append("❌ pandas not installed. Run: pip install pandas")
    
    # Check Flask
    try:
        import flask
        print("✓ Flask is installed")
    except ImportError:
        issues.append("❌ Flask not installed. Run: pip install Flask")
    
    print()
    print("="*70)
    
    if issues:
        print("CRITICAL ISSUES:")
        for issue in issues:
            print(issue)
        print()
        print("Fix these issues before updating.")
        return False
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(warning)
        print()
        print("Install missing packages: pip install openpyxl")
        print()
    
    if not issues and not warnings:
        print("✓ System is ready for the update!")
        print()
        print("Next steps:")
        print("1. Backup your current app.py and templates/admin_customers.html")
        print("2. Replace app.py with the new version")
        print("3. Replace templates/admin_customers.html with the new version")
        print("4. Restart your app: python app.py")
    
    print("="*70)
    
    return len(issues) == 0


def backup_files():
    """Backup current files"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\nCreating backups...")
    
    # Backup app.py
    if os.path.exists('app.py'):
        backup_name = f'app.py.backup_{timestamp}'
        shutil.copy2('app.py', backup_name)
        print(f"✓ Backed up app.py to {backup_name}")
    
    # Backup admin_customers.html
    template_path = 'templates/admin_customers.html'
    if os.path.exists(template_path):
        backup_name = f'templates/admin_customers.html.backup_{timestamp}'
        shutil.copy2(template_path, backup_name)
        print(f"✓ Backed up admin_customers.html to {backup_name}")
    
    print("\nBackup complete!")


if __name__ == '__main__':
    print()
    
    if check_updates():
        print()
        choice = input("Would you like to create backups of your current files? (yes/no): ")
        if choice.lower() in ['yes', 'y']:
            backup_files()
            print()
            print("Now you can safely replace the files with new versions.")
        else:
            print("Skipping backup. Make sure to backup manually!")
    
    print()