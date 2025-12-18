import re
import instaloader
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path


class InstagramService:
    def __init__(self):
        # Configure Instaloader to look like a real browser (avoid bot detection)
        self.loader = instaloader.Instaloader(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            request_timeout=30.0,
            max_connection_attempts=3,
            sleep=True,  # Add random delays between requests
            quiet=False,
            compress_json=False
        )
        self.logged_in = False
        self.session_dir = Path(__file__).parent / "instagram_sessions"
        self.session_dir.mkdir(exist_ok=True)
    
    def load_session(self, username: str) -> bool:
        """Load a saved session from file"""
        try:
            session_file = self.session_dir / f"session-{username}"
            if session_file.exists():
                self.loader.load_session_from_file(username, str(session_file))
                self.logged_in = True
                print(f"✅ Loaded saved session for @{username}")
                return True
            return False
        except Exception as e:
            print(f"⚠️  Failed to load session: {e}")
            return False
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """Login to Instagram (tries saved session first, then password)"""
        if not username:
            return False
        
        # Try to load saved session first
        if self.load_session(username):
            return True
        
        # If no saved session, try password login
        if password:
            try:
                self.loader.login(username, password)
                self.logged_in = True
                
                # Save session for future use
                session_file = self.session_dir / f"session-{username}"
                self.loader.save_session_to_file(str(session_file))
                print(f"✅ Login successful and session saved for @{username}")
                
                return True
            except Exception as e:
                print(f"Login failed: {e}")
                return False
        return False
    
    def extract_shortcode(self, post_url: str) -> str:
        """Extract shortcode from Instagram URL"""
        # https://www.instagram.com/p/DSAYQxiDfwR/ -> DSAYQxiDfwR
        match = re.search(r'/p/([A-Za-z0-9_-]+)', post_url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Instagram post URL")
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from comment text"""
        # Find all @username mentions
        mentions = re.findall(r'@([a-zA-Z0-9._]+)', text)
        return list(set(mentions))  # Remove duplicates
    
    def scrape_post_comments(self, post_url: str) -> Dict:
        """Scrape all comments from an Instagram post using Playwright (browser automation)"""
        try:
            # Use Playwright scraper instead of Instaloader
            from playwright_scraper import scrape_post_with_playwright
            return scrape_post_with_playwright(post_url)
            
        except Exception as e:
            raise Exception(f"Failed to scrape post: {str(e)}")
    
    def check_user_follows(self, username: str, target_username: str) -> bool:
        """Check if a user follows a specific account"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            target_profile = instaloader.Profile.from_username(self.loader.context, target_username)
            
            # Check if target is in user's followees
            followees = set(profile.get_followees())
            return target_profile in followees
        except Exception as e:
            print(f"Error checking follow status: {e}")
            return False
    
    def check_profile_public(self, username: str) -> bool:
        """Check if a user's profile is public"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            return not profile.is_private
        except Exception as e:
            print(f"Error checking profile: {e}")
            return False
    
    def check_user_liked_post(self, username: str, shortcode: str) -> bool:
        """Check if a user liked a specific post (requires login)"""
        if not self.logged_in:
            # Cannot check likes without login
            return None
        
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            # Note: Instagram API doesn't easily expose who liked a post
            # This is a limitation - we may need to skip this validation
            # or require manual verification
            return None
        except Exception as e:
            print(f"Error checking like: {e}")
            return None
    
    def are_mutual_followers(self, username1: str, username2: str) -> bool:
        """Check if two users follow each other"""
        try:
            profile1 = instaloader.Profile.from_username(self.loader.context, username1)
            profile2 = instaloader.Profile.from_username(self.loader.context, username2)
            
            # Check if they follow each other
            followees1 = set(profile1.get_followees())
            followees2 = set(profile2.get_followees())
            
            return profile2 in followees1 and profile1 in followees2
        except Exception as e:
            print(f"Error checking mutual followers: {e}")
            return False
    
    def validate_participant(
        self, 
        username: str, 
        tagged_users: List[str],
        required_follows: List[str],
        shortcode: str,
        require_public: bool = True,
        require_mutual: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a participant against raffle rules
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if tagged at least one user
        if not tagged_users:
            errors.append("Não marcou nenhum amigo")
        
        # Check if profile is public
        if require_public:
            if not self.check_profile_public(username):
                errors.append("Perfil privado")
        
        # Check if follows required accounts
        for account in required_follows:
            if not self.check_user_follows(username, account):
                errors.append(f"Não segue @{account}")
        
        # Check mutual friendship with tagged users
        if require_mutual and tagged_users:
            for tagged in tagged_users:
                if not self.are_mutual_followers(username, tagged):
                    errors.append(f"Não é amigo de @{tagged}")
        
        # Note: Like checking is not implemented due to API limitations
        # This would require manual verification or Instagram login
        
        is_valid = len(errors) == 0
        return is_valid, errors


# Singleton instance
instagram_service = InstagramService()
