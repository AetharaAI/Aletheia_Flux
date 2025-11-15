#!/usr/bin/env python3
"""Test database connection and table existence."""
import sys
sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend')

from supabase import create_client
from config import settings

print("=" * 70)
print("Testing Supabase Connection")
print("=" * 70)

# Initialize Supabase
try:
    supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
    print(f"✓ Supabase client initialized")
    print(f"  URL: {settings.supabase_url}")
except Exception as e:
    print(f"✗ Failed to initialize Supabase: {e}")
    sys.exit(1)

# Check if tables exist
tables = [
    'discovered_agents',
    'agent_outreach',
    'discovery_runs',
    'agent_verification_queue',
    'agent_categories'
]

print("\n" + "=" * 70)
print("Checking Tables")
print("=" * 70)

for table in tables:
    try:
        result = supabase.table(table).select("*", count="exact").limit(0).execute()
        print(f"✓ Table '{table}' exists (count: {result.count})")
    except Exception as e:
        print(f"✗ Table '{table}' error: {str(e)[:100]}")

# Test discovery_runs specifically
print("\n" + "=" * 70)
print("Testing Discovery Stats Query")
print("=" * 70)

try:
    # Try the same query the endpoint uses
    runs_result = supabase.table('discovery_runs').select("id, status, created_at").order('created_at', desc=True).limit(10).execute()
    print(f"✓ discovery_runs query successful: {len(runs_result.data)} rows")

    agents_result = supabase.table('discovered_agents').select("id", count="exact").limit(0).execute()
    print(f"✓ discovered_agents query successful: {agents_result.count} total")

    verified_result = supabase.table('discovered_agents').select("id", count="exact").eq('is_verified', True).limit(0).execute()
    print(f"✓ Verified agents query successful: {verified_result.count} verified")

except Exception as e:
    print(f"✗ Query failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Done")
print("=" * 70)