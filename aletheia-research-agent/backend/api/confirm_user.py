"""Quick script to auto-confirm a user in Supabase."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def confirm_user(email):
    """Confirm a user by email."""
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        return

    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "apikey": SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }

    # First, get all users
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching users: {response.status_code}")
        print(response.text)
        return

    users = response.json().get("users", [])
    user = next((u for u in users if u["email"] == email), None)

    if not user:
        print(f"User with email {email} not found")
        print("Available users:")
        for u in users:
            print(f"  - {u['email']} (id: {u['id']}, confirmed: {u['email_confirmed_at'] is not None})")
        return

    print(f"Found user: {user['email']}")
    print(f"  ID: {user['id']}")
    print(f"  Confirmed: {user['email_confirmed_at'] is not None}")

    # Update user to confirm
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user['id']}"
    data = {
        "email_confirm": True
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print("\n✓ User confirmed successfully!")
        print("They can now log in.")
    else:
        print(f"\nError confirming user: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        confirm_user(sys.argv[1])
    else:
        print("Usage: python confirm_user.py <email>")
