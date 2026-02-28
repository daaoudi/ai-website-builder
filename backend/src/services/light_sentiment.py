from transformers import pipeline
import logging
import re
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightSentimentAnalyzer:
    def __init__(self):
        """Initialize a lightweight sentiment analysis pipeline"""
        self.classifier = None
        self.model_loaded = False
        logger.info("Initializing LightSentimentAnalyzer...")
        
    def load_model(self):
        """Lazy load the model only when needed"""
        if not self.model_loaded:
            try:
                # Use DistilBERT which is much smaller and faster
                logger.info("Loading lightweight sentiment model (DistilBERT)...")
                self.classifier = pipeline(
                    'sentiment-analysis',
                    model='distilbert-base-uncased-finetuned-sst-2-english',
                    device=-1  # Use CPU
                )
                self.model_loaded = True
                logger.info("✅ Lightweight model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                self.classifier = None
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'([!?.]){2,}', r'\1', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate to 512 characters (model limit)
        text = text[:512]
        
        return text.strip()
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        # Lazy load model
        self.load_model()
        
        # If model failed to load, return neutral
        if not self.classifier:
            logger.warning("Model not available, returning neutral")
            return {
                'label': 'neutral',
                'confidence': 0.5,
                'error': 'Model not loaded'
            }
        
        try:
            # Preprocess
            cleaned_text = self.preprocess_text(text)
            
            if not cleaned_text:
                return {
                    'label': 'neutral',
                    'confidence': 0.5
                }
            
            # Get prediction
            result = self.classifier(cleaned_text)[0]
            
            logger.debug(f"Raw result: {result}")
            
            # Map to our label format
            label_map = {
                'POSITIVE': 'positive',
                'NEGATIVE': 'negative'
            }
            
            label = label_map.get(result['label'], 'neutral')
            confidence = result['score']
            
            # Add neutral for low confidence
            if confidence < 0.6:
                # Check for neutral phrases
                neutral_words = ['okay', 'fine', 'alright', 'not bad', 'decent', 'average']
                if any(word in cleaned_text.lower() for word in neutral_words):
                    label = 'neutral'
                    confidence = 0.5
            
            logger.info(f"✅ Analysis: '{cleaned_text[:30]}...' -> {label} ({confidence:.2f})")
            
            return {
                'label': label,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                'label': 'neutral',
                'confidence': 0.5,
                'error': str(e)
            }
    
    def analyze_batch(self, texts: list) -> list:
        """Analyze multiple texts"""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results

# Create singleton instance
_analyzer = None

def get_analyzer():
    """Get or create the analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = LightSentimentAnalyzer()
    return _analyzer

def analyze_sentiment(text: str) -> Dict:
    """Convenience function to analyze sentiment"""
    analyzer = get_analyzer()
    return analyzer.analyze(text)