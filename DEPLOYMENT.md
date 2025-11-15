# Thread Engagement Calculator - Deployment Guide

## 🚀 Deployment Options

Since this is a **Flask (Python)** application, it **cannot** be deployed to Netlify (Netlify only supports static sites and serverless functions).

---

## ✅ Recommended: Deploy to Render.com (FREE)

### Why Render?
- ✅ Free tier available
- ✅ Easy Python/Flask support
- ✅ Automatic deployments from Git
- ✅ HTTPS included
- ✅ No credit card required for free tier

### Step-by-Step Deployment:

#### 1. Prepare Your Repository

First, initialize a Git repository if you haven't:

```powershell
cd "D:\Thread Engagement"
git init
git add .
git commit -m "Initial commit - Thread Engagement Calculator v2.0"
```

#### 2. Push to GitHub

Create a new repository on GitHub, then:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/thread-engagement-calculator.git
git branch -M main
git push -u origin main
```

#### 3. Deploy on Render

1. Go to https://render.com and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in the settings:
   - **Name:** `thread-engagement-calculator`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

5. Click **"Create Web Service"**

6. Wait 2-3 minutes for deployment

7. Your app will be live at: `https://thread-engagement-calculator.onrender.com`

---

## 🔧 Alternative Deployment Options

### Option 2: Railway.app (FREE)

1. Visit https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Flask and deploys
6. Live at: `https://your-app.up.railway.app`

**Pros:**
- Even easier than Render
- Great free tier
- Fast deployments

---

### Option 3: PythonAnywhere (FREE)

1. Visit https://www.pythonanywhere.com
2. Sign up for free account
3. Upload your code via Files tab
4. Create a new web app (Flask)
5. Configure WSGI file
6. Live at: `https://yourusername.pythonanywhere.com`

**Pros:**
- Persistent storage
- Easy file management
- Python-focused platform

**Cons:**
- More manual setup
- Limited free tier hours

---

### Option 4: Google Cloud Run (PAY-AS-YOU-GO)

1. Install Google Cloud SDK
2. Create Dockerfile (provided below)
3. Deploy with one command

```powershell
gcloud run deploy thread-calculator --source .
```

**Pros:**
- Scales automatically
- Pay only for usage
- Very generous free tier

---

### Option 5: Heroku (PAID - $5/month minimum)

Heroku removed their free tier, but if you're willing to pay $5/month:

```powershell
heroku create thread-engagement-calc
git push heroku main
heroku open
```

---

## 📦 Docker Deployment (For Cloud Run, AWS, Azure)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

---

## 🔒 Environment Variables

For production deployment, set these environment variables:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this
PORT=8080
```

On Render/Railway, set in dashboard → Environment Variables

---

## ⚙️ Production Configuration

Update `app.py` for production (already done):

```python
# Development
if __name__ == '__main__':
    app.run(debug=True)

# Production uses gunicorn (no changes needed)
```

---

## 🎯 My Recommendation

**For this project, use Render.com:**

### Pros:
✅ Completely free (forever for basic apps)  
✅ No credit card required  
✅ Easy GitHub integration  
✅ Automatic HTTPS  
✅ Automatic deploys on Git push  
✅ Great for Flask apps  
✅ Professional URL  

### Setup Time: 5 minutes

### Performance:
- Free tier sleeps after 15 min inactivity
- First request after sleep: ~30 seconds
- Subsequent requests: < 1 second
- Perfect for demos and portfolio

---

## 🚫 Why NOT Netlify?

Netlify is for **static sites** (HTML/CSS/JS only), not Python apps.

To use Netlify, you'd need to:
1. Rewrite entire app in JavaScript
2. Use Netlify Functions (serverless)
3. Major architecture change
4. Not recommended for this Flask app

---

## 📝 Quick Start: Render Deployment

```powershell
# 1. Install gunicorn (already in requirements.txt)
pip install gunicorn

# 2. Test locally
gunicorn app:app

# Visit http://localhost:8000 to test

# 3. Initialize Git (if not done)
git init
git add .
git commit -m "Ready for deployment"

# 4. Push to GitHub
# (Create repo on GitHub first)
git remote add origin YOUR_GITHUB_URL
git push -u origin main

# 5. Deploy on Render.com
# - Sign up at render.com
# - New Web Service
# - Connect GitHub repo
# - Deploy!
```

---

## ✅ Verification After Deployment

Once deployed, test:

1. ✅ Homepage loads
2. ✅ Calculator works (try M10, 15000N)
3. ✅ Materials dropdown populates
4. ✅ Batch analysis works
5. ✅ Advanced options (torque, fatigue, etc.)
6. ✅ PDF export downloads
7. ✅ Dark mode toggle
8. ✅ Mobile responsive

---

## 🆘 Troubleshooting

### App won't start:
- Check logs on Render dashboard
- Verify `requirements.txt` is complete
- Ensure `Procfile` is correct

### Calculator not working:
- Check browser console for errors
- Verify all Python packages installed
- Test locally first

### PDF export fails:
- Ensure `reportlab` in requirements.txt
- Check write permissions
- Verify matplotlib backend

---

## 📞 Support

For deployment issues:
- **Render:** https://docs.render.com
- **Railway:** https://docs.railway.app
- **PythonAnywhere:** https://help.pythonanywhere.com

---

## 🎉 You're Ready!

Follow the Render.com steps above to get your Thread Engagement Calculator live on the web!

**Estimated Time:** 10 minutes  
**Cost:** $0.00 (free forever)  
**URL:** `https://your-app-name.onrender.com`

Good luck! 🚀
