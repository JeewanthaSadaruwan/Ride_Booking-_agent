"""Authentication UI components for Streamlit."""

import streamlit as st
from auth import signup_user, login_user, get_user_by_id


def show_login_form():
    """Display login form."""
    st.markdown("### 🔐 Login to Your Account")
    st.markdown("---")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("📝 Create Account", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                result = login_user(email, password)
                if result["success"]:
                    st.session_state.user = result["user"]
                    st.session_state.authenticated = True
                    st.success(result["message"])
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result["message"])


def show_signup_form():
    """Display signup form."""
    st.markdown("### 📝 Create Your Account")
    st.markdown("---")
    
    with st.form("signup_form"):
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        phone = st.text_input("Phone Number", placeholder="+94771234567 or 0771234567")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("✅ Create Account", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("← Back to Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
        
        if submit:
            # Validation
            if not all([full_name, email, phone, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                result = signup_user(email, password, full_name, phone)
                if result["success"]:
                    st.success(result["message"])
                    st.info("You can now login with your credentials")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error(result["message"])


def show_user_profile():
    """Display user profile in sidebar."""
    if not st.session_state.get("authenticated"):
        return
    
    user = st.session_state.get("user")
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Your Profile")
        st.markdown(f"**{user['full_name']}**")
        st.markdown(f"📧 {user['email']}")
        st.markdown(f"📱 {user['phone']}")
        
        # Get user stats
        from db.database import get_user_stats
        stats = get_user_stats(user['user_id'])
        
        st.markdown("---")
        st.markdown("### 📊 Your Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Bookings", stats['total_bookings'])
        with col2:
            st.metric("Completed", stats['completed_bookings'])
        st.metric("Total Spent", f"LKR {stats['total_spent']:,.0f}")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.messages = []  # Clear chat history
            st.rerun()


def show_booking_history():
    """Display user's booking history."""
    if not st.session_state.get("authenticated"):
        st.warning("Please login to view your booking history")
        return
    
    user = st.session_state.get("user")
    from db.database import get_user_bookings
    
    st.markdown("## 📋 Your Booking History")
    st.markdown("---")
    
    bookings = get_user_bookings(user['user_id'], limit=20)
    
    if not bookings:
        st.info("You haven't made any bookings yet. Start by booking a ride!")
        return
    
    for booking in bookings:
        status_emoji = {
            'confirmed': '✅',
            'completed': '🏁',
            'cancelled': '❌'
        }.get(booking['status'], '📦')
        
        with st.expander(f"{status_emoji} {booking['booking_id']} - {booking['pickup_location']} → {booking['dropoff_location']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Vehicle:** {booking['make']} {booking['model']} ({booking['type']})")
                st.markdown(f"**Pickup Time:** {booking['pickup_time']}")
                st.markdown(f"**Passengers:** {booking['passenger_count']}")
                if booking['special_requirements']:
                    st.markdown(f"**Requirements:** {booking['special_requirements']}")
            
            with col2:
                if booking['distance_km']:
                    st.markdown(f"**Distance:** {booking['distance_km']:.1f} km")
                if booking['duration_minutes']:
                    st.markdown(f"**Duration:** {booking['duration_minutes']} min")
                if booking['estimated_cost']:
                    st.markdown(f"**Cost:** LKR {booking['estimated_cost']:,.0f}")
                st.markdown(f"**Status:** {booking['status'].title()}")
            
            st.markdown(f"*Booked on: {booking['created_at']}*")
            
            # Cancel button for confirmed bookings
            if booking['status'] == 'confirmed':
                if st.button(f"Cancel Booking", key=f"cancel_{booking['booking_id']}"):
                    from db.database import cancel_booking
                    if cancel_booking(booking['booking_id']):
                        st.success("Booking cancelled successfully")
                        st.rerun()
                    else:
                        st.error("Failed to cancel booking")


def require_auth():
    """Check if user is authenticated, show login if not."""
    if not st.session_state.get("authenticated"):
        # Initialize auth mode
        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"
        
        # Show login or signup based on mode
        if st.session_state.auth_mode == "login":
            show_login_form()
        else:
            show_signup_form()
        
        return False
    return True
