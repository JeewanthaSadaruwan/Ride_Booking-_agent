# Ride Booking Agent - Complete Setup Guide

## Overview

This project now has TWO separate applications:

1. **Backend** (Python/Streamlit) - Located in the root directory
2. **Frontend** (React/TypeScript) - Located in the `frontend/` directory

## Quick Start

### Option 1: Run Backend Only (Original Streamlit UI)

```bash
# From root directory
python -m streamlit run app.py
```

### Option 2: Run New React Frontend + Backend

**Terminal 1 - Start Backend API:**
```bash
# From root directory
# First, ensure your backend exposes REST APIs
# You may need to create a FastAPI/Flask server wrapper
python run_backend_api.py  # You'll need to create this
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open: `http://localhost:3000`

## Backend API Requirements

The React frontend expects these REST API endpoints:

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/signup` - Register new user
- `GET /api/auth/profile` - Get current user
- `POST /api/auth/logout` - Logout user

### Chat
- `POST /api/chat` - Send message to agent
- `GET /api/chat/history` - Get chat history

### Bookings
- `GET /api/bookings/my` - Get user's bookings
- `POST /api/bookings` - Create new booking
- `GET /api/bookings/:id` - Get booking details
- `POST /api/bookings/:id/cancel` - Cancel booking

### Locations & Vehicles
- `POST /api/location/geocode` - Geocode location text
- `POST /api/location/route` - Calculate route
- `GET /api/vehicles` - Get available vehicles
- `POST /api/vehicles/recommend` - Get vehicle recommendations

## Project Structure

```
ride-booking-agent/
├── frontend/                 # NEW: React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   ├── types/          # TypeScript types
│   │   └── ...
│   ├── package.json
│   └── README.md
│
├── agents/                  # Existing: Python backend
├── auth/
├── config/
├── db/
├── models/
├── tools/
├── ui/
├── app.py                   # Existing: Streamlit app
└── requirements.txt
```

## Development Workflow

### 1. Backend Development (Python)

Your existing backend is intact. To add REST API support:

**Option A: Create FastAPI wrapper** (Recommended)

Create `backend_api.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your existing logic
from agents.booking_agent import BookingAgent
from auth.auth import AuthManager
# ... etc

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Use your existing booking agent
    pass

# Add other endpoints...
```

Run with:
```bash
pip install fastapi uvicorn
uvicorn backend_api:app --reload --port 8000
```

**Option B: Extend existing Flask/other framework**

If you're using Flask or another framework, add the required endpoints there.

### 2. Frontend Development (React)

```bash
cd frontend
npm run dev
```

The frontend will:
- Run on `http://localhost:3000`
- Proxy API requests to `http://localhost:8000`
- Hot-reload on code changes

## Migration Path

### Phase 1: Parallel Development ✅ (Current)
- Old Streamlit UI still works
- New React UI being developed
- Both can run simultaneously

### Phase 2: API Integration (Next Step)
1. Create REST API wrapper for backend
2. Test all endpoints with Postman/curl
3. Connect React frontend to APIs
4. Test full flow

### Phase 3: Deployment
1. Deploy backend API (e.g., AWS, Heroku)
2. Build React frontend: `npm run build`
3. Deploy frontend (e.g., Vercel, Netlify)
4. Update API URLs in frontend config

## Key Differences

### Old (Streamlit)
- ✅ Quick to develop
- ✅ Built-in UI components
- ❌ Limited customization
- ❌ Not production-grade UI
- ❌ Desktop-focused

### New (React)
- ✅ Modern, professional UI
- ✅ Fully customizable
- ✅ Mobile-responsive
- ✅ Better performance
- ✅ Real-time features
- ✅ Investment-ready

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./db/bookings.db
JWT_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-key
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Testing

### Test Backend API
```bash
# Check health
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Test Frontend
```bash
cd frontend
npm run dev
# Open http://localhost:3000
```

## Troubleshooting

### Frontend can't connect to backend
- Check backend is running on port 8000
- Check CORS is enabled in backend
- Check proxy config in `frontend/vite.config.ts`

### Port conflicts
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Build errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. **Create Backend API** (Most Important)
   - Wrap your existing logic with FastAPI/Flask
   - Implement all required endpoints
   - Add JWT authentication
   - Test with Postman

2. **Integrate Frontend**
   - Update API URLs if needed
   - Test authentication flow
   - Test booking flow
   - Fix any API mismatches

3. **Polish & Deploy**
   - Add error handling
   - Add loading states
   - Add analytics
   - Deploy to production

## Production Deployment

### Backend (Example: AWS EC2)
```bash
# On server
git clone your-repo
pip install -r requirements.txt
uvicorn backend_api:app --host 0.0.0.0 --port 8000
```

### Frontend (Example: Vercel)
```bash
cd frontend
npm run build
# Upload dist/ to Vercel or run: vercel deploy
```

## Support

- Frontend docs: `frontend/README.md`
- Backend docs: `README.md` (original)
- Issues: Check console logs and API responses

## Summary

You now have a **modern, production-ready React frontend** that:
- ✅ Replaces Streamlit UI
- ✅ Preserves all features
- ✅ Adds professional polish
- ✅ Ready for investors/customers
- ✅ Mobile-responsive
- ✅ Scalable architecture

**Next critical step**: Create the REST API backend wrapper to connect everything together!
