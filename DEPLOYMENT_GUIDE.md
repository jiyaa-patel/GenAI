# GenAI Legal - Website Deployment Guide

## 🚀 Production URLs
- **Frontend**: https://genai-silk-beta.vercel.app/
- **Django Backend**: https://gen-ai-legal.uc.r.appspot.com
- **FastAPI Service**: https://fastapi-dot-gen-ai-legal.uc.r.appspot.com

## 📋 Pre-Deployment Checklist

### ✅ Configuration Files Updated
- [x] `Final_Frontend/.env` - Production environment variables
- [x] `Final_Frontend/.env.production` - Vercel production config
- [x] `Final_Frontend/vercel.json` - Vercel deployment configuration
- [x] Backend CORS settings updated for your frontend URL

## 🌐 Frontend Deployment (Vercel)

### Option 1: Automatic Deployment (Recommended)
1. **Push to GitHub**:
   ```bash
   cd Final_Frontend
   git add .
   git commit -m "Update production URLs for deployment"
   git push origin main
   ```

2. **Vercel Auto-Deploy**:
   - Vercel will automatically detect the push and deploy
   - Check deployment status at: https://vercel.com/dashboard

### Option 2: Manual Deployment
1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy from Frontend Directory**:
   ```bash
   cd Final_Frontend
   vercel --prod
   ```

### Option 3: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Import your GitHub repository
3. Set environment variables in Vercel dashboard:
   - `VITE_GOOGLE_CLIENT_ID`: `488637618552-fs78i0lr0tul8qo38dmt45mn5hm3h50q.apps.googleusercontent.com`
   - `VITE_DJANGO_BASE_URL`: `https://gen-ai-legal.uc.r.appspot.com`
   - `VITE_FASTAPI_BASE_URL`: `https://fastapi-dot-gen-ai-legal.uc.r.appspot.com`

## 🔧 Backend Services (Already Deployed)

### Django Backend
- **URL**: https://gen-ai-legal.uc.r.appspot.com
- **Status**: ✅ Deployed and configured
- **Handles**: Authentication, user management, chat sessions

### FastAPI Service  
- **URL**: https://fastapi-dot-gen-ai-legal.uc.r.appspot.com
- **Status**: ✅ Deployed and configured
- **Handles**: Document processing, AI chat, file uploads

## 🔍 Post-Deployment Verification

### 1. Test Frontend Access
```bash
curl -I https://genai-silk-beta.vercel.app/
# Should return: HTTP/2 200
```

### 2. Test API Connections
Open browser console on your frontend and check:
- Django URL should show in console logs
- FastAPI URL should show in console logs
- No CORS errors should appear

### 3. Test Full Flow
1. Visit https://genai-silk-beta.vercel.app/
2. Sign up/Login with Google
3. Upload a PDF document
4. Start chatting with the document
5. Verify chat history is saved

## 🛠 Environment Variables Summary

### Frontend (Vercel)
```env
VITE_GOOGLE_CLIENT_ID="488637618552-fs78i0lr0tul8qo38dmt45mn5hm3h50q.apps.googleusercontent.com"
VITE_DJANGO_BASE_URL="https://gen-ai-legal.uc.r.appspot.com"
VITE_FASTAPI_BASE_URL="https://fastapi-dot-gen-ai-legal.uc.r.appspot.com"
```

### Django Backend (App Engine)
```yaml
env_variables:
  GCP_PROJECT: "gen-ai-legal"
  GCS_BUCKET_NAME: "legal-agreement-analyzer-gen-ai-legal"
```

### FastAPI Service (App Engine)
```yaml
env_variables:
  GCP_PROJECT: "gen-ai-legal"
  GCS_BUCKET_NAME: "legal-agreement-analyzer-gen-ai-legal"
  GEMINI_API_KEY: "AIzaSyANsEjkReSfVGOkXg3v3XS82UXoaz7J95A"
```

## 🔐 Security Features
- ✅ CORS configured for your frontend domain
- ✅ Authentication tokens properly handled
- ✅ Secure API communication between services
- ✅ Environment-based configuration

## 📊 Monitoring & Logs

### Frontend (Vercel)
- Dashboard: https://vercel.com/dashboard
- Function logs available in Vercel dashboard

### Backend Services (Google Cloud)
```bash
# Django logs
gcloud app logs tail -s default

# FastAPI logs  
gcloud app logs tail -s fastapi
```

## 🚨 Troubleshooting

### Common Issues:
1. **CORS Errors**: Check that frontend URL is in backend CORS settings
2. **API Not Found**: Verify environment variables are set correctly
3. **Authentication Issues**: Check Google OAuth client ID configuration

### Quick Fixes:
```bash
# Redeploy if needed
cd Final_Backend
gcloud app deploy app.yaml

cd geniai  
gcloud app deploy fastapi.yaml
```

## 🎉 Success Indicators
- ✅ Frontend loads at https://genai-silk-beta.vercel.app/
- ✅ User can sign up/login
- ✅ Document upload works
- ✅ AI chat responds to questions
- ✅ Chat history is preserved
- ✅ No console errors

Your website is now ready for production! 🚀