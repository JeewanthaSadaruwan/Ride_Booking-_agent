"""
FastAPI Backend for Ride Booking Agent React Frontend

This file provides REST API endpoints that the React frontend can consume.
It wraps your existing Python backend logic (agents, tools, auth, db) with HTTP endpoints.

To run:
    python backend_api.py
"""

import os

# Enable tool console mode for Strands agent (shows tool calls in terminal)
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import sqlite3
import requests

# Import your existing auth functions
from auth.auth import signup_user, login_user, get_user_by_id
from tools.geocode_location import geocode_location
from tools.calculate_route import calculate_route
from db.database import get_booking_by_id, cancel_booking as cancel_booking_db

# Initialize FastAPI
app = FastAPI(title="Ride Booking Agent API", version="1.0.0")

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-this-in-production-2026"  # Change in production
ALGORITHM = "HS256"
DB_PATH = "vehicles.db"

# ============================================================================
# Request/Response Models
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class LocationModel(BaseModel):
    text: str
    lat: float
    lon: float

class CreateBookingRequest(BaseModel):
    pickup: LocationModel
    dropoff: LocationModel
    vehicleId: str
    scheduledTime: Optional[str] = None

class GeocodeRequest(BaseModel):
    location: str

class RouteRequest(BaseModel):
    pickup: LocationModel
    dropoff: LocationModel

class ReverseGeocodeRequest(BaseModel):
    lat: float
    lon: float

# ============================================================================
# Authentication Helpers
# ============================================================================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {"message": "Ride Booking Agent API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login with email and password"""
    try:
        print(f"Login request: email={request.email}")
        
        # Use your existing login function
        result = login_user(request.email, request.password)
        
        print(f"Login result: {result}")
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])
        
        # Extract user data from result
        user = result["user"]
        
        # Create JWT token
        token = create_access_token({"sub": user["user_id"]})
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": user["user_id"],
                    "email": user["email"],
                    "name": user["full_name"],
                    "phone": user["phone"]
                },
                "token": token
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """Register new user"""
    try:
        print(f"Signup request: email={request.email}, name={request.name}, phone={request.phone}")
        
        # Use your existing signup function
        result = signup_user(
            email=request.email,
            password=request.password,
            full_name=request.name,
            phone=request.phone
        )
        
        print(f"Signup result: {result}")
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Get the newly created user
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, full_name, phone 
            FROM users WHERE user_id = ?
        """, (result["user_id"],))
        user_data = cursor.fetchone()
        conn.close()
        
        # Create JWT token
        token = create_access_token({"sub": str(user_data[0])})
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": str(user_data[0]),
                    "email": user_data[1],
                    "name": user_data[2],
                    "phone": user_data[3]
                },
                "token": token
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/profile")
async def get_profile(user_id: str = Depends(verify_token)):
    """Get current user profile"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, full_name, phone 
            FROM users WHERE user_id = ?
        """, (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "data": {
                "id": str(user_data[0]),
                "email": user_data[1],
                "name": user_data[2],
                "phone": user_data[3]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/logout")
async def logout(user_id: str = Depends(verify_token)):
    """Logout user"""
    return {"success": True, "message": "Logged out successfully"}

# ============================================================================
# Chat Endpoints
# ============================================================================

from agents.booking_agent import BookingAgent
import asyncio

booking_agent = BookingAgent()

@app.post("/api/chat")
async def chat(request: ChatRequest, user_id: str = Depends(verify_token)):
    """Send message to booking agent"""
    try:
        print(f"Chat request from user {user_id}: {request.message}")
        
        # Get user details for context
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, full_name FROM users WHERE user_id = ?
        """, (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        # Add user context to message so agent knows who is making the request
        user_name = user_data[1] if user_data else "User"
        user_email = user_data[0] if user_data else ""
        
        # Format message with user context that agent can extract
        message_with_context = f"[User: {user_name} ({user_email}) | user_id: {user_id}]\n\n{request.message}"
        if request.context:
            pickup = request.context.get("pickup")
            dropoff = request.context.get("dropoff")
            context_lines = []
            if pickup:
                context_lines.append(
                    f"[MapSelection] Pickup: {pickup.get('text', 'Pinned location')} "
                    f"({pickup.get('lat')}, {pickup.get('lon')})"
                )
            if dropoff:
                context_lines.append(
                    f"[MapSelection] Dropoff: {dropoff.get('text', 'Pinned location')} "
                    f"({dropoff.get('lat')}, {dropoff.get('lon')})"
                )
            if pickup and dropoff:
                try:
                    lat_diff = abs(float(pickup.get("lat")) - float(dropoff.get("lat")))
                    lon_diff = abs(float(pickup.get("lon")) - float(dropoff.get("lon")))
                    if lat_diff > 0.0005 or lon_diff > 0.0005:
                        context_lines.append(
                            "[MapSelection] Pickup and dropoff coordinates are different."
                        )
                except Exception:
                    pass
            if context_lines and "selected my" in request.message.lower():
                context_lines.append(
                    "[MapSelection] Reply should confirm locations recorded without repeating full addresses."
                )
            if context_lines:
                message_with_context = f"{message_with_context}\n\n" + "\n".join(context_lines)
        
        print(f"Sending to agent with context: {message_with_context[:150]}...")
        
        # Forward the message to the booking agent
        response = await booking_agent.chat(message_with_context)
        
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)
        
        print(f"Sending response to frontend: {response[:100]}...")
        
        return {
            "success": True,
            "data": {
                "message": response.strip(),
                "needsMoreInfo": False
            }
        }
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Booking Endpoints
# ============================================================================

