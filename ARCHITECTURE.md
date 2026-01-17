# Ride Booking Agent - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:3000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND (Vite)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pages                                                    │   │
│  │  • LoginPage     • SignupPage                            │   │
│  │  • BookRidePage  • MyBookingsPage                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Components                                               │   │
│  │  • Sidebar       • Layout        • ChatContainer         │   │
│  │  • MapComponent  • VehicleCard   • Modal                │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  State Management (Zustand)                              │   │
│  │  • authStore (user, token, isAuthenticated)             │   │
│  │  • bookingStore (messages, locations, route, vehicles)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services (React Query + Axios)                          │   │
│  │  • authService    • chatService                          │   │
│  │  • bookingService • locationService                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests (JSON)
                             │ Authorization: Bearer <JWT>
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                          │
│                  http://localhost:8000/api                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints                                       │   │
│  │  • POST /api/auth/login                                  │   │
│  │  • POST /api/auth/signup                                 │   │
│  │  • POST /api/chat                                        │   │
│  │  • GET  /api/bookings/my                                 │   │
│  │  • POST /api/bookings                                    │   │
│  │  • POST /api/location/geocode                            │   │
│  │  • POST /api/location/route                              │   │
│  │  • GET  /api/vehicles                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXISTING PYTHON BACKEND (Your Code)                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  agents/                                                  │   │
│  │  • booking_agent.py (AI Agent Logic)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  tools/                                                   │   │
│  │  • geocode_location.py (OpenStreetMap Nominatim)        │   │
│  │  • calculate_route.py (OSRM)                            │   │
│  │  • list_available_vehicles.py                           │   │
│  │  • book_vehicle.py                                       │   │
│  │  • get_my_bookings.py                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  auth/                                                    │   │
│  │  • auth.py (Authentication Manager)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  db/                                                      │   │
│  │  • database.py (SQLite Database)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  models/                                                  │   │
│  │  • openai_model.py (AWS Strands + GPT-4o)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Booking a Ride

```
1. USER INTERACTION
   User types: "I need a ride from Colombo to Kandy"
   
   ▼

2. REACT FRONTEND
   • ChatInput component captures message
   • useBookingStore adds user message to state
   • chatService.sendMessage() called
   
   ▼

3. AXIOS REQUEST
   POST http://localhost:8000/api/chat
   Headers: { Authorization: "Bearer <JWT>" }
   Body: { message: "I need a ride from Colombo to Kandy" }
   
   ▼

4. BACKEND API (FastAPI)
   • Verifies JWT token
   • Extracts user_id
   • Calls booking_agent.process_message()
   
   ▼

5. BOOKING AGENT (Your Code)
   • Parses message with GPT-4o
   • Identifies: pickup="Colombo", dropoff="Kandy"
   • Calls geocode_location() for both
   • Calls calculate_route()
   • Calls list_available_vehicles()
   • Returns structured response
   
   ▼

6. BACKEND API RESPONSE
   {
     "success": true,
     "data": {
       "message": "I found your locations!",
       "pickup": { "text": "Colombo", "lat": 6.9271, "lon": 79.8612 },
       "dropoff": { "text": "Kandy", "lat": 7.2906, "lon": 80.6337 },
       "route": { "distance": 116, "duration": 200, "polyline": [...] },
       "vehicles": [...]
     }
   }
   
   ▼

7. REACT FRONTEND
   • React Query receives response
   • useBookingStore updates state:
     - Sets pickup location
     - Sets dropoff location
     - Sets route
     - Sets available vehicles
   • Components re-render:
     - ChatContainer shows agent message
     - ChatContainer shows system notifications
     - MapComponent displays markers and route
     - VehicleCard list appears
   
   ▼

8. USER SEES
   • Chat: "I found your locations!"
   • System: "✓ Pickup location identified: Colombo"
   • System: "✓ Dropoff location identified: Kandy"
   • System: "✓ Route calculated: 116 km, 200 minutes"
   • Map: Shows route with markers
   • Sidebar: Vehicle options with prices
```

## Component Hierarchy

