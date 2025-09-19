
# Cloud SQL Connection Troubleshooting Guide

## 🚨 **Current Issue: Connection Timeout**

Your Django application is failing to connect to Cloud SQL PostgreSQL at `35.224.143.5:5432` with a connection timeout error.

## 🔍 **Possible Causes & Solutions**

### 1. **Cloud SQL Instance Issues**

**Check if your Cloud SQL instance is running:**
```bash
# Using gcloud CLI (if you have it installed)
gcloud sql instances list
gcloud sql instances describe YOUR_INSTANCE_NAME
```

**Common issues:**
- Instance is stopped
- Instance is in maintenance mode
- Instance is overloaded
- Network connectivity issues

### 2. **Network Configuration**

**Check Cloud SQL network settings:**
- Ensure your IP address is whitelisted
- Check if you're using Cloud SQL Proxy (recommended)
- Verify firewall rules

### 3. **Connection Pooling Issues**

**If using connection pooling:**
- Too many concurrent connections
- Connection timeout settings too low
- Database is locked

## 🛠️ **Immediate Solutions**

### **Option 1: Use Cloud SQL Proxy (Recommended)**

```bash
# Install Cloud SQL Proxy
# Download from: https://cloud.google.com/sql/docs/mysql/sql-proxy

# Start proxy (replace with your instance details)
./cloud_sql_proxy -instances=YOUR_PROJECT:YOUR_REGION:YOUR_INSTANCE=tcp:5432

# Then update your Django settings to connect to localhost
```

**Updated Django settings for proxy:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gen_ai_db',
        'USER': 'postgres',
        'PASSWORD': 'Temp#1234',
        'HOST': '127.0.0.1',  # Localhost when using proxy
        'PORT': '5432',
    }
}
```

### **Option 2: Use SQLite for Development**

**Temporarily switch to SQLite for local development:**

```python
# In settings.py - comment out PostgreSQL and use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'gen_ai_db',
#         'USER': 'postgres',
#         'PASSWORD': 'Temp#1234',
#         'HOST': '35.224.143.5',
#         'PORT': '5432',
#     }
# }
```

### **Option 3: Check Cloud SQL Instance Status**

**Using Google Cloud Console:**
1. Go to Cloud SQL in Google Cloud Console
2. Check if your instance is running
3. Verify network settings
4. Check connection logs

**Using gcloud CLI:**
```bash
# Check instance status
gcloud sql instances list --filter="name:YOUR_INSTANCE_NAME"

# Check instance details
gcloud sql instances describe YOUR_INSTANCE_NAME

# Check connection logs
gcloud sql operations list --instance=YOUR_INSTANCE_NAME
```

## 🔧 **Quick Fix: Switch to SQLite for Now**

Let me help you switch to SQLite temporarily so you can continue development:
