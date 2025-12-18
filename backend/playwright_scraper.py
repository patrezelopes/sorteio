"""
Instagram scraper using Playwright (real browser automation)
This bypasses Instagram's bot detection by using a real browser
"""

import re
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
import time
import shutil

# iPhone 12 Pro device configuration (manual, since devices may not be available)
IPHONE_12_PRO = {
    'viewport': {'width': 1920, 'height': 1080},
    'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
}



class PlaywrightInstagramScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.logged_in = False
        self.user_data_dir = Path(__file__).parent / "browser_data"
        self.user_data_dir.mkdir(exist_ok=True)
        
    async def init_browser(self, headless: bool = True):
        """Initialize Playwright browser with persistent context"""
        try:
            # Clean up lock files if they exist (fixes ProcessSingleton error)
            lock_file = self.user_data_dir / "SingletonLock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                    print("🔓 Removed stale browser lock file")
                except Exception as e:
                    print(f"⚠️  Could not remove lock file: {e}")
            
            playwright = await async_playwright().start()
            
            # Build args list
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
            
            # Add DevTools auto-open when not headless
            if not headless:
                browser_args.append('--auto-open-devtools-for-tabs')
            
            # Use persistent context to save cookies and login state
            self.context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=headless,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                args=browser_args,
                devtools=not headless  # Open DevTools automatically when not headless
            )
            
            # Get the default page or create new one
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
                
        except Exception as e:
            error_msg = str(e)
            if "Executable doesn't exist" in error_msg or "chromium" in error_msg.lower():
                raise Exception(
                    "❌ Playwright browsers not installed!\n\n"
                    "Please run the following command to install:\n"
                    "  cd backend\n"
                    "  uv run playwright install chromium\n\n"
                    f"Original error: {error_msg}"
                )
            raise Exception(f"Failed to initialize browser: {error_msg}")
        
    async def close_browser(self):
        """Close browser context"""
        if hasattr(self, 'context') and self.context:
            await self.context.close()
    
    def cleanup_browser_data(self):
        """Clean up browser data directory and lock files"""
        try:
            lock_file = self.user_data_dir / "SingletonLock"
            if lock_file.exists():
                lock_file.unlink()
                print("🔓 Removed browser lock file")
            
            # Optionally remove entire browser data directory
            # Uncomment if you want to start fresh each time
            # if self.user_data_dir.exists():
            #     shutil.rmtree(self.user_data_dir)
            #     print("🗑️  Removed browser data directory")
        except Exception as e:
            print(f"⚠️  Error cleaning up browser data: {e}")
    
    def extract_shortcode(self, post_url: str) -> str:
        """Extract shortcode from Instagram URL"""
        match = re.search(r'/p/([A-Za-z0-9_-]+)', post_url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Instagram post URL")
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from comment text"""
        mentions = re.findall(r'@([a-zA-Z0-9._]+)', text)
        return list(set(mentions))
    
    async def login(self, username: str, password: str) -> bool:
        """Login to Instagram (only needed once, session persists)"""
        try:
            if not hasattr(self, 'page'):
                await self.init_browser(headless=False)
            
            page = self.page
            
            # Go to Instagram
            await page.goto('https://www.instagram.com/accounts/login/')
            await page.wait_for_timeout(2000)
            
            # Check if already logged in
            if 'accounts/login' not in page.url:
                print("✅ Already logged in from previous session!")
                self.logged_in = True
                return True
            
            # Fill login form
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)
            
            # Click login button
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            
            # Check if login was successful
            if 'challenge' in page.url or 'two_factor' in page.url:
                print("⚠️  Login requires additional verification")
                print("   Please complete verification in the browser window")
                print("   Session will be saved after verification")
                return False
            
            self.logged_in = True
            print(f"✅ Login successful for @{username}")
            print(f"💾 Session saved - you won't need to login again!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    async def scrape_post_comments(self, post_url: str, max_comments: int = 500) -> Dict:
        """Scrape comments from Instagram post using browser automation"""
        # Check if context exists and is still valid
        if not hasattr(self, 'context') or self.context is None:
            print("🔄 Initializing browser for the first time...")
            await self.init_browser(headless=False)
        
        # Create a new page for this scrape with MOBILE EMULATION
        # Flow: blank page → DevTools → mobile mode → navigate to comments
        page = None
        try:
            # Step 1: Open blank page first
            page = await self.context.new_page()
            print("📄 Página em branco aberta")
            await page.goto('about:blank')
            await page.wait_for_timeout(500)
            
            # Step 2: DevTools opens automatically (configured in init_browser)
            print("🔧 DevTools aberto automaticamente")
            
            # Step 3: Configure mobile emulation (simulates Ctrl+Shift+M)
            await page.set_viewport_size(IPHONE_12_PRO['viewport'])
            await page.set_extra_http_headers({
                'User-Agent': IPHONE_12_PRO['userAgent']
            })
            print("📱 Modo mobile ativado (iPhone 12 Pro)")
            print("💡 Aguardando 3 segundos para estabilizar...")
            await page.wait_for_timeout(3000)  # Delay de 3 segundos após modo mobile
            
        except Exception as e:
            # If context is closed, reinitialize
            print(f"⚠️  Context was closed, reinitializing browser...")
            await self.init_browser(headless=False)
            page = await self.context.new_page()
            await page.goto('about:blank')
            await page.wait_for_timeout(1000)
            await page.set_viewport_size(IPHONE_12_PRO['viewport'])
            await page.set_extra_http_headers({
                'User-Agent': IPHONE_12_PRO['userAgent']
            })
        
        try:
            shortcode = self.extract_shortcode(post_url)
            
            # Step 4: NOW navigate to COMMENTS page (after mobile is configured)
            comments_url = f"https://www.instagram.com/p/{shortcode}/comments/"
            print(f"🌐 Navegando para: {comments_url}")
            await page.goto(comments_url, wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(500)  # Reduzido para 500ms (ultra rápido)
            
            # Verify we're on the comments page
            current_url = page.url
            print(f"📍 URL atual: {current_url}")
            
            if '/comments/' not in current_url:
                print(f"⚠️  AVISO: Não estamos na página de comments!")
                print(f"   Esperado: {comments_url}")
                print(f"   Atual: {current_url}")
                # Try to navigate again
                print("🔄 Tentando navegar novamente...")
                await page.goto(comments_url, wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(800)  # Reduzido para 800ms
                current_url = page.url
                print(f"📍 Nova URL: {current_url}")
            
            
            # Get post metadata
            post_data = {
                'shortcode': shortcode,
                'owner_username': '',
                'caption': '',
                'likes': 0,
                'comments_count': 0,
                'timestamp': datetime.now(),
                'url': post_url,
                'participants': []
            }
            
            # Try to get owner username
            try:
                owner_element = await page.query_selector('a[href^="/"][href$="/"]')
                if owner_element:
                    owner_href = await owner_element.get_attribute('href')
                    post_data['owner_username'] = owner_href.strip('/')
            except:
                pass
            
            # Wait for comments section to load (try multiple selectors)
            print("🔍 Waiting for comments to load...")
            
            # Try different selectors that Instagram might use
            comment_selectors = [
                'ul ul li',  # Nested list items (common in Instagram)
                'article ul li',  # Comments in article
                '[role="button"]:has-text("comment")',  # Comment button
                'span:has-text("@")',  # Any mention
            ]
            
            comments_found = False
            for selector in comment_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    print(f"  ✅ Found comments using selector: {selector}")
                    comments_found = True
                    break
                except:
                    continue
            
            if not comments_found:
                print("  ⚠️  No comments container found, will try to extract anyway...")
            
            # Give it extra time for dynamic content
            await page.wait_for_timeout(500)  # Reduzido para 500ms
            
            # Scroll to load comments - FIND THE SCROLLABLE CONTAINER
            print("📜 Carregando TODOS os comentários (rolando container)...")
            print("=" * 60)
            previous_comment_count = 0
            no_change_count = 0
            max_attempts = 20  # Reduzido para 20 (muito mais rápido)
            
            # Try to find the scrollable comments container
            print("🔍 Procurando container de comentários...")
            scrollable_container = None
            
            # Try to find the main scrollable element
            container_selectors = [
                'div[style*="overflow"]',  # Any div with overflow
                'article',  # Main article
                'main',  # Main content
            ]
            
            for scroll_attempt in range(max_attempts):
                try:
                    # Wrap entire iteration in timeout (2 seconds max per iteration)
                    async def scroll_iteration():
                        # Count current comments (use a more generic selector)
                        current_elements = await page.query_selector_all('a[href^="/"][role="link"]')
                        current_count = len(current_elements)
                        
                        # Visual progress bar
                        progress = int((scroll_attempt / max_attempts) * 40)
                        bar = "█" * progress + "░" * (40 - progress)
                        print(f"\r  [{bar}] {scroll_attempt + 1}/{max_attempts} | 💬 {current_count} links encontrados", end="", flush=True)
                        
                        # Execute all scroll methods in one go (faster)
                        try:
                            # Combined scroll: page + containers + mouse wheel
                            await page.evaluate('''
                                () => {
                                    // Scroll page
                                    window.scrollTo(0, document.body.scrollHeight);
                                    
                                    // Scroll all containers
                                    const scrollables = document.querySelectorAll('div[style*="overflow"], article, main');
                                    scrollables.forEach(el => {
                                        if (el.scrollHeight > el.clientHeight) {
                                            el.scrollTop = el.scrollHeight;
                                        }
                                    });
                                }
                            ''')
                            
                            # Mouse wheel and keyboard in parallel
                            await page.mouse.wheel(0, 10000)
                            await page.keyboard.press('End')
                            
                            # Reduced wait time - ultra rápido
                            await page.wait_for_timeout(150)  # Reduzido para 150ms
                        except Exception as e:
                            # If scroll fails, just continue
                            pass
                        
                        return current_count
                    
                    # Execute with timeout (1 segundo por iteração)
                    current_count = await asyncio.wait_for(scroll_iteration(), timeout=1.0)
                    
                except asyncio.TimeoutError:
                    print(f"\n  ⚠️  Timeout na iteração {scroll_attempt + 1}, continuando...")
                    current_count = previous_comment_count
                except Exception as e:
                    print(f"\n  ⚠️  Erro na iteração {scroll_attempt + 1}: {e}")
                    current_count = previous_comment_count
                
                # Try to click "Load more comments" buttons
                try:
                    load_more_selectors = [
                        'button:has-text("Load more comments")',
                        'button:has-text("View more comments")',
                        'button:has-text("Ver mais comentários")',
                        'svg[aria-label*="Load"]',
                        'div[role="button"]',
                    ]
                    
                    for selector in load_more_selectors:
                        try:
                            load_more = await page.query_selector(selector)
                            if load_more:
                                await load_more.click()
                                print(f"\n  ⏳ Clicou em botão de carregar mais")
                                await page.wait_for_timeout(500)  # Reduzido para 500ms
                                break
                        except:
                            continue
                except:
                    pass
                
                # Check if we got new comments
                if current_count == previous_comment_count:
                    no_change_count += 1
                    print(f"\n  ⏸️  Sem mudanças ({no_change_count}/1)", end="", flush=True)
                    if no_change_count >= 1:  # Para após 1 tentativa (muito mais rápido)
                        print(f"\n  ✅ Finalizado! Total: {current_count} links encontrados")
                        print("=" * 60)
                        break
                else:
                    no_change_count = 0
                    previous_comment_count = current_count
                
                # Early exit if we have a good amount of comments and no change
                if current_count > 50 and no_change_count >= 1:
                    print(f"\n  ✅ Finalizado antecipadamente! Total: {current_count} links")
                    print("=" * 60)
                    break
            
            print(f"\n📊 Scroll completo! Total de {previous_comment_count} links encontrados")
            
            # Extract comments - CONTAINER-BASED APPROACH
            print("💬 Extraindo comentários...")
            
            # Find comment containers instead of all links
            # This prevents clicking on tagged user links within comments
            try:
                # Try multiple selectors for comment containers
                comment_containers = []
                container_selectors = [
                    'ul ul li',  # Nested list items (common in Instagram)
                    'article ul li',  # Comments in article
                    'div[role="button"]',  # Comment containers with button role
                ]
                
                for selector in container_selectors:
                    try:
                        containers = await page.query_selector_all(selector)
                        if len(containers) > len(comment_containers):
                            comment_containers = containers
                            print(f"  ✓ Usando seletor: {selector}")
                            break
                    except:
                        continue
                
                print(f"  ✓ Encontrados {len(comment_containers)} containers de comentários")
            except Exception as e:
                print(f"  ⚠️  Erro ao buscar containers: {e}")
                comment_containers = []
            
            comments = []
            seen_usernames = set()
            processed = 0
            max_to_process = min(len(comment_containers), 500)  # Limit processing to avoid hanging
            
            print(f"  🔄 Processando até {max_to_process} containers...")
            
            for container in comment_containers[:max_to_process]:  # Limit the loop
                try:
                    processed += 1
                    if processed % 50 == 0:  # Progress every 50 items
                        print(f"\r  📊 Processados: {processed}/{max_to_process} | Comentários válidos: {len(comments)}", end="", flush=True)
                    
                    # Get the FIRST link in this container (the comment author)
                    # This avoids clicking on tagged user links
                    author_link = await container.query_selector('a[href^="/"][role="link"]')
                    if not author_link:
                        continue
                    
                    href = await author_link.get_attribute('href')
                    if not href or href == '/' or '/p/' in href or '/reel/' in href:
                        continue
                    
                    # Extract username from href (remove leading/trailing slashes)
                    username = href.strip('/').split('/')[0]
                    
                    # Skip if already processed or is post owner
                    if not username or username in seen_usernames or username == post_data.get('owner_username'):
                        continue
                    
                    # Get text content from the container
                    text_content = await container.text_content()
                    
                    if not text_content or len(text_content.strip()) < 3:
                        continue
                    
                    # Look for @ mentions in the text
                    mentions = self.extract_mentions(text_content)
                    
                    # Only add if there are mentions (requirement for raffle)
                    if mentions:
                        comment_data = {
                            'username': username,
                            'text': text_content.strip()[:500],  # Limit text length
                            'created_at': datetime.now(),
                            'likes': 0,
                            'tagged_users': mentions
                        }
                        comments.append(comment_data)
                        seen_usernames.add(username)
                    
                except Exception as e:
                    continue
            
            post_data['participants'] = comments
            post_data['comments_count'] = len(comments)
            
            print(f"✅ Collected {len(comments)} comments with mentions!")
            
            # Close page and browser context
            await page.close()
            print("🔒 Fechando navegador...")
            await self.close_browser()
            
            return post_data
            
        except Exception as e:
            if page:
                await page.close()
            await self.close_browser()
            raise Exception(f"Failed to scrape post: {str(e)}")


# Singleton instance
playwright_scraper = PlaywrightInstagramScraper()
