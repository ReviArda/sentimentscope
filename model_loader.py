from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging
import re

logger = logging.getLogger(__name__)

import os

MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"
FINE_TUNED_DIR = "./fine_tuned_model"
_sentiment_pipeline = None

def load_model():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        reload_model()

def reload_model():
    global _sentiment_pipeline
    try:
        # Check if fine-tuned model exists
        target_model = MODEL_NAME
        if os.path.exists(FINE_TUNED_DIR) and os.listdir(FINE_TUNED_DIR):
            logger.info(f"Found fine-tuned model at {FINE_TUNED_DIR}. Loading...")
            target_model = FINE_TUNED_DIR
        else:
            logger.info(f"Loading base IndoBERT model: {MODEL_NAME}...")

        # Load tokenizer and model explicitly
        tokenizer = AutoTokenizer.from_pretrained(target_model)
        model = AutoModelForSequenceClassification.from_pretrained(target_model)
        
        _sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model=model, 
            tokenizer=tokenizer
        )
        logger.info(f"✅ Model loaded successfully from {target_model}!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # Fallback to base model if fine-tuned fails
        if target_model == FINE_TUNED_DIR:
            logger.warning("Falling back to base model...")
            try:
                tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
                _sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
                logger.info("✅ Base model loaded successfully!")
            except Exception as ex:
                logger.error(f"Failed to load base model: {ex}")
                raise
        else:
            raise

def predict_sentiment_bert(text):
    """
    Predict sentiment using IndoBERT
    Returns: (sentiment_label, confidence_score)
    """
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        load_model()
        
    try:
        # Truncate text to avoid token limit issues (BERT limit is usually 512 tokens)
        # We limit characters roughly to ensure we don't crash, pipeline handles truncation too
        result = _sentiment_pipeline(text[:1500], truncation=True, max_length=512)[0]
        
        label = result['label']
        score = result['score']
        
        # Map labels to Indonesian
        # Common labels for this model: 'positive', 'neutral', 'negative'
        sentiment_map = {
            'positive': 'Positif',
            'neutral': 'Netral',
            'negative': 'Negatif',
            'LABEL_0': 'Negatif',
            'LABEL_1': 'Netral',
            'LABEL_2': 'Positif'
        }
        
        sentiment = sentiment_map.get(label.lower(), label)
        
        return sentiment, float(score)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

def predict_aspect_sentiment(text):
    """
    Analyze sentiment per aspect using rule-based segmentation + BERT
    Returns: List of dicts {aspect, sentiment, text}
    """
    # 1. Define Aspect Keywords
    aspect_keywords = {
        'Makanan': ['makan', 'rasa', 'menu', 'porsi', 'bumbu', 'enak', 'lezat', 'asin', 'manis', 'pedas', 'minum'],
        'Pelayanan': ['pelayan', 'staff', 'ramah', 'lambat', 'cepat', 'antri', 'service', 'sopan', 'jutek'],
        'Harga': ['harga', 'mahal', 'murah', 'biaya', 'bayar', 'worth', 'kantong'],
        'Suasana': ['suasana', 'tempat', 'bersih', 'kotor', 'nyaman', 'musik', 'ac', 'view', 'luas', 'sempit']
    }

    # 2. Split text into segments
    # Split by common conjunctions and punctuation
    segments = re.split(r'[,.]|tapi|namun|sedangkan|dan|serta|walaupun|meskipun', text.lower())
    
    results = []
    
    for segment in segments:
        segment = segment.strip()
        if len(segment) < 3: continue
        
        # Check which aspect this segment belongs to
        found_aspect = None
        for aspect, keywords in aspect_keywords.items():
            if any(k in segment for k in keywords):
                found_aspect = aspect
                break
        
        if found_aspect:
            # Predict sentiment for this segment
            sentiment, score = predict_sentiment_bert(segment)
            results.append({
                'aspect': found_aspect,
                'sentiment': sentiment,
                'text': segment
            })
            
    return results

def is_model_loaded():
    return _sentiment_pipeline is not None
