# Agent Discovery System - Deployment Guide

Complete step-by-step guide to deploy the Agent Discovery System on top of your existing Aletheia Flux installation.

## Prerequisites Checklist

- [ ] Aletheia Flux installed and running
- [ ] Python 3.10+ environment
- [ ] Supabase project with existing tables
- [ ] MiniMax API key (existing)
- [ ] Tavily API key (existing)
- [ ] Grok API key (NEW - get from x.ai)
- [ ] Firecrawl API key (NEW - get from firecrawl.dev)

## Step 1: Get New API Keys

### Grok API (X.AI)
1. Go to https://x.ai
2. Sign up / Log in
3. Navigate to API section
4. Generate API key
5. Copy key (starts with `xai-...`)

**Cost**: ~$0.01 per search

### Firecrawl API
1. Go to https://firecrawl.dev
2. Sign up for account
3. Go to dashboard
4. Generate API key
5. Copy key

**Cost**: ~$0.02 per page scraped

## Step 2: Install Dependencies

```bash
cd /path/to/aletheia-flux/backend

# Install new dependencies
pip install firecrawl-py==0.0.5
pip install schedule==1.2.1
pip install apscheduler==3.10.4

# Verify installation
python -c "import firecrawl; print('Firecrawl OK')"
```

## Step 3: Update Environment Variables

Add to your `backend/.env`:

```bash
# ============================================================================
# NEW - Agent Discovery System
# ============================================================================

# Grok API (X.AI)
GROK_API_KEY=xai-your-key-here

# Firecrawl
FIRECRAWL_API_KEY=your-firecrawl-key-here

# Discovery Configuration
DISCOVERY_ENABLED=true
DISCOVERY_SCHEDULE_HOUR=2  # Run at 2 AM daily
DISCOVERY_MAX_RESULTS=50
DISCOVERY_AUTO_VERIFY_THRESHOLD=0.9  # Auto-verify agents with 90%+ confidence
```

## Step 4: Database Migration

### Option A: Using Supabase Dashboard

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Copy contents of `backend/database/schema.sql`
4. Execute the SQL
5. Verify tables created:
   - discovered_agents
   - agent_outreach
   - discovery_runs
   - agent_verification_queue
   - agent_categories

### Option B: Using psql

```bash
# Get your Supabase connection string
SUPABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres"

# Run migration
psql $SUPABASE_URL -f backend/database/schema.sql

# Verify tables
psql $SUPABASE_URL -c "\dt discovered_agents"
```

### Verify Migration

```sql
-- Should return 8 rows (the default categories)
SELECT COUNT(*) FROM agent_categories;

-- Should exist and be empty
SELECT COUNT(*) FROM discovered_agents;
SELECT COUNT(*) FROM agent_outreach;
SELECT COUNT(*) FROM discovery_runs;
```

## Step 5: Add Discovery Tools

Copy the new tool files into your Aletheia backend:

```bash
# From agent-discovery-system/ directory
cp backend/tools/grok_search.py /path/to/aletheia-flux/backend/tools/
cp backend/tools/firecrawl_scraper.py /path/to/aletheia-flux/backend/tools/

# Verify
ls -la /path/to/aletheia-flux/backend/tools/
# Should see: web_search.py, grok_search.py, firecrawl_scraper.py
```

## Step 6: Add Discovery Agent

Copy the discovery agent:

```bash
cp backend/agents/discovery_agent.py /path/to/aletheia-flux/backend/agents/

# Verify
ls -la /path/to/aletheia-flux/backend/agents/
# Should see: research_agent.py, discovery_agent.py
```

## Step 7: Test Tools Individually

### Test Grok Search

```bash
cd /path/to/aletheia-flux/backend
python tools/grok_search.py
```

Expected output:
```
Testing single search...
Found 5 results
  - LangChain Agents: https://...
  - CrewAI Framework: https://...
  ...
```

### Test Firecrawl

```bash
python tools/firecrawl_scraper.py
```

Expected output:
```
Testing single page scrape...
Scraped 15234 characters
Contacts: {'emails': ['contact@example.com'], 'github': 'https://...'}
```

## Step 8: Create Discovery Config

Create `backend/config/discovery_sources.py`:

```python
"""
Discovery sources and keywords configuration
"""

DISCOVERY_SOURCES = {
    "directories": [
        "https://github.com/topics/ai-agents",
        "https://huggingface.co/models",
        "https://www.langchain.com/",
        "https://www.crewai.com/",
        "https://autogpt.net/",
        "https://www.producthunt.com/topics/ai-agents",
    ],
    
    "communities": [
        "https://www.reddit.com/r/artificial/",
        "https://www.reddit.com/r/LocalLLaMA/",
        "https://news.ycombinator.com/",
    ],
    
    "frameworks": [
        "https://python.langchain.com/docs/use_cases/agents",
        "https://docs.crewai.com/",
        "https://www.langflow.org/",
    ]
}

SEARCH_KEYWORDS = [
    # General
    "AI agent",
    "autonomous agent",
    "LLM agent",
    
    # Framework-specific
    "LangChain agent",
    "CrewAI agent",
    "AutoGPT agent",
    
    # Use case specific
    "research agent",
    "coding agent",
    "data analysis agent",
    
    # Recent
    "AI agent 2024",
    "AI agent 2025",
]
```

