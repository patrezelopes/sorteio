"""
File-based scraper for Instagram raffles
Reads participants from base.txt instead of scraping Instagram
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime


class FileBasedScraper:
    def __init__(self, base_file_path: str = "../base.txt"):
        self.base_file_path = Path(__file__).parent.parent / "base.txt"
    
    def read_participants_from_file(self) -> Dict:
        """Read participants from base.txt file"""
        participants = []
        
        if not self.base_file_path.exists():
            raise FileNotFoundError(f"File not found: {self.base_file_path}")
        
        print(f"📂 Reading participants from: {self.base_file_path}")
        
        with open(self.base_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                username = line.strip()
                
                # Skip empty lines
                if not username:
                    continue
                
                # Remove @ if present
                if username.startswith('@'):
                    username = username[1:]
                
                if username:
                    participants.append({
                        'username': username,
                        'text': f'Participante importado de base.txt (linha {line_num})',
                        'created_at': datetime.now(),
                        'likes': 0,
                        'tagged_users': []  # No tagged users from file
                    })
        
        print(f"✅ Imported {len(participants)} participants from file")
        
        return {
            'shortcode': 'file_import',
            'owner_username': '',
            'caption': '',
            'likes': 0,
            'comments_count': len(participants),
            'timestamp': datetime.now(),
            'url': 'file://base.txt',
            'participants': participants
        }


# Singleton instance
file_scraper = FileBasedScraper()
