# Agent Discovery System - Implementation Guide

## Overview
Extending Aletheia Flux into a specialized AI Agent Discovery System by adding:
- Grok integration for fast web sweeps
- Firecrawl for deep content extraction
- Agent-specific classification logic
- Structured agent database schema
- Automated outreach generation

## Architecture Extension

```
┌─────────────────────────────────────────────────────────────────┐
│              Agent Discovery System (Extended)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    ┌────────────────────────────────────────────────┐
    │         Aletheia Flux Core (Existing)          │
    │  - MiniMax M2 (Intelligence)                   │
    │  - Tavily (Deep Research)                      │
    │  - LangGraph (Workflow)                        │
    │  - Supabase (Storage)                          │
    └────────────────────────────────────────────────┘
                              ↓
    ┌────────────────────────────────────────────────┐
    │            New Components Added                │
    │  - Grok (Fast Web Sweep)                       │
    │  - Firecrawl (Content Extraction)              │
    │  - Agent Classifier (ML Classification)        │
    │  - Outreach Generator (Contact Automation)     │
    └────────────────────────────────────────────────┘
```

## Component Details

### 1. Grok Integration
**File**: `backend/tools/grok_search.py`

Fast web search for initial discovery sweep.

**Purpose**:
- Quick scanning of large web spaces
- Find agent-related pages rapidly
- Low-cost bulk discovery

**API**:
```python
class GrokSearchTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
    
    async def search(
        self, 
        query: str, 
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fast web search using Grok
        
        Returns:
        [{
            "title": str,
            "url": str,
            "snippet": str,
            "relevance_score": float
        }]
        """
        # Implementation uses Grok's native web search
        pass
```

### 2. Firecrawl Integration
**File**: `backend/tools/firecrawl_scraper.py`

Deep content extraction from discovered pages.

**Purpose**:
- Extract full page content
- Parse structured data (GitHub, docs, etc.)
- Handle JavaScript-heavy sites
- Extract contact information

**API**:
```python
class FirecrawlTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
    
    async def scrape(
        self,
        url: str,
        extract_contacts: bool = True,
        include_markdown: bool = True
    ) -> Dict:
        """
        Scrape full content from URL
        
        Returns:
        {
            "markdown": str,
            "html": str,
            "metadata": {
                "title": str,
                "description": str,
                "og_image": str
            },
            "contacts": {
                "emails": List[str],
                "social": List[str],
                "github": str
            }
        }
        """
        pass
    
    async def crawl_site(
        self,
        base_url: str,
        max_pages: int = 10
    ) -> List[Dict]:
        """
        Crawl multiple pages from a site
        """
        pass
```

### 3. Agent Discovery Workflow
**File**: `backend/agents/discovery_agent.py`

Extends ResearchAgent with agent-specific discovery logic.

**Workflow**:
```
┌─────────────┐
│   Initialize│
│   Discovery │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Grok Sweep   │  ← Fast search across target sources
│ (Bulk Find)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Filter &     │  ← MiniMax classifies relevance
│ Classify     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Tavily Deep  │  ← Research promising leads
│ Research     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Firecrawl    │  ← Extract full details
│ Extraction   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ MiniMax      │  ← Structure and classify
│ Analysis     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Store in DB  │  ← Save to Supabase
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Generate     │  ← Prepare outreach
│ Outreach     │
└──────────────┘
```

**State Schema**:
```python
class DiscoveryState(TypedDict):
    # Input
    search_targets: List[str]  # Sources to search
    keywords: List[str]        # Search terms
    
    # Discovery
    grok_results: List[Dict]   # Initial sweep results
    filtered_leads: List[Dict] # Classified as relevant
    
    # Research
    tavily_research: List[Dict]  # Deep research results
    scraped_content: List[Dict]  # Full page content
    
    # Analysis
    classified_agents: List[Dict] # Structured agent data
    
    # Output
    agents_to_store: List[Dict]   # Ready for database
    outreach_list: List[Dict]     # Contact information
    
    # Metadata
    thinking_steps: List[Dict]
    sources: List[Dict]
```

### 4. Agent Classification Logic
**File**: `backend/agents/classifier.py`

Uses MiniMax to structure unstructured agent data.