## Step 9: Add Discovery API Routes

Create `backend/api/discovery_routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import asyncio

from backend.auth.jwt_handler import get_current_user
from backend.agents.discovery_agent import AgentDiscoverySystem

router = APIRouter(prefix="/api/discovery", tags=["discovery"])

# Initialize discovery system (do this properly with your clients)
discovery_system = None  # Will be initialized in main.py

@router.post("/run")
async def start_discovery_run(
    keywords: Optional[List[str]] = None,
    max_results: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Start a new discovery run"""
    if not discovery_system:
        raise HTTPException(status_code=500, detail="Discovery system not initialized")
    
    # Run discovery asynchronously
    result = await discovery_system.discover(
        keywords=keywords,
        max_results=max_results
    )
    
    return {
        "success": True,
        "run_id": result["run_id"],
        "status": result["status"],
        "agents_found": len(result["classified_agents"]),
        "agents_stored": len(result["agents_to_store"])
    }

@router.get("/agents")
async def list_discovered_agents(
    verified: Optional[bool] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List discovered agents with filters"""
    from backend.config import supabase
    
    query = supabase.table("discovered_agents").select("*")
    
    if verified is not None:
        query = query.eq("verified", verified)
    if category:
        query = query.eq("category", category)
    
    result = query\
        .order("confidence_score", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return {"agents": result.data, "count": len(result.data)}

@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a discovered agent"""
    from backend.config import supabase
    
    result = supabase.table("discovered_agents")\
        .select("*")\
        .eq("id", agent_id)\
        .single()\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"agent": result.data}

@router.post("/agents/{agent_id}/verify")
async def verify_agent(
    agent_id: str,
    verification_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Mark agent as verified (manual verification)"""
    from backend.config import supabase
    
    result = supabase.table("discovered_agents").update({
        "verified": True,
        "verified_at": datetime.utcnow().isoformat(),
        "verified_by": current_user.get("email"),
        "verification_notes": verification_notes
    }).eq("id", agent_id).execute()
    
    return {"success": True, "agent": result.data[0]}

@router.get("/runs")
async def list_discovery_runs(limit: int = 20):
    """List recent discovery runs with statistics"""
    from backend.config import supabase
    
    result = supabase.table("discovery_runs")\
        .select("*")\
        .order("started_at", desc=True)\
        .limit(limit)\
        .execute()
    
    return {"runs": result.data}

@router.get("/stats")
async def get_discovery_stats():
    """Get overall discovery statistics"""
    from backend.config import supabase
    
    # Total discovered
    total = supabase.table("discovered_agents")\
        .select("id", count="exact")\
        .execute()
    
    # Verified
    verified = supabase.table("discovered_agents")\
        .select("id", count="exact")\
        .eq("verified", True)\
        .execute()
    
    # Registered
    registered = supabase.table("discovered_agents")\
        .select("id", count="exact")\
        .eq("registered", True)\
        .execute()
    
    # By category
    by_category = supabase.rpc("get_agents_by_category").execute()
    
    return {
        "total_discovered": total.count,
        "verified": verified.count,
        "registered": registered.count,
        "by_category": by_category.data if hasattr(by_category, 'data') else []
    }
```

## Step 10: Update main.py

Add to your `backend/main.py`:

```python
# Import discovery routes
from backend.api import discovery_routes

# Initialize discovery system
from backend.agents.discovery_agent import AgentDiscoverySystem
from backend.llm.minimax_client import MiniMaxClient
from backend.tools.web_search import WebSearchTool

discovery_system = AgentDiscoverySystem(
    minimax_client=minimax_client,  # Your existing client
    tavily_client=WebSearchTool(),  # Your existing Tavily tool
    grok_api_key=settings.grok_api_key,
    firecrawl_api_key=settings.firecrawl_api_key,
    supabase_client=supabase
)

# Set system in routes
discovery_routes.discovery_system = discovery_system

# Register routes
app.include_router(discovery_routes.router)
```

## Step 11: Test Discovery Workflow

### Manual Test

Create `backend/test_discovery.py`:

```python
import asyncio
from backend.agents.discovery_agent import AgentDiscoverySystem
from backend.config import supabase, settings
from backend.llm.minimax_client import MiniMaxClient
from backend.tools.web_search import WebSearchTool

async def test_discovery():
    print("Initializing discovery system...")
    
    system = AgentDiscoverySystem(
        minimax_client=MiniMaxClient(settings.minimax_api_key),
        tavily_client=WebSearchTool(settings.tavily_api_key),
        grok_api_key=settings.grok_api_key,
        firecrawl_api_key=settings.firecrawl_api_key,
        supabase_client=supabase
    )
    
    print("Starting discovery run...")
    result = await system.discover(
        keywords=["LangChain agents"],
        max_results=10  # Small test
    )
    
    print(f"\nDiscovery {result['status']}")
    print(f"Grok results: {len(result['grok_results'])}")
    print(f"Filtered leads: {len(result['filtered_leads'])}")
    print(f"Classified agents: {len(result['classified_agents'])}")
    print(f"Stored agents: {len(result['agents_to_store'])}")
    print(f"\nThinking steps: {len(result['thinking_steps'])}")
    
    # Show first agent
    if result['agents_to_store']:
        agent = result['agents_to_store'][0]
        print(f"\nExample agent:")
        print(f"  Name: {agent['name']}")
        print(f"  Category: {agent['category']}")
        print(f"  Framework: {agent['framework']}")
        print(f"  Confidence: {agent['confidence_score']}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
```

