#!/usr/bin/env python3
"""
Test script for file_scraper module
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from file_scraper import file_scraper

def test_file_scraper():
    """Test the file scraper"""
    print("🧪 Testing file_scraper...")
    print("=" * 60)
    
    try:
        # Read participants
        data = file_scraper.read_participants_from_file()
        
        print(f"\n📊 Results:")
        print(f"  Total participants: {len(data['participants'])}")
        print(f"  Shortcode: {data['shortcode']}")
        print(f"  Comments count: {data['comments_count']}")
        
        print(f"\n👥 First 5 participants:")
        for i, p in enumerate(data['participants'][:5], 1):
            print(f"  {i}. @{p['username']}")
        
        print(f"\n✅ Test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_scraper()
    sys.exit(0 if success else 1)
