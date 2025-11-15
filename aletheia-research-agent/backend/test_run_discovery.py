#!/usr/bin/env python3
"""Test running a small discovery."""
import asyncio
import sys
import os
sys.path.insert(0, '/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend')

# Load .env file
from dotenv import load_dotenv
load_dotenv('/home/cory/Desktop/Aletheia_Flux/aletheia-research-agent/backend/.env')

from config import supabase
from agents.discovery_agent import AgentDiscoverySystem
from llm.minimax_client import MiniMaxClient
from tools.web_search import WebSearchTool

async def test_discovery():
    print("=" * 70)
    print("Testing Agent Discovery System")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing Discovery System...")
    try:
        system = AgentDiscoverySystem(
            minimax_client=MiniMaxClient(),
            tavily_client=WebSearchTool(),
            grok_api_key='',  # Will read from settings
            firecrawl_api_key='',  # Will read from settings
            supabase_client=supabase
        )
        print("✓ Discovery system initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return

    # Run a small discovery
    print("\n[2] Running test discovery...")
    try:
        result = await system.discover(
            keywords=["LangChain agents"],
            max_results=5  # Small test
        )

        print(f"\n✓ Discovery completed!")
        print(f"  - Keywords: {result.get('keywords', [])}")
        print(f"  - Agents to store: {len(result.get('agents_to_store', []))}")
        print(f"  - Total found: {result.get('total_found', 0)}")
        print(f"  - All result keys: {list(result.keys())}")

        if result['agents_to_store']:
            print(f"\n[3] First agent preview:")
            first_agent = result['agents_to_store'][0]
            print(f"  Name: {first_agent.get('name', 'N/A')}")
            print(f"  Framework: {first_agent.get('framework', 'N/A')}")
            print(f"  URL: {first_agent.get('source_url', 'N/A')}")
            print(f"  Confidence: {first_agent.get('confidence_score', 'N/A')}")

    except Exception as e:
        print(f"✗ Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_discovery())