# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Railway deployment config"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `medusa_tools` repository
6. Railway will automatically detect it's a Python app and deploy!

### Step 3: Environment Variables (Optional)
In Railway dashboard, go to your project → Variables tab:
- `SECRET_KEY`: Generate a secure secret key
- `UPLOAD_FOLDER`: Leave empty (uses temp folder)

### Step 4: Custom Domain (Optional)
- In Railway dashboard → Settings → Domains
- Add your custom domain or use the provided railway.app URL

## 🔧 Local Testing with Production Config
```bash
pip install -r requirements_web.txt
PORT=8000 python web_app.py
```

## 📊 Monitoring
- Railway provides automatic metrics and logs
- Check the dashboard for usage and performance
- Free tier: 500 hours/month (enough for hobby use)

## 🆙 Scaling
When you outgrow free tier:
- Upgrade to Pro plan ($5/month)
- Automatic scaling based on traffic
- More memory and CPU resources

## 🛠️ Troubleshooting
- Check Railway logs in dashboard
- Most common issues: missing dependencies or timeout errors
- Audio processing timeout: increase in `railway.toml` if needed 