from celery import Celery
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
app = Celery(
    'generation_worker',
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
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

@app.task(name='generate_website')
def generate_website(project_id, brief):
    """Generate website code based on brief"""
    print(f"🎨 Starting website generation for project {project_id}")
    print(f"📋 Brief: {brief.get('business_name')} - {brief.get('industry')}")
    print(f"📄 Pages: {brief.get('pages')}")
    print(f"🎨 Colors: {brief.get('colors')}")
    
    # Simulate work
    time.sleep(5)
    
    # Mock preview URL
    preview_url = f"http://localhost:3000/preview/{project_id}"
    
    print(f"✅ Generation completed: {preview_url}")
    
    return {
        'project_id': project_id,
        'preview_url': preview_url,
        'status': 'completed',
        'message': 'Website generated successfully'
    }

if __name__ == "__main__":
    app.start()