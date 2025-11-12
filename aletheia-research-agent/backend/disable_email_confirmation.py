"""Script to disable email confirmation in Supabase for development."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def disable_email_confirmation():
    """Disable email confirmation in Supabase auth settings."""
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        return

    # Supabase Management API endpoint
    url = f"{SUPABASE_URL}/auth/v1/admin/config"

    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "apikey": SERVICE_ROLE_KEY,
        "Content-Type": "application/json"
    }

    # Get current config
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching config: {response.status_code}")
        print(response.text)
        return

    config = response.json()
    print("Current Auth Config:")
    print(f"  Email Confirmation: {config.get('MAILER_AUTOCONFIRM', 'not set')}")

    # Update config to disable email confirmation
    config["MAILER_AUTOCONFIRM"] = True
    config["MAILER_URLPATHS"] = {
        "confirmation": "/auth/confirm",
        "recovery": "/auth/recovery",
        "email_change": "/auth/email-change",
        "invite": "/auth/invite"
    }

    response = requests.put(url, headers=headers, json=config)

    if response.status_code == 200:
        print("\n✓ Email confirmation disabled successfully!")
        print("Users can now sign up and log in without email confirmation.")
    else:
        print(f"\nError updating config: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    disable_email_confirmation()
