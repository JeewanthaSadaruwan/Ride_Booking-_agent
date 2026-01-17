"""Streamlit UI for Ride Booking Agent - Single Page with Interactive Map."""

import streamlit as st
import sys
from pathlib import Path
import folium
from streamlit_folium import st_folium
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.booking_agent import booking_agent
from db.init_db import init_database
from tools.geocode_location import geocode_location
from tools.calculate_route import calculate_route
from ui.auth_ui import require_auth, show_user_profile, show_booking_history

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Ride Booking Agent",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def setup_database():
    try:
        init_database()
    except Exception as e:
        st.error(f"Database error: {e}")

setup_database()

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pickup_location" not in st.session_state:
    st.session_state.pickup_location = None
if "dropoff_location" not in st.session_state:
    st.session_state.dropoff_location = None
if "pickup_coords" not in st.session_state:
    st.session_state.pickup_coords = None
if "dropoff_coords" not in st.session_state:
    st.session_state.dropoff_coords = None
if "route_data" not in st.session_state:
    st.session_state.route_data = None
if "locations_confirmed" not in st.session_state:
    st.session_state.locations_confirmed = False

# Helper function to create interactive map
def create_interactive_map(pickup_coords=None, dropoff_coords=None, route_data=None):
    """Create an interactive map where user can click to set locations."""
    
    # Default center: Sri Lanka (Colombo)
    center_lat = 6.9271
    center_lon = 79.8612
    zoom = 8
    
    if pickup_coords and dropoff_coords:
        # Center between pickup and dropoff
        center_lat = (pickup_coords[0] + dropoff_coords[0]) / 2
        center_lon = (pickup_coords[1] + dropoff_coords[1]) / 2
        zoom = 10
    elif pickup_coords:
        center_lat = pickup_coords[0]
        center_lon = pickup_coords[1]
        zoom = 12
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    
    # Add click handler instruction
    folium.Marker(
        [center_lat, center_lon],
        popup="<b>🗺️ Click anywhere on map to set dropoff location</b>",
        icon=folium.Icon(color="lightgray", icon="info-sign")
    ).add_to(m)
    
    # Add pickup marker (green)
    if pickup_coords:
        folium.Marker(
            pickup_coords,
            popup=f"<b>📍 Pickup</b><br>{st.session_state.pickup_location or 'Your Location'}",
            tooltip="Pickup Location",
            icon=folium.Icon(color="green", icon="play", prefix="fa")
        ).add_to(m)
    
    # Add dropoff marker (red) - DRAGGABLE
    if dropoff_coords:
        folium.Marker(
            dropoff_coords,
            popup=f"<b>🎯 Dropoff</b><br>{st.session_state.dropoff_location or 'Destination'}",
            tooltip="Dropoff Location (Click map to move)",
            icon=folium.Icon(color="red", icon="stop", prefix="fa"),
            draggable=True
        ).add_to(m)
    
    # Draw route if both locations exist
    if pickup_coords and dropoff_coords and route_data and route_data.get("success"):
        folium.PolyLine(
            [pickup_coords, dropoff_coords],
            color="blue",
            weight=4,
            opacity=0.7,
            tooltip=f"{route_data.get('distance_km', 0)} km, ~{route_data.get('duration_minutes', 0)} min"
        ).add_to(m)
        
        # Add route info box
        info_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    background-color: white; 
                    padding: 15px; 
                    border: 2px solid #007bff;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    z-index: 9999;">
            <h4 style="margin: 0 0 10px 0; color: #007bff;">📍 Route Details</h4>
            <p style="margin: 5px 0;"><b>Distance:</b> {route_data['distance_km']} km</p>
            <p style="margin: 5px 0;"><b>Duration:</b> ~{route_data['duration_minutes']} min</p>
            <p style="margin: 5px 0; font-size: 0.85em; color: #666;">
                Via: {route_data.get('route_summary', 'Road')}
            </p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_html))
    
    # Fit bounds to show all markers
    if pickup_coords and dropoff_coords:
        m.fit_bounds([pickup_coords, dropoff_coords])
    
    return m

