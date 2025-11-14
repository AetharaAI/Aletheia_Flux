# Dual-Use Setup & Branching Strategy

## Question 1: Can I Still Use This for General Research?

**YES! Absolutely.** The discovery agent is just an **extension** of your Aletheia Flux research agent, not a replacement.

### How It Works

You have **two agents** that share the same infrastructure:

```
Aletheia Flux Infrastructure (Shared)
├── MiniMax M2 (LLM)
├── Tavily (Web Search)
├── LangGraph (Workflow)
├── Supabase (Database)
└── FastAPI (API)
    │
    ├─→ Research Agent (EXISTING)
    │   └── General research queries
    │   └── Academic research
    │   └── Any topic research
    │
    └─→ Discovery Agent (NEW)
        └── AI agent discovery only
        └── Autonomous scheduled runs
        └── Specialized workflow
```

### Two Ways to Run Research

#### Option 1: Keep Both Separate (Recommended)

**For General Research** - Use your existing Aletheia interface:
```python
# Your existing research_agent.py (unchanged)
from backend.agents.research_agent import ResearchAgent

agent = ResearchAgent()
result = await agent.run("Research quantum computing trends")
# Uses: MiniMax + Tavily only
# No Grok, no Firecrawl, no agent-specific logic
```

**For Agent Discovery** - Use the new discovery agent:
```python
# New discovery_agent.py
from backend.agents.discovery_agent import AgentDiscoverySystem

discovery = AgentDiscoverySystem(...)
result = await discovery.discover(keywords=["LangChain agents"])
# Uses: MiniMax + Tavily + Grok + Firecrawl
# Agent-specific workflow
```

#### Option 2: Unified Interface with Mode Selection

Create a wrapper that routes to the right agent:

```python
# backend/agents/unified_agent.py

class UnifiedAgent:
    def __init__(self, minimax, tavily, grok, firecrawl, supabase):
        self.research_agent = ResearchAgent(minimax, tavily)
        self.discovery_agent = AgentDiscoverySystem(
            minimax, tavily, grok, firecrawl, supabase
        )
    
    async def run(self, query: str, mode: str = "research"):
        """
        Unified interface for both agents
        
        Args:
            query: User query
            mode: 'research' (general) or 'discovery' (agent discovery)
        """
        if mode == "discovery":
            # Parse query for keywords
            keywords = self._extract_keywords(query)
            return await self.discovery_agent.discover(keywords=keywords)
        else:
            # General research
            return await self.research_agent.run(query)
```

**Usage:**
```python
# General research (uses existing agent)
result = await unified.run(
    "What are the latest developments in quantum computing?",
    mode="research"
)

# Agent discovery (uses new agent)
result = await unified.run(
    "Find AI agents for research and data analysis",
    mode="discovery"
)
```

### API Endpoint Example

Add to your existing chat routes:

```python
# backend/api/chat_routes.py

@router.post("/api/chat/send")
async def send_message(request: ChatRequest):
    # Detect if this is an agent discovery query
    is_discovery_query = (
        "find agents" in request.message.lower() or
        "discover agents" in request.message.lower() or
        request.mode == "discovery"  # Explicit mode
    )
    
    if is_discovery_query:
        # Use discovery agent
        result = await discovery_agent.discover(...)
    else:
        # Use regular research agent (EXISTING)
        result = await research_agent.run(...)
    
    return result
```

### Frontend Toggle

Add a mode selector to your UI:

```tsx
// frontend/app/chat/page.tsx

const [mode, setMode] = useState<'research' | 'discovery'>('research');

<div className="mode-selector">
  <button 
    onClick={() => setMode('research')}
    className={mode === 'research' ? 'active' : ''}
  >
    General Research
  </button>
  <button 
    onClick={() => setMode('discovery')}
    className={mode === 'discovery' ? 'active' : ''}
  >
    Agent Discovery
  </button>
</div>

// Send with mode
fetch('/api/chat/send', {
  method: 'POST',
  body: JSON.stringify({
    message: query,
    mode: mode,  // 'research' or 'discovery'
    enable_search: true
  })
})
```

### Database Separation

Your databases are already separate:

**Existing (Research)**
- `conversations` - General research chats
- `messages` - Research responses
- `sources` - Research citations

**New (Discovery)**
- `discovered_agents` - Found AI agents
- `agent_outreach` - Outreach tracking
- `discovery_runs` - Discovery batches

No overlap, no conflicts.

---

## Question 2: Git Branching Strategy

**Great idea!** Here's the recommended branching approach:

### Branching Strategy

```
main (Production - Stable Aletheia Flux)
├─→ development (Active development)
├─→ grok-discovery (Feature branch for agent discovery)
└─→ hotfix/* (Emergency fixes)
```

### Step-by-Step Setup

#### 1. Initial Backup

```bash
cd /path/to/aletheia-flux

# Make sure you're on main and it's clean
git checkout main
git status

# Create a backup branch (just in case)
git checkout -b backup-before-discovery
git push origin backup-before-discovery

# Back to main
git checkout main
```

#### 2. Create Feature Branch

```bash
# Create and switch to discovery feature branch
git checkout -b grok-discovery

# Verify you're on the new branch
git branch
# Should show: * grok-discovery
```

#### 3. Add Discovery Files

```bash
# Copy new files from the zip
cp /path/to/agent-discovery-system/backend/tools/grok_search.py backend/tools/
cp /path/to/agent-discovery-system/backend/tools/firecrawl_scraper.py backend/tools/
cp /path/to/agent-discovery-system/backend/agents/discovery_agent.py backend/agents/

# Copy database migration
cp /path/to/agent-discovery-system/backend/database/schema.sql backend/database/discovery_schema.sql

# Add new dependencies
cat /path/to/agent-discovery-system/requirements.txt >> requirements.txt

# Stage files
git add backend/tools/grok_search.py
git add backend/tools/firecrawl_scraper.py
git add backend/agents/discovery_agent.py
git add backend/database/discovery_schema.sql
git add requirements.txt

# Commit
git commit -m "feat: Add agent discovery system

- Add Grok search tool for fast web discovery
- Add Firecrawl scraper for deep content extraction
- Add discovery agent workflow (7-phase)
- Add database schema for discovered agents
- Add new dependencies (firecrawl, schedule)

Extends Aletheia Flux without modifying existing research agent."
```

#### 4. Create Discovery Configuration

```bash
# Create config file for discovery-specific settings
cat > backend/config/discovery_config.py << 'EOF'
"""
Discovery System Configuration
Separate from main Aletheia config to keep concerns isolated
"""
import os
from typing import List

class DiscoveryConfig:
    # API Keys
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # Discovery Settings
    ENABLED = os.getenv("DISCOVERY_ENABLED", "false").lower() == "true"
    MAX_RESULTS_PER_RUN = int(os.getenv("DISCOVERY_MAX_RESULTS", "50"))
    AUTO_VERIFY_THRESHOLD = float(os.getenv("DISCOVERY_AUTO_VERIFY_THRESHOLD", "0.9"))
    
    # Scheduling
    SCHEDULE_ENABLED = os.getenv("DISCOVERY_SCHEDULE_ENABLED", "false").lower() == "true"
    SCHEDULE_HOUR = int(os.getenv("DISCOVERY_SCHEDULE_HOUR", "2"))
    
    # Default sources
    DISCOVERY_SOURCES = {
        "directories": [
            "https://github.com/topics/ai-agents",
            "https://huggingface.co/models",
        ],
        "frameworks": [
            "https://python.langchain.com/docs",
            "https://docs.crewai.com/",
        ]
    }
    
    SEARCH_KEYWORDS = [
        "AI agent",
        "LangChain agent",
        "research agent",
        "autonomous agent"
    ]

discovery_config = DiscoveryConfig()
EOF

git add backend/config/discovery_config.py
git commit -m "feat: Add discovery-specific configuration

Keeps discovery settings separate from main Aletheia config"
```

#### 5. Create Feature Flag

Add feature flag to control discovery system:

```python
# backend/config.py (modify existing)

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Discovery System (NEW)
    discovery_enabled: bool = False
    grok_api_key: Optional[str] = None
    firecrawl_api_key: Optional[str] = None
```

Update `.env`:
```bash
# Add to backend/.env
DISCOVERY_ENABLED=false  # Set to true when ready
GROK_API_KEY=your-key-here
FIRECRAWL_API_KEY=your-key-here
```

#### 6. Conditional Initialization in main.py

