# Vercel Deployment Guide for Ride Booking Frontend

## Quick Deploy to Vercel (5 minutes)

### 1. Install Vercel CLI (optional)
```bash
npm install -g vercel
```

### 2. Deploy via Vercel Website (Easiest)

1. **Go to [vercel.com](https://vercel.com/)** and sign in with GitHub

2. **Click "Add New" → "Project"**

3. **Import your GitHub repository:**
   - Select: `JeewanthaSadaruwan/Ride_Booking-_agent`
   - Branch: `sample`

4. **Configure Project:**
   - Framework Preset: **Vite**
   - Root Directory: **frontend**
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)

5. **Add Environment Variable:**
   - Name: `VITE_API_URL`
   - Value: `YOUR_AMP_BACKEND_URL` (e.g., `https://your-agent.anthropic.com`)
   
6. **Click "Deploy"** 🚀

Your frontend will be live at: `https://ride-booking-xxx.vercel.app`

### 3. Deploy via CLI (Alternative)

```bash
cd frontend
vercel
# Follow the prompts:
# - Link to existing project? No
# - Project name: ride-booking-frontend
# - Directory: ./
# - Build Command: npm run build
# - Output Directory: dist

# Set environment variable
vercel env add VITE_API_URL production
# Enter your backend URL when prompted

# Deploy to production
vercel --prod
```

---

## Option 2: Netlify

### Deploy to Netlify

1. **Go to [netlify.com](https://netlify.com)** and sign in

2. **Click "Add new site" → "Import an existing project"**

3. **Connect GitHub** and select your repo

4. **Configure:**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

5. **Environment Variables:**
   - `VITE_API_URL`: Your backend URL

6. **Deploy!**

---

## Option 3: Railway (Same place as backend)

```bash
# In frontend directory
railway login
railway init
railway up

# Add environment variable in Railway dashboard
# VITE_API_URL = your-backend-url
```

---

## Update Backend CORS

After deploying, update your backend's CORS settings to allow your frontend domain:

In `backend_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://your-frontend.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Test Your Deployment

1. Visit your deployed frontend URL
2. Sign up for an account
3. Try booking a ride
4. Check if data is saved in Supabase

---

## Troubleshooting

**API calls failing?**
- Check VITE_API_URL is set correctly
- Verify backend CORS allows your frontend domain
- Check browser console for errors

**Environment variables not working?**
- Variable names must start with `VITE_`
- Redeploy after adding variables
- Check vercel dashboard → Settings → Environment Variables
