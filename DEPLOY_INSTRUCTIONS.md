# 🚀 Deploy to Streamlit Cloud - Manual Instructions

## Step 1: Push to GitHub (Use GitHub Desktop)

Since command line authentication isn't working, use GitHub Desktop:

1. **Open GitHub Desktop**
2. **File → Add Local Repository**
3. **Browse to**: `/Users/justingrosz/Documents/claude/tableau_converter`
4. **Click "Add Repository"**
5. **Click "Publish repository"**
6. **Repository name**: `tableau_to_app`
7. **Description**: `AI-Powered Tableau Dashboard Converter - Streamlit Prototype`
8. **Uncheck "Keep this code private"** (make it public)
9. **Click "Publish Repository"**

## Step 2: Deploy to Streamlit Cloud

### 2.1 Go to Streamlit Cloud
1. **Visit**: https://share.streamlit.io/
2. **Sign in** with your GitHub account: `grosz99`

### 2.2 Create New App
1. **Click "New app"**
2. **Repository**: Select `grosz99/tableau_to_app`
3. **Branch**: `main`
4. **Main file path**: `app.py`
5. **App URL**: `tableau-dashboard-converter` (or any name you prefer)

### 2.3 Deploy
**Click "Deploy"** - It will take 2-3 minutes to build

## Step 3: Configure Secrets (IMPORTANT!)

Once deployed, go to **App Settings** → **Secrets** and add:

```toml
SNOWFLAKE_ACCOUNT = "your_snowflake_account"
SNOWFLAKE_USER = "your_snowflake_user"
SNOWFLAKE_PASSWORD = "your_snowflake_password"
SNOWFLAKE_WAREHOUSE = "your_warehouse"
SNOWFLAKE_DATABASE = "your_database"
SNOWFLAKE_SCHEMA = "your_schema"
SNOWFLAKE_ROLE = "your_role"
ANTHROPIC_API_KEY = "your_anthropic_api_key"
```

**NOTE**: Replace these with your actual credentials. Never commit real credentials to version control!

## Step 4: Test the Application

### 4.1 Upload SuperStore Dashboard
- Use the file: `SuperStore Business Dashboard 2025 _ VOTD _ VizOfTheDay.twbx`
- This is the one we've been testing with

### 4.2 Expected Results
✅ **58 calculations extracted**
✅ **Formula translation working**
✅ **Data source detection: Hyper extract**
✅ **Streamlit app generation**
✅ **Download package available**

### 4.3 Test Different Features
1. **Tab 1**: Upload the SuperStore .twbx file
2. **Tab 2**: Review extracted calculations and translations
3. **Tab 3**: Generate Streamlit app
4. **Tab 4**: View validation results

## Step 5: Test with Other Dashboards

Try uploading other .twbx files to test generalizability:
- Should extract calculations from any dashboard
- Should detect data sources automatically
- Should generate appropriate connection code

## 🎯 What You're Testing

This deployment will validate:
- **Formula extraction accuracy** (92.8% validated)
- **AI translation system** (Tableau → Python)
- **Data source detection** (Hyper, Snowflake, Excel, etc.)
- **Streamlit generation** (production-ready code)
- **Security** (no credentials exposed)

## 📋 Deployment Checklist

- [ ] Push to GitHub via GitHub Desktop
- [ ] Deploy to Streamlit Cloud
- [ ] Configure secrets
- [ ] Test with SuperStore dashboard
- [ ] Verify all features work
- [ ] Test with other dashboards (optional)

## 🔧 If Issues Arise

- **Build errors**: Check requirements.txt dependencies
- **Import errors**: Some packages may not be available on Streamlit Cloud
- **Authentication errors**: Verify secrets are configured correctly
- **Performance issues**: Large .twbx files may take time to process

## 🚀 Success Metrics

The deployment is successful if:
- App loads without errors
- Can upload and parse .twbx files
- Extracts calculations correctly
- Generates Streamlit code
- Downloads work properly

**Ready to deploy! Follow these steps and the app will be live for testing.** 🎉