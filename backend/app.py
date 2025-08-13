from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import custom modules
from twitter_api import TwitterAnalyzer
from data_processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize analyzers
twitter_analyzer = TwitterAnalyzer()
data_processor = DataProcessor()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze SNS data"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(key in data for key in ['platform', 'username', 'period']):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        platform = data['platform']
        username = data['username']
        period = int(data['period'])
        analysis_types = data.get('analysis_types', ['engagement'])
        
        logger.info(f"Starting analysis for {platform}/@{username} for {period} days")
        
        if platform == 'twitter':
            # Get Twitter data
            user_data = twitter_analyzer.get_user_info(username)
            if not user_data:
                return jsonify({'error': 'User not found or API error'}), 404
            
            tweets_data = twitter_analyzer.get_user_tweets(username, period)
            if not tweets_data:
                return jsonify({'error': 'No tweets found or API error'}), 404
            
            # Process data
            result = data_processor.process_twitter_data(
                user_data, tweets_data, analysis_types
            )
            
        elif platform == 'instagram':
            # Instagram implementation would go here
            return jsonify({'error': 'Instagram analysis not yet implemented'}), 501
        
        else:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        logger.info(f"Analysis completed for {platform}/@{username}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/export/sheets', methods=['POST'])
def export_to_sheets():
    """Export data to Google Sheets"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Google Sheets export implementation would go here
        # For now, return a mock response
        return jsonify({
            'success': True,
            'sheet_url': 'https://docs.google.com/spreadsheets/d/mock-sheet-id',
            'message': 'Google Sheets export is not yet implemented'
        })
        
    except Exception as e:
        logger.error(f"Google Sheets export error: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check for required environment variables
    required_vars = ['TWITTER_BEARER_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Please set up your .env file with the required API keys")
    
    # Run the app
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)