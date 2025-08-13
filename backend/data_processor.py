import pandas as pd
from datetime import datetime, timedelta
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        """Initialize data processor"""
        pass
    
    def process_twitter_data(self, user_data, tweets_data, analysis_types):
        """Process Twitter data and return analysis results"""
        try:
            if not tweets_data:
                return self._empty_result()
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(tweets_data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Basic stats
            stats = self._calculate_basic_stats(user_data, df)
            
            # Initialize result
            result = {
                'platform': 'twitter',
                'username': user_data['username'],
                'stats': stats,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Process each analysis type
            if 'engagement' in analysis_types:
                result['engagement_data'] = self._analyze_engagement(df)
            
            if 'hashtags' in analysis_types:
                result['hashtag_data'] = self._analyze_hashtags(df)
            
            if 'timing' in analysis_types:
                result['timing_data'] = self._analyze_timing(df)
            
            if 'content' in analysis_types:
                result['content_data'] = self._analyze_content(df)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Twitter data: {e}")
            return self._empty_result(error=str(e))
    
    def process_instagram_data(self, user_data, media_data, analysis_types):
        """Process Instagram data and return analysis results"""
        try:
            if not media_data:
                return self._empty_result()
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(media_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Basic stats for Instagram
            stats = self._calculate_instagram_stats(user_data, df)
            
            # Initialize result
            result = {
                'platform': 'instagram',
                'username': user_data['username'],
                'stats': stats,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Process each analysis type for Instagram
            if 'engagement' in analysis_types:
                result['engagement_data'] = self._analyze_instagram_engagement(df)
            
            if 'hashtags' in analysis_types:
                result['hashtag_data'] = self._analyze_instagram_hashtags(df)
            
            if 'timing' in analysis_types:
                result['timing_data'] = self._analyze_instagram_timing(df)
            
            if 'content' in analysis_types:
                result['content_data'] = self._analyze_instagram_content(df)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Instagram data: {e}")
            return self._empty_result(error=str(e))
    
    def _calculate_basic_stats(self, user_data, df):
        """Calculate basic statistics"""
        try:
            stats = {
                'total_posts': len(df),
                'follower_count': user_data['public_metrics']['followers_count'],
                'following_count': user_data['public_metrics']['following_count'],
                'total_likes': df['public_metrics'].apply(lambda x: x['like_count']).sum(),
                'total_retweets': df['public_metrics'].apply(lambda x: x['retweet_count']).sum(),
                'total_replies': df['public_metrics'].apply(lambda x: x['reply_count']).sum(),
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
    
    def _analyze_engagement(self, df):
        """Analyze engagement over time"""
        try:
            if df.empty:
                return {'labels': [], 'values': []}
            
            # Group by date and calculate engagement
            df['date'] = df['created_at'].dt.date
            daily_engagement = []
            
            for date in df['date'].unique():
                day_tweets = df[df['date'] == date]
                total_engagement = 0
                
                for _, tweet in day_tweets.iterrows():
                    metrics = tweet['public_metrics']
                    engagement = metrics['like_count'] + metrics['retweet_count'] + metrics['reply_count']
                    total_engagement += engagement
                
                avg_engagement = total_engagement / len(day_tweets) if len(day_tweets) > 0 else 0
                daily_engagement.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'engagement': avg_engagement
                })
            
            # Sort by date
            daily_engagement.sort(key=lambda x: x['date'])
            
            return {
                'labels': [item['date'] for item in daily_engagement],
                'values': [item['engagement'] for item in daily_engagement]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_hashtags(self, df):
        """Analyze hashtag usage and performance"""
        try:
            if df.empty:
                return {'top_hashtags': [], 'hashtag_performance': []}
            
            all_hashtags = []
            hashtag_performance = {}
            
            for _, tweet in df.iterrows():
                # Extract hashtags from entities
                entities = tweet.get('entities', {})
                hashtags = entities.get('hashtags', [])
                
                tweet_engagement = (
                    tweet['public_metrics']['like_count'] + 
                    tweet['public_metrics']['retweet_count'] + 
                    tweet['public_metrics']['reply_count']
                )
                
                for hashtag in hashtags:
                    tag = hashtag['tag'].lower()
                    all_hashtags.append(tag)
                    
                    if tag not in hashtag_performance:
                        hashtag_performance[tag] = {
                            'count': 0,
                            'total_engagement': 0,
                            'avg_engagement': 0
                        }
                    
                    hashtag_performance[tag]['count'] += 1
                    hashtag_performance[tag]['total_engagement'] += tweet_engagement
            
            # Calculate average engagement for each hashtag
            for tag in hashtag_performance:
                if hashtag_performance[tag]['count'] > 0:
                    hashtag_performance[tag]['avg_engagement'] = (
                        hashtag_performance[tag]['total_engagement'] / 
                        hashtag_performance[tag]['count']
                    )
            
            # Get top hashtags by frequency
            hashtag_counts = Counter(all_hashtags)
            top_hashtags = [
                {'hashtag': f"#{tag}", 'count': count} 
                for tag, count in hashtag_counts.most_common(10)
            ]
            
            # Get top performing hashtags
            top_performing = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['avg_engagement'],
                reverse=True
            )[:10]
            
            performance_data = [
                {
                    'hashtag': f"#{tag}",
                    'count': data['count'],
                    'avg_engagement': round(data['avg_engagement'], 2)
                }
                for tag, data in top_performing
            ]
            
            return {
                'top_hashtags': top_hashtags,
                'hashtag_performance': performance_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing hashtags: {e}")
            return {'top_hashtags': [], 'hashtag_performance': []}
    
    def _analyze_timing(self, df):
        """Analyze posting timing patterns"""
        try:
            if df.empty:
                return {'labels': [], 'values': []}
            
            # Analyze posting by hour of day
            df['hour'] = df['created_at'].dt.hour
            hourly_counts = df['hour'].value_counts().sort_index()
            
            # Create labels for hours
            hour_labels = [f"{hour:02d}:00" for hour in range(24)]
            hour_values = [hourly_counts.get(hour, 0) for hour in range(24)]
            
            return {
                'labels': hour_labels,
                'values': hour_values
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timing: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_content(self, df):
        """Analyze content patterns"""
        try:
            if df.empty:
                return {'word_frequency': [], 'content_types': []}
            
            # Extract all words from tweets
            all_words = []
            content_types = {
                'with_media': 0,
                'with_urls': 0,
                'with_hashtags': 0,
                'with_mentions': 0,
                'text_only': 0
            }
            
            for _, tweet in df.iterrows():
                text = tweet['text'].lower()
                
                # Remove URLs, mentions, and hashtags for word analysis
                clean_text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
                words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text)
                all_words.extend(words)
                
                # Categorize content type
                entities = tweet.get('entities', {})
                
                if entities.get('urls'):
                    content_types['with_urls'] += 1
                elif entities.get('hashtags'):
                    content_types['with_hashtags'] += 1
                elif entities.get('mentions'):
                    content_types['with_mentions'] += 1
                else:
                    content_types['text_only'] += 1
            
            # Get most common words
            word_counts = Counter(all_words)
            # Filter out common stop words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            filtered_words = [(word, count) for word, count in word_counts.most_common(20) if word not in stop_words]
            
            word_frequency = [
                {'word': word, 'count': count} 
                for word, count in filtered_words[:10]
            ]
            
            content_type_list = [
                {'type': type_name.replace('_', ' ').title(), 'count': count}
                for type_name, count in content_types.items()
            ]
            
            return {
                'word_frequency': word_frequency,
                'content_types': content_type_list
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {'word_frequency': [], 'content_types': []}
    
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
    
    def export_to_csv(self, data, filename):
        """Export analysis data to CSV"""
        try:
            # Create a comprehensive dataset
            export_data = []
            
            # Add basic stats
            stats = data.get('stats', {})
            export_data.append(['統計', '値'])
            for key, value in stats.items():
                export_data.append([key, value])
            
            # Add engagement data
            engagement = data.get('engagement_data', {})
            if engagement.get('labels'):
                export_data.append(['', ''])  # Empty row
                export_data.append(['日付', 'エンゲージメント'])
                for i, label in enumerate(engagement['labels']):
                    value = engagement['values'][i] if i < len(engagement['values']) else 0
                    export_data.append([label, value])
            
            # Save to CSV
            df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False, header=False, encoding='utf-8-sig')
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def _calculate_instagram_stats(self, user_data, df):
        """Calculate basic statistics for Instagram"""
        try:
            stats = {
                'total_posts': len(df),
                'follower_count': 0,  # Not available in Basic Display API
                'following_count': 0,  # Not available in Basic Display API
                'total_likes': df['like_count'].sum(),
                'total_comments': df['comments_count'].sum(),
                'total_retweets': 0,  # Not applicable for Instagram
                'avg_engagement': 0,
                'total_impressions': 0,  # Not available in Basic Display API
                'media_count': user_data.get('media_count', len(df))
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
    
    def _analyze_instagram_engagement(self, df):
        """Analyze Instagram engagement over time"""
        try:
            if df.empty:
                return {'labels': [], 'values': []}
            
            # Group by date and calculate engagement
            df['date'] = df['timestamp'].dt.date
            daily_engagement = []
            
            for date in df['date'].unique():
                day_posts = df[df['date'] == date]
                total_engagement = 0
                
                for _, post in day_posts.iterrows():
                    engagement = post['like_count'] + post['comments_count']
                    total_engagement += engagement
                
                avg_engagement = total_engagement / len(day_posts) if len(day_posts) > 0 else 0
                daily_engagement.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'engagement': avg_engagement
                })
            
            # Sort by date
            daily_engagement.sort(key=lambda x: x['date'])
            
            return {
                'labels': [item['date'] for item in daily_engagement],
                'values': [item['engagement'] for item in daily_engagement]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram engagement: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_instagram_hashtags(self, df):
        """Analyze Instagram hashtag usage"""
        try:
            if df.empty:
                return {'top_hashtags': [], 'hashtag_performance': []}
            
            all_hashtags = []
            hashtag_performance = {}
            
            for _, post in df.iterrows():
                caption = post.get('caption', '')
                if not caption:
                    continue
                
                # Extract hashtags from caption
                hashtags = re.findall(r'#(\w+)', caption.lower())
                post_engagement = post['like_count'] + post['comments_count']
                
                for hashtag in hashtags:
                    all_hashtags.append(hashtag)
                    
                    if hashtag not in hashtag_performance:
                        hashtag_performance[hashtag] = {
                            'count': 0,
                            'total_engagement': 0,
                            'avg_engagement': 0
                        }
                    
                    hashtag_performance[hashtag]['count'] += 1
                    hashtag_performance[hashtag]['total_engagement'] += post_engagement
            
            # Calculate average engagement for each hashtag
            for tag in hashtag_performance:
                if hashtag_performance[tag]['count'] > 0:
                    hashtag_performance[tag]['avg_engagement'] = (
                        hashtag_performance[tag]['total_engagement'] / 
                        hashtag_performance[tag]['count']
                    )
            
            # Get top hashtags by frequency
            hashtag_counts = Counter(all_hashtags)
            top_hashtags = [
                {'hashtag': f"#{tag}", 'count': count} 
                for tag, count in hashtag_counts.most_common(10)
            ]
            
            # Get top performing hashtags
            top_performing = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['avg_engagement'],
                reverse=True
            )[:10]
            
            performance_data = [
                {
                    'hashtag': f"#{tag}",
                    'count': data['count'],
                    'avg_engagement': round(data['avg_engagement'], 2)
                }
                for tag, data in top_performing
            ]
            
            return {
                'top_hashtags': top_hashtags,
                'hashtag_performance': performance_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram hashtags: {e}")
            return {'top_hashtags': [], 'hashtag_performance': []}
    
    def _analyze_instagram_timing(self, df):
        """Analyze Instagram posting timing patterns"""
        try:
            if df.empty:
                return {'labels': [], 'values': []}
            
            # Analyze posting by hour of day
            df['hour'] = df['timestamp'].dt.hour
            hourly_counts = df['hour'].value_counts().sort_index()
            
            # Create labels for hours
            hour_labels = [f"{hour:02d}:00" for hour in range(24)]
            hour_values = [hourly_counts.get(hour, 0) for hour in range(24)]
            
            return {
                'labels': hour_labels,
                'values': hour_values
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram timing: {e}")
            return {'labels': [], 'values': []}
    
    def _analyze_instagram_content(self, df):
        """Analyze Instagram content patterns"""
        try:
            if df.empty:
                return {'content_types': [], 'word_frequency': []}
            
            # Analyze content types
            content_types = df['media_type'].value_counts()
            content_type_list = [
                {'type': media_type, 'count': count}
                for media_type, count in content_types.items()
            ]
            
            # Extract words from captions
            all_words = []
            for _, post in df.iterrows():
                caption = post.get('caption', '')
                if caption:
                    # Remove hashtags, mentions, and URLs for word analysis
                    clean_text = re.sub(r'#\w+|@\w+|http\S+|www\S+', '', caption.lower())
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text)
                    all_words.extend(words)
            
            # Get most common words
            word_counts = Counter(all_words)
            # Filter out common stop words
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