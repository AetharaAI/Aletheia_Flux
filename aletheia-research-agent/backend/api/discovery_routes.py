"""
Discovery API Routes - Agent Discovery System
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.jwt_handler import get_current_user_id
from agents.discovery_agent import AgentDiscoverySystem
from config import settings, supabase
from llm.minimax_client import MiniMaxClient
from tools.web_search import WebSearchTool

router = APIRouter(prefix="/api/discovery", tags=["discovery"])

# Global discovery system instance (will be initialized in main.py)
discovery_system: Optional[AgentDiscoverySystem] = None


def get_discovery_system() -> AgentDiscoverySystem:
    """Get the discovery system instance"""
    global discovery_system
    if discovery_system is None:
        raise HTTPException(
            status_code=500,
            detail="Discovery system not initialized. Please check server configuration."
        )
    return discovery_system


@router.post("/run")
async def start_discovery_run(
    keywords: Optional[List[str]] = None,
    max_results: int = 50,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Start a new discovery run

    Args:
        keywords: Custom keywords to search for (optional)
        max_results: Maximum number of agents to discover (default: 50)
        current_user_id: User ID from JWT token

    Returns:
        Discovery run status and summary
    """
    discovery = get_discovery_system()

    # Run discovery asynchronously in the background
    task = asyncio.create_task(
        discovery.discover(
            keywords=keywords,
            max_results=max_results
        )
    )

    # Return immediately with task info
    return {
        "success": True,
        "message": "Discovery run started",
        "status": "running",
        "max_results": max_results,
        "keywords_count": len(keywords) if keywords else "default"
    }


