**docs/INSTALLATION.md**

# Installation Guide - Equestrian Management System

This guide covers local development setup and preparation for deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Project Structure](#project-structure)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running Locally](#running-locally)
- [Testing the API](#testing-the-api)

---

## Prerequisites

### Required Software

- **Python 3.8+** (Python 3.10 recommended)
- **pip** (Python package manager)
- **Git** (for version control)
- **MySQL** or **SQLite** (for local development)
- **Modern web browser** (Chrome, Firefox, Safari, or Edge)

### Optional Tools

- **Postman** or **Insomnia** (for API testing)
- **VS Code** or **PyCharm** (recommended IDEs)
- **Python virtual environment** (venv or virtualenv)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/equestrian-management.git
cd equestrian-management
````

### 2. Create Project Structure

Ensure your project follows this structure:

```
equestrian-management/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── riders.py
│   │   ├── horses.py
│   │   ├── recurring_lessons.py
│   │   ├── availability.py
│   │   ├── schedule.py
│   │   └── stats.py
│   ├── models.py
│   ├── config.py
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── core/
│           ├── utils/
│           ├── services/
│           ├── components/
│           └── app/
├── docs/
│   ├── INSTALLATION.md
│   └── DEPLOYMENT.md
└── README.md
```

### 3. Set Up Python Virtual Environment

- Navigate to backend directory
`cd backend

- Create virtual environment
`python3 -m venv venv`

- Activate virtual environment
 On macOS/Linux:
`source venv/bin/activate

### 4. Install Python Dependencies
`
pip install --upgrade pip
pip install -r requirements.txt
`


**requirements.txt contents:**

Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
PyMySQL==1.1.0
python-dotenv==1.0.0
cryptography==41.0.7


⸻


## Project Structure

### Backend Structure
```
backend/
├── routes/              # API endpoint blueprints
│   ├── riders.py        # Rider CRUD operations
│   ├── horses.py        # Horse CRUD operations
│   ├── recurring_lessons.py  # Recurring lesson management
│   ├── availability.py  # Weekly availability slots
│   ├── schedule.py      # Session scheduling
│   └── stats.py         # Statistics and reports
├── models.py            # SQLAlchemy database models
├── config.py            # Application configuration
├── app.py               # Flask application factory
└── requirements.txt     # Python dependencies
```

## Frontend Structure

```
frontend/
├── index.html           # Main HTML file
├── css/
│   └── styles.css       # Application styles
└── js/core/
    ├── utils/           # Utility functions (dates, validation, etc.)
    ├── services/        # API communication layer
    ├── components/      # UI components (modals, tables, etc.)
    └── app/             # Application core logic
```


## Environment Configuration

1. Create Environment File

Copy the example environment file:


` cp .env.example .env`


2. Configure `.env` File

Edit `.env` with your local settings:

```
# Flask Configuration
SECRET_KEY=your-local-secret-key-change-this
DEBUG=True

# Database Configuration (SQLite for local dev)
# Option 1: SQLite (easier for local development)
DATABASE_URL=sqlite:///equestrian.db

# Option 2: MySQL (if you have local MySQL)
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_DB=equestrian_db

# CORS Configuration
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

3. Update `config.py` for SQLite (Optional)

For local development with SQLite, modify `config.py`:

```
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Use SQLite for local development if DATABASE_URL is set
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL and DATABASE_URL.startswith('sqlite'):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # MySQL Configuration
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'equestrian_db')
        
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
```

⸻


## Database Setup

Option 1: SQLite (Recommended for Local Development)

SQLite databases are created automatically when you run the app for the first time.


The database file will be created at backend/equestrian.db
`python app.py`


Option 2: MySQL (Local Installation)

If using MySQL locally:


### Create database
`mysql -u root -p
CREATE DATABASE equestrian_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;`

### Run Flask app to create tables
`python app.py`


⸻


### Running Locally

1. Start the Backend API

Ensure virtual environment is activated
`cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows`

Run Flask development server
`python app.py`


You should see:

 * Running on http://127.0.0.1:5000
 * Database tables created successfully


2. Serve the Frontend

**Using Python's built-in server**


In a new terminal, navigate to frontend directory
`cd frontend`

Start simple HTTP server
Python 3:
`python -m http.server 8000`



Access the app at: `http://localhost:8000`




3. Update Frontend API Configuration

Edit `frontend/js/core/utils/config.js`:

```
const APP_CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:5000/api',  // Local backend
    APP_NAME: 'Equestrian Management',
    VERSION: '1.0.0',
    DEFAULT_LOCALE: 'en-US',
    DATE_FORMAT: 'YYYY-MM-DD',
    TIME_FORMAT: 'HH:mm'
};
```

⸻


## Testing the API

Health Check

curl http://127.0.0.1:5000/health


Expected response:

{"status": "healthy"}

⸻


## Troubleshooting

Port Already in Use

### Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

### Kill the process or use a different port
python app.py --port 5001


Database Connection Errors

### Check if MySQL is running
sudo service mysql status  # Linux
brew services list  # macOS

### Verify credentials in .env file
Check database exists
mysql -u root -p -e "SHOW DATABASES;"


CORS Errors

Ensure `CORS_ORIGINS` in `.env` includes your frontend URL:

CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000


Module Import Errors

 Reinstall dependencies
pip install --upgrade -r requirements.txt

Verify Python path
python -c "import sys; print('\n'.join(sys.path))"


⸻


Additional Resources
• [Flask Documentation](https://flask.palletsprojects.com/)
• [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
• [PythonAnywhere Documentation](https://help.pythonanywhere.com/)



**Last Updated:** November 2024


