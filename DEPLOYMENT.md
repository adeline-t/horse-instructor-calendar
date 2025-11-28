Deployment Guide - PythonAnywhere

Complete guide for deploying the Equestrian Management System on PythonAnywhere.


⸻


Table of Contents
• [Overview](#overview)
• [Prerequisites](#prerequisites)
• [PythonAnywhere Account Setup](#pythonanywhere-account-setup)
• [Backend Deployment](#backend-deployment)
• [Database Configuration](#database-configuration)
• [WSGI Configuration](#wsgi-configuration)
• [Environment Variables](#environment-variables)
• [Frontend Deployment](#frontend-deployment)
• [Testing Deployment](#testing-deployment)
• [Troubleshooting](#troubleshooting)
• [Maintenance](#maintenance)
• [Security & Performance](#security--performance)
• [Deployment Checklist](#deployment-checklist)


⸻


Overview

This guide deploys a full-stack application with separated frontend and backend:


Component	Platform	Technology
**Backend API**	PythonAnywhere	Flask + MySQL + Python 3.10
**Frontend**	GitHub Pages / Netlify / Vercel	Static HTML/CSS/JS

**Architecture Flow:**

┌─────────────────┐         ┌──────────────────────┐
│  Static Frontend│   →     │  Backend API         │
│  (GitHub Pages) │  HTTPS  │  (PythonAnywhere)    │
│                 │         │  - Flask REST API    │
│  HTML/CSS/JS    │         │  - MySQL Database    │
└─────────────────┘         └──────────────────────┘


⸻


Prerequisites

Required Accounts
• ✅ **PythonAnywhere Account** (Free or Paid)
- Sign up: [pythonanywhere.com/registration](https://www.pythonanywhere.com/registration/register/beginner/)
• ✅ **GitHub Account** (for version control + optional hosting)
• ✅ **Git** installed locally


Files Ready

Ensure you have completed [INSTALLATION.md](./INSTALLATION.md) and tested locally.


Required Files Structure

equestrian-management/
├── backend/
│   ├── routes/
│   ├── models.py
│   ├── config.py
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── css/
    └── js/


⸻


PythonAnywhere Account Setup

1. Create Account
1. Visit [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Click **"Start running Python online in less than a minute!"**
3. Choose a plan:


Free Account (Beginner)
• ✅ 1 web app
• ✅ MySQL database included
• ⚠️ Limited CPU seconds/day
• ⚠️ Whitelisted external sites only
• ⚠️ No scheduled tasks


Paid Account ($5+/month)
• ✅ Multiple web apps
• ✅ More CPU & bandwidth
• ✅ Any external site access
• ✅ Scheduled tasks (cron)
• ✅ Larger databases


**Recommendation:** Free for testing, Paid for production.


⸻


Backend Deployment

Step 1: Upload Code to PythonAnywhere

Option A: Git Clone (Recommended)

# Open PythonAnywhere Bash console
cd ~
git clone https://github.com/yourusername/equestrian-management.git
cd equestrian-management/backend


Option B: Manual Upload
1. Go to **Files** tab in PythonAnywhere
2. Navigate to `/home/yourusername/`
3. Create directory: `equestrian_backend`
4. Upload files:
- `app.py`
- `config.py`
- `models.py`
- `requirements.txt`
- Entire `routes/` directory


⸻


Step 2: Create Virtual Environment

# In PythonAnywhere Bash console
cd ~/equestrian_backend

# Create virtual environment with Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 equestrian-env

# It will auto-activate. Verify:
python --version
# Expected: Python 3.10.x


**Note:** Virtual environment is now active (prompt shows `(equestrian-env)`).


⸻


Step 3: Install Dependencies

# Ensure virtual environment is active
workon equestrian-env

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installations
pip list


**Expected Packages:**

Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
PyMySQL==1.1.0
python-dotenv==1.0.0
cryptography==41.0.7


⸻


Step 4: Create Environment File

# Create .env in backend directory
nano .env


**Add this configuration:**


# Flask Configuration
SECRET_KEY=your-production-secret-key-change-this-to-random-string
DEBUG=False

# MySQL Configuration
MYSQL_USER=yourusername
MYSQL_PASSWORD=your_db_password
MYSQL_HOST=yourusername.mysql.pythonanywhere-services.com
MYSQL_DB=yourusername$equestrian_db

# CORS Configuration (update with your actual frontend URL)
CORS_ORIGINS=https://yourusername.github.io,https://yourdomain.com


**Generate Strong SECRET_KEY:**

python -c "import secrets; print(secrets.token_hex(32))"


Copy output and paste as `SECRET_KEY` value.


**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`.


⸻


Database Configuration

Step 1: Create MySQL Database
1. Go to **Databases** tab in PythonAnywhere dashboard
2. **Set MySQL Password** (first time only)
- Enter a strong password
- Click "Set password"
3. **Note your MySQL hostname:**
```
yourusername.mysql.pythonanywhere-services.com
```
4. **Create Database:**
- Database name: `yourusername$equestrian_db`
- Click **"Create"**


**Important:** Database name MUST follow format: `username$dbname`


⸻


Step 2: Initialize Database Tables

# In Bash console, ensure environment is active
workon equestrian-env
cd ~/equestrian_backend

# Start Python interactive shell
python


**In Python shell, run:**


from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")

exit()


⸻


Step 3: Verify Tables

# Connect to MySQL
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p

# Enter your MySQL password when prompted

# Select database
USE yourusername$equestrian_db;

# Show tables
SHOW TABLES;


**Expected Output:**

+----------------------------+
| Tables_in_yourusername$... |
+----------------------------+
| availability               |
| horse                      |
| recurring_lesson           |
| rider                      |
| schedule                   |
+----------------------------+
5 rows in set


**Exit MySQL:**

EXIT;


⸻


WSGI Configuration

Step 1: Create Web App
1. Go to **Web** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose domain (or use default: `yourusername.pythonanywhere.com`)
4. Select **"Manual configuration"**
5. Choose **Python 3.10**
6. Click **"Next"**


⸻


Step 2: Configure WSGI File
1. In **Web** tab, find **"Code"** section
2. Click WSGI configuration file link:
```
/var/www/yourusername_pythonanywhere_com_wsgi.py
```
3. **Delete ALL existing content**
4. **Replace with:**


"""
WSGI Configuration for Equestrian Management System
"""
import sys
import os

# Add project directory to Python path
project_home = '/home/yourusername/equestrian_backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask application
from app import create_app
application = create_app()


⚠️ **IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username.

1. **Save the file:** Click **Save** button or press `Ctrl+S`


⸻


Step 3: Configure Virtual Environment
1. In **Web** tab, scroll to **"Virtualenv"** section
2. Enter path to your virtual environment:
```
/home/yourusername/.virtualenvs/equestrian-env
```
3. Click the **checkmark** ✓ to save


⸻


Step 4: Configure Static Files (Optional)

*Only needed if serving static files from backend (not recommended for this architecture)*


**Skip this section if using separate frontend hosting.**


If needed:
• **URL:** `/static/`
• **Directory:** `/home/yourusername/equestrian_backend/static/`


⸻


Environment Variables

Option 1: Using .env File ✅ (Already Configured)

The `.env` file created earlier is automatically loaded by the WSGI configuration.


**Verify it exists:**

ls -la ~/equestrian_backend/.env
cat ~/equestrian_backend/.env


⸻


Option 2: PythonAnywhere Environment Variables (Alternative)

If you prefer not to use `.env` file:

1. In **Web** tab, scroll to **"Environment variables"** section
2. Add each variable:


Variable Name	Example Value
`SECRET_KEY`	`a1b2c3d4e5f6...` (64 chars)
`DEBUG`	`False`
`MYSQL_USER`	`yourusername`
`MYSQL_PASSWORD`	`your_db_password`
`MYSQL_HOST`	`yourusername.mysql.pythonanywhere-services.com`
`MYSQL_DB`	`yourusername$equestrian_db`
`CORS_ORIGINS`	`https://yourusername.github.io`

⸻


Reload and Test Backend

Step 1: Reload Web App
1. In **Web** tab, click the big green **"Reload yourusername.pythonanywhere.com"** button
2. Wait 10-20 seconds for reload to complete
3. Watch for confirmation message


⸻


Step 2: Check Error Log
1. In **Web** tab, find **"Log files"** section
2. Click **"Error log"** link
3. Check for any errors (should be empty or show successful startup)


**Common startup messages (normal):**

Database tables created successfully


**If you see errors:**
• Import errors → Check virtual environment path
• Database errors → Verify credentials in `.env`
• Module not found → Reinstall requirements


⸻


Step 3: Test API Endpoints

# Health check
curl https://yourusername.pythonanywhere.com/health

# Expected: {"status":"healthy"}

# Test riders endpoint
curl https://yourusername.pythonanywhere.com/api/riders

# Expected: [] (empty array if no data)

# Create test rider
curl -X POST https://yourusername.pythonanywhere.com/api/riders \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Rider","email":"test@example.com","active":true}'

# Expected: {...} (created rider object with id)


✅ **Backend deployment complete!**


⸻


Frontend Deployment

Option 1: GitHub Pages (Recommended)

Step 1: Update API Configuration

Edit `frontend/js/core/utils/config.js`:


const APP_CONFIG = {
    API_BASE_URL: 'https://yourusername.pythonanywhere.com/api',
    APP_NAME: 'Equestrian Management',
    VERSION: '1.0.0',
    DEFAULT_LOCALE: 'en-US',
    DATE_FORMAT: 'YYYY-MM-DD',
    TIME_FORMAT: 'HH:mm'
};


⚠️ Replace `yourusername` with your PythonAnywhere username.


⸻


Step 2: Push to GitHub

# In your local project root
cd equestrian-management

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment - frontend and backend"

# Add remote repository
git remote add origin https://github.com/yourusername/equestrian-management.git

# Push to GitHub
git push -u origin main


⸻


Step 3: Enable GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Pages** in left sidebar
4. Under **"Source"**:
- Branch: `main`
- Folder: `/` (root) or `/frontend` if using subdirectory
5. Click **"Save"**


**Your site will be available at:**

https://yourusername.github.io/equestrian-management/


GitHub will take 1-2 minutes to build and deploy.


⸻


Step 4: Update CORS in Backend

Now that you know your frontend URL, update backend `.env`:


# SSH into PythonAnywhere Bash console
nano ~/equestrian_backend/.env


**Update CORS_ORIGINS:**

CORS_ORIGINS=https://yourusername.github.io


**Save and reload web app** in PythonAnywhere Web tab.


⸻


Option 2: Netlify

Quick Steps:
1. Sign up at [netlify.com](https://netlify.com)
2. Click **"New site from Git"**
3. Connect GitHub repository
4. **Build settings:**
- Base directory: `frontend`
- Build command: *(leave empty)*
- Publish directory: `.`
5. Click **"Deploy site"**


Netlify assigns URL: `https://random-name-12345.netlify.app`


**Update backend CORS** with Netlify URL.


⸻


Option 3: Vercel

Quick Steps:
1. Sign up at [vercel.com](https://vercel.com)
2. Click **"Import Project"**
3. Connect GitHub repository
4. **Settings:**
- Root directory: `frontend`
5. Click **"Deploy"**


Vercel assigns URL: `https://project-name.vercel.app`


**Update backend CORS** with Vercel URL.


⸻


Testing Deployment

Backend API Tests

# Set base URL
export API_URL="https://yourusername.pythonanywhere.com/api"

# Health check
curl $API_URL/../health

# Get all riders
curl $API_URL/riders

# Create rider
curl -X POST $API_URL/riders \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@test.com","phone":"555-1234","active":true}'

# Get all horses
curl $API_URL/horses

# Create horse
curl -X POST $API_URL/horses \
  -H "Content-Type: application/json" \
  -d '{"name":"Thunder","type":"Arabian","active":true}'

# Get schedule (with date filter)
curl "$API_URL/schedule?start_date=2024-01-01&end_date=2024-12-31"

# Get statistics
curl $API_URL/statistics


⸻


Frontend Tests
1. **Open frontend URL** in browser
2. **Open Developer Console** (F12)
3. **Check Console tab** for errors
4. **Test core functionality:**
- ✅ Navigation works
- ✅ Add a rider
- ✅ Add a horse
- ✅ Create a lesson
- ✅ View schedule
- ✅ Check statistics


**Expected behavior:**
• No CORS errors in console
• API calls return data
• UI updates correctly


⸻


Troubleshooting

Issue 1: 500 Internal Server Error

**Symptoms:**

Internal Server Error


**Check error log:**
1. Go to **Web** tab
2. Click **"Error log"**
3. Look for Python tracebacks


**Common Causes & Fixes:**


Cause	Fix
Database connection failed	Verify `.env` credentials, check MySQL password
Module import error	Check virtual environment path in Web tab
Missing `.env` file	Create `.env` file with all required variables
Wrong Python version	Ensure using Python 3.10 in virtualenv

**Quick Fix:**

workon equestrian-env
cd ~/equestrian_backend
pip install --upgrade -r requirements.txt
# Reload web app in Web tab


⸻


Issue 2: CORS Error

**Symptoms:**

Access to fetch at 'https://...' from origin 'https://...' 
has been blocked by CORS policy


**Fix:**


Update `CORS_ORIGINS` in `.env`:

CORS_ORIGINS=https://yourusername.github.io,https://another-domain.com


**Reload web app** after changing.


**Verify CORS headers:**

curl -I https://yourusername.pythonanywhere.com/api/riders
# Look for: Access-Control-Allow-Origin header


⸻


Issue 3: Database Connection Error

**Symptoms:**

sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")


**Checklist:**
• MySQL host correct: `yourusername.mysql.pythonanywhere-services.com`
• Database name format: `yourusername$equestrian_db`
• Password is correct (no typos)
• Database was created in Databases tab


**Test connection:**

mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p
# Enter password
# If successful, you'll see MySQL prompt


⸻


Issue 4: Module Not Found

**Symptoms:**

ModuleNotFoundError: No module named 'flask'


**Fix:**

workon equestrian-env
cd ~/equestrian_backend
pip install -r requirements.txt


**Verify virtualenv path** in Web tab:

/home/yourusername/.virtualenvs/equestrian-env


⸻


Issue 5: Frontend Can't Reach API

**Symptoms:**
• Network errors in browser console
• Failed to fetch


**Checklist:**
• `API_BASE_URL` in `config.js` is correct
• Backend is running (check health endpoint)
• CORS is configured correctly
• HTTPS is used (not HTTP mixed with HTTPS)


**Test from browser console:**

fetch('https://yourusername.pythonanywhere.com/health')
  .then(r => r.json())
  .then(d => console.log(d));


⸻


Maintenance

Updating Backend Code

# SSH into PythonAnywhere or use Bash console
cd ~/equestrian_backend

# Pull latest changes from GitHub
git pull origin main

# Activate virtual environment
workon equestrian-env

# Install any new dependencies
pip install -r requirements.txt

# Reload web app
# Go to Web tab and click "Reload" button


⸻


Database Backups

**Export (Backup):**

# Create backup directory
mkdir -p ~/backups

# Export database
mysqldump -u yourusername \
  -h yourusername.mysql.pythonanywhere-services.com \
  -p \
  yourusername\$equestrian_db > ~/backups/backup_$(date +%Y%m%d).sql


**Import (Restore):**

mysql -u yourusername \
  -h yourusername.mysql.pythonanywhere-services.com \
  -p \
  yourusername\$equestrian_db < ~/backups/backup_20241128.sql


**Schedule Automated Backups** (Paid accounts):

# Create backup script
nano ~/backup_db.sh


#!/bin/bash
mysqldump -u yourusername \
  -h yourusername.mysql.pythonanywhere-services.com \
  -p'your_password' \
  yourusername\$equestrian_db > ~/backups/backup_$(date +%Y%m%d).sql


Add to scheduled tasks in PythonAnywhere (Tasks tab).


⸻


Monitoring

**Check logs regularly:**


Log Type	Location	Purpose
Error log	Web tab → Log files	Application errors
Server log	Web tab → Log files	HTTP requests
Access log	Web tab → Log files	Traffic patterns

**Monitor resources:**
• CPU usage dashboard (Account tab)
• Database size (Databases tab)
• File storage (Files tab)


⸻


Updating Frontend

# On local machine
cd equestrian-management/frontend

# Make changes
nano js/core/utils/config.js

# Commit and push
git add .
git commit -m "Update frontend configuration"
git push origin main

# GitHub Pages / Netlify / Vercel will auto-deploy


⸻


Security & Performance

Security Checklist
• `DEBUG=False` in production `.env`
• Strong `SECRET_KEY` (32+ random hex characters)
• CORS restricted to specific domains (not `*`)
• MySQL password is strong (16+ chars, mixed case, numbers, symbols)
• `.env` file in `.gitignore` (never commit secrets)
• Regular database backups scheduled
• HTTPS enabled (automatic on PythonAnywhere/GitHub Pages)
• SQL injection protection (using SQLAlchemy ORM)
• Input validation on all endpoints


⸻


Performance Optimization

Backend

**1. Database Indexing:**


Add to `models.py`:

from sqlalchemy import Index

class Rider(db.Model):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_rider_email', 'email'),
        Index('idx_rider_active', 'active'),
    )

class Schedule(db.Model):
    # ... existing fields ...
    
    __table_args__ = (
        Index('idx_schedule_start', 'start_time'),
        Index('idx_schedule_rider', 'rider_id'),
        Index('idx_schedule_horse', 'horse_id'),
    )


**2. Query Optimization:**
• Use `.filter()` instead of loading all then filtering
• Implement pagination for large result sets
• Use `lazy='select'` for relationships


**3. Connection Pooling:**


Already configured in `config.py`:

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 280,  # Recycle connections before MySQL timeout
    'pool_pre_ping': True,  # Verify connections before use
}


Frontend

**1. Minify Assets:**

# Install minification tools
npm install -g uglify-js cssnano-cli

# Minify JavaScript
uglifyjs js/app.js -c -m -o js/app.min.js

# Minify CSS
cssnano css/styles.css css/styles.min.css


**2. Enable Browser Caching:**


Add to your hosting platform:

Cache-Control: public, max-age=31536000


**3. Lazy Loading:**
• Load components on-demand
• Defer non-critical JavaScript
• Use intersection observer for images


⸻


Scaling Considerations

When to Upgrade PythonAnywhere Plan

Upgrade if you experience:
• ⚠️ CPU seconds limit reached frequently
• ⚠️ More than 100 concurrent users
• ⚠️ Need for scheduled tasks (cron jobs)
• ⚠️ Multiple applications needed
• ⚠️ Database size exceeds free tier


Database Scaling

**Strategies:**
• Upgrade to paid MySQL plan (more storage/connections)
• Implement Redis caching layer
• Use read replicas for heavy read workloads
• Archive old data regularly


Application Scaling

**Horizontal Scaling:**
• Load balancer across multiple PythonAnywhere instances
• CDN for static assets (Cloudflare)
• Microservices architecture for high-traffic components


⸻


Support Resources
• **PythonAnywhere Help:** [help.pythonanywhere.com](https://help.pythonanywhere.com/)
• **PythonAnywhere Forums:** [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums/)
• **Flask Documentation:** [flask.palletsprojects.com](https://flask.palletsprojects.com/)
• **Project Issues:** GitHub repository Issues tab


⸻


Deployment Checklist

Pre-Deployment
• Local testing complete (all features working)
• All API endpoints tested
• Database migrations prepared
• Environment variables documented
• Frontend `config.js` points to production API
• `.gitignore` includes `.env` and sensitive files
• README.md updated with deployment info


Deployment
• Code uploaded to PythonAnywhere
• Virtual environment created (Python 3.10)
• Dependencies installed (`requirements.txt`)
• MySQL database created
• Database tables initialized
• WSGI file configured correctly
• Virtualenv path set in Web tab
• Environment variables configured (`.env` or Web tab)
• Web app reloaded successfully


Post-Deployment
• Health check endpoint returns `{"status":"healthy"}`
• All API endpoints tested and working
• Frontend deployed (GitHub Pages / Netlify / Vercel)
• Frontend can communicate with backend
• CORS configured correctly (no browser errors)
• Error logs checked (no critical errors)
• Test data created successfully
• Database backup strategy in place
• Monitoring set up (logs, CPU usage)
• Documentation updated with live URLs


⸻


🎉 Deployment Complete!

Your Equestrian Management System is now live and accessible:


Live URLs
• **Backend API:** `https://yourusername.pythonanywhere.com/api`
• **API Health:** `https://yourusername.pythonanywhere.com/health`
• **Frontend:** `https://yourusername.github.io/equestrian-management/`


Quick Links
• **PythonAnywhere Dashboard:** [pythonanywhere.com/user/yourusername](https://www.pythonanywhere.com/user/yourusername/)
• **Web App:** Web tab
• **Database:** Databases tab
• **Files:** Files tab
• **Console:** Consoles tab


Next Steps
1. ✅ Test all functionality end-to-end
2. ✅ Add sample data for demonstration
3. ✅ Share with users and collect feedback
4. ✅ Set up monitoring and alerts
5. ✅ Plan regular maintenance schedule


⸻


**Last Updated:** November 28, 2024  
**Version:** 1.0.0  
**Author:** Your Development Team


⸻


**Need Help?**  
Refer to [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or open an issue on GitHub.