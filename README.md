# Ride Booking Agent - AI-Powered Ride Booking System

A complete ride booking application for Sri Lanka using OpenAI GPT-4o and AWS Strands. Book rides from anywhere to anywhere with real-time vehicle availability, route calculation, and cost estimation by simply specifying your pickup and dropoff locations.

---

## Features

- **AI-Powered Agent**: Natural language conversation using GPT-4o
- **Smart Location Detection**: Automatic geocoding and route calculation from text input
- **Real-Time Vehicle Search**: 50 vehicles with live availability
- **Dynamic Pricing**: Distance and time-based cost calculation
- **Calendar Integration**: Auto-booking with Google Calendar
- **Modern UI**: Streamlit-based responsive interface

---

## Quick Start

### 1. Install Dependencies
```bash
cd /home/jeewanthas/Desktop/vehicle-dispatch-agent
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Set Up Google Calendar (Optional)
For calendar integration features:

1. **Enable Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create OAuth 2.0 Client ID (Desktop App)
   - Download credentials and save as `credentials.json`

2. **Authenticate**:
   ```bash
   python google_calendar_auth.py
   ```
   This will open your browser to authorize access and save `token.json`

### 4. Run the Application
```bash
python3 -m streamlit run app.py --server.port 8501
```

Or use the startup script:
```bash
./run_app.sh
```

### 5. Access the App
Open your browser at: **http://localhost:8501**

---

## How to Use

### Basic Ride Request
```
User: "I need to go from Galle to Kandy"
```

**What happens:**
1. System geocodes "Galle" location
2. System geocodes "Kandy" location
3. Calculates route with distance and duration
4. Agent searches for available vehicles
5. Agent presents top 3 vehicle options with pricing

### With Vehicle Preferences
```
User: "I want to go from Colombo to Kandy in a luxury car"
```

The system handles:
- Location detection (Colombo → Kandy)
- Vehicle preference filtering (luxury cars only)
- Cost estimation and recommendations

### Confirm Booking
```
User: "Book the first vehicle"
or
User: "Book the sedan"
```

Agent confirms and:
- Dispatches the vehicle
- Creates calendar booking
- Provides tracking information

---

## Architecture

### Tech Stack
- **Frontend**: Streamlit
- **AI Agent**: AWS Strands with OpenAI GPT-4o
- **Database**: SQLite (vehicles, trips, dispatches)
- **Geocoding**: Nominatim API (OpenStreetMap)
- **Routing**: OpenStreetMap Routing Service
- **Calendar**: Google Calendar API

### Project Structure
```
ride-booking-agent/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── vehicles.db                 # SQLite database
├── run_app.sh                  # Startup script
├── google_calendar_auth.py     # Google Calendar authentication
├── credentials.json            # Google OAuth credentials (not in git)
├── token.json                  # Google OAuth token (not in git)
│
├── agents/
│   └── booking_agent.py        # AI agent configuration
│
├── tools/                      # 13 specialized tools
│   ├── geocode_location.py     # Location geocoding
│   ├── calculate_route.py      # Route calculation
│   ├── list_available_vehicles.py
│   ├── filter_vehicles_by_constraints.py
│   ├── recommend_best_vehicle.py
│   ├── estimate_trip_cost.py
│   ├── book_vehicle.py         # Book and dispatch vehicle
│   ├── get_my_bookings.py      # User booking history
│   ├── cancel_booking.py       # Cancel bookings
│   ├── create_calendar_booking.py
│   ├── list_calendar_bookings.py
│   └── get_current_datetime.py
│
├── auth/
│   └── auth.py                 # Authentication logic
│
├── ui/
│   └── auth_ui.py              # Authentication UI
│
├── config/
│   └── settings.py             # Configuration
│
├── models/
│   └── openai_model.py         # OpenAI model wrapper
│
├── db/
│   ├── init_db.py              # Database initialization
│   └── database.py             # Database operations
│
├── csv/                        # Sample data
│   └── vehicles.csv            # 50 vehicles
│
└── logs/
    └── booking_agent.log       # Application logs
└── logs/
    └── booking_agent.log       # Application logs
```

---

## Conversation Flow

### Phase 1: Location Identification
System automatically:
1. Parses user message for locations
2. Geocodes pickup location
3. Geocodes dropoff location
4. Calculates route with distance and duration

### Phase 2: Vehicle Search
Agent performs:
1. Search available vehicles
2. Filter by user preferences
3. Calculate costs for each option
4. Rank by suitability, ETA, and price
5. Present top 3 recommendations

### Phase 3: Booking & Confirmation
1. User confirms vehicle choice
2. Agent dispatches vehicle
3. Calendar event created
4. Tracking information provided

---

## Available Tools (13 Total)

### Location & Routing
- `geocode_location` - Convert address to GPS coordinates
- `calculate_route` - Calculate distance and duration between locations

### Vehicle Management
- `list_available_vehicles` - Search available vehicles
- `filter_vehicles_by_constraints` - Filter vehicles by preferences (type, capacity, features)
- `recommend_best_vehicle` - Get top vehicle recommendations based on trip requirements

### Cost & Time Estimation
- `estimate_trip_cost` - Calculate ride cost based on distance and duration

### Booking & Dispatch
- `book_vehicle` - Book and dispatch vehicle for a trip
- `get_my_bookings` - Retrieve user's booking history
- `cancel_booking` - Cancel a specific booking by ID
- `cancel_bookings_by_date` - Cancel all bookings for a specific date

### Calendar Integration
- `create_calendar_booking` - Auto-create Google Calendar event for booking
- `list_calendar_bookings` - List upcoming calendar bookings

### Time Management
- `get_current_datetime` - Get current date and time

---

## Pricing Formula

```
Total Cost = Base Fare + Distance Cost + Time Cost