**Prompt Template**:
```python
CLASSIFICATION_PROMPT = """
You are an AI agent classifier. Given information about a potential AI agent,
extract structured data.

INPUT:
{raw_data}

EXTRACT:
1. Agent Name
2. Description (1-2 sentences)
3. Primary Capabilities (list)
4. Framework (LangChain, CrewAI, Custom, etc.)
5. Category (productivity, development, creative, automation, research)
6. Tags (list of keywords)
7. Endpoint URL (if available)
8. Contact Information (email, GitHub, Twitter)
9. Status (active, inactive, unknown)
10. Confidence Score (0-1)

Return as JSON:
{
  "name": "",
  "description": "",
  "capabilities": [],
  "framework": "",
  "category": "",
  "tags": [],
  "endpoint_url": "",
  "contacts": {
    "email": "",
    "github": "",
    "twitter": ""
  },
  "status": "",
  "confidence": 0.0
}

If information is missing, use null. Be conservative with confidence scores.
"""
```

### 5. Database Schema Extension
**File**: `backend/database/schema.sql`

New tables for discovered agents:

```sql
-- Discovered agents (before manual verification)
CREATE TABLE discovered_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    
    -- Classification
    framework VARCHAR(100),
    category VARCHAR(100),
    tags TEXT[],
    capabilities JSONB,
    
    -- Technical
    endpoint_url VARCHAR(500),
    source_url VARCHAR(500) NOT NULL,
    documentation_url VARCHAR(500),
    
    -- Contacts
    contact_email VARCHAR(255),
    github_url VARCHAR(500),
    twitter_handle VARCHAR(100),
    
    -- Discovery Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    discovered_by VARCHAR(50) DEFAULT 'grok_sweep',
    confidence_score DECIMAL(3,2),
    
    -- Verification Status
    verified BOOLEAN DEFAULT FALSE,
    verification_notes TEXT,
    
    -- Source Data
    raw_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Outreach tracking
CREATE TABLE agent_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES discovered_agents(id),
    
    -- Contact Details
    contact_method VARCHAR(50), -- 'email', 'twitter', 'github'
    contact_address VARCHAR(255),
    
    -- Outreach
    outreach_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'replied', 'registered'
    message_template TEXT,
    personalization_data JSONB,
    
    -- Tracking
    sent_at TIMESTAMP,
    replied_at TIMESTAMP,
    registered_at TIMESTAMP,
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Discovery runs (batches)
CREATE TABLE discovery_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Run Info
    run_type VARCHAR(50), -- 'scheduled', 'manual', 'targeted'
    target_sources TEXT[],
    keywords TEXT[],
    
    -- Results
    agents_found INTEGER DEFAULT 0,
    agents_classified INTEGER DEFAULT 0,
    agents_stored INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed'
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Metadata
    thinking_trace JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_discovered_agents_category ON discovered_agents(category);
CREATE INDEX idx_discovered_agents_verified ON discovered_agents(verified);
CREATE INDEX idx_discovered_agents_confidence ON discovered_agents(confidence_score DESC);
CREATE INDEX idx_agent_outreach_status ON agent_outreach(outreach_status);
CREATE INDEX idx_discovery_runs_status ON discovery_runs(status);
```

### 6. Discovery Targets
**File**: `backend/config/discovery_sources.py`

Predefined sources to search:

```python
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
    
    "social": [
        "twitter.com/search?q=AI%20agent%20launch",
        "twitter.com/search?q=LangChain%20agent",
        "twitter.com/search?q=autonomous%20agent",
    ],
    
    "frameworks": [
        "https://python.langchain.com/docs/use_cases/agents",
        "https://docs.crewai.com/",
        "https://www.langflow.org/",
        "https://github.com/Significant-Gravitas/AutoGPT",
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
    "LangGraph workflow",
    
    # Use case specific
    "research agent",
    "coding agent",
    "data analysis agent",
    "automation agent",
    
    # Recent
    "new AI agent 2025",
    "agent launch",
    "agent release"
]
```

### 7. Outreach Generator
**File**: `backend/tools/outreach_generator.py`

Generates personalized outreach messages.

```python
class OutreachGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def generate_message(
        self,
        agent_data: Dict,
        template: str = "standard"
    ) -> str:
        """
        Generate personalized outreach message
        """
        
        prompt = f"""
        Generate a professional, personalized outreach email to the creator
        of this AI agent, inviting them to register on AetherPro.tech.
        
        AGENT INFO:
        - Name: {agent_data['name']}
        - Description: {agent_data['description']}
        - Framework: {agent_data['framework']}
        - Category: {agent_data['category']}
        
        REQUIREMENTS:
        - Friendly, not salesy
        - Acknowledge their specific work
        - Explain AetherPro as infrastructure (like DNS for agents)
        - Keep it under 150 words
        - Include clear CTA
        
        EMAIL:
        """
        
        message = await self.llm.generate(prompt)
        return message
```

## Implementation Steps

### Phase 1: Add New Tools (Week 1)
1. Install dependencies:
```bash
pip install firecrawl-py grok-client
```

