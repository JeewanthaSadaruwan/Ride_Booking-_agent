# Backend API Specification

This document specifies the exact REST API endpoints that the React frontend expects.

## Base URL

Development: `http://localhost:8000/api`  
Production: `https://your-domain.com/api`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

---

## Authentication Endpoints

### POST /api/auth/login

Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "+94 71 234 5678"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

### POST /api/auth/signup

Register new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "phone": "+94 71 234 5678",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "+94 71 234 5678"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "error": "Email already exists"
}
```

---

### GET /api/auth/profile

Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+94 71 234 5678"
  }
}
```

---

### POST /api/auth/logout

Logout user (optional endpoint, frontend also clears local token).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Chat Endpoints

### POST /api/chat

Send message to booking agent.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "message": "I want to go from Colombo to Kandy",
  "context": {
    "pickup": {
      "text": "Colombo",
      "lat": 6.9271,
      "lon": 79.8612
    },
    "dropoff": null
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "I found your locations! The route is 116 km.",
    "pickup": {
      "text": "Colombo",
      "lat": 6.9271,
      "lon": 79.8612
    },
    "dropoff": {
      "text": "Kandy",
      "lat": 7.2906,
      "lon": 80.6337
    },
    "route": {
      "distance": 116.5,
      "duration": 200,
      "polyline": [[6.9271, 79.8612], [7.0, 80.0], [7.2906, 80.6337]]
    },
    "vehicles": [
      {
        "id": "vehicle_1",
        "type": "Economy",
        "name": "Toyota Prius",
        "capacity": 4,
        "features": ["Air Conditioning", "GPS Navigation"],
        "pricePerKm": 50,
        "basePrice": 200,
        "estimatedPrice": 6025,
        "eta": 5,
        "available": true
      }
    ],
    "needsMoreInfo": false
  }
}
```

---

## Booking Endpoints

### GET /api/bookings/my

Get all bookings for current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "booking_123",
      "userId": "user_123",
      "pickup": {
        "text": "Colombo Fort",
        "lat": 6.9271,
        "lon": 79.8612
      },
      "dropoff": {
        "text": "Kandy City",
        "lat": 7.2906,
        "lon": 80.6337
      },
      "vehicle": {
        "id": "vehicle_1",
        "type": "Economy",
        "name": "Toyota Prius",
        "capacity": 4,
        "features": ["Air Conditioning"],
        "pricePerKm": 50,
        "basePrice": 200,
        "available": true
      },
      "status": "confirmed",
      "scheduledTime": "2026-01-16T15:00:00Z",
      "estimatedCost": 6025,
      "distance": 116.5,
      "duration": 200,
      "driverName": "Kasun Perera",
      "driverPhone": "+94 77 123 4567",
      "createdAt": "2026-01-16T14:30:00Z",
      "updatedAt": "2026-01-16T14:30:00Z"
    }
  ]
}
```

---

### POST /api/bookings

Create new booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "pickup": {
    "text": "Colombo Fort",
    "lat": 6.9271,
    "lon": 79.8612
  },
  "dropoff": {
    "text": "Kandy City",
    "lat": 7.2906,
    "lon": 80.6337
  },
  "vehicleId": "vehicle_1",
  "scheduledTime": "2026-01-16T15:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "booking_123",
    "userId": "user_123",
    "pickup": {
      "text": "Colombo Fort",
      "lat": 6.9271,
      "lon": 79.8612
    },
    "dropoff": {
      "text": "Kandy City",
      "lat": 7.2906,
      "lon": 80.6337
    },
    "vehicle": {
      "id": "vehicle_1",
      "type": "Economy",
      "name": "Toyota Prius",
      "capacity": 4,
      "features": ["Air Conditioning"],
      "pricePerKm": 50,
      "basePrice": 200,
      "available": true
    },
    "status": "confirmed",
    "scheduledTime": "2026-01-16T15:00:00Z",
    "estimatedCost": 6025,
    "distance": 116.5,
    "duration": 200,
    "driverName": "Kasun Perera",
    "driverPhone": "+94 77 123 4567",
    "createdAt": "2026-01-16T14:30:00Z",
    "updatedAt": "2026-01-16T14:30:00Z"
  }
}
```

---

### GET /api/bookings/:id

Get booking details.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "booking_123",
    "userId": "user_123",
    "pickup": {
      "text": "Colombo Fort",
      "lat": 6.9271,
      "lon": 79.8612
    },
    "dropoff": {
      "text": "Kandy City",
      "lat": 7.2906,
      "lon": 80.6337
    },
    "vehicle": {
      "id": "vehicle_1",
      "type": "Economy",
      "name": "Toyota Prius",
      "capacity": 4,
      "features": ["Air Conditioning"],
      "pricePerKm": 50,
      "basePrice": 200,
      "available": true
    },
    "status": "confirmed",
    "scheduledTime": "2026-01-16T15:00:00Z",
    "estimatedCost": 6025,
    "distance": 116.5,
    "duration": 200,
    "driverName": "Kasun Perera",
    "driverPhone": "+94 77 123 4567",
    "createdAt": "2026-01-16T14:30:00Z",
    "updatedAt": "2026-01-16T14:30:00Z"
  }
}
```

---

### POST /api/bookings/:id/cancel

Cancel booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Booking cancelled successfully"
}
```

---

## Location Endpoints

### POST /api/location/geocode

Geocode location text to coordinates.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "location": "Colombo Fort"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "text": "Colombo Fort",
    "lat": 6.9271,
    "lon": 79.8612
  }
}
```

---

### POST /api/location/route

Calculate route between two locations.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "pickup": {
    "text": "Colombo Fort",
    "lat": 6.9271,
    "lon": 79.8612
  },
  "dropoff": {
    "text": "Kandy City",
    "lat": 7.2906,
    "lon": 80.6337
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "distance": 116.5,
    "duration": 200,
    "polyline": [
      [6.9271, 79.8612],
      [6.95, 79.90],
      [7.0, 80.0],
      [7.2906, 80.6337]
    ]
  }
}
```

---

## Vehicle Endpoints

### GET /api/vehicles

Get all available vehicles.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "vehicle_1",
      "type": "Economy",
      "name": "Toyota Prius",
      "capacity": 4,
      "features": ["Air Conditioning", "GPS Navigation"],
      "pricePerKm": 50,
      "basePrice": 200,
      "available": true
    },
    {
      "id": "vehicle_2",
      "type": "SUV",
      "name": "Toyota Land Cruiser",
      "capacity": 7,
      "features": ["Air Conditioning", "GPS Navigation", "WiFi"],
      "pricePerKm": 80,
      "basePrice": 300,
      "available": true
    }
  ]
}
```

---

### POST /api/vehicles/recommend

Get vehicle recommendations based on distance.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "distance": 116.5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "vehicle_1",
      "type": "Economy",
      "name": "Toyota Prius",
      "capacity": 4,
      "features": ["Air Conditioning", "GPS Navigation"],
      "pricePerKm": 50,
      "basePrice": 200,
      "estimatedPrice": 6025,
      "eta": 5,
      "available": true
    },
    {
      "id": "vehicle_2",
      "type": "SUV",
      "name": "Toyota Land Cruiser",
      "capacity": 7,
      "features": ["Air Conditioning", "GPS Navigation", "WiFi"],
      "pricePerKm": 80,
      "basePrice": 300,
      "estimatedPrice": 9620,
      "eta": 5,
      "available": true
    }
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

### Common HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## TypeScript Types (Frontend)

The frontend expects these types. Make sure your backend returns data matching these structures:

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
}

interface Location {
  text: string;
  lat: number;
  lon: number;
}

interface Route {
  distance: number; // km
  duration: number; // minutes
  polyline: [number, number][]; // [lat, lon] pairs
}

interface Vehicle {
  id: string;
  type: 'Economy' | 'SUV' | 'Luxury';
  name: string;
  capacity: number;
  features: string[];
  pricePerKm: number;
  basePrice: number;
  estimatedPrice?: number;
  eta?: number; // minutes
  available: boolean;
}

interface Booking {
  id: string;
  userId: string;
  pickup: Location;
  dropoff: Location;
  vehicle: Vehicle;
  status: 'confirmed' | 'completed' | 'cancelled' | 'pending';
  scheduledTime: string; // ISO 8601 format
  estimatedCost: number;
  distance: number;
  duration: number;
  driverName?: string;
  driverPhone?: string;
  createdAt: string;
  updatedAt: string;
}
```

---

## CORS Configuration

Your backend must allow requests from the frontend origin:

```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## JWT Token Format

The JWT token should contain:

```json
{
  "sub": "user_123",
  "exp": 1642348800
}
```

Use HS256 algorithm and store the secret key securely.

---

## Testing Endpoints

Use curl or Postman to test:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get bookings (with token)
curl -X GET http://localhost:8000/api/bookings/my \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Implementation Checklist

- [ ] Set up FastAPI/Flask server
- [ ] Add CORS middleware
- [ ] Implement JWT authentication
- [ ] Create all auth endpoints
- [ ] Create all chat endpoints
- [ ] Create all booking endpoints
- [ ] Create all location endpoints
- [ ] Create all vehicle endpoints
- [ ] Test each endpoint with Postman
- [ ] Verify response formats match TypeScript types
- [ ] Handle all error cases
- [ ] Add input validation
- [ ] Add rate limiting (optional)
- [ ] Add logging

---

This specification ensures the frontend and backend work seamlessly together!
