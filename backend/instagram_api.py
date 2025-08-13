import requests
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InstagramAnalyzer:
    def __init__(self):
        """Initialize Instagram Basic Display API client"""
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.app_id = os.getenv('INSTAGRAM_APP_ID')
        self.app_secret = os.getenv('INSTAGRAM_APP_SECRET')
        self.base_url = 'https://graph.instagram.com'
        
        if not self.access_token:
            logger.warning("Instagram Access Token not found in environment variables")
    
    def get_user_info(self):
        """Get user's basic profile information"""
        if not self.access_token:
            logger.error("Instagram access token not configured")
            return None
        
        try:
            url = f"{self.base_url}/me"
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'id': data.get('id'),
                    'username': data.get('username'),
                    'account_type': data.get('account_type'),
                    'media_count': data.get('media_count', 0)
                }
            else:
                logger.error(f"Instagram API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Instagram user info: {e}")
            return None
    
    def get_user_media(self, limit=25):
        """Get user's recent media posts"""
        if not self.access_token:
            logger.error("Instagram access token not configured")
            return None
        
        try:
            url = f"{self.base_url}/me/media"
            params = {
                'fields': 'id,media_type,media_url,thumbnail_url,permalink,caption,timestamp,like_count,comments_count',
                'limit': min(limit, 25),  # API limit
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                media_list = []
                
                for media in data.get('data', []):
                    media_data = {
                        'id': media.get('id'),
                        'media_type': media.get('media_type'),
                        'media_url': media.get('media_url'),
                        'thumbnail_url': media.get('thumbnail_url'),
                        'permalink': media.get('permalink'),
                        'caption': media.get('caption', ''),
                        'timestamp': media.get('timestamp'),
                        'like_count': media.get('like_count', 0),
                        'comments_count': media.get('comments_count', 0)
                    }
                    media_list.append(media_data)
                
                logger.info(f"Retrieved {len(media_list)} Instagram media posts")
                return media_list
            else:
                logger.error(f"Instagram API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Instagram media: {e}")
            return None
    
    def get_media_insights(self, media_id):
        """Get insights for a specific media post (requires Instagram Business Account)"""
        if not self.access_token:
            logger.error("Instagram access token not configured")
            return None
        
        try:
            url = f"{self.base_url}/{media_id}/insights"
            params = {
                'metric': 'impressions,reach,engagement',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                insights = {}
                
                for insight in data.get('data', []):
                    metric_name = insight.get('name')
                    metric_values = insight.get('values', [])
                    if metric_values:
                        insights[metric_name] = metric_values[0].get('value', 0)
                
                return insights
            else:
                logger.warning(f"Instagram Insights not available: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Instagram insights: {e}")
            return None
    
    def generate_demo_data(self):
        """Generate demo data for testing without API access"""
        import random
        from datetime import datetime, timedelta
        
        logger.info("Generating Instagram demo data")
        
        # Demo user info
        user_info = {
            'id': 'demo_user_id',
            'username': 'demo_user',
            'account_type': 'PERSONAL',
            'media_count': 50
        }
        
        # Generate demo media posts
        media_types = ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']
        demo_captions = [
            "Beautiful sunset today! 🌅 #photography #nature",
            "New recipe tried! 🍝 #cooking #foodie",
            "Weekend vibes ✨ #weekend #relaxation",
            "Coffee and books ☕📚 #coffeetime #reading",
            "Workout complete! 💪 #fitness #health",
            "Amazing concert last night! 🎵 #music #concert",
            "Travel memories 🗺️ #travel #adventure",
            "Friends gathering 👥 #friends #goodtimes",
            "Art inspiration 🎨 #art #creativity",
            "Morning routine ☀️ #morning #mindfulness"
        ]
        
        media_list = []
        base_date = datetime.now()
        
        for i in range(20):
            post_date = base_date - timedelta(days=i, hours=random.randint(0, 23))
            
            media_data = {
                'id': f'demo_media_{i}',
                'media_type': random.choice(media_types),
                'media_url': f'https://example.com/demo_image_{i}.jpg',
                'thumbnail_url': f'https://example.com/demo_thumb_{i}.jpg',
                'permalink': f'https://instagram.com/p/demo_{i}',
                'caption': random.choice(demo_captions),
                'timestamp': post_date.isoformat(),
                'like_count': random.randint(10, 500),
                'comments_count': random.randint(0, 50)
            }
            media_list.append(media_data)
        
        return user_info, media_list
    
    def refresh_access_token(self):
        """Refresh long-lived access token"""
        if not self.access_token:
            return None
        
        try:
            url = f"{self.base_url}/refresh_access_token"
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                expires_in = data.get('expires_in')
                
                logger.info(f"Instagram access token refreshed, expires in {expires_in} seconds")
                return new_token
            else:
                logger.error(f"Failed to refresh Instagram token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error refreshing Instagram token: {e}")
            return None