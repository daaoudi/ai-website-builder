from celery import Celery
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
app = Celery(
    'sentiment_worker',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=5 * 60,
    task_soft_time_limit=4 * 60,
)

@app.task(name='analyze_sentiment')
def analyze_sentiment(text, language=None):
    """Analyze sentiment of text"""
    print(f"📊 Analyzing sentiment: {text[:50]}...")
    
    # Simulate work
    time.sleep(2)
    
    # Mock sentiment result
    sentiments = ['positive', 'neutral', 'negative']
    weights = [0.6, 0.3, 0.1]  # 60% positive, 30% neutral, 10% negative
    
    result = {
        'label': random.choices(sentiments, weights=weights)[0],
        'confidence': round(random.uniform(0.7, 0.99), 2),
        'language': language or 'en',
        'has_pii': False
    }
    
    print(f"✅ Sentiment: {result['label']} ({result['confidence']})")
    return result

@app.task(name='batch_analyze_sentiments')
def batch_analyze_sentiments(comments):
    """Analyze multiple comments in batch"""
    results = []
    for comment in comments:
        result = analyze_sentiment(
            comment.get('text'), 
            comment.get('language')
        )
        result['comment_id'] = comment.get('id')
        results.append(result)
    return results

if __name__ == "__main__":
    app.start()