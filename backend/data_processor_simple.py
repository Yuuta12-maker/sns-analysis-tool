from datetime import datetime
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        """Initialize data processor"""
        pass
    
    def process_twitter_data(self, user_data, tweets_data, analysis_types):
        """Process Twitter data and return analysis results (simplified without pandas)"""
        try:
            if not tweets_data:
                return self._empty_result()
            
            # Basic stats
            stats = self._calculate_basic_stats(user_data, tweets_data)
            
            # Initialize result
            result = {
                'platform': 'twitter',
                'username': user_data['username'],
                'stats': stats,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Process each analysis type
            if 'engagement' in analysis_types:
                result['engagement_data'] = self._analyze_engagement(tweets_data)
            
            if 'hashtags' in analysis_types:
                result['hashtag_data'] = self._analyze_hashtags(tweets_data)
            
            if 'timing' in analysis_types:
                result['timing_data'] = self._analyze_timing(tweets_data)
            
            if 'content' in analysis_types:
                result['content_data'] = self._analyze_content(tweets_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Twitter data: {e}")
            return self._empty_result(error=str(e))
    
    def process_instagram_data(self, user_data, media_data, analysis_types):
        """Process Instagram data and return analysis results (simplified without pandas)"""
        try:
            if not media_data:
                return self._empty_result()
            
            # Basic stats for Instagram
            stats = self._calculate_instagram_stats(user_data, media_data)
            
            # Initialize result
            result = {
                'platform': 'instagram',
                'username': user_data['username'],
                'stats': stats,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Process each analysis type for Instagram
            if 'engagement' in analysis_types:
                result['engagement_data'] = self._analyze_instagram_engagement(media_data)
            
            if 'hashtags' in analysis_types:
                result['hashtag_data'] = self._analyze_instagram_hashtags(media_data)
            
            if 'timing' in analysis_types:
                result['timing_data'] = self._analyze_instagram_timing(media_data)
            
            if 'content' in analysis_types:
                result['content_data'] = self._analyze_instagram_content(media_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Instagram data: {e}")
            return self._empty_result(error=str(e))
    
    def _calculate_basic_stats(self, user_data, tweets_data):
        """Calculate basic statistics"""
        try:
            total_likes = sum(tweet['public_metrics']['like_count'] for tweet in tweets_data)
            total_retweets = sum(tweet['public_metrics']['retweet_count'] for tweet in tweets_data)
            total_replies = sum(tweet['public_metrics']['reply_count'] for tweet in tweets_data)
            
            stats = {
                'total_posts': len(tweets_data),
                'follower_count': user_data['public_metrics']['followers_count'],
                'following_count': user_data['public_metrics']['following_count'],
                'total_likes': total_likes,
                'total_retweets': total_retweets,
                'total_replies': total_replies,
                'avg_engagement': 0,
                'total_impressions': 0  # Not available in basic API
            }
            
            # Calculate average engagement rate
            if stats['total_posts'] > 0 and stats['follower_count'] > 0:
                total_engagement = stats['total_likes'] + stats['total_retweets'] + stats['total_replies']
                stats['avg_engagement'] = (total_engagement / stats['total_posts'] / stats['follower_count']) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating basic stats: {e}")
            return {
                'total_posts': 0,
                'follower_count': 0,
                'following_count': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0,
                'avg_engagement': 0,
                'total_impressions': 0
            }
    
    def _calculate_instagram_stats(self, user_data, media_data):
        """Calculate basic statistics for Instagram"""
        try:
            total_likes = sum(media.get('like_count', 0) for media in media_data)
            total_comments = sum(media.get('comments_count', 0) for media in media_data)
            
            stats = {
                'total_posts': len(media_data),
                'follower_count': 0,  # Not available in Basic Display API
                'following_count': 0,  # Not available in Basic Display API
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_retweets': 0,  # Not applicable for Instagram
                'avg_engagement': 0,
                'total_impressions': 0,  # Not available in Basic Display API
                'media_count': user_data.get('media_count', len(media_data))
            }
            
            # Calculate average engagement rate (likes + comments per post)
            if stats['total_posts'] > 0:
                total_engagement = stats['total_likes'] + stats['total_comments']
                stats['avg_engagement'] = total_engagement / stats['total_posts']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating Instagram stats: {e}")
            return {
                'total_posts': 0,
                'follower_count': 0,
                'following_count': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_retweets': 0,
                'avg_engagement': 0,
                'total_impressions': 0,
                'media_count': 0
            }
    
    def _analyze_engagement(self, tweets_data):
        """Analyze engagement over time (simplified)"""
        try:
            if not tweets_data:
                return {'labels': [], 'values': []}
            
            # Group by date
            daily_data = {}
            for tweet in tweets_data:
                # Simple date extraction
                date_str = tweet['created_at'][:10]  # YYYY-MM-DD
                engagement = (tweet['public_metrics']['like_count'] + 
                            tweet['public_metrics']['retweet_count'] + 
                            tweet['public_metrics']['reply_count'])
                
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(engagement)
            
            # Calculate averages
            labels = sorted(daily_data.keys())
            values = [sum(daily_data[date]) / len(daily_data[date]) for date in labels]
            
            return {'labels': labels, 'values': values}
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_instagram_engagement(self, media_data):
        """Analyze Instagram engagement over time (simplified)"""
        try:
            if not media_data:
                return {'labels': [], 'values': []}
            
            # Group by date
            daily_data = {}
            for media in media_data:
                # Simple date extraction
                date_str = media['timestamp'][:10]  # YYYY-MM-DD
                engagement = media.get('like_count', 0) + media.get('comments_count', 0)
                
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(engagement)
            
            # Calculate averages
            labels = sorted(daily_data.keys())
            values = [sum(daily_data[date]) / len(daily_data[date]) for date in labels]
            
            return {'labels': labels, 'values': values}
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram engagement: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_hashtags(self, tweets_data):
        """Analyze hashtag usage (simplified)"""
        try:
            all_hashtags = []
            for tweet in tweets_data:
                entities = tweet.get('entities', {})
                hashtags = entities.get('hashtags', [])
                for hashtag in hashtags:
                    all_hashtags.append(hashtag['tag'].lower())
            
            hashtag_counts = Counter(all_hashtags)
            top_hashtags = [
                {'hashtag': f"#{tag}", 'count': count} 
                for tag, count in hashtag_counts.most_common(10)
            ]
            
            return {'top_hashtags': top_hashtags, 'hashtag_performance': []}
            
        except Exception as e:
            logger.error(f"Error analyzing hashtags: {e}")
            return {'top_hashtags': [], 'hashtag_performance': []}
    
    def _analyze_instagram_hashtags(self, media_data):
        """Analyze Instagram hashtags (simplified)"""
        try:
            all_hashtags = []
            for media in media_data:
                caption = media.get('caption', '')
                if caption:
                    hashtags = re.findall(r'#(\w+)', caption.lower())
                    all_hashtags.extend(hashtags)
            
            hashtag_counts = Counter(all_hashtags)
            top_hashtags = [
                {'hashtag': f"#{tag}", 'count': count} 
                for tag, count in hashtag_counts.most_common(10)
            ]
            
            return {'top_hashtags': top_hashtags, 'hashtag_performance': []}
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram hashtags: {e}")
            return {'top_hashtags': [], 'hashtag_performance': []}
    
    def _analyze_timing(self, tweets_data):
        """Analyze timing patterns (simplified)"""
        try:
            hour_counts = [0] * 24
            for tweet in tweets_data:
                # Extract hour from timestamp
                timestamp = tweet['created_at']
                hour = int(timestamp[11:13])  # Extract hour
                hour_counts[hour] += 1
            
            hour_labels = [f"{hour:02d}:00" for hour in range(24)]
            return {'labels': hour_labels, 'values': hour_counts}
            
        except Exception as e:
            logger.error(f"Error analyzing timing: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_instagram_timing(self, media_data):
        """Analyze Instagram timing patterns (simplified)"""
        try:
            hour_counts = [0] * 24
            for media in media_data:
                # Extract hour from timestamp
                timestamp = media['timestamp']
                hour = int(timestamp[11:13])  # Extract hour
                hour_counts[hour] += 1
            
            hour_labels = [f"{hour:02d}:00" for hour in range(24)]
            return {'labels': hour_labels, 'values': hour_counts}
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram timing: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_content(self, tweets_data):
        """Analyze content patterns (simplified)"""
        try:
            all_words = []
            for tweet in tweets_data:
                text = tweet['text'].lower()
                clean_text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
                words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text)
                all_words.extend(words)
            
            word_counts = Counter(all_words)
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            filtered_words = [(word, count) for word, count in word_counts.most_common(20) if word not in stop_words]
            
            word_frequency = [
                {'word': word, 'count': count} 
                for word, count in filtered_words[:10]
            ]
            
            return {'word_frequency': word_frequency, 'content_types': []}
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {'word_frequency': [], 'content_types': []}
    
    def _analyze_instagram_content(self, media_data):
        """Analyze Instagram content patterns (simplified)"""
        try:
            # Content types
            content_types = Counter()
            all_words = []
            
            for media in media_data:
                media_type = media.get('media_type', 'UNKNOWN')
                content_types[media_type] += 1
                
                caption = media.get('caption', '')
                if caption:
                    clean_text = re.sub(r'#\w+|@\w+|http\S+|www\S+', '', caption.lower())
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text)
                    all_words.extend(words)
            
            content_type_list = [
                {'type': media_type, 'count': count}
                for media_type, count in content_types.items()
            ]
            
            word_counts = Counter(all_words)
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            filtered_words = [(word, count) for word, count in word_counts.most_common(20) if word not in stop_words]
            
            word_frequency = [
                {'word': word, 'count': count} 
                for word, count in filtered_words[:10]
            ]
            
            return {
                'content_types': content_type_list,
                'word_frequency': word_frequency
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram content: {e}")
            return {'content_types': [], 'word_frequency': []}
    
    def _empty_result(self, error=None):
        """Return empty result structure"""
        result = {
            'platform': 'unknown',
            'username': 'unknown',
            'stats': {
                'total_posts': 0,
                'follower_count': 0,
                'following_count': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0,
                'avg_engagement': 0,
                'total_impressions': 0
            },
            'engagement_data': {'labels': [], 'values': []},
            'hashtag_data': {'top_hashtags': [], 'hashtag_performance': []},
            'timing_data': {'labels': [], 'values': []},
            'content_data': {'word_frequency': [], 'content_types': []},
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        if error:
            result['error'] = error
        
        return result