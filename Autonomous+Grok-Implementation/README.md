# Agent Discovery System

**Extends Aletheia Flux into an autonomous AI agent discovery and outreach system**

Built on top of your existing Aletheia Flux research agent, this system autonomously:
- Discovers AI agents across the web
- Classifies and structures agent data
- Stores in a searchable registry
- Generates personalized outreach
- Tracks registration conversions

## What's New

### Added Components
1. **Grok Integration** - Fast web search for bulk discovery
2. **Firecrawl Integration** - Deep content extraction and scraping
3. **Discovery Agent** - Multi-phase agent discovery workflow
4. **Extended Database** - Tables for discovered agents, outreach, and runs
5. **Automated Scheduling** - Daily discovery runs

### Architecture Extension

```
Aletheia Flux (Base)                 Agent Discovery (Extension)
─────────────────────                ──────────────────────────
MiniMax M2 (LLM)          →          Agent Classification
Tavily (Research)         →          Deep Research on Leads
LangGraph (Workflow)      →          Discovery Workflow
Supabase (Database)       →          Extended Schema
                                     + Grok (Fast Search)
                                     + Firecrawl (Scraping)
```

## Discovery Workflow

```
1. Grok Sweep          → Fast bulk discovery (20 results per keyword)
2. Filter & Classify   → MiniMax relevance scoring (keep 60%+)
3. Tavily Research     → Deep research on top leads
4. Firecrawl Extract   → Full content & contact extraction
5. MiniMax Analysis    → Structure and classify data
6. Store Results       → Save to Supabase
7. Generate Outreach   → Personalized messages
```

## Quick Start

### Prerequisites
- Python 3.10+
- Existing Aletheia Flux installation
- API Keys:
  - MiniMax (existing)
  - Tavily (existing)
  - **Grok** (new - from x.ai)
  - **Firecrawl** (new - from firecrawl.dev)

### Installation

1. **Install dependencies**
```bash
cd backend
pip install -r ../requirements.txt
```

2. **Add environment variables**
```bash
# Add to backend/.env
GROK_API_KEY=your-grok-key
FIRECRAWL_API_KEY=your-firecrawl-key
```

3. **Run database migrations**
```bash
# Connect to Supabase and run:
psql $DATABASE_URL < backend/database/schema.sql
```

4. **Test the tools**
```bash
python backend/tools/grok_search.py
python backend/tools/firecrawl_scraper.py
```

### Running Discovery

#### Manual Run
```python
from backend.agents.discovery_agent import AgentDiscoverySystem

# Initialize
system = AgentDiscoverySystem(
    minimax_client=your_minimax_client,
    tavily_client=your_tavily_client,
    grok_api_key=os.getenv("GROK_API_KEY"),
    firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY"),
    supabase_client=your_supabase_client
)

# Run discovery
result = await system.discover(
    keywords=["LangChain agents", "research agents"],
    max_results=50
)

print(f"Found {len(result['classified_agents'])} agents")
```

#### Scheduled Run
```python
import schedule
import time

def daily_discovery():
    result = asyncio.run(system.discover(
        keywords=["AI agent", "LangChain agent", "autonomous agent"],
        max_results=50
    ))
    print(f"Discovery run completed: {result['status']}")

# Run every day at 2 AM
schedule.every().day.at("02:00").do(daily_discovery)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## API Integration

### Add Discovery Endpoints

Create `backend/api/discovery_routes.py`:

```python
from fastapi import APIRouter, Depends
from backend.agents.discovery_agent import AgentDiscoverySystem

router = APIRouter(prefix="/api/discovery", tags=["discovery"])