```
App
├── Router
│   ├── /login → LoginPage
│   ├── /signup → SignupPage
│   └── /app → ProtectedRoute
│       └── Layout
│           ├── Sidebar
│           │   ├── User Profile Card
│           │   ├── Stats (bookings, trips, spent)
│           │   └── Start New Trip Button
│           │
│           └── TabContent
│               ├── Tab: Book a Ride
│               │   └── BookRidePage
│               │       ├── ChatContainer
│               │       │   ├── ChatMessage (multiple)
│               │       │   └── TypingIndicator
│               │       ├── ChatInput
│               │       ├── MapComponent (Leaflet)
│               │       ├── VehicleCard (multiple)
│               │       └── BookingConfirmationModal
│               │
│               └── Tab: My Bookings
│                   └── MyBookingsPage
│                       └── BookingCard (multiple)
│                           ├── StatusBadge
│                           └── Cancel Button
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────┐
│                   ZUSTAND STORES                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  authStore                                               │
│  ├── user: User | null                                   │
│  ├── token: string | null                                │
│  ├── isAuthenticated: boolean                            │
│  ├── setUser()                                           │
│  ├── setToken()                                          │
│  └── logout()                                            │
│                                                          │
│  bookingStore                                            │
│  ├── messages: Message[]                                 │
│  ├── isAgentTyping: boolean                              │
│  ├── pickup: Location | null                             │
│  ├── dropoff: Location | null                            │
│  ├── route: Route | null                                 │
│  ├── availableVehicles: Vehicle[]                        │
│  ├── selectedVehicle: Vehicle | null                     │
│  ├── showConfirmationModal: boolean                      │
│  ├── addMessage()                                        │
│  ├── setPickup()                                         │
│  ├── setDropoff()                                        │
│  ├── setRoute()                                          │
│  ├── setSelectedVehicle()                                │
│  └── resetBooking()                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## API Service Layer

```
┌─────────────────────────────────────────────────────────┐
│                   SERVICES                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  authService                                             │
│  ├── login(credentials) → AuthResponse                   │
│  ├── signup(data) → AuthResponse                         │
│  ├── getProfile() → User                                 │
│  └── logout() → void                                     │
│                                                          │
│  chatService                                             │
│  ├── sendMessage(request) → ChatResponse                 │
│  └── getChatHistory() → ChatResponse[]                   │
│                                                          │
│  bookingService                                          │
│  ├── getMyBookings() → Booking[]                         │
│  ├── createBooking(request) → Booking                    │
│  ├── getBooking(id) → Booking                            │
│  └── cancelBooking(id) → void                            │
│                                                          │
│  locationService                                         │
│  ├── geocode(text) → Location                            │
│  └── calculateRoute(pickup, dropoff) → Route             │
│                                                          │
│  vehicleService                                          │
│  ├── getAvailableVehicles() → Vehicle[]                  │
│  └── getRecommendations(distance) → Vehicle[]            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                          │
│  React Components, Tailwind CSS, Animations              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   STATE MANAGEMENT                       │
│  Zustand (Client State) + React Query (Server State)    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    API LAYER                             │
│  Axios, JWT Auth, Request/Response Interceptors         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   BACKEND API                            │
│  FastAPI, JWT Verification, CORS                         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  BUSINESS LOGIC                          │
│  Booking Agent, Tools, Database                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              EXTERNAL SERVICES                           │
│  OpenStreetMap, OSRM, OpenAI GPT-4o                     │
└─────────────────────────────────────────────────────────┘
```

## File Structure Mapping

```
frontend/src/
│
├── main.tsx ──────────────► Entry point, renders App
│
├── App.tsx ───────────────► Router, Query Provider, Toast
│
├── pages/
│   ├── LoginPage ─────────► /login route
│   ├── SignupPage ────────► /signup route
│   ├── BookRidePage ──────► Main booking interface
│   └── MyBookingsPage ────► Bookings list
│
├── components/
│   ├── Layout ────────────► Main app structure
│   ├── Sidebar ───────────► Left navigation panel
│   ├── Chat* ─────────────► Chat interface
│   ├── Map* ──────────────► Leaflet map
│   ├── Vehicle* ──────────► Vehicle selection
│   ├── Booking* ──────────► Booking modals
│   └── UI Components ─────► Button, Input, Card, etc.
│
├── services/
│   ├── api.ts ────────────► Axios setup, interceptors
│   └── *Service.ts ───────► API method implementations
│
├── store/
│   ├── authStore ─────────► User & token state
│   └── bookingStore ──────► Booking flow state
│
├── types/
│   └── index.ts ──────────► TypeScript definitions
│
└── utils/
    └── helpers.ts ────────► Utility functions
```

## Authentication Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. Open /app
       ▼
┌──────────────────┐
│  ProtectedRoute  │
│  Check token     │
└──────┬───────────┘
       │
       ├── Token exists? ──NO──► Redirect to /login
       │
       └── YES
           │
           ▼
       ┌────────────────┐
       │  Verify Token  │
       │  with Backend  │
       └────────┬───────┘
                │
                ├── Valid? ──NO──► Clear token, redirect /login
                │
                └── YES
                    │
                    ▼
                ┌────────────┐
                │  Load App  │
                │  Show UI   │
                └────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      PRODUCTION                          │
└─────────────────────────────────────────────────────────┘

FRONTEND (Static Hosting)
├── Vercel / Netlify / S3
├── CDN (CloudFlare)
└── Domain: ridebook.com

BACKEND API (Server)
├── AWS EC2 / Heroku / DigitalOcean
├── Docker container
├── Nginx reverse proxy
└── Domain: api.ridebook.com

DATABASE
└── PostgreSQL / MySQL (instead of SQLite)

EXTERNAL SERVICES
├── OpenStreetMap Nominatim
├── OSRM (Open Source Routing Machine)
└── OpenAI API (GPT-4o)
```

This architecture ensures:
- ✅ Clean separation of concerns
- ✅ Scalable and maintainable
- ✅ Type-safe (TypeScript)
- ✅ Testable components
- ✅ Production-ready