@app.get("/api/bookings/my")
async def get_my_bookings(user_id: str = Depends(verify_token)):
    """Get all bookings for current user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if vehicle_type column exists
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Use pickup_time instead of scheduled_time
        if 'vehicle_type' in columns:
            cursor.execute("""
                SELECT booking_id, user_id, vehicle_id, pickup_location, dropoff_location,
                       vehicle_type, status, pickup_time, estimated_cost,
                       distance_km, duration_minutes, created_at, passenger_count
                FROM bookings WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT booking_id, user_id, vehicle_id, pickup_location, dropoff_location,
                       status, pickup_time, estimated_cost,
                       distance_km, duration_minutes, created_at, passenger_count
                FROM bookings WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
        
        bookings_data = cursor.fetchall()
        
        # Get vehicle details for each booking
        vehicle_cache = {}
        
        bookings = []
        for b in bookings_data:
            if 'vehicle_type' in columns:
                # With vehicle_type: booking_id, user_id, vehicle_id, pickup, dropoff, vehicle_type, status, pickup_time, cost, distance, duration, created_at, passengers
                vehicle_id = b[2]
                bookings.append({
                    "id": str(b[0]),
                    "userId": str(b[1]),
                    "pickup": {"text": b[3], "lat": 0, "lon": 0},
                    "dropoff": {"text": b[4], "lat": 0, "lon": 0},
                    "vehicle": {
                        "id": vehicle_id,
                        "type": b[5] or "Economy",
                        "name": b[5] or "Economy Car",
                        "capacity": int(b[12]) if b[12] else 4,
                        "features": ["Air Conditioning"],
                        "pricePerKm": 50,
                        "basePrice": 200,
                        "available": True
                    },
                    "status": b[6] or "confirmed",
                    "scheduledTime": b[7] or datetime.now().isoformat(),
                    "estimatedCost": float(b[8]) if b[8] else 0,
                    "distance": float(b[9]) if b[9] else 0,
                    "duration": float(b[10]) if b[10] else 0,
                    "createdAt": b[11] or datetime.now().isoformat(),
                    "updatedAt": b[11] or datetime.now().isoformat()
                })
            else:
                # Without vehicle_type: booking_id, user_id, vehicle_id, pickup, dropoff, status, pickup_time, cost, distance, duration, created_at, passengers
                vehicle_id = b[2]
                
                # Get vehicle info from vehicles table if not cached
                if vehicle_id not in vehicle_cache:
                    cursor2 = conn.cursor()
                    cursor2.execute("SELECT type, make, model FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                    vehicle_data = cursor2.fetchone()
                    if vehicle_data:
                        vehicle_cache[vehicle_id] = {
                            "type": vehicle_data[0],
                            "name": f"{vehicle_data[1]} {vehicle_data[2]}"
                        }
                    else:
                        vehicle_cache[vehicle_id] = {"type": "Economy", "name": "Economy Car"}
                
                vehicle_info = vehicle_cache[vehicle_id]
                
                bookings.append({
                    "id": str(b[0]),
                    "userId": str(b[1]),
                    "pickup": {"text": b[3], "lat": 0, "lon": 0},
                    "dropoff": {"text": b[4], "lat": 0, "lon": 0},
                    "vehicle": {
                        "id": vehicle_id,
                        "type": vehicle_info["type"],
                        "name": vehicle_info["name"],
                        "capacity": int(b[11]) if b[11] else 4,
                        "features": ["Air Conditioning"],
                        "pricePerKm": 50,
                        "basePrice": 200,
                        "available": True
                    },
                    "status": b[5] or "confirmed",
                    "scheduledTime": b[6] or datetime.now().isoformat(),
                    "estimatedCost": float(b[7]) if b[7] else 0,
                    "distance": float(b[8]) if b[8] else 0,
                    "duration": float(b[9]) if b[9] else 0,
                    "createdAt": b[10] or datetime.now().isoformat(),
                    "updatedAt": b[10] or datetime.now().isoformat()
                })
        
        conn.close()
        
        return {
            "success": True,
            "data": bookings
        }
    except Exception as e:
        print(f"Error getting bookings: {e}")
        return {
            "success": True,
            "data": []
        }

@app.post("/api/bookings")
async def create_booking(request: CreateBookingRequest, user_id: str = Depends(verify_token)):
    """Create new booking"""
    try:
        # For now, return a mock booking
        # TODO: Integrate with your booking system
        booking_id = f"booking_{datetime.now().timestamp()}"
        
        return {
            "success": True,
            "data": {
                "id": booking_id,
                "userId": user_id,
                "pickup": request.pickup.dict(),
                "dropoff": request.dropoff.dict(),
                "vehicle": {
                    "id": request.vehicleId,
                    "type": "Economy",
                    "name": "Toyota Prius",
                    "capacity": 4,
                    "features": ["Air Conditioning"],
                    "pricePerKm": 50,
                    "basePrice": 200,
                    "available": True
                },
                "status": "confirmed",
                "scheduledTime": request.scheduledTime or datetime.now().isoformat(),
                "estimatedCost": 5000,
                "distance": 100,
                "duration": 180,
                "driverName": "Kasun Perera",
                "driverPhone": "+94 77 123 4567",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/bookings/{booking_id}")
async def get_booking(booking_id: str, user_id: str = Depends(verify_token)):
    """Get booking details"""
    try:
        # TODO: Get from database
        return {
            "success": True,
            "data": {
                "id": booking_id,
                "userId": user_id,
                "status": "confirmed"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, user_id: str = Depends(verify_token)):
    """Cancel booking"""
    try:
        booking = get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if str(booking.get("user_id")) != str(user_id):
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

        if booking.get("status") == "cancelled":
            return {
                "success": True,
                "message": "Booking already cancelled"
            }

        if not cancel_booking_db(booking_id):
            raise HTTPException(status_code=400, detail="Failed to cancel booking")

        return {
            "success": True,
            "message": "Booking cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Location & Vehicle Endpoints
# ============================================================================

@app.post("/api/location/geocode")
async def geocode(request: GeocodeRequest, user_id: str = Depends(verify_token)):
    """Geocode location text to coordinates"""
    try:
        result = geocode_location(request.location)
        if not result.get("success"):
            message = result.get("message") or result.get("error") or "Failed to geocode location"
            raise HTTPException(status_code=400, detail=message)

        return {
            "success": True,
            "data": {
                "text": request.location,
                "lat": result["coordinates"]["latitude"],
                "lon": result["coordinates"]["longitude"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/location/route")
async def route(request: RouteRequest, user_id: str = Depends(verify_token)):
    """Calculate route between two locations"""
    try:
        result = calculate_route(
            request.pickup.lat,
            request.pickup.lon,
            request.dropoff.lat,
            request.dropoff.lon,
            request.pickup.text,
            request.dropoff.text
        )

        if not result.get("success"):
            message = result.get("message") or result.get("error") or "Failed to calculate route"
            raise HTTPException(status_code=400, detail=message)

        return {
            "success": True,
            "data": {
                "distance": result["distance_km"],
                "duration": result["duration_minutes"],
                "polyline": [
                    [request.pickup.lat, request.pickup.lon],
                    [request.dropoff.lat, request.dropoff.lon]
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/location/reverse")
async def reverse_geocode(request: ReverseGeocodeRequest, user_id: str = Depends(verify_token)):
    """Reverse geocode coordinates into a readable address"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": request.lat,
            "lon": request.lon,
            "format": "json",
            "zoom": 18,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "ride-booking-agent/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Reverse geocoding failed")
        data = response.json()
        display_name = data.get("display_name")
        if not display_name:
            raise HTTPException(status_code=400, detail="No address found for location")
        return {
            "success": True,
            "data": {
                "text": display_name,
                "lat": float(request.lat),
                "lon": float(request.lon)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/vehicles")
async def get_vehicles(user_id: str = Depends(verify_token)):
    """Get available vehicles"""
    try:
        # TODO: Use your list_available_vehicles tool
        return {
            "success": True,
            "data": [
                {
                    "id": "vehicle_1",
                    "type": "Economy",
                    "name": "Toyota Prius",
                    "capacity": 4,
                    "features": ["Air Conditioning", "GPS"],
                    "pricePerKm": 50,
                    "basePrice": 200,
                    "available": True
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/vehicles/recommend")
async def recommend_vehicles(distance: float, user_id: str = Depends(verify_token)):
    """Get vehicle recommendations based on distance"""
    try:
        vehicles = [
            {
                "id": "vehicle_1",
                "type": "Economy",
                "name": "Toyota Prius",
                "capacity": 4,
                "features": ["Air Conditioning", "GPS"],
                "pricePerKm": 50,
                "basePrice": 200,
                "estimatedPrice": 200 + (distance * 50),
                "eta": 5,
                "available": True
            }
        ]
        
        return {
            "success": True,
            "data": vehicles
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Run the server
# ============================================================================

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