@router.post("/run")
async def start_discovery_run(
    keywords: List[str] = None,
    max_results: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Start a new discovery run"""
    result = await discovery_system.discover(
        keywords=keywords,
        max_results=max_results
    )
    return result

@router.get("/agents")
async def list_discovered_agents(
    verified: bool = None,
    category: str = None,
    limit: int = 50
):
    """List discovered agents"""
    query = supabase.table("discovered_agents").select("*")
    
    if verified is not None:
        query = query.eq("verified", verified)
    if category:
        query = query.eq("category", category)
    
    result = query.limit(limit).order("confidence_score", desc=True).execute()
    return {"agents": result.data}

@router.post("/agents/{agent_id}/verify")
async def verify_agent(
    agent_id: str,
    verification_notes: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Mark agent as verified"""
    result = supabase.table("discovered_agents").update({
        "verified": True,
        "verified_at": datetime.utcnow().isoformat(),
        "verified_by": current_user["email"],
        "verification_notes": verification_notes
    }).eq("id", agent_id).execute()
    
    return {"success": True, "agent": result.data[0]}

@router.get("/runs")
async def list_discovery_runs(limit: int = 20):
    """List recent discovery runs"""
    result = supabase.table("discovery_runs")\
        .select("*")\
        .order("started_at", desc=True)\
        .limit(limit)\
        .execute()
    
    return {"runs": result.data}

@router.get("/stats")
async def get_discovery_stats():
    """Get overall discovery statistics"""
    stats = {
        "total_discovered": supabase.table("discovered_agents").select("count").execute().count,
        "verified": supabase.table("discovered_agents").select("count").eq("verified", True).execute().count,
        "registered": supabase.table("discovered_agents").select("count").eq("registered", True).execute().count,
    }
    return stats
```

Register in `backend/main.py`:
```python
from backend.api import discovery_routes

app.include_router(discovery_routes.router)
```

## Database Schema

### New Tables

1. **discovered_agents** - Stores discovered AI agents
2. **agent_outreach** - Tracks outreach attempts and responses
3. **discovery_runs** - Logs each discovery run
4. **agent_verification_queue** - Manual verification workflow
5. **agent_categories** - Reference data for categories

### Key Views

- `unverified_high_confidence_agents` - Agents needing verification
- `agents_ready_for_outreach` - Verified agents to contact
- `discovery_run_stats` - Daily run statistics
- `outreach_performance` - Conversion metrics

## Configuration

### Discovery Sources

Edit `backend/config/discovery_sources.py`:

```python
DISCOVERY_SOURCES = {
    "directories": [
        "https://github.com/topics/ai-agents",
        "https://huggingface.co/models",
        # Add more sources
    ],
    "frameworks": [
        "https://python.langchain.com/docs",
        "https://docs.crewai.com/",
        # Add more frameworks
    ]
}

SEARCH_KEYWORDS = [
    "AI agent",
    "LangChain agent",
    "research agent",
    # Add more keywords
]
```

### Outreach Templates

Customize outreach generation in `discovery_agent.py`:

```python
async def _generate_outreach(self, state: DiscoveryState) -> DiscoveryState:
    # Modify the prompt to match your tone/brand
    prompt = f"""
    Generate outreach email...
    
    YOUR CUSTOM INSTRUCTIONS HERE
    """
```

## Cost Management

### Estimated Monthly Costs (50 agents/day)

| Service | Cost per Unit | Monthly Usage | Monthly Cost |
|---------|--------------|---------------|--------------|
| Grok | $0.01/search | ~1,000 searches | $10 |
| Tavily | $0.25/search | ~500 searches | $125 |
| Firecrawl | $0.02/page | ~2,000 pages | $40 |
| MiniMax | $0.0001/token | ~10M tokens | $1,000 |
| **Total** | | | **~$1,175** |

### Cost Optimization

1. **Cache Grok results** (7 days TTL)
2. **Filter before Tavily** (only high-confidence leads)
3. **Batch Firecrawl requests** (10 at a time)
4. **Use cheaper models for classification** (MiniMax is already cheap)

## Monitoring

### Key Metrics

Dashboard should show:
- Agents discovered today/week/month
- Verification rate (verified / discovered)
- Outreach response rate
- Registration conversion rate
- API costs per run
- Discovery run duration

### Logging

All runs logged to `discovery_runs` table with:
- Full thinking trace
- API call counts
- Cost estimates
- Performance metrics

## Integration with AetherPro Registry

Once agents are verified, automatically register them:

```python
async def promote_to_registry(agent_id: str):
    """Promote discovered agent to main AetherPro registry"""
    
    # Get verified agent
    agent = supabase.table("discovered_agents")\
        .select("*")\
        .eq("id", agent_id)\
        .eq("verified", True)\
        .single()\
        .execute()
    
    # Create registry entry
    registry_agent = {
        "name": agent.data["name"],
        "subdirectory_slug": agent.data["slug"],
        "description": agent.data["description"],
        "capabilities": agent.data["capabilities"],
        "framework": agent.data["framework"],
        "category": agent.data["category"],
        "tags": agent.data["tags"],
        "endpoint_url": agent.data["endpoint_url"],
        "verified": True,
        "source": "discovery_system"
    }
    
    result = supabase.table("agents").insert(registry_agent).execute()
    
    # Update discovered agent
    supabase.table("discovered_agents").update({
        "registered": True,
        "registered_at": datetime.utcnow().isoformat(),
        "aetherpro_agent_id": result.data[0]["id"]
    }).eq("id", agent_id).execute()
```

## Next Steps

### Week 1: Setup & Test
- [ ] Install dependencies
- [ ] Get API keys (Grok, Firecrawl)
- [ ] Run database migrations
- [ ] Test tools individually
- [ ] Run first manual discovery

### Week 2: Integration
- [ ] Add discovery routes to API
- [ ] Build verification UI
- [ ] Test full workflow
- [ ] Set up monitoring

### Week 3: Automation
- [ ] Deploy scheduler
- [ ] Configure daily runs
- [ ] Set up alerts
- [ ] Monitor costs

### Week 4: Outreach
- [ ] Verify first batch
- [ ] Send outreach emails
- [ ] Track responses
- [ ] Iterate on messaging

## Troubleshooting

### Common Issues

**Grok API errors**
- Check API key is valid
- Verify rate limits not exceeded
- Try reducing max_results

**Firecrawl timeouts**
- Increase timeout in scraper
- Skip problematic URLs
- Use crawl for multiple pages

**Low confidence scores**
- Adjust classification prompt
- Add more context to searches
- Improve filtering logic

**Duplicate agents**
- Check URL deduplication
- Add name fuzzy matching
- Review classification logic

## Support

- GitHub Issues: [Link to repo]
- Documentation: [Link to docs]
- Email: support@aetherpro.tech

---

**Built on Aletheia Flux** - Your existing research agent powers the intelligence behind agent discovery. This extension just adds specialized tools and workflows for finding and onboarding AI agents to the AetherPro ecosystem.