# Function to parse and extract locations from user message
def parse_and_geocode_locations(message):
    """Parse locations from message and geocode them step by step."""
    message_lower = message.lower()
    pickup_found = False
    dropoff_found = False
    
    # Handle typos: "form" -> "from", "frm" -> "from"
    message_lower = message_lower.replace(" form ", " from ").replace(" frm ", " from ")
    
    # Extract BOTH pickup and dropoff in one pass
    pickup_text = None
    dropoff_text = None
    
    # Pattern 1: "from X to Y"
    if "from" in message_lower and "to" in message_lower:
        parts = message_lower.split("from")
        if len(parts) > 1:
            between = parts[1].split("to")
            if len(between) >= 2:
                pickup_text = between[0].strip()
                dropoff_text = between[1].strip()
    
    # Pattern 2: Just "to Y" (assume pickup is current location)
    elif "to" in message_lower and "from" not in message_lower:
        parts = message_lower.split("to")
        if len(parts) > 1:
            dropoff_text = parts[1].strip()
    
    # Clean up extracted text
    if pickup_text:
        # Remove common filler words
        for word in ["i want", "i need", "need", "want", "go", "ride", "book", "a ride"]:
            pickup_text = pickup_text.replace(word, "").strip()
    
    if dropoff_text:
        # Remove common filler words and vehicle preferences
        for word in ["in a", "by", "with", "using", "?"]:
            dropoff_text = dropoff_text.split(word)[0].strip()
        dropoff_text = dropoff_text.rstrip("?.,!")
    
    # Geocode PICKUP if found and not already set
    if pickup_text and not st.session_state.pickup_location:
        st.session_state.pickup_location = pickup_text.title()
        logger.info(f"🔍 Geocoding pickup location: {pickup_text}")
        
        try:
            pickup_geo = geocode_location(pickup_text)
            if pickup_geo.get("success"):
                st.session_state.pickup_coords = [
                    pickup_geo["coordinates"]["latitude"],
                    pickup_geo["coordinates"]["longitude"]
                ]
                pickup_found = True
                logger.info(f"✅ Pickup found: {pickup_text} -> {st.session_state.pickup_coords}")
            else:
                logger.warning(f"⚠️ Could not geocode pickup: {pickup_text}")
        except Exception as e:
            logger.error(f"❌ Geocoding error for pickup '{pickup_text}': {e}")
    
    # Geocode DROPOFF if found and not already set
    if dropoff_text and not st.session_state.dropoff_location:
        st.session_state.dropoff_location = dropoff_text.title()
        logger.info(f"🔍 Geocoding dropoff location: {dropoff_text}")
        
        try:
            dropoff_geo = geocode_location(dropoff_text)
            if dropoff_geo.get("success"):
                st.session_state.dropoff_coords = [
                    dropoff_geo["coordinates"]["latitude"],
                    dropoff_geo["coordinates"]["longitude"]
                ]
                dropoff_found = True
                logger.info(f"✅ Dropoff found: {dropoff_text} -> {st.session_state.dropoff_coords}")
            else:
                logger.warning(f"⚠️ Could not geocode dropoff: {dropoff_text}")
        except Exception as e:
            logger.error(f"❌ Geocoding error for dropoff '{dropoff_text}': {e}")
    
    # Calculate route if both locations exist
    if st.session_state.pickup_coords and st.session_state.dropoff_coords and not st.session_state.route_data:
        try:
            logger.info(f"🗺️ Calculating route from {st.session_state.pickup_location} to {st.session_state.dropoff_location}")
            route_data = calculate_route(
                st.session_state.pickup_coords[0],
                st.session_state.pickup_coords[1],
                st.session_state.dropoff_coords[0],
                st.session_state.dropoff_coords[1],
                st.session_state.pickup_location or "Pickup",
                st.session_state.dropoff_location or "Dropoff"
            )
            st.session_state.route_data = route_data
            logger.info(f"✅ Route calculated: {route_data.get('distance_km')} km, {route_data.get('duration_minutes')} min")
        except Exception as e:
            logger.error(f"❌ Route calculation error: {e}")
    
    return pickup_found, dropoff_found