Run test:
```bash
cd backend
python test_discovery.py
```

## Step 12: Set Up Scheduler (Optional)

Create `backend/scheduler.py`:

```python
import schedule
import time
import asyncio
from datetime import datetime
from backend.agents.discovery_agent import AgentDiscoverySystem
from backend.config import settings, supabase
# ... import your clients

def run_daily_discovery():
    """Daily discovery job"""
    print(f"[{datetime.now()}] Starting daily discovery...")
    
    system = AgentDiscoverySystem(
        minimax_client=your_minimax_client,
        tavily_client=your_tavily_client,
        grok_api_key=settings.grok_api_key,
        firecrawl_api_key=settings.firecrawl_api_key,
        supabase_client=supabase
    )
    
    result = asyncio.run(system.discover(
        keywords=None,  # Uses defaults
        max_results=50
    ))
    
    print(f"[{datetime.now()}] Discovery completed: {result['status']}")
    print(f"  Agents found: {len(result['classified_agents'])}")
    print(f"  Agents stored: {len(result['agents_to_store'])}")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(run_daily_discovery)

print("Scheduler started. Running daily at 2 AM...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

Run scheduler:
```bash
# In background or use systemd/supervisor
nohup python backend/scheduler.py &
```

## Step 13: Monitoring & Alerts

### Create Monitoring Script

`backend/monitor_discovery.py`:

```python
from backend.config import supabase
from datetime import datetime, timedelta

def check_discovery_health():
    """Check discovery system health"""
    
    # Check last successful run
    last_run = supabase.table("discovery_runs")\
        .select("*")\
        .eq("status", "completed")\
        .order("started_at", desc=True)\
        .limit(1)\
        .execute()
    
    if last_run.data:
        last_time = datetime.fromisoformat(last_run.data[0]["started_at"])
        hours_since = (datetime.utcnow() - last_time).total_seconds() / 3600
        
        if hours_since > 48:
            print(f"WARNING: No successful discovery in {hours_since:.1f} hours")
        else:
            print(f"OK: Last discovery {hours_since:.1f} hours ago")
    else:
        print("WARNING: No completed discovery runs found")
    
    # Check verification queue
    unverified = supabase.table("discovered_agents")\
        .select("id", count="exact")\
        .eq("verified", False)\
        .gte("confidence_score", 0.7)\
        .execute()
    
    print(f"Verification queue: {unverified.count} high-confidence agents")
    
    # Check outreach performance
    outreach = supabase.rpc("get_outreach_stats").execute()
    print(f"Outreach stats: {outreach.data}")

if __name__ == "__main__":
    check_discovery_health()
```

## Step 14: Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/discovery-scheduler.service`:

```ini
[Unit]
Description=Agent Discovery Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/aletheia-flux/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discovery-scheduler
sudo systemctl start discovery-scheduler
sudo systemctl status discovery-scheduler
```

### Using Docker (if containerized)

Add to your docker-compose.yml:

```yaml
services:
  discovery-scheduler:
    build: ./backend
    command: python scheduler.py
    environment:
      - GROK_API_KEY=${GROK_API_KEY}
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    restart: always
```

## Verification Checklist

After deployment, verify:

- [ ] Tools tested individually (Grok, Firecrawl)
- [ ] Database tables created
- [ ] Discovery agent runs successfully
- [ ] API endpoints responding
- [ ] Scheduler running (if enabled)
- [ ] Agents appearing in database
- [ ] Monitoring script works
- [ ] Cost tracking enabled

## Troubleshooting

### Discovery Not Finding Agents

1. Check API keys are valid
2. Verify search keywords are relevant
3. Review Grok search results
4. Check filtering logic
5. Increase confidence threshold

### High Costs

1. Reduce max_results
2. Cache Grok results longer
3. Skip Firecrawl for low-confidence leads
4. Use cheaper classification models
5. Reduce discovery frequency

### Database Errors

1. Verify schema migrated correctly
2. Check RLS policies (if using Supabase Auth)
3. Review connection limits
4. Check indexes created

## Next Steps

1. **Run First Discovery** - Start with small test (10 agents)
2. **Verify Results** - Manually check agent quality
3. **Tune Parameters** - Adjust confidence thresholds
4. **Enable Scheduling** - Set up daily runs
5. **Build Dashboard** - Visualize metrics
6. **Start Outreach** - Contact verified agents

---

**Support**: If you encounter issues, check:
1. Logs in `backend/logs/`
2. Discovery runs table for errors
3. API rate limits
4. Database connections
