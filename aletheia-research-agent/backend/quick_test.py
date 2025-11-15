#!/usr/bin/env python3
"""
Quick test of discovery tools with real API keys
"""

import sys
import os
sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent')

# Load environment from .env
from dotenv import load_dotenv
load_dotenv('/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend/.env')

print("="*70)
print("TESTING DISCOVERY TOOLS WITH REAL API KEYS")
print("="*70)

# Test 1: Grok Search Tool
print("\n[TEST 1] GrokSearchTool")
print("-" * 70)
try:
    from backend.tools.grok_search import GrokSearchTool

    # Check API key
    grok_key = os.getenv("GROK_API_KEY")
    print(f"API Key present: {grok_key[:20]}...{grok_key[-10:] if grok_key else 'NONE'}")
    print(f"Key starts with 'xai-': {grok_key.startswith('xai-') if grok_key else False}")

    # Initialize tool
    grok = GrokSearchTool()
    print(f"✓ GrokSearchTool initialized successfully")
    print(f"  Base URL: {grok.base_url}")
    print(f"  Model: {grok.model}")

except Exception as e:
    print(f"✗ GrokSearchTool failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Firecrawl Tool
print("\n[TEST 2] FirecrawlTool")
print("-" * 70)
try:
    from backend.tools.firecrawl_scraper import FirecrawlTool

    # Check API key
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    print(f"API Key present: {firecrawl_key[:20]}...{firecrawl_key[-10:] if firecrawl_key else 'NONE'}")
    print(f"Key starts with 'fc-': {firecrawl_key.startswith('fc-') if firecrawl_key else False}")

    # Initialize tool
    firecrawl = FirecrawlTool()
    print(f"✓ FirecrawlTool initialized successfully")
    print(f"  Base URL: {firecrawl.base_url}")

except Exception as e:
    print(f"✗ FirecrawlTool failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Discovery Agent
print("\n[TEST 3] AgentDiscoverySystem")
print("-" * 70)
try:
    from backend.agents.discovery_agent import AgentDiscoverySystem
    from backend.config.discovery_sources import DISCOVERY_SOURCES, SEARCH_KEYWORDS

    print(f"✓ Discovery sources configured:")
    print(f"  - Directories: {len(DISCOVERY_SOURCES.get('directories', []))}")
    print(f"  - Keywords: {len(SEARCH_KEYWORDS)}")

    # Check other required keys
    print(f"\n✓ Other API keys:")
    print(f"  - MINIMAX_API_KEY: {'✓' if os.getenv('MINIMAX_API_KEY') else '✗'}")
    print(f"  - TAVILY_API_KEY: {'✓' if os.getenv('TAVILY_API_KEY') else '✗'}")
    print(f"  - SUPABASE_URL: {'✓' if os.getenv('SUPABASE_URL') else '✗'}")

except Exception as e:
    print(f"✗ AgentDiscoverySystem check failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("READY TO RUN DISCOVERY!")
print("="*70)
print("\nNext step: Start the backend server and test discovery:")
print("  1. cd /home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend")
print("  2. source venv/bin/activate")
print("  3. uvicorn main:app --reload --port 8001 --host 0.0.0.0")
print("\nThen access: http://localhost:8001/api/discovery/health")
print("="*70)
