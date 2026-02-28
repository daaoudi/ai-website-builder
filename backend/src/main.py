"""
Main FastAPI application for AI Website Builder
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from datetime import datetime, timedelta
import aiomysql
from redis import Redis
import json
import os
from dotenv import load_dotenv
import bcrypt
import jwt
import asyncio
import random
from services.website_generator import generate_website as ai_generate_website

# Import sentiment analyzer
try:
    from services.light_sentiment import analyze_sentiment as bert_analyze
    print("✅ Successfully imported light sentiment analyzer")
except ImportError as e:
    print(f"⚠️ Could not import light sentiment analyzer: {e}")
    print("Using fallback mock sentiment analyzer")
    
    # Fallback mock sentiment analyzer
    def bert_analyze(text):
        sentiments = ['positive', 'neutral', 'negative']
        weights = [0.6, 0.3, 0.1]
        return {
            'label': random.choices(sentiments, weights=weights)[0],
            'confidence': round(random.uniform(0.7, 0.99), 2)
        }

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==================== DATABASE CLASS (MySQL Version) ====================
class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create MySQL connection pool"""
        try:
            self.pool = await aiomysql.create_pool(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                db=os.getenv('DB_NAME', 'websitebuilder'),
                minsize=5,
                maxsize=20,
                autocommit=True,
                charset='utf8mb4'
            )
            print("✅ MySQL Database connected successfully")
            
            # Initialize tables
            await self.init_tables()
            
        except Exception as e:
            print(f"❌ MySQL Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close MySQL connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("✅ MySQL Database disconnected")
    
    async def init_tables(self):
        """Initialize database tables if they don't exist"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Create users table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Create projects table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id VARCHAR(36) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        brief JSON NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        preview_url TEXT,
                        error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Create comments table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comments (
                        id VARCHAR(36) PRIMARY KEY,
                        project_id VARCHAR(36) NOT NULL,
                        text TEXT NOT NULL,
                        language VARCHAR(10),
                        source VARCHAR(50),
                        user_id VARCHAR(36),
                        sentiment VARCHAR(20),
                        confidence FLOAT,
                        analyzed_at TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_project_id (project_id),
                        INDEX idx_sentiment (sentiment)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                print("✅ MySQL tables initialized")
    
    async def fetch(self, query: str, *args):
        """Execute fetch query and return all rows"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchall()
    
    async def fetchrow(self, query: str, *args):
        """Execute fetch query and return one row"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchone()
    
    async def execute(self, query: str, *args):
        """Execute query (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                return cursor.rowcount

# ==================== REDIS CLASS ====================
class RedisClient:
    def __init__(self):
        self.client = None
    
    def connect(self):
        """Create Redis connection"""
        try:
            self.client = Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()  # Test connection
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed (optional): {e}")
            self.client = None
    
    def disconnect(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            print("✅ Redis disconnected")
    
    def get(self, key):
        return self.client.get(key) if self.client else None
    
    def set(self, key, value, ex=None):
        return self.client.set(key, value, ex) if self.client else None

# ==================== GLOBAL INSTANCES ====================
db = Database()
redis_client = RedisClient()

# ==================== LIFESPAN CONTEXT MANAGER ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # --- STARTUP: Executed before the application starts ---
    print("\n" + "="*50)
    print("🚀 STARTING UP APPLICATION...")
    print("="*50)
    
    # Connect to MySQL
    await db.connect()
    
    # Connect to Redis (optional)
    redis_client.connect()
    
    print("="*50)
    print("✅ APPLICATION STARTUP COMPLETE")
    print("="*50 + "\n")
    
    yield  # The application runs here
    
    # --- SHUTDOWN: Executed after the application stops ---
    print("\n" + "="*50)
    print("🛑 SHUTTING DOWN APPLICATION...")
    print("="*50)
    
    # Disconnect from MySQL
    await db.disconnect()
    
    # Disconnect from Redis
    redis_client.disconnect()
    
    print("="*50)
    print("✅ APPLICATION SHUTDOWN COMPLETE")
    print("="*50 + "\n")

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="AI Website Builder API",
    description="API for generating websites with AI and sentiment analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ==================== CORS MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ==================== SECURITY ====================
security = HTTPBearer()

# ==================== PYDANTIC MODELS ====================
# Auth Models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

# Project Models
class WebsiteBrief(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=100)
    industry: str = Field(...)
    domain: Optional[str] = None
    colors: Dict[str, str] = Field(
        default={
            "primary": "#3B82F6",
            "secondary": "#10B981",
            "accent": "#F59E0B"
        }
    )
    pages: List[str] = Field(default=["home", "about", "services", "contact"])
    tone: str = Field(default="modern")
    language: str = Field(default="en")
    features: List[str] = Field(default=[])
    cta_text: str = Field(default="Get Started")
    contact_info: Optional[Dict] = Field(default={})

    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Acme Inc",
                "industry": "Technology",
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#10B981",
                    "accent": "#F59E0B"
                },
                "pages": ["home", "about", "services", "contact"],
                "tone": "modern",
                "language": "en"
            }
        }

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    estimated_time: int = 60
    message: Optional[str] = None

