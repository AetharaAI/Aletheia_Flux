#!/usr/bin/env python3
"""Test Grok API endpoints."""
import os
import httpx
import asyncio

# Load .env
from dotenv import load_dotenv
load_dotenv('/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend/.env')

API_KEY = os.getenv("GROK_API_KEY")
if not API_KEY:
    print("GROK_API_KEY not set!")
    exit(1)

print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")

# Test different endpoints
endpoints = [
    "https://api.x.ai/v1/chat/completions",
    "https://api.x.ai/v1beta/chat/completions",
    "https://api.x.ai/v1/grok/chat/completions",
    "https://api.x.ai/v1/chat/completions",
]

async def test_endpoint(url):
    print(f"\nTesting: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ]
                },
                timeout=10.0
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ SUCCESS!")
                return True
            else:
                print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")
    return False

async def main():
    for endpoint in endpoints:
        success = await test_endpoint(endpoint)
        if success:
            print(f"\n✓ Found working endpoint: {endpoint}")
            break

asyncio.run(main())