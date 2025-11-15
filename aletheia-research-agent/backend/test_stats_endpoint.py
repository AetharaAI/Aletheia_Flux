#!/usr/bin/env python3
"""Test the stats endpoint logic."""
import sys
sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend')

from supabase import create_client
from config import settings

print("=" * 70)
print("Testing Discovery Stats Logic")
print("=" * 70)

supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

# Total discovered
print("\n[1] Total discovered...")
try:
    total_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .execute()
    print(f"  ✓ Total: {total_result.count}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Verified
print("\n[2] Verified...")
try:
    verified_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .eq("verified", True) \
        .execute()
    print(f"  ✓ Verified: {verified_result.count}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Registered
print("\n[3] Registered...")
try:
    registered_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .eq("registered", True) \
        .execute()
    print(f"  ✓ Registered: {registered_result.count}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# By category (RPC)
print("\n[4] By category (RPC)...")
try:
    by_category_result = supabase.rpc("get_agents_by_category").execute()
    print(f"  ✓ RPC Success: {len(by_category_result.data) if by_category_result.data else 0} categories")
    if by_category_result.data:
        for row in by_category_result.data:
            print(f"    - {row}")
except Exception as e:
    print(f"  ✗ RPC Error: {e}")
    print(f"  Message: {e.message if hasattr(e, 'message') else 'No message'}")
    print(f"  Code: {e.code if hasattr(e, 'code') else 'No code'}")

# Last discovery run
print("\n[5] Last discovery run...")
try:
    last_run = supabase.table("discovery_runs") \
        .select("*") \
        .eq("status", "completed") \
        .order("started_at", desc=True) \
        .limit(1) \
        .execute()
    print(f"  ✓ Last run: {len(last_run.data) if last_run.data else 0} runs")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)