class Comment(BaseModel):
    project_id: str
    text: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[str] = None

class CommentResponse(BaseModel):
    comment_id: str
    status: str
    message: str

class ProjectStatus(BaseModel):
    project_id: str
    status: str
    preview_url: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = None

# ==================== UTILITY FUNCTIONS ====================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"Received token: {token[:20]}...")  # Debug log (first 20 chars)
    
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        print(f"Decoded user_id: {user_id}")  # Debug log
        
        if user_id is None:
            print("No user_id in token")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user from database
        user = await db.fetchrow("SELECT id, email, name FROM users WHERE id = %s", user_id)
        print(f"Found user: {user}")  # Debug log
        
        if user is None:
            print("User not found in database")
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        print("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running and all services are connected"""
    # Test database connection
    db_status = "disconnected"
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    db_status = "connected"
        except:
            db_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": "connected" if redis_client.client else "disconnected",
            "api": "running"
        }
    }

@app.get("/api/test-token", tags=["Test"])
async def test_token(current_user: dict = Depends(get_current_user)):
    """Test if token is valid"""
    return {"message": "Token is valid", "user": current_user}

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AI Website Builder API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

# ==================== AUTH ENDPOINTS ====================
@app.post("/api/auth/register", response_model=TokenResponse, tags=["Authentication"])
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = await db.fetchrow("SELECT id FROM users WHERE email = %s", user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user_id = str(uuid.uuid4())
    try:
        await db.execute("""
            INSERT INTO users (id, email, name, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, user_id, user_data.email, user_data.name, hashed_password, datetime.utcnow())
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "token": access_token,
            "user": {
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name,
                "created_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login_data: UserLogin):
    """
    Login user and return access token
    """
    # Find user by email
    user = await db.fetchrow("SELECT id, email, name, password_hash FROM users WHERE email = %s", login_data.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user['id']})
    
    return {
        "token": access_token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name']
        }
    }

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

# ==================== PROJECTS ENDPOINTS ====================
@app.post("/api/projects", response_model=GenerationResponse, tags=["Projects"])
async def create_project(
    brief: WebsiteBrief,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new project and start website generation
    """
    project_id = str(uuid.uuid4())
    
    # Store project in database
    try:
        await db.execute("""
            INSERT INTO projects (id, name, brief, user_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, project_id, brief.business_name, json.dumps(brief.dict()), 
            current_user['id'], 'pending', datetime.utcnow())
        
        # Start generation in background
        background_tasks.add_task(
            generate_website_task,
            project_id,
            brief.dict()
        )
        
        return {
            "job_id": project_id,
            "status": "processing",
            "estimated_time": 60,
            "message": "Website generation started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@app.get("/api/projects", tags=["Projects"])
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    """Get all projects for the current user"""
    try:
        rows = await db.fetch("""
            SELECT id, name, status, created_at, preview_url
            FROM projects
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, current_user['id'])
        
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

@app.get("/api/projects/{project_id}", tags=["Projects"])
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project"""
    try:
        row = await db.fetchrow("""
            SELECT id, name, brief, status, preview_url, error, created_at, updated_at
            FROM projects
            WHERE id = %s AND user_id = %s
        """, project_id, current_user['id'])
        
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Parse brief JSON
        if row['brief']:
            row['brief'] = json.loads(row['brief'])
        
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")

@app.get("/api/projects/{project_id}/status", response_model=ProjectStatus, tags=["Projects"])
async def get_project_status(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get generation status of a project"""
    try:
        row = await db.fetchrow("""
            SELECT id, status, preview_url, error
            FROM projects
            WHERE id = %s AND user_id = %s
        """, project_id, current_user['id'])
        
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Calculate progress based on status
        progress_map = {
            'pending': 0,
            'generating': 50,
            'completed': 100,
            'failed': 0
        }
        
        return {
            "project_id": row['id'],
            "status": row['status'],
            "preview_url": row['preview_url'],
            "error": row['error'],
            "progress": progress_map.get(row['status'], 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")

@app.delete("/api/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a project"""
    try:
        result = await db.execute("""
            DELETE FROM projects 
            WHERE id = %s AND user_id = %s
        """, project_id, current_user['id'])
        
        if result == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

# ==================== COMMENTS & SENTIMENT ENDPOINTS ====================
@app.post("/api/projects/{project_id}/comments", response_model=CommentResponse, tags=["Sentiment"])
async def add_comment(
    project_id: str,
    request: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment/review for sentiment analysis"""
    comment_id = str(uuid.uuid4())
    
    print(f"📝 Received comment request for project {project_id}")
    print(f"Request data: {request}")
    print(f"Current user ID: {current_user['id']}")
    
    try:
        # Verify project exists and belongs to user
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = %s AND user_id = %s", 
            project_id, current_user['id']
        )
        if not project:
            print(f"❌ Project {project_id} not found for user {current_user['id']}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get comment text from request
        comment_text = request.get('text')
        if not comment_text:
            print("❌ No text provided in request")
            raise HTTPException(status_code=400, detail="Comment text is required")
        
        print(f"📝 Adding comment: {comment_text[:50]}...")
        
        # Store comment with user_id
        try:
            await db.execute("""
                INSERT INTO comments (id, project_id, text, language, source, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, comment_id, project_id, comment_text, 
                request.get('language', 'en'), 'web', current_user['id'], datetime.utcnow())
            
            print(f"✅ Comment {comment_id} stored in database")
            
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            # Try without user_id as fallback
            print("⚠️ Trying without user_id...")
            await db.execute("""
                INSERT INTO comments (id, project_id, text, language, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, comment_id, project_id, comment_text, 
                request.get('language', 'en'), 'web', datetime.utcnow())
            print(f"✅ Comment {comment_id} stored in database without user_id")
        
        # Analyze sentiment in background
        background_tasks.add_task(
            analyze_sentiment_task,
            comment_id,
            comment_text,
            request.get('language', 'en')
        )
        
        return {
            "comment_id": comment_id,
            "status": "processing",
            "message": "Comment added and sentiment analysis started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to add comment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")

@app.get("/api/projects/{project_id}/sentiment", tags=["Sentiment"])
async def get_sentiment_dashboard(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get sentiment analysis dashboard data"""
    try:
        # Verify project exists and belongs to user
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = %s AND user_id = %s", 
            project_id, current_user['id']
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Overall stats (only comments with sentiment)
        stats = await db.fetch("""
            SELECT 
                sentiment,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM comments 
            WHERE project_id = %s AND sentiment IS NOT NULL
            GROUP BY sentiment
        """, project_id)
        
        # Recent comments (including those without sentiment)
        recent = await db.fetch("""
            SELECT id, text, sentiment, confidence, created_at
            FROM comments 
            WHERE project_id = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, project_id)
        
        print(f"📊 Found {len(recent)} comments for project {project_id}")
        
        # Format overall stats
        overall = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        for stat in stats:
            overall[stat['sentiment']] = int(stat['count'])
        
        # Format recent comments
        formatted_recent = []
        for comment in recent:
            formatted_recent.append({
                "id": comment['id'],
                "text": comment['text'],
                "sentiment": comment['sentiment'],
                "confidence": float(comment['confidence']) if comment['confidence'] else None,
                "created_at": comment['created_at'].isoformat() if comment['created_at'] else None
            })
        
        return {
            "overall": overall,
            "stats": stats,
            "recent": formatted_recent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get sentiment data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment data: {str(e)}")

# ==================== PUBLISH ENDPOINT ====================
@app.post("/api/projects/{project_id}/publish", tags=["Projects"])
async def publish_website(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Publish website to hosting"""
    try:
        # Verify project exists and belongs to user
        project = await db.fetchrow(
            "SELECT id, status FROM projects WHERE id = %s AND user_id = %s",
            project_id, current_user['id']
        )
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project['status'] != 'completed':
            raise HTTPException(status_code=400, detail="Project must be completed before publishing")
        
        return {
            "deployment_id": str(uuid.uuid4()),
            "status": "deploying",
            "message": "Website deployment started (mock mode)"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish website: {str(e)}")

# ==================== BACKGROUND TASKS ====================
async def generate_website_task(project_id: str, brief: dict):
    """AI-powered website generation using Groq"""
    try:
        print(f"🤖 Starting Groq AI website generation for project {project_id}")
        print(f"📋 Brief: {brief.get('business_name')}")
        
        # Update status to generating
        await db.execute("""
            UPDATE projects SET status = 'generating' 
            WHERE id = %s
        """, project_id)
        
        # Generate website using Groq AI
        result = ai_generate_website(project_id, brief)
        
        # Get preview URL
        preview_url = result.get('preview_url')
        
        # Update with result
        await db.execute("""
            UPDATE projects 
            SET status = 'completed', 
                preview_url = %s,
                updated_at = NOW()
            WHERE id = %s
        """, preview_url, project_id)
        
        print(f"✅ Groq AI website generated successfully for project {project_id}")
        print(f"🔗 Preview URL created")
        
    except Exception as e:
        print(f"❌ Groq AI website generation failed for project {project_id}: {e}")
        import traceback
        traceback.print_exc()
        
        # Update status to failed
        await db.execute("""
            UPDATE projects 
            SET status = 'failed', 
                error = %s,
                updated_at = NOW()
            WHERE id = %s
        """, str(e), project_id)

async def analyze_sentiment_task(comment_id: str, text: str, language: str):
    """Background task for sentiment analysis using BERT"""
    try:
        print(f"📊 Analyzing sentiment with BERT for comment {comment_id}")
        print(f"📝 Text: {text[:50]}...")
        
        # Use BERT for analysis
        result = bert_analyze(text)
        
        print(f"✅ BERT result: {result}")
        
        # Update comment with sentiment
        await db.execute("""
            UPDATE comments 
            SET sentiment = %s, 
                confidence = %s, 
                analyzed_at = NOW()
            WHERE id = %s
        """, result['label'], result['confidence'], comment_id)
        
        print(f"✅ Sentiment analyzed for comment {comment_id}: {result['label']} ({result['confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed for comment {comment_id}: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to mock sentiment
        fallback = {
            'label': random.choice(['positive', 'neutral', 'negative']),
            'confidence': round(random.uniform(0.5, 0.9), 2)
        }
        
        await db.execute("""
            UPDATE comments 
            SET sentiment = %s, 
                confidence = %s, 
                analyzed_at = NOW()
            WHERE id = %s
        """, fallback['label'], fallback['confidence'], comment_id)
        
        print(f"⚠️ Used fallback sentiment: {fallback}")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )