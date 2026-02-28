# AI Website Builder with Sentiment Analysis

Full-stack web application that uses AI (Groq + open-source LLMs) to generate complete websites from user descriptions and includes real-time sentiment analysis of user feedback using lightweight BERT-style models.

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Groq-FF6F61?style=for-the-badge&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
</p>

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Usage Guide](#-usage-guide)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Website Generation
- AI-powered full website generation using Groq + Mixtral / Llama models
- Custom inputs: business name, industry, colors, pages, tone, features, CTA
- Instant responsive preview (desktop / tablet / mobile)
- Export clean HTML + CSS + JS

### Sentiment Analysis
- Lightweight BERT-based sentiment classification
- Real-time analysis of user comments & feedback
- Sentiment distribution dashboard (positive / neutral / negative)
- Historical trend visualization

### User & Project Management
- Secure JWT authentication
- Multiple projects per user
- Clean dashboard with project status & quick actions

## 🛠 Tech Stack

### Frontend
- React 18
- React Router v6
- Tailwind CSS
- React Hook Form
- Axios
- Heroicons
- react-hot-toast
- react-colorful (color picker)
- @headlessui/react

### Backend
- FastAPI
- MySQL + aiomysql
- Redis (optional – caching / Celery)
- PyJWT + bcrypt
- Groq API (LLM inference)
- Hugging Face `transformers` (sentiment)
- Celery (optional background tasks)

## 📁 Project Structure
```
project-root/
├── frontend/
│   └── myapp/
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── contexts/
│       │   ├── pages/
│       │   ├── App.js
│       │   ├── index.js
│       │   └── index.css
│       ├── package.json
│       └── tailwind.config.js
│
├── backend/
│   ├── src/
│   │   └── services/
│   ├── workers/
│   ├── .env
│   └── requirements.txt
│
└── README.md
```


## 🔧 Prerequisites

- Node.js ≥ 18
- Python ≥ 3.9
- MySQL ≥ 8.0
- Redis (optional)
- Groq API key

## 📦 Installation

### Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
# or: venv\Scripts\activate   # Windows

pip install -r requirements.txt

# ML dependencies (transformers + torch)
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# ^ use /cu121 if you have NVIDIA GPU and want GPU acceleration

Frontend
```
cd frontend/myapp
npm install
```

⚙️ Configuration
Backend – backend/.env
```
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=websitebuilder

# Optional Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=change-this-in-production-very-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Groq
GROQ_API_KEY=gsk_........................................

# App
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Frontend – frontend/myapp/.env
```
REACT_APP_API_URL=http://localhost:8000
```

🚀 Running the Application
Backend
```
cd backend
uvicorn src.main:app --reload --port 8000
```
Frontend
```
cd frontend/myapp
npm start
```

→ Open http://localhost:3000
Optional – Celery (background generation & sentiment)

```
# Redis (if not already running)
redis-server

# Generation worker
celery -A workers.generation_worker worker --loglevel=info --pool=solo

# Sentiment worker
celery -A workers.sentiment_worker worker --loglevel=info --pool=solo
```

📚 API Documentation

Interactive docs: http://localhost:8000/docs
Alternative: http://localhost:8000/redoc

📖 Quick Usage Guide

Register → /register
Login → /login
Create project from dashboard
Wait for AI generation (or check status)
Preview, copy code, add comments
View sentiment analysis & trends

🤝 Contributing

Fork the repo
Create feature branch (git checkout -b feature/amazing-thing)
Commit (git commit -m 'Add amazing thing')
Push (git push origin feature/amazing-thing)
Open Pull Request

📄 License
MIT License
See LICENSE for full text.