2. Add environment variables:
```bash
# .env
GROK_API_KEY=xxx
FIRECRAWL_API_KEY=xxx
```

3. Create tool files:
- `backend/tools/grok_search.py`
- `backend/tools/firecrawl_scraper.py`

### Phase 2: Extend Database (Week 1)
1. Run SQL migrations
2. Create Supabase tables
3. Set up indexes
4. Test database operations

### Phase 3: Build Discovery Agent (Week 2)
1. Create `backend/agents/discovery_agent.py`
2. Extend LangGraph workflow
3. Implement classification logic
4. Add thinking trace entries
5. Test with sample data

### Phase 4: API Endpoints (Week 2)
1. Add discovery routes:
```python
# backend/api/discovery_routes.py
POST /api/discovery/run       # Start discovery run
GET  /api/discovery/runs       # List runs
GET  /api/discovery/runs/{id}  # Get run details
GET  /api/discovery/agents     # List discovered agents
POST /api/discovery/verify     # Mark agent as verified
POST /api/discovery/outreach   # Generate outreach
```

### Phase 5: Frontend Integration (Week 3)
1. Add discovery dashboard
2. Display discovered agents
3. Verification interface
4. Outreach management
5. Run history

### Phase 6: Automation (Week 4)
1. Set up cron jobs:
```python
# Schedule daily discovery runs
schedule.every().day.at("02:00").do(run_discovery)

# Weekly comprehensive sweep
schedule.every().monday.at("00:00").do(run_comprehensive_sweep)
```

2. Email integration for outreach
3. Response tracking
4. Registration conversion tracking

## Usage Examples

### Manual Discovery Run
```python
# Run discovery on specific sources
result = await discovery_agent.run({
    "search_targets": ["github.com/topics/ai-agents"],
    "keywords": ["LangChain agent", "autonomous agent"],
    "max_results": 50
})

print(f"Found {len(result['agents_to_store'])} agents")
```

### Scheduled Discovery
```python
# config/scheduler.py
import schedule
import time

def daily_discovery():
    discovery_agent.run({
        "search_targets": DISCOVERY_SOURCES["directories"],
        "keywords": SEARCH_KEYWORDS[:5],  # Top 5 keywords
        "max_results": 20
    })

schedule.every().day.at("02:00").do(daily_discovery)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Generate Outreach
```python
# Get uncontacted agents
agents = supabase.table("discovered_agents")\
    .select("*")\
    .eq("verified", True)\
    .is_("contacted_at", None)\
    .execute()

for agent in agents.data:
    message = await outreach_generator.generate_message(agent)
    
    # Store outreach record
    supabase.table("agent_outreach").insert({
        "agent_id": agent["id"],
        "contact_method": "email",
        "contact_address": agent["contact_email"],
        "message_template": message,
        "outreach_status": "pending"
    }).execute()
```

## Monitoring & Metrics

### Key Metrics to Track
1. **Discovery Efficiency**
   - Agents found per run
   - Relevance rate (how many are actual agents)
   - Duplicate rate

2. **Classification Accuracy**
   - Confidence score distribution
   - Manual verification rate
   - Classification errors

3. **Outreach Performance**
   - Response rate
   - Registration conversion rate
   - Time to response

4. **System Health**
   - API usage (Grok, Tavily, Firecrawl)
   - Discovery run duration
   - Error rates

### Dashboard Metrics
```python
# Get metrics for dashboard
metrics = {
    "total_discovered": count_discovered_agents(),
    "verified": count_verified_agents(),
    "contacted": count_contacted_agents(),
    "registered": count_registered_agents(),
    "last_run": get_last_discovery_run(),
    "pending_outreach": count_pending_outreach()
}
```

## Cost Estimation

### API Costs (Monthly)
- **Grok**: $0.01 per search × 1000 searches = $10
- **Tavily**: $0.25 per search × 500 searches = $125
- **Firecrawl**: $0.02 per page × 2000 pages = $40
- **MiniMax**: $0.0001 per token × 10M tokens = $1000
- **Total**: ~$1,175/month

### Optimization Strategies
1. Cache Grok results (7 days)
2. Rate limit Tavily to high-confidence leads only
3. Batch Firecrawl requests
4. Use MiniMax only for classification (not generation)

## Next Steps

After implementation:
1. **Registry Integration**: Auto-populate AetherPro registry
2. **Quality Control**: Human-in-the-loop verification
3. **Outreach Automation**: Email/DM automation
4. **Analytics Dashboard**: Track ecosystem growth
5. **API Access**: Let others contribute discoveries

---

**Ready to start building?** Next steps:
1. Install dependencies
2. Add Grok + Firecrawl tools
3. Extend database schema
4. Build discovery agent
5. Test with sample run
