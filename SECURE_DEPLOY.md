# 🚀 Secure Deployment Guide - Streamlit Cloud

## 🔒 Security First

**IMPORTANT**: This guide contains NO actual credentials. All sensitive information must be added securely in Streamlit Cloud.

## Step 1: Push to GitHub (GitHub Desktop)

1. **Open GitHub Desktop**
2. **File → Add Local Repository**
3. **Browse to**: `/Users/justingrosz/Documents/claude/tableau_converter`
4. **Click "Add Repository"**
5. **Click "Publish repository"**
6. **Repository name**: `tableau_to_app`
7. **Description**: `AI-Powered Tableau Dashboard Converter`
8. **Make it public**
9. **Click "Publish Repository"**

## Step 2: Deploy to Streamlit Cloud

1. **Visit**: https://share.streamlit.io/
2. **Sign in** with GitHub account
3. **Click "New app"**
4. **Repository**: `grosz99/tableau_to_app`
5. **Branch**: `main`
6. **Main file**: `app.py`
7. **Click "Deploy"**

## Step 3: Configure Secrets (SECURE)

In Streamlit Cloud **App Settings** → **Secrets**, add:

```toml
# Snowflake Configuration
SNOWFLAKE_ACCOUNT = "your_account"
SNOWFLAKE_USER = "your_user"
SNOWFLAKE_PASSWORD = "your_password"
SNOWFLAKE_WAREHOUSE = "your_warehouse"
SNOWFLAKE_DATABASE = "your_database"
SNOWFLAKE_SCHEMA = "your_schema"
SNOWFLAKE_ROLE = "your_role"

# AI Configuration
ANTHROPIC_API_KEY = "your_anthropic_api_key"
```

**⚠️ SECURITY NOTES:**
- Replace ALL placeholder values with your actual credentials
- NEVER commit real credentials to GitHub
- Only add credentials in Streamlit Cloud secrets
- Keep your API keys secure

## Step 4: Test the Application

### Upload Test File
Use your SuperStore dashboard TWBX file to test:
- Formula extraction
- Data source detection
- Streamlit app generation

### Expected Features
✅ Extract calculations from any .twbx file
✅ Detect data sources automatically
✅ Generate Streamlit applications
✅ Download working packages

## 🛡️ Security Checklist

- [ ] No credentials in GitHub repository
- [ ] Secrets configured in Streamlit Cloud only
- [ ] API keys kept secure
- [ ] Repository is clean of sensitive data

## 🚀 Ready for Safe Deployment

This deployment is secure and ready for testing!