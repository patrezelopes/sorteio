#!/usr/bin/env python3
"""
Utility script to clean up Playwright browser lock files
Run this if you get "Failed to create a ProcessSingleton" errors
"""

from pathlib import Path
import shutil

def cleanup_browser_locks():
    """Remove browser lock files and optionally the entire browser data directory"""
    browser_data_dir = Path(__file__).parent / "browser_data"
    
    if not browser_data_dir.exists():
        print("✅ No browser data directory found - nothing to clean")
        return
    
    # Remove lock file
    lock_file = browser_data_dir / "SingletonLock"
    if lock_file.exists():
        try:
            lock_file.unlink()
            print("🔓 Removed browser lock file")
        except Exception as e:
            print(f"❌ Error removing lock file: {e}")
    else:
        print("ℹ️  No lock file found")
    
    # Ask if user wants to remove entire browser data
    print("\nDo you want to remove the entire browser data directory?")
    print("This will log you out of Instagram and you'll need to login again.")
    response = input("Remove browser data? (y/N): ").strip().lower()
    
    if response == 'y':
        try:
            shutil.rmtree(browser_data_dir)
            print("🗑️  Removed browser data directory")
        except Exception as e:
            print(f"❌ Error removing browser data: {e}")
    else:
        print("✅ Browser data preserved")

if __name__ == "__main__":
    cleanup_browser_locks()
