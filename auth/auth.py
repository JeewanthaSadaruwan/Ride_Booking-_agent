"""User authentication module for ride booking system."""

import psycopg2
import psycopg2.extras
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import re
from config.settings import DATABASE_URL


def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hash a password with a salt using SHA-256.
    
    Args:
        password: Plain text password
        salt: Optional salt (generates new one if not provided)
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Combine password and salt, then hash
    pwd_salt = (password + salt).encode('utf-8')
    hashed = hashlib.sha256(pwd_salt).hexdigest()
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hashed password
        salt: Salt used for hashing
        
    Returns:
        True if password matches, False otherwise
    """
    check_hash, _ = hash_password(password, salt)
    return check_hash == hashed_password


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate Sri Lankan phone number format."""
    # Sri Lankan phone numbers: +94XXXXXXXXX or 0XXXXXXXXX
    pattern = r'^(\+94|0)[0-9]{9}$'
    return re.match(pattern, phone) is not None


def signup_user(email: str, password: str, full_name: str, phone: str) -> Dict:
    """
    Create a new user account.
    
    Args:
        email: User's email address
        password: User's password (will be hashed)
        full_name: User's full name
        phone: User's phone number
        
    Returns:
        Dict with success status and message/user_id
    """
    # Validate inputs
    if not validate_email(email):
        return {"success": False, "message": "Invalid email format"}
    
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}
    
    if not full_name or len(full_name.strip()) < 2:
        return {"success": False, "message": "Please provide your full name"}
    
    if not validate_phone(phone):
        return {"success": False, "message": "Invalid phone number format (use +94XXXXXXXXX or 0XXXXXXXXX)"}
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email.lower(),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Email already registered"}
        
        # Hash password
        hashed_pwd, salt = hash_password(password)
        
        # Generate user ID
        import uuid
        user_id = str(uuid.uuid4())
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (user_id, email, password_hash, salt, full_name, phone, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, email.lower(), hashed_pwd, salt, full_name, phone, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True, 
            "message": "Account created successfully!",
            "user_id": user_id
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error creating account: {str(e)}"}


def login_user(email: str, password: str) -> Dict:
    """
    Authenticate a user.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Dict with success status and user info or error message
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get user by email
        cursor.execute("""
            SELECT user_id, email, password_hash, salt, full_name, phone, created_at
            FROM users WHERE email = %s
        """, (email.lower(),))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return {"success": False, "message": "Invalid email or password"}
        
        # Verify password
        if not verify_password(password, user['password_hash'], user['salt']):
            return {"success": False, "message": "Invalid email or password"}
        
        # Update last login
        update_last_login(user['user_id'])
        
        return {
            "success": True,
            "message": "Login successful!",
            "user": {
                "user_id": user['user_id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "phone": user['phone'],
                "created_at": user['created_at']
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"Login error: {str(e)}"}


def update_last_login(user_id: str):
    """Update user's last login timestamp."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_login = %s WHERE user_id = %s
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass  # Silent fail - not critical


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user information by user ID."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT user_id, email, full_name, phone, created_at, last_login
            FROM users WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return dict(user) if user else None
        
    except:
        return None


def update_user_profile(user_id: str, full_name: str = None, phone: str = None) -> Dict:
    """
    Update user profile information.
    
    Args:
        user_id: User's ID
        full_name: New full name (optional)
        phone: New phone number (optional)
        
    Returns:
        Dict with success status and message
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        if phone:
            if not validate_phone(phone):
                return {"success": False, "message": "Invalid phone number format"}
            updates.append("phone = %s")
            params.append(phone)
        
        if not updates:
            return {"success": False, "message": "No updates provided"}
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Update error: {str(e)}"}


def change_password(user_id: str, old_password: str, new_password: str) -> Dict:
    """
    Change user's password.
    
    Args:
        user_id: User's ID
        old_password: Current password
        new_password: New password
        
    Returns:
        Dict with success status and message
    """
    try:
        # Verify old password
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT password_hash, salt FROM users WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return {"success": False, "message": "User not found"}
        
        if not verify_password(old_password, user['password_hash'], user['salt']):
            cursor.close()
            conn.close()
            return {"success": False, "message": "Current password is incorrect"}
        
        # Validate new password
        if len(new_password) < 6:
            cursor.close()
            conn.close()
            return {"success": False, "message": "New password must be at least 6 characters"}
        
        # Hash new password
        new_hash, new_salt = hash_password(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users SET password_hash = %s, salt = %s WHERE user_id = %s
        """, (new_hash, new_salt, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Password changed successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Error changing password: {str(e)}"}