@router.get("/agents")
async def list_discovered_agents(
    verified: Optional[bool] = None,
    category: Optional[str] = None,
    registered: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List discovered agents with optional filters

    Args:
        verified: Filter by verification status
        category: Filter by category
        registered: Filter by registration status
        limit: Number of results to return (max: 100)
        offset: Offset for pagination

    Returns:
        List of discovered agents
    """
    query = supabase.table("discovered_agents").select("*")

    if verified is not None:
        query = query.eq("verified", verified)
    if category:
        query = query.eq("category", category)
    if registered is not None:
        query = query.eq("registered", registered)

    result = query \
        .order("confidence_score", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    return {
        "agents": result.data,
        "count": len(result.data),
        "total": result.count
    }


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """
    Get detailed information about a specific discovered agent

    Args:
        agent_id: UUID of the agent

    Returns:
        Detailed agent information
    """
    result = supabase.table("discovered_agents") \
        .select("*") \
        .eq("id", agent_id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get outreach history
    outreach = supabase.table("agent_outreach") \
        .select("*") \
        .eq("agent_id", agent_id) \
        .order("created_at", desc=True) \
        .execute()

    return {
        "agent": result.data,
        "outreach_history": outreach.data
    }


@router.post("/agents/{agent_id}/verify")
async def verify_agent(
    agent_id: str,
    verification_notes: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Mark an agent as verified (manual verification)

    Args:
        agent_id: UUID of the agent
        verification_notes: Optional notes about verification
        current_user_id: User ID from JWT token

    Returns:
        Updated agent information
    """
    # Get user info
    user_result = supabase.table("auth.users") \
        .select("email") \
        .eq("id", current_user_id) \
        .single() \
        .execute()

    user_email = user_result.data.get("email") if user_result.data else "unknown"

    result = supabase.table("discovered_agents").update({
        "verified": True,
        "verified_at": datetime.utcnow().isoformat(),
        "verified_by": user_email,
        "verification_notes": verification_notes
    }).eq("id", agent_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "success": True,
        "agent": result.data[0],
        "message": "Agent verified successfully"
    }


@router.get("/runs")
async def list_discovery_runs(limit: int = 20):
    """
    List recent discovery runs with statistics

    Args:
        limit: Number of runs to return (max: 100)

    Returns:
        List of discovery runs
    """
    result = supabase.table("discovery_runs") \
        .select("*") \
        .order("started_at", desc=True) \
        .limit(limit) \
        .execute()

    return {
        "runs": result.data,
        "count": len(result.data)
    }


@router.get("/runs/{run_id}")
async def get_discovery_run_details(run_id: str):
    """
    Get detailed information about a specific discovery run

    Args:
        run_id: UUID of the discovery run

    Returns:
        Detailed run information
    """
    result = supabase.table("discovery_runs") \
        .select("*") \
        .eq("id", run_id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Discovery run not found")

    return {
        "run": result.data
    }


@router.get("/stats")
async def get_discovery_stats():
    """
    Get overall discovery system statistics

    Returns:
        Comprehensive statistics
    """
    # Total discovered
    total_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .execute()

    # Verified
    verified_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .eq("verified", True) \
        .execute()

    # Registered
    registered_result = supabase.table("discovered_agents") \
        .select("id", count="exact") \
        .eq("registered", True) \
        .execute()

    # By category
    try:
        by_category_result = supabase.rpc("get_agents_by_category").execute()
        by_category = by_category_result.data if by_category_result.data else []
    except Exception:
        by_category = []

    # Last discovery run
    last_run = supabase.table("discovery_runs") \
        .select("*") \
        .eq("status", "completed") \
        .order("started_at", desc=True) \
        .limit(1) \
        .execute()

    return {
        "total_discovered": total_result.count,
        "verified": verified_result.count,
        "registered": registered_result.count,
        "by_category": by_category,
        "last_discovery_run": last_run.data[0] if last_run.data else None,
        "stats": {
            "verified_rate": round(
                (verified_result.count or 0) * 100.0 / max(total_result.count or 1, 1), 2
            ),
            "registration_rate": round(
                (registered_result.count or 0) * 100.0 / max(total_result.count or 1, 1), 2
            )
        }
    }


@router.get("/queue")
async def get_verification_queue(limit: int = 50):
    """
    Get agents in the verification queue (high confidence, unverified)

    Args:
        limit: Number of agents to return

    Returns:
        List of agents needing verification
    """
    result = supabase.table("unverified_high_confidence_agents") \
        .select("*") \
        .limit(limit) \
        .execute()

    return {
        "agents": result.data,
        "count": len(result.data)
    }


@router.get("/outreach")
async def get_outreach_ready_agents(limit: int = 50):
    """
    Get agents ready for outreach (verified but not contacted)

    Args:
        limit: Number of agents to return

    Returns:
        List of agents ready for outreach
    """
    result = supabase.table("agents_ready_for_outreach") \
        .select("*") \
        .limit(limit) \
        .execute()

    return {
        "agents": result.data,
        "count": len(result.data)
    }


@router.post("/agents/{agent_id}/outreach")
async def generate_outreach(
    agent_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate personalized outreach message for an agent

    Args:
        agent_id: UUID of the agent
        current_user_id: User ID from JWT token

    Returns:
        Generated outreach message
    """
    from backend.llm.minimax_client import MiniMaxClient

    # Get agent details
    agent_result = supabase.table("discovered_agents") \
        .select("*") \
        .eq("id", agent_id) \
        .single() \
        .execute()

    if not agent_result.data:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agent_result.data

    # Generate outreach using MiniMax
    minimax = MiniMaxClient(settings.minimax_api_key)

    prompt = f"""
    Generate a professional, personalized outreach email to invite this AI agent creator
    to register on AetherPro.tech - the infrastructure layer for AI agents.

    AGENT INFORMATION:
    - Name: {agent.get('name', 'Unknown')}
    - Description: {agent.get('description', 'N/A')}
    - Framework: {agent.get('framework', 'Unknown')}
    - Category: {agent.get('category', 'Unknown')}
    - Capabilities: {', '.join(agent.get('capabilities', [])) if isinstance(agent.get('capabilities'), list) else agent.get('capabilities', 'N/A')}

    REQUIREMENTS:
    - Friendly and professional tone
    - Acknowledge their specific work on this agent
    - Explain AetherPro as infrastructure (like DNS for agents)
    - Keep it under 150 words
    - Include a clear call-to-action
    - Be genuine, not salesy

    EMAIL:
    """

    # Generate the message
    message = await minimax.generate(
        prompt,
        temperature=0.7,
        max_tokens=300
    )

    return {
        "agent_id": agent_id,
        "message": message,
        "suggested_subject": f"Register {agent.get('name', 'Your AI Agent')} on AetherPro"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the discovery system

    Returns:
        System health status
    """
    return {
        "status": "healthy",
        "service": "agent-discovery",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
