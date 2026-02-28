AI Website Builder with Sentiment Analysis
A full-stack web application that generates AI-powered websites based on user requirements and provides sentiment analysis on user feedback. The application uses Groq API with open-source models for intelligent website generation and BERT-based models for sentiment analysis.

📋 Table of Contents
Features

Tech Stack

Project Structure

Prerequisites

Installation

Configuration

Running the Application

API Documentation

Usage Guide

Contributing

License

✨ Features
Website Generation
AI-Powered Website Creation: Generate complete websites using Groq API with open-source models (Mixtral, Llama, etc.)

Customizable Templates: Input business details, industry, color schemes, and desired pages

Real-time Preview: View generated websites instantly with responsive design previews

Code Export: View and copy the generated HTML/CSS/JS code

Sentiment Analysis
BERT-Based Analysis: Analyze user comments and feedback using lightweight BERT models

Sentiment Dashboard: Visual representation of positive, neutral, and negative feedback

Real-time Processing: Asynchronous sentiment analysis of comments

Historical Data: Track sentiment trends over time

User Management
JWT Authentication: Secure user registration and login

Project Management: Create, view, and manage multiple website projects

User Dashboard: Centralized view of all projects and their status

🛠 Tech Stack
Frontend
React 18 - UI library

React Router 6 - Navigation and routing

Tailwind CSS - Styling and responsive design

React Hook Form - Form management

Axios - HTTP client

Heroicons - Icon library

React Hot Toast - Notification system

React Colorful - Color picker component

Headless UI - Accessible UI components

Backend
FastAPI - Python web framework

MySQL - Database (with aiomysql for async operations)

Redis - Caching and message broker (optional)

JWT - Authentication

bcrypt - Password hashing

Groq API - AI website generation

Transformers - BERT models for sentiment analysis

Celery - Background task processing (optional)

📁 Project Structure
text
project/
├── frontend/
│   ├── myapp/
│   │   ├── public/
│   │   │   └── index.html
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── CommentBox.js
│   │   │   │   ├── Navbar.js
│   │   │   │   ├── Preview.js
│   │   │   │   ├── PrivateRoute.js
│   │   │   │   └── ProjectForm.js
│   │   │   ├── contexts/
│   │   │   │   └── AuthContext.js
│   │   │   ├── pages/
│   │   │   │   ├── Dashboard.js
│   │   │   │   ├── Login.js
│   │   │   │   ├── ProjectDetails.js
│   │   │   │   ├── Register.js
│   │   │   │   ├── SentimentDashboard.js
│   │   │   │   ├── Settings.js
│   │   │   │   └── WebsitePreview.js
│   │   │   ├── App.js
│   │   │   ├── index.js
│   │   │   └── index.css
│   │   ├── package.json
│   │   └── tailwind.config.js
│   └── README.md
│
├── backend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── groq_website_generator.py
│   │   │   ├── light_sentiment.py
│   │   │   └── website_generator.py
│   │   └── main.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── generation_worker.py
│   │   └── sentiment_worker.py
│   ├── .env
│   └── requirements.txt
│
└── README.md
🔧 Prerequisites
Node.js (v18 or higher)

Python (v3.9 or higher)

MySQL (v8.0 or higher)

Redis (optional, for Celery)

Groq API Key (for AI website generation)

📦 Installation
Backend Setup
Navigate to backend directory

bash
cd backend
Create virtual environment

bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install Python dependencies

bash
pip install -r requirements.txt
Install additional ML libraries

bash
pip install transformers torch torchvision torchaudio
Frontend Setup
Navigate to frontend directory

bash
cd frontend/myapp
Install Node dependencies

bash
npm install
⚙️ Configuration
Backend Environment Variables (.env)
Create a .env file in the backend directory:

env
# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=websitebuilder

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq API
GROQ_API_KEY=your_groq_api_key_here

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]
Frontend Configuration
Create a .env file in frontend/myapp:

env
REACT_APP_API_URL=http://localhost:8000
🚀 Running the Application
Start Backend Server
bash
cd backend
python src/main.py
The backend will start at http://localhost:8000

Start Frontend Development Server
bash
cd frontend/myapp
npm start
The frontend will start at http://localhost:3000

Optional: Start Celery Workers (for background tasks)
bash
# Terminal 1 - Start Redis (if using Celery)
redis-server

# Terminal 2 - Start Generation Worker
cd backend/workers
celery -A generation_worker worker --loglevel=info --pool=solo

# Terminal 3 - Start Sentiment Worker
cd backend/workers
celery -A sentiment_worker worker --loglevel=info --pool=solo
📚 API Documentation
Once the backend is running, access the automatic API documentation at:

Swagger UI: http://localhost:8000/api/docs

ReDoc: http://localhost:8000/api/redoc

Main Endpoints
Authentication
POST /api/auth/register - Register new user

POST /api/auth/login - Login user

GET /api/auth/me - Get current user info

Projects
POST /api/projects - Create new project

GET /api/projects - Get all user projects

GET /api/projects/{id} - Get project details

GET /api/projects/{id}/status - Get project generation status

Comments & Sentiment
POST /api/projects/{id}/comments - Add comment

GET /api/projects/{id}/sentiment - Get sentiment dashboard

📖 Usage Guide
1. User Registration/Login
Navigate to http://localhost:3000/register to create an account

Login at http://localhost:3000/login with your credentials

2. Creating a Project
From the dashboard, click "New Project"

Fill in the project details:

Business name

Industry

Custom domain (optional)

Pages to include

Design tone

Brand colors

Features

Call-to-action text

Submit the form to start AI website generation

3. Viewing Generated Website
After generation completes, click on the project

Navigate to the "Preview & Edit" tab

View the AI-generated website

Toggle between desktop, tablet, and mobile views

View the generated HTML code

4. Adding Comments
Go to the "Comments & Sentiment" tab

Add comments about the website

View sentiment analysis results in real-time

Track positive, neutral, and negative feedback

5. Sentiment Dashboard
Click "Full Dashboard" in the comments section

View sentiment distribution over time

Analyze top keywords and trends

Filter comments by sentiment

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Groq for providing fast AI inference API

Hugging Face for transformer models

Tailwind CSS for the amazing CSS framework

FastAPI for the excellent Python web framework

📧 Contact
For questions or support, please open an issue on the GitHub repository.