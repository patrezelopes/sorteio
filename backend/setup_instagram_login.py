"""
Helper script to login to Instagram once and save the session
Run this script once to login, then the session will persist forever
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright_scraper import playwright_scraper


async def do_login():
    """Interactive login that saves session"""
    print("=" * 60)
    print("🔐 INSTAGRAM LOGIN - ONE TIME SETUP")
    print("=" * 60)
    
    # Load credentials from .env
    load_dotenv()
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")
    
    if not username or not password:
        print("\n⚠️  No credentials found in .env file!")
        print("Please add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to backend/.env\n")
        return
    
    print(f"\n📋 Using credentials from .env:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print("\nThis will open a browser window for you to login.")
    print("After login, the session will be saved and you won't")
    print("need to login again!\n")
    
    input("Press Enter to continue...")
    
    print("\n🌐 Opening browser...")
    await playwright_scraper.init_browser(headless=False)
    
    success = await playwright_scraper.login(username, password)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print("\n💾 Session saved in browser_data/")
        print("🎉 You can now use the system without logging in again!")
        print("\nNext steps:")
        print("1. Start the backend: uv run python main.py")
        print("2. Use the Instagram raffle feature normally")
        print("3. Browser will remember your login!\n")
    else:
        print("\n" + "=" * 60)
        print("⚠️  LOGIN INCOMPLETE")
        print("=" * 60)
        print("\nIf Instagram asked for verification:")
        print("1. Complete the verification in the browser")
        print("2. Wait for it to redirect to Instagram home")
        print("3. Press Enter here to save the session")
        
        input("\nPress Enter after completing verification...")
        print("💾 Session saved!")
    
    print("\nClosing browser...")
    await playwright_scraper.close_browser()
    print("Done!\n")


if __name__ == "__main__":
    asyncio.run(do_login())
