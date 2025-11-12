#!/usr/bin/env python3
"""
Fix script to resolve authentication and CORS issues.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def check_cors():
    """Check if CORS is configured correctly."""
    print_header("Checking CORS Configuration")

    import subprocess
    result = subprocess.run(
        [
            "curl", "-I",
            "http://localhost:8001/api/chat/send",
            "-X", "OPTIONS",
            "-H", "Origin: http://localhost:3001",
            "-H", "Access-Control-Request-Method: POST"
        ],
        capture_output=True,
        text=True
    )

    if "access-control-allow-origin" in result.stdout.lower():
        print("✓ CORS is configured correctly!")
        print("  Frontend can communicate with backend.")
    else:
        print("✗ CORS may have issues")
    print("\nResponse headers:")
    print(result.stdout)

def list_users():
    """List all users in Supabase."""
    print_header("Listing Users in Supabase")

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("✗ Supabase credentials not found in .env")
        return []

    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "apikey": SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }

    try:
        url = f"{SUPABASE_URL}/auth/v1/admin/users"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"✗ Error fetching users: {response.status_code}")
            return []

        users = response.json().get("users", [])
        print(f"Found {len(users)} user(s):\n")

        for i, user in enumerate(users, 1):
            status = "✓ Confirmed" if user.get("email_confirmed_at") else "✗ Not Confirmed"
            print(f"{i}. {user['email']}")
            print(f"   ID: {user['id']}")
            print(f"   Status: {status}")
            print()

        return users
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def confirm_user(user_id):
    """Confirm a user by ID."""
    print_header(f"Confirming User: {user_id}")

    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "apikey": SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }

    try:
        url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
        data = {"email_confirm": True}

        response = requests.put(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            print(f"✓ User confirmed successfully!")
            print("They can now log in.")
            return True
        else:
            print(f"✗ Error confirming user: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  ALETHEIA - Authentication Fix Tool")
    print("="*60)

    # Check CORS
    check_cors()

    # List users
    users = list_users()

    if not users:
        print("\n" + "="*60)
        print("  No users found. Sign up at http://localhost:3001/login")
        print("="*60 + "\n")
        return

    # Ask which user to confirm
    unconfirmed = [u for u in users if not u.get("email_confirmed_at")]

    if unconfirmed:
        print(f"\n{len(unconfirmed)} unconfirmed user(s) found.")
        print("\nTo confirm a user, run:")
        print(f"  python fix_auth.py --confirm <USER_ID>")
        print("\nOr run with --confirm-all to confirm all unconfirmed users:")
        print(f"  python fix_auth.py --confirm-all")
    else:
        print("\n✓ All users are confirmed!")

    # Check if we should confirm a specific user
    if len(sys.argv) > 1:
        if sys.argv[1] == "--confirm" and len(sys.argv) > 2:
            user_id = sys.argv[2]
            confirm_user(user_id)
        elif sys.argv[1] == "--confirm-all":
            print_header("Confirming All Unconfirmed Users")
            for user in unconfirmed:
                if confirm_user(user["id"]):
                    print(f"  ✓ Confirmed {user['email']}")

    print("\n" + "="*60)
    print("  Next Steps:")
    print("="*60)
    print("1. Go to http://localhost:3001/login")
    print("2. Log in with your confirmed account")
    print("3. Start chatting with Aletheia!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