# Function to handle agent conversation
def chat_with_agent(user_message):
    """Send message to agent and get response."""
    try:
        # Add context about current location status
        context_msg = user_message
        
        # Add user info if authenticated
        if st.session_state.get("authenticated") and st.session_state.get("user"):
            user = st.session_state.user
            user_info = f"[User: {user['full_name']} (user_id: {user['user_id']})] "
            context_msg = user_info + context_msg
        
        # If locations are already set, tell the agent
        if st.session_state.pickup_location and st.session_state.dropoff_location:
            context_msg = f"[Locations confirmed: From {st.session_state.pickup_location} to {st.session_state.dropoff_location}]\n{context_msg}"
        elif st.session_state.pickup_location:
            context_msg = f"[Pickup location set: {st.session_state.pickup_location}. Still need dropoff location.]\n{context_msg}"
        
        # Call the agent directly - it's a callable object
        response = booking_agent(context_msg)
        return response
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"⚠️ Error: {str(e)}\n\nPlease try rephrasing your request."

# Check authentication - show login/signup if not authenticated
if not require_auth():
    st.stop()

# Sidebar with branding and user profile
with st.sidebar:
    st.markdown("# 🚗 Ride Booking Agent")
    st.markdown("---")
    
    # Show user profile
    show_user_profile()
    
    st.markdown("---")
    
    # Reset/New Trip button
    if st.button("🔄 Start New Trip", use_container_width=True):
        # Clear all trip-related session state
        st.session_state.messages = []
        st.session_state.pickup_location = None
        st.session_state.dropoff_location = None
        st.session_state.pickup_coords = None
        st.session_state.dropoff_coords = None
        st.session_state.route_data = None
        st.session_state.locations_confirmed = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    AI-powered ride booking system for Sri Lanka.
    
    **Features:**
    - 🗺️ Smart location detection
    - 🤖 Natural language booking
    - 🚗 Real-time vehicle search
    - 💰 Dynamic pricing
    """)

# Main UI Layout with tabs
tab1, tab2 = st.tabs(["💬 Book a Ride", "📋 My Bookings"])

with tab1:
    st.markdown("**Chat with AI Agent**")
    
    # Chat container - maximize height
    chat_container = st.container(height=680)

    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input - OUTSIDE container so it stays fixed at bottom
    if prompt := st.chat_input("Type your ride request... (e.g., 'I need to go from Colombo to Kandy')"):
        # STEP 1: Add user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    
    # Process the last message if it's from user and hasn't been responded to yet
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_user_message = st.session_state.messages[-1]["content"]
        
        # STEP 2: Parse and geocode locations
        pickup_found, dropoff_found = parse_and_geocode_locations(last_user_message)
        
        # STEP 3: Build location confirmation messages
        location_updates = []
        if pickup_found:
            location_updates.append(f"📍 **Pickup location identified:** {st.session_state.pickup_location}")
        if dropoff_found:
            location_updates.append(f"🎯 **Dropoff location identified:** {st.session_state.dropoff_location}")
        
        # STEP 4: Get agent response with spinner
        with st.spinner("🔍 Processing your request..."):
            # If we found locations, inform user first
            if location_updates:
                for update in location_updates:
                    st.session_state.messages.append({"role": "assistant", "content": update})
            
            # Now get agent response
            response = chat_with_agent(last_user_message)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # STEP 5: Auto-confirm if both locations are set
        if st.session_state.pickup_coords and st.session_state.dropoff_coords and not st.session_state.locations_confirmed:
            route_info = f"\n\n✅ **Route confirmed:**\n"
            route_info += f"- Distance: {st.session_state.route_data.get('distance_km', 'N/A')} km\n"
            route_info += f"- Duration: ~{st.session_state.route_data.get('duration_minutes', 'N/A')} minutes\n\n"
            route_info += "Now, let me find available vehicles for you..."
            st.session_state.messages.append({"role": "assistant", "content": route_info})
            st.session_state.locations_confirmed = True
        
        st.rerun()

with tab2:
    show_booking_history()

# Footer
st.markdown("---")
st.caption("🚗 Ride Booking Agent | Powered by OpenStreetMap & GPT-4o")