Base Fare: $2.50
Distance: $1.50 per km
Time: $0.30 per minute

Example: 50km trip taking 60 minutes
= $2.50 + (50 × $1.50) + (60 × $0.30)
= $2.50 + $75.00 + $18.00
= $95.50
```

---

## Database Schema

### Vehicles Table
```sql
- vehicle_id (TEXT, PRIMARY KEY)
- type (TEXT) - Sedan, SUV, Van, Luxury
- capacity (INTEGER)
- features (TEXT) - AC, WiFi, wheelchair, etc.
- current_location (TEXT)
- status (TEXT) - available, busy, maintenance
- license_plate (TEXT)
- year (INTEGER)
- make (TEXT)
- model (TEXT)
```

### Trips Table
```sql
- trip_id (TEXT, PRIMARY KEY)
- pickup_location (TEXT)
- dropoff_location (TEXT)
- passenger_count (INTEGER)
- requested_time (TEXT)
- special_requirements (TEXT)
- status (TEXT)
- created_at (TEXT)
```

### Dispatches Table
```sql
- dispatch_id (TEXT, PRIMARY KEY)
- vehicle_id (TEXT, FOREIGN KEY)
- trip_id (TEXT, FOREIGN KEY)
- dispatch_time (TEXT)
- estimated_arrival (TEXT)
- actual_arrival (TEXT)
- status (TEXT)
- cost (REAL)
```

---

## Configuration

### Settings (`config/settings.py`)
```python
SESSION_ID = "ride-booking-agent-session"
```

### Agent Configuration (`agents/booking_agent.py`)
```python
model = OpenAIModel(
    model_id="gpt-4o",
    params={
        "max_tokens": 4000,
        "temperature": 0.7,
    }
)
```

---

## UI Components

### Chat Interface
- Message history with user/agent distinction
- Real-time streaming responses
- Location status indicators
- Action buttons (Confirm/Reset)

### Status Section
- Pickup location status
- Dropoff location status
- Route calculation status
- Distance and duration display

---

## Troubleshooting

### App won't start
```bash
# Kill existing processes
pkill -9 -f streamlit

# Restart
python3 -m streamlit run app.py --server.port 8501
```

### Database errors
```bash
# Remove and reinitialize database
rm vehicles.db
# App will auto-create on next start
```

### Location not geocoding
- Check spelling of location name
- Use more specific names (e.g., "Galle Fort" vs "Galle")
- Provide complete address when possible
- Use well-known landmarks or city names

### Agent not responding
- Check `.env` file has valid `OPENAI_API_KEY`
- Check terminal for error messages
- Look at `logs/booking_agent.log`

---

## Example Conversations

### Simple Booking
```
User: I need a ride from Colombo to Kandy
Agent: Perfect! I've identified your route from Colombo to Kandy 
       (115 km, ~2.5 hours). Let me find available vehicles...
       
       Here are your top 3 options:
       1. Toyota Sedan - $175.50 (arrives in 5 min)
       2. Honda SUV - $195.00 (arrives in 8 min)
       3. Mercedes Luxury - $240.00 (arrives in 10 min)

User: Book the first one
Agent: Great choice! I've dispatched the Toyota Sedan...
```

### With Preferences
```
User: I need a luxury car from Galle to Matara for 4 people
Agent: Got it! Route from Galle to Matara (45 km, ~1 hour).
       Looking for luxury vehicles with 4+ capacity...
       
       Here are luxury options:
       1. Mercedes E-Class - $72.00
       2. BMW 5 Series - $75.50
       
User: Book the Mercedes
Agent: Excellent! Mercedes E-Class is on the way...
```

---

## Security & Privacy

- API keys stored in `.env` (not committed to git)
- User location data not stored permanently
- Trip data anonymized after completion
- Secure communication with external APIs

---

<!-- ## Features in Development

- [ ] Real-time GPS tracking
- [ ] Payment integration (Stripe/PayPal)
- [ ] Driver mobile app
- [ ] Multi-language support (Sinhala/Tamil)
- [ ] Push notifications
- [ ] Advanced analytics dashboard
- [ ] Driver ratings and reviews

--- -->

<!-- ## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

--- -->

<!-- ## License

This project is for educational and demonstration purposes.

--- -->

## Support

For issues:
1. Check `logs/booking_agent.log`
2. Review terminal error messages
3. Verify all dependencies are installed
4. Ensure `.env` file is properly configured

---

## Quick Commands Reference

```bash
# Start app
python3 -m streamlit run app.py --server.port 8501

# Stop app
pkill -9 -f streamlit

# View logs
tail -f logs/booking_agent.log

# Reset database
rm vehicles.db

# Install dependencies
pip install -r requirements.txt

# Run with script
./run_app.sh
```

---

**Built with OpenAI GPT-4o, AWS Strands, and Streamlit**

*Last Updated: January 15, 2026*
