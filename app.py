"""
Flask Backend for Sentiment Classification App
Enhanced version with logging, better error handling, and input validation
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import pandas as pd
from datetime import datetime
from extensions import db, jwt, limiter
from auth import auth_bp
from models import Analysis
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from model_loader import predict_sentiment_bert, predict_aspect_sentiment, is_model_loaded, reload_model
from scraper import get_youtube_comments
from train import train
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentiment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-in-production'

# Global Training Status
TRAINING_STATUS = {
    'is_training': False,
    'message': '',
    'timestamp': None
}

# Initialize Extensions
db.init_app(app)
jwt.init_app(app)
limiter.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)

# Create Database Tables
with app.app_context():
    db.create_all()

# Configuration constants
MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 1000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/classify', methods=['POST'])
def classify_sentiment():
    """
    API endpoint to classify sentiment from text input
    {
        "text_input": "Your text here"
    }
    
    Returns JSON format:
    {
        "status": "success",
        "sentiment": "Positif/Negatif/Netral",
        "text_length": 123
    }
    
    Error responses:
    - 400: Invalid input (missing, empty, too short, too long)
    - 500: Server error during processing
    """
    try:
        # Log incoming request
        logger.info(f"Received classification request from {request.remote_addr}")
        
        # Validate Content-Type
        if not request.is_json:
            logger.warning("Request without JSON content-type")
            return jsonify({
                'status': 'error',
                'message': 'Content-Type harus application/json'
            }), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        # Check if data exists
        if data is None:
            logger.warning("Empty JSON body")
            return jsonify({
                'status': 'error',
                'message': 'Request body tidak valid'
            }), 400
        
        # Extract text input
        text_input = data.get('text_input', '')
        
        # Validate input exists
        if not text_input or text_input.strip() == '':
            logger.warning("Empty text input received")
            return jsonify({
                'status': 'error',
                'message': 'Teks tidak boleh kosong'
            }), 400
        
        # Clean and get text length
        text_input = text_input.strip()
        text_length = len(text_input)
        
        # Validate minimum length
        if text_length < MIN_TEXT_LENGTH:
            logger.warning(f"Text too short: {text_length} characters")
            return jsonify({
                'status': 'error',
                'message': f'Teks terlalu pendek (minimal {MIN_TEXT_LENGTH} karakter)'
            }), 400
        
        # Validate maximum length
        if text_length > MAX_TEXT_LENGTH:
            logger.warning(f"Text too long: {text_length} characters")
            return jsonify({
                'status': 'error',
                'message': f'Teks terlalu panjang (maksimal {MAX_TEXT_LENGTH} karakter)'
            }), 400
        
        # Log the analysis
        logger.info(f"Analyzing text ({text_length} characters): {text_input[:100]}...")
        
        # Get sentiment prediction
        sentiment, confidence = predict_sentiment_bert(text_input)
        
        # Get aspect-based sentiment
        aspects = predict_aspect_sentiment(text_input)
        
        # Save to DB if authenticated
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            if current_user_id:
                analysis = Analysis(
                    user_id=current_user_id,
                    text=text_input,
                    sentiment=sentiment,
                    confidence=confidence
                )
                db.session.add(analysis)
                db.session.commit()
                logger.info(f"Analysis saved for user {current_user_id}")
        except Exception as e:
            logger.warning(f"Failed to save analysis history: {e}")
            # Don't fail the request just because history saving failed
        
        # Return successful response
        response = {
            'status': 'success',
            'sentiment': sentiment,
            'confidence': confidence,
            'aspects': aspects,
            'text_length': text_length,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Classification successful: {sentiment}, Aspects: {len(aspects)}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Input tidak valid'
        }), 400
    
    except Exception as e:
        # Handle any unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Terjadi kesalahan pada server. Silakan coba lagi.'
        }), 500


@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    """
    Get analysis history for the current user
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Analysis.query.filter_by(user_id=current_user_id)\
        .order_by(Analysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
        
    history = [item.to_dict() for item in pagination.items]
    
    return jsonify({
        'status': 'success',
        'history': history,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route('/api/stats/trend', methods=['GET'])
@jwt_required()
def get_sentiment_trend():
    """
    Get daily sentiment counts for the last 7 days
    """
    current_user_id = get_jwt_identity()
    from sqlalchemy import func, text
    from datetime import timedelta
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Query to group by date and sentiment
    # SQLite-specific date formatting
    results = db.session.query(
        func.date(Analysis.created_at).label('date'),
        Analysis.sentiment,
        func.count(Analysis.id)
    ).filter(
        Analysis.user_id == current_user_id,
        Analysis.created_at >= seven_days_ago
    ).group_by(
        func.date(Analysis.created_at),
        Analysis.sentiment
    ).all()
    
    # Process results
    dates = []
    # Create a map for easy lookup
    data_map = {}
    
    # Initialize last 7 days
    for i in range(7):
        d = (seven_days_ago + timedelta(days=i+1)).strftime('%Y-%m-%d')
        dates.append(d)
        data_map[d] = {'Positif': 0, 'Negatif': 0, 'Netral': 0}
        
    for r in results:
        date_str = r[0]
        sentiment = r[1]
        count = r[2]
        if date_str in data_map:
            data_map[date_str][sentiment] = count
            
    # Format for Chart.js
    response = {
        'dates': dates,
        'positive': [data_map[d]['Positif'] for d in dates],
        'negative': [data_map[d]['Negatif'] for d in dates],
        'neutral': [data_map[d]['Netral'] for d in dates]
    }
    
    return jsonify(response), 200


@app.route('/api/stats/wordcloud', methods=['GET'])
@jwt_required()
def get_wordcloud_data():
    """
    Get word frequency for word cloud
    """
    current_user_id = get_jwt_identity()
    import re
    from collections import Counter
    
    # Get all text from user's history
    analyses = Analysis.query.filter_by(user_id=current_user_id).all()
    
    if not analyses:
        return jsonify([]), 200
        
    all_text = " ".join([a.text.lower() for a in analyses])
    
    # Simple tokenization and cleanup
    # Remove non-alphanumeric characters
    words = re.findall(r'\w+', all_text)
    
    # Indonesian Stopwords (Basic list)
    stopwords = set([
        'yang', 'di', 'dan', 'itu', 'dengan', 'untuk', 'tidak', 'ini', 'dari',
        'dalam', 'akan', 'pada', 'juga', 'saya', 'ke', 'karena', 'tersebut',
        'bisa', 'ada', 'mereka', 'lebih', 'sudah', 'atau', 'saat', 'oleh',
        'sebagai', 'adalah', 'apa', 'kita', 'kamu', 'dia', 'anda', 'aku',
        'sangat', 'tapi', 'namun', 'jika', 'kalau', 'maka', 'sehingga',
        'banyak', 'sedikit', 'kurang', 'cukup', 'paling', 'seperti', 'hanya'
    ])
    
    # Filter words
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Count frequency
    word_counts = Counter(filtered_words)
    
    # Format for word cloud library (e.g., [{text: 'word', weight: 10}])
    # Return top 50
    result = [
        {'text': word, 'weight': count} 
        for word, count in word_counts.most_common(50)
    ]
    
    return jsonify(result), 200


@app.route('/api/scrape', methods=['POST'])
def scrape_and_analyze():
    """
    Scrape comments from a URL and analyze sentiment
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'status': 'error', 'message': 'URL is required'}), 400
            
        # Limit to 20 comments for performance
        comments = get_youtube_comments(url, limit=20)
        
        if not comments:
            return jsonify({'status': 'error', 'message': 'No comments found or invalid URL'}), 400
            
        results = []
        stats = {'Positif': 0, 'Negatif': 0, 'Netral': 0}
        
        for text in comments:
            # Skip very short comments
            if len(text) < 3:
                continue
                
            sentiment, confidence = predict_sentiment_bert(text)
            results.append({
                'text': text,
                'sentiment': sentiment,
                'confidence': confidence
            })
            stats[sentiment] += 1
            
        return jsonify({
            'status': 'success',
            'results': results,
            'stats': stats,
            'total': len(results)
        }), 200
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500




@app.route('/api/batch-classify', methods=['POST'])
def batch_classify():
    """
    Classify sentiment for a batch of texts from CSV/Excel file
    """
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
            
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({'status': 'error', 'message': 'File must be CSV or Excel'}), 400
            
        # Read file
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error reading file: {str(e)}'}), 400
            
        # Find text column
        text_col = None
        possible_cols = ['text', 'review', 'content', 'komentar', 'ulasan', 'comment']
        
        for col in df.columns:
            if col.lower() in possible_cols:
                text_col = col
                break
                
        if not text_col:
            # If no matching column, take the first string column
            for col in df.columns:
                if df[col].dtype == 'object':
                    text_col = col
                    break
                    
        if not text_col:
             return jsonify({'status': 'error', 'message': 'Could not find a text column in the file'}), 400
             
        # Limit rows for performance
        if len(df) > 1000:
            df = df.head(1000)
            
        results = []
        stats = {'Positif': 0, 'Negatif': 0, 'Netral': 0}
        
        for index, row in df.iterrows():
            text = str(row[text_col])
            if len(text) < 3:
                continue
                
            sentiment, confidence = predict_sentiment_bert(text)
            
            results.append({
                'text': text,
                'sentiment': sentiment,
                'confidence': confidence,
                'original_row': index
            })
            stats[sentiment] += 1
            
        return jsonify({
            'status': 'success',
            'results': results,
            'stats': stats,
            'total': len(results),
            'filename': file.filename
        }), 200
        
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/<int:analysis_id>', methods=['POST'])
@jwt_required()
def submit_feedback(analysis_id):
    """
    Submit user feedback for an analysis
    """
    try:
        data = request.get_json()
        correction = data.get('correction')
        
        if not correction or correction not in ['Positif', 'Negatif', 'Netral']:
            return jsonify({'status': 'error', 'message': 'Invalid correction label'}), 400
            
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return jsonify({'status': 'error', 'message': 'Analysis not found'}), 404
            
        # Ensure user owns this analysis
        current_user_id = get_jwt_identity()
        if analysis.user_id != current_user_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
            
        analysis.correction = correction
        db.session.commit()
        
        logger.info(f"Feedback received for analysis {analysis_id}: {correction}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback saved',
            'analysis': analysis.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/upload-train-data', methods=['POST'])
def upload_train_data():
    """
    Upload CSV for training and trigger fine-tuning
    """
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'status': 'error', 'message': 'File must be CSV'}), 400
            
        # Save file
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        filepath = os.path.join(upload_dir, 'training_data.csv')
        file.save(filepath)
        
        # Trigger training in background thread to avoid blocking
        # Note: In production, use Celery/Redis
        def run_training():
            global TRAINING_STATUS
            TRAINING_STATUS['is_training'] = True
            TRAINING_STATUS['message'] = 'Training in progress...'
            TRAINING_STATUS['timestamp'] = datetime.now().isoformat()
            
            try:
                logger.info("Starting background training...")
                train(data_path=filepath)
                logger.info("Background training completed.")
                
                # Reload the model to use the new weights
                reload_model()
                
                TRAINING_STATUS['message'] = 'Training completed successfully!'
            except Exception as e:
                logger.error(f"Training failed: {e}")
                TRAINING_STATUS['message'] = f'Training failed: {str(e)}'
            finally:
                TRAINING_STATUS['is_training'] = False

        thread = threading.Thread(target=run_training)
        thread.start()
        
        return jsonify({
            'status': 'success', 
            'message': 'File uploaded. Training started in background.'
        }), 200
        
    except Exception as e:
        logger.error(f"Upload training data error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/training-status', methods=['GET'])
def get_training_status():
    """
    Get current training status
    """
    return jsonify(TRAINING_STATUS), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server is running
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': is_model_loaded()
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        'status': 'error',
        'message': 'Endpoint tidak ditemukan'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"405 error: {request.method} on {request.url}")
    return jsonify({
        'status': 'error',
        'message': 'Method tidak diizinkan'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Terjadi kesalahan internal server'
    }), 500


if __name__ == '__main__':
    logger.info("\n" + "="*50)
    logger.info("Starting Sentiment Classification Application")
    logger.info("="*50)
    logger.info("Server running at: http://127.0.0.1:5000")
    logger.info(f"Character limits: {MIN_TEXT_LENGTH}-{MAX_TEXT_LENGTH}")
    logger.info("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
