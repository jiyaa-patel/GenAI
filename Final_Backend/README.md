# Legal Agreement Analyzer - Backend Setup

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backEnd
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the `geniai/` directory:
```env
# Database Configuration (Already configured in settings.py)
# HOST: 35.224.143.5
# PORT: 5432
# DATABASE: gen-ai
# USER: postgres
# PASSWORD: Temp#1234

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=credentials/gen-ai-legal-536c695ad0a1.json
GCP_PROJECT=gen-ai-legal
GCS_BUCKET_NAME=legal-agreement-analyzer-gen-ai-legal

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start Services

**Django (Port 8000):**
```bash
python manage.py runserver
```

**FastAPI (Port 8001): (on different terminal)** 
```bash
python -m geniai.run_fastapi
```

## 🔧 Troubleshooting

### ❌ Database Connection Error
```
psycopg2.OperationalError: connection to server at "35.224.143.5", port 5432 failed
```

**Database Details:**
- **Host:** `35.224.143.5`
- **Port:** `5432`
- **Database:** `gen-ai`
- **Username:** `postgres`
- **Password:** `Temp#1234`

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **SQL** → **gen-ai-legal** (database instance)
3. Click **Connections** → **Networking**
4. Under **Authorized Networks**, click **Add Network**
5. Add your IP address: `YOUR_IP/32`
6. Click **Save**

**Find Your IP:**
- Visit [whatismyipaddress.com](https://whatismyipaddress.com/)
- Copy your IPv4 address

**⚠️ CRITICAL:** You MUST add your IP to authorized networks before the backend will work!

### ❌ GCS Bucket Error
```
The specified bucket does not exist
```

**Solution:**
1. Verify bucket name in `.env` file
2. Check GCS credentials path
3. Ensure service account has Storage Admin permissions

### ❌ Import Errors
```
ModuleNotFoundError: No module named 'xyz'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

## 📁 Project Structure
```
backEnd/
├── geniai/                 # FastAPI app
│   ├── api.py             # Main FastAPI routes
│   ├── run_fastapi.py     # FastAPI server
│   └── models.py          # Django models
├── users/                 # User management
├── credentials/           # GCS service account key
├── manage.py             # Django management
└── requirements.txt      # Python dependencies
```

## 🔑 Required Services

### Google Cloud Services
- **Cloud SQL (PostgreSQL)** - Database
- **Cloud Storage** - File storage
- **Vertex AI** - AI processing
- **Secret Manager** - API keys

### API Keys Needed
- **Gemini API Key** - For AI responses
- **Google Cloud Service Account** - For GCS access

## 🌐 API Endpoints

### Django (Port 8000)
- `POST /api/login/` - User authentication
- `GET /api/geniai/chat-sessions/` - Get chat sessions
- `POST /api/geniai/chat-sessions/{id}/messages/` - Save messages

### FastAPI (Port 8001)
- `POST /api/upload-document` - Upload PDF documents
- `POST /api/ask-question` - Chat with AI
- `GET /api/health` - Health check

## 🔒 Security Notes

### Database Security
- Database is protected by IP whitelist
- Add your IP to authorized networks in GCS
- Use strong database passwords

### API Security
- JWT tokens for authentication
- CORS enabled for frontend
- Service account for GCS access

## 📝 Common Issues

### 1. Authentication Errors (401)
- Check if user is logged in
- Verify JWT tokens in localStorage
- Ensure database connection is working

### 2. File Upload Errors (500)
- Verify GCS bucket exists
- Check service account permissions
- Ensure correct bucket name in config

### 3. AI Response Errors
- Verify Gemini API key
- Check Vertex AI quotas
- Ensure document is processed

## 🆘 Need Help?

1. **Check logs** in terminal for detailed errors
2. **Verify environment variables** in `.env` file
3. **Test database connection** with `python manage.py dbshell`
4. **Check GCS access** by visiting bucket in console
5. **Restart services** if configuration changes

## 📞 Support

If you encounter issues:
1. Check this README first
2. Look at error logs in terminal
3. Verify all environment variables are set
4. Ensure your IP is whitelisted in GCS
5. Contact the development team

---

**⚠️ Important:** Always add your IP address to the database authorized networks before starting the backend services.