```python
# backend/main.py

from backend.config import settings

# Existing research agent (ALWAYS loaded)
from backend.agents.research_agent import ResearchAgent
research_agent = ResearchAgent(...)

# Discovery agent (CONDITIONAL)
if settings.discovery_enabled:
    from backend.agents.discovery_agent import AgentDiscoverySystem
    from backend.tools.grok_search import GrokSearchTool
    from backend.tools.firecrawl_scraper import FirecrawlTool
    
    discovery_system = AgentDiscoverySystem(
        minimax_client=minimax_client,
        tavily_client=tavily_client,
        grok_api_key=settings.grok_api_key,
        firecrawl_api_key=settings.firecrawl_api_key,
        supabase_client=supabase
    )
    
    # Register discovery routes
    from backend.api import discovery_routes
    discovery_routes.discovery_system = discovery_system
    app.include_router(discovery_routes.router)
    
    print("✅ Discovery system enabled")
else:
    print("ℹ️  Discovery system disabled (set DISCOVERY_ENABLED=true to enable)")
```

Commit:
```bash
git add backend/main.py backend/config.py backend/.env.example
git commit -m "feat: Add feature flag for discovery system

Discovery system only loads when DISCOVERY_ENABLED=true
Existing research agent always works regardless"
```

#### 7. Push Feature Branch

```bash
# Push to remote
git push origin grok-discovery

# Or if you're the only one working on this
git push -u origin grok-discovery
```

### Workflow

#### Development Workflow

```bash
# Work on discovery features
git checkout grok-discovery

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat: improve agent classification accuracy"

# Push
git push origin grok-discovery
```

#### Testing Before Merge

```bash
# On grok-discovery branch
DISCOVERY_ENABLED=true python backend/main.py

# Test discovery
curl -X POST http://localhost:8001/api/discovery/run \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"keywords": ["test agent"], "max_results": 5}'

# Test that regular research still works
curl -X POST http://localhost:8001/api/chat/send \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "What is quantum computing?"}'
```

#### Merging to Main

```bash
# Switch to main
git checkout main

# Merge feature branch
git merge grok-discovery

# Or use pull request if using GitHub/GitLab

# Push to main
git push origin main
```

#### Keeping Branches in Sync

```bash
# On grok-discovery branch
git checkout grok-discovery

# Pull latest from main
git merge main

# Or rebase (cleaner history)
git rebase main

# Resolve conflicts if any
# Then push
git push origin grok-discovery
```

### Branch Protection

If you want to be extra careful:

```bash
# Never work directly on main
# Always create feature branches

# For discovery work
git checkout -b grok-discovery

# For other features
git checkout -b feature/new-ui
git checkout -b fix/tavily-timeout
git checkout -b refactor/database-queries
```

### Rollback Strategy

If discovery system causes issues:

```bash
# Quick disable via environment
DISCOVERY_ENABLED=false

# Or revert the merge
git checkout main
git revert -m 1 <merge-commit-hash>

# Or hard reset (dangerous!)
git reset --hard <commit-before-merge>
```

### Recommended Structure

```
main (always deployable)
│
├─→ development (integration branch)
│   │
│   ├─→ grok-discovery (your current work)
│   ├─→ feature/improved-classification
│   └─→ feature/outreach-automation
│
└─→ hotfix/* (emergency fixes to production)
```

**Workflow:**
1. Create feature branch from `development`
2. Develop and test
3. Merge to `development`
4. Test integration
5. Merge `development` to `main` when stable

---

## Summary

### Question 1: Can I still use for general research?
**YES!** Two approaches:

1. **Separate agents** (easiest)
   - Keep using research_agent.py for general research
   - Use discovery_agent.py only for agent discovery
   - No conflicts, clean separation

2. **Unified interface** (advanced)
   - Add mode parameter to chat
   - Routes to correct agent based on query/mode
   - Single UI, dual functionality

### Question 2: Branching strategy?
**Recommended:**

```bash
# Create feature branch
git checkout -b grok-discovery

# Add all discovery files
git add backend/tools/grok_search.py
git add backend/tools/firecrawl_scraper.py
git add backend/agents/discovery_agent.py
git commit -m "feat: Add agent discovery system"

# Add feature flag
DISCOVERY_ENABLED=false  # Default off

# Test thoroughly on branch

# Merge when ready
git checkout main
git merge grok-discovery
```

**This way:**
- Main branch stays stable
- Discovery features isolated
- Easy to enable/disable
- Easy to rollback if needed
- General research unaffected

---

Want me to create a script that sets up the branching and feature flag for you?