import tweepy
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TwitterAnalyzer:
    def __init__(self):
        """Initialize Twitter API client"""
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Initialize Tweepy client
        self.client = None
        if self.bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API client: {e}")
        else:
            logger.warning("Twitter Bearer Token not found in environment variables")
    
    def get_user_info(self, username):
        """Get user information"""
        if not self.client:
            logger.error("Twitter API client not initialized")
            return None
        
        try:
            # Remove @ symbol if present
            username = username.lstrip('@')
            
            user = self.client.get_user(
                username=username,
                user_fields=['public_metrics', 'created_at', 'description', 'verified']
            )
            
            if user.data:
                return {
                    'id': user.data.id,
                    'username': user.data.username,
                    'name': user.data.name,
                    'description': user.data.description,
                    'verified': user.data.verified,
                    'created_at': user.data.created_at,
                    'public_metrics': user.data.public_metrics
                }
            else:
                logger.error(f"User @{username} not found")
                return None
                
        except tweepy.Unauthorized:
            logger.error("Twitter API: Unauthorized access")
            return None
        except tweepy.NotFound:
            logger.error(f"User @{username} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def get_user_tweets(self, username, days=30, max_results=100):
        """Get user's recent tweets"""
        if not self.client:
            logger.error("Twitter API client not initialized")
            return None
        
        try:
            # Remove @ symbol if present
            username = username.lstrip('@')
            
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                logger.error(f"User @{username} not found")
                return None
            
            user_id = user.data.id
            
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Get tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                start_time=start_time,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                exclude=['retweets', 'replies']  # Focus on original tweets
            )
            
            if tweets.data:
                tweet_list = []
                for tweet in tweets.data:
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'public_metrics': tweet.public_metrics,
                        'entities': getattr(tweet, 'entities', {}),
                        'context_annotations': getattr(tweet, 'context_annotations', [])
                    }
                    tweet_list.append(tweet_data)
                
                logger.info(f"Retrieved {len(tweet_list)} tweets for @{username}")
                return tweet_list
            else:
                logger.warning(f"No tweets found for @{username}")
                return []
                
        except tweepy.Unauthorized:
            logger.error("Twitter API: Unauthorized access")
            return None
        except tweepy.TooManyRequests:
            logger.error("Twitter API: Rate limit exceeded")
            return None
        except Exception as e:
            logger.error(f"Error getting user tweets: {e}")
            return None
    
    def search_tweets(self, query, days=7, max_results=100):
        """Search for tweets with a specific query"""
        if not self.client:
            logger.error("Twitter API client not initialized")
            return None
        
        try:
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Search tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                start_time=start_time,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'context_annotations'],
                expansions=['author_id']
            )
            
            if tweets.data:
                tweet_list = []
                users = {user.id: user for user in tweets.includes.get('users', [])}
                
                for tweet in tweets.data:
                    author = users.get(tweet.author_id, {})
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'public_metrics': tweet.public_metrics,
                        'author': {
                            'id': tweet.author_id,
                            'username': getattr(author, 'username', 'unknown'),
                            'name': getattr(author, 'name', 'unknown')
                        },
                        'context_annotations': getattr(tweet, 'context_annotations', [])
                    }
                    tweet_list.append(tweet_data)
                
                logger.info(f"Found {len(tweet_list)} tweets for query: {query}")
                return tweet_list
            else:
                logger.warning(f"No tweets found for query: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return None
    
    def get_hashtag_analytics(self, hashtag, days=7):
        """Get analytics for a specific hashtag"""
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        tweets = self.search_tweets(hashtag, days=days)
        if not tweets:
            return None
        
        analytics = {
            'hashtag': hashtag,
            'total_tweets': len(tweets),
            'total_likes': sum(tweet['public_metrics']['like_count'] for tweet in tweets),
            'total_retweets': sum(tweet['public_metrics']['retweet_count'] for tweet in tweets),
            'total_replies': sum(tweet['public_metrics']['reply_count'] for tweet in tweets),
            'avg_engagement': 0,
            'top_tweets': []
        }
        
        # Calculate average engagement
        if analytics['total_tweets'] > 0:
            total_engagement = analytics['total_likes'] + analytics['total_retweets'] + analytics['total_replies']
            analytics['avg_engagement'] = total_engagement / analytics['total_tweets']
        
        # Get top performing tweets
        sorted_tweets = sorted(
            tweets, 
            key=lambda x: x['public_metrics']['like_count'] + x['public_metrics']['retweet_count'],
            reverse=True
        )
        analytics['top_tweets'] = sorted_tweets[:5]
        
        return analytics