# 🔧 Configuration Guide: Google Cloud & Vertex AI Setup

## 📋 What You Need to Configure

You need to set up **3 things**:

1. **Google Cloud Project ID** - Your project identifier
2. **Service Account Key** - Authentication credentials
3. **Environment Variables** - Tell the app where to find your credentials

---

## 🎯 Step 1: Get Your Google Cloud Project ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Look at the top-left corner - you'll see your project name
3. Click on the project name to see your **Project ID**
4. Copy the Project ID (it looks like `my-project-123456`)

---

## 🔑 Step 2: Create Service Account & Download Key

### 2.1 Create Service Account
1. In Google Cloud Console, go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Fill in:
   - **Service account name**: `vertex-ai-service`
   - **Service account ID**: Will auto-generate
   - **Description**: `Service account for Vertex AI document processing`
4. Click **Create and Continue**

### 2.2 Assign Roles
1. Click **Select a role**
2. Search for and select these roles:
   - **Vertex AI User**
   - **Vertex AI Service Agent**
3. Click **Continue**
4. Click **Done**

### 2.3 Download JSON Key
1. Find your service account in the list and click on it
2. Go to **Keys** tab
3. Click **Add Key** → **Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. **Save the JSON file** to a safe location (e.g., `C:\credentials\service-account-key.json`)

---

## ⚙️ Step 3: Configure Your Application

### Option A: Environment Variables (Recommended)

Open PowerShell and run these commands:

```powershell
# Replace with your actual values
$env:GCP_PROJECT_ID = "your-actual-project-id"
$env:GCP_LOCATION = "us-central1"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\your\service-account-key.json"
```

### Option B: Edit config.py directly

Open `backEnd/ai/config.py` and replace the values:

```python
VERTEX_AI_CONFIG = {
    'project_id': 'your-actual-project-id',  # Replace this
    'location': 'us-central1',               # Change if needed
    'model_name': 'gemini-1.0-pro',          # Change if needed
}
```

---

## 🧪 Step 4: Test Your Configuration

Run this command to test if everything is working:

```bash
cd backEnd
python test_vertex_ai.py
```

**Expected Output:**
```
🧪 Vertex AI Configuration Test
==================================================
Testing Vertex AI connection...
Project ID: your-actual-project-id
Location: us-central1
Model: gemini-1.0-pro
--------------------------------------------------
✅ Vertex AI connection successful!
Response: [Your Vertex AI response here]

🎉 Your Vertex AI setup is working correctly!

✅ All tests passed! You're ready to use the document processing feature.
```

---

## 🚨 Troubleshooting

### Error: "Project ID not found"
- Double-check your Project ID in Google Cloud Console
- Make sure you're using the Project ID, not the Project Name

### Error: "Authentication failed"
- Verify your service account JSON key file path
- Make sure the JSON file contains valid credentials
- Check that the service account has the required roles

### Error: "Vertex AI API not enabled"
- Go to Google Cloud Console → APIs & Services → Library
- Search for "Vertex AI API"
- Click "Enable"

### Error: "Permission denied"
- Make sure your service account has these roles:
  - Vertex AI User
  - Vertex AI Service Agent

---

## 📁 File Structure Example

```
D:\Hackathon\genAi\
├── backEnd\
│   ├── ai\
│   │   ├── config.py          # Your configuration here
│   │   └── views.py           # Uses the config
│   └── credentials\           # Create this folder
│       └── service-account-key.json  # Your key file here
```

---

## ✅ Success Checklist

- [ ] Google Cloud Project ID obtained
- [ ] Service Account created with correct roles
- [ ] JSON key file downloaded and saved
- [ ] Environment variables set OR config.py updated
- [ ] Test script runs successfully
- [ ] Django server starts without errors

---

## 🚀 Next Steps

Once configuration is complete:

1. **Start Django server:**
   ```bash
   cd backEnd
   python manage.py runserver
   ```

2. **Start React frontend:**
   ```bash
   cd FrontEnd/frontEnd
   npm run dev
   ```

3. **Test the complete flow:**
   - Log in to your application
   - Upload a document (PDF, DOCX, or TXT)
   - Check if AI analysis appears

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all credentials are correct
3. Ensure Vertex AI API is enabled
4. Check that your service account has proper permissions
