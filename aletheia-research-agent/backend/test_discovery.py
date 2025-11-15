#!/usr/bin/env python3
"""
Test script for Agent Discovery System
"""

import asyncio
import os
from datetime import datetime

async def test_discovery_imports():
    """Test that all discovery modules can be imported"""
    print("\n" + "="*60)
    print("TEST: Import Discovery Modules")
    print("="*60)

    import sys
    sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent')

    try:
        from backend.tools.grok_search import GrokSearchTool
        print("✓ GrokSearchTool imported")
    except Exception as e:
        print(f"✗ GrokSearchTool failed: {e}")
        return False

    try:
        from backend.tools.firecrawl_scraper import FirecrawlTool
        print("✓ FirecrawlTool imported")
    except Exception as e:
        print(f"✗ FirecrawlTool failed: {e}")
        return False

    try:
        from backend.agents.discovery_agent import AgentDiscoverySystem
        print("✓ AgentDiscoverySystem imported")
    except Exception as e:
        print(f"✗ AgentDiscoverySystem failed: {e}")
        return False

    try:
        from backend.api.discovery_routes import router as discovery_router
        print("✓ Discovery routes imported")
    except Exception as e:
        print(f"✗ Discovery routes failed: {e}")
        return False

    return True


async def test_api_keys():
    """Test that API keys are configured"""
    print("\n" + "="*60)
    print("TEST: API Keys Configuration")
    print("="*60)

    grok_key = os.getenv("GROK_API_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")

    if grok_key and grok_key != "placeholder-will-get-real-key":
        print(f"✓ GROK_API_KEY configured (starts with: {grok_key[:10]}...)")
    else:
        print("⚠ GROK_API_KEY not configured (you'll need a real API key from x.ai)")

    if firecrawl_key and firecrawl_key != "placeholder-will-get-real-key":
        print(f"✓ FIRECRAWL_API_KEY configured (starts with: {firecrawl_key[:10]}...)")
    else:
        print("⚠ FIRECRAWL_API_KEY not configured (you'll need a real API key from firecrawl.dev)")

    return True


async def test_database_schema():
    """Test that database schema can be loaded"""
    print("\n" + "="*60)
    print("TEST: Database Schema")
    print("="*60)

    try:
        with open("backend/database/schema.sql", "r") as f:
            schema = f.read()

        # Check for key tables
        tables = [
            "discovered_agents",
            "agent_outreach",
            "discovery_runs",
            "agent_verification_queue",
            "agent_categories"
        ]

        for table in tables:
            if table in schema:
                print(f"✓ Table '{table}' found in schema")
            else:
                print(f"✗ Table '{table}' missing from schema")
                return False

        print(f"\n✓ Schema file loaded successfully ({len(schema)} bytes)")

    except FileNotFoundError:
        print("✗ Schema file not found at backend/database/schema.sql")
        return False
    except Exception as e:
        print(f"✗ Error loading schema: {e}")
        return False

    return True


async def test_discovery_config():
    """Test that discovery configuration loads"""
    print("\n" + "="*60)
    print("TEST: Discovery Configuration")
    print("="*60)

    import sys
    sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent')

    try:
        from backend.config.discovery_sources import DISCOVERY_SOURCES, SEARCH_KEYWORDS

        print(f"✓ DISCOVERY_SOURCES loaded")
        print(f"  - Directories: {len(DISCOVERY_SOURCES.get('directories', []))}")
        print(f"  - Communities: {len(DISCOVERY_SOURCES.get('communities', []))}")
        print(f"  - Frameworks: {len(DISCOVERY_SOURCES.get('frameworks', []))}")

        print(f"\n✓ SEARCH_KEYWORDS loaded ({len(SEARCH_KEYWORDS)} keywords)")
        print(f"  - First 5: {', '.join(SEARCH_KEYWORDS[:5])}")

    except Exception as e:
        print(f"✗ Configuration load failed: {e}")
        return False

    return True


async def test_api_routes():
    """Test that API routes can be imported"""
    print("\n" + "="*60)
    print("TEST: API Routes")
    print("="*60)

    import sys
    sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent')

    try:
        from backend.api.discovery_routes import (
            router as discovery_router,
            list_discovered_agents,
            get_discovery_stats,
            start_discovery_run
        )

        print("✓ All discovery route handlers imported")
        print(f"  - Routes defined: {len(discovery_router.routes)}")

        # List some routes
        routes = [route.path for route in discovery_router.routes]
        print(f"\n  Available endpoints:")
        for route in sorted(routes):
            print(f"    - GET {route}" if hasattr(route, 'path') else f"    - {route}")

    except Exception as e:
        print(f"✗ API routes import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AGENT DISCOVERY SYSTEM TESTS" + " "*18 + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        ("Imports", test_discovery_imports),
        ("API Keys", test_api_keys),
        ("Database Schema", test_database_schema),
        ("Configuration", test_discovery_config),
        ("API Routes", test_api_routes),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Discovery system is ready to use.")
        print("\nNext steps:")
        print("1. Get your Grok API key from: https://x.ai")
        print("2. Get your Firecrawl API key from: https://firecrawl.dev")
        print("3. Update your .env file with the real keys")
        print("4. Run the database migration (see backend/database/schema.sql)")
        print("5. Test with a small discovery run!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the errors above.")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
