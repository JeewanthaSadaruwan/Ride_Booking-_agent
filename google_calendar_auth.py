"""
One-time authentication script for Google Calendar API.

Prerequisites:
1. Enable Google Calendar API in Google Cloud Console
2. Create OAuth 2.0 credentials (Desktop App)
3. Download credentials.json to this directory

Usage:
    python google_calendar_auth.py

This will:
- Open browser for Google login
- Request calendar access permission
- Save token.json for future use
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate():
    """Authenticate with Google Calendar and save token."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

        print("✅ Authentication successful!")
        print("✅ token.json saved.")
        print("\n📝 You can now use the Google Calendar integration in your agent.")
        
    except FileNotFoundError:
        print("❌ Error: credentials.json not found!")
        print("\n📋 Setup Instructions:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Enable Google Calendar API")
        print("3. Create OAuth 2.0 Client ID (Desktop App)")
        print("4. Download credentials.json")
        print("5. Place credentials.json in this directory")
        print("6. Run this script again")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    print("🔐 Google Calendar Authentication")
    print("=" * 50)
    authenticate()
