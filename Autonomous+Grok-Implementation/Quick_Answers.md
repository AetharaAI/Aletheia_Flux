# Quick Answers to Your Questions

## Question 1: Can I still use this for general research?

### Short Answer
**YES!** The discovery agent is completely separate. Your existing research agent works exactly as before.

### How It Works
```
Your Aletheia Flux:
├── Research Agent (EXISTING) ✅
│   └── Use for ANY research topic
│   └── Quantum computing, history, science, etc.
│   └── Unchanged, works exactly as before
│
└── Discovery Agent (NEW) ✅
    └── ONLY for finding AI agents
    └── Runs independently
    └── Can be enabled/disabled via flag
```

### Usage

**General Research** (unchanged):
```bash
# Your existing endpoints work as always
POST /api/chat/send
{
  "message": "Explain quantum computing",
  "enable_search": true
}
# Uses: MiniMax + Tavily
# No discovery code touched
```

**Agent Discovery** (new):
```bash
# New endpoint for agent discovery only
POST /api/discovery/run
{
  "keywords": ["LangChain agents"],
  "max_results": 50
}
# Uses: MiniMax + Tavily + Grok + Firecrawl
# Separate workflow
```

### They Don't Interfere
- **Different files**: `research_agent.py` vs `discovery_agent.py`
- **Different databases**: `conversations` vs `discovered_agents`
- **Different routes**: `/api/chat/*` vs `/api/discovery/*`
- **Feature flag**: Discovery disabled by default (`DISCOVERY_ENABLED=false`)

---

## Question 2: Git Branching Strategy

### Short Answer
Use the included setup script! It does everything automatically.

### Automated Setup

```bash
# From your aletheia-flux directory
bash /path/to/agent-discovery-system/setup_discovery_branch.sh

# Follow the prompts:
# 1. Confirms you're in right directory
# 2. Creates backup branch (safety)
# 3. Creates grok-discovery branch
# 4. Copies all files
# 5. Creates config with feature flag
# 6. Commits everything
```

**What the script does:**
1. ✅ Creates backup branch (just in case)
2. ✅ Creates `grok-discovery` feature branch
3. ✅ Copies all discovery files
4. ✅ Creates feature flag config (disabled by default)
5. ✅ Updates requirements.txt
6. ✅ Stages and commits everything
7. ✅ Gives you next steps

### Manual Alternative

If you prefer manual control:

```bash
cd /path/to/aletheia-flux

# 1. Create feature branch
git checkout -b grok-discovery

# 2. Copy files
cp agent-discovery-system/backend/tools/*.py backend/tools/
cp agent-discovery-system/backend/agents/discovery_agent.py backend/agents/
cp agent-discovery-system/backend/database/schema.sql backend/database/discovery_schema.sql

# 3. Commit
git add .
git commit -m "feat: Add agent discovery system (disabled by default)"

# 4. Test before merging
DISCOVERY_ENABLED=true python backend/main.py

# 5. Merge when ready
git checkout main
git merge grok-discovery
```

### Branch Workflow

```
main (production, always stable)
  │
  └─→ grok-discovery (development)
      │
      ├─ Work here
      ├─ Test thoroughly
      └─ Merge to main when ready
```

**Switch between branches:**
```bash
# Work on discovery
git checkout grok-discovery

# Back to stable main
git checkout main

# The feature flag means discovery is off by default
# So main stays stable even after merge
```

---

## TL;DR

### Question 1: Research Agent
✅ **Still works!** Discovery is separate. Feature flag means it's disabled by default.

### Question 2: Branching
✅ **Use the script!** `bash setup_discovery_branch.sh` does everything.

Or manually:
```bash
git checkout -b grok-discovery
# copy files
git commit -m "feat: Add discovery (off by default)"
```

---

## Feature Flag Safety

The discovery system is **disabled by default**:

```bash
# In .env
DISCOVERY_ENABLED=false  # Safe, nothing loads

# When you're ready
DISCOVERY_ENABLED=true   # Enables discovery
```

**This means:**
- Merge to main anytime without risk
- Discovery code doesn't load unless you enable it
- Research agent works regardless
- No performance impact when disabled

---

## Next Steps

1. **Run the setup script** (easiest):
   ```bash
   bash agent-discovery-system/setup_discovery_branch.sh
   ```

2. **Get API keys**:
   - Grok: https://x.ai
   - Firecrawl: https://firecrawl.dev

3. **Add to .env**:
   ```bash
   DISCOVERY_ENABLED=true
   GROK_API_KEY=...
   FIRECRAWL_API_KEY=...
   ```

4. **Test discovery**:
   ```bash
   python backend/agents/discovery_agent.py
   ```

5. **Keep using research as normal**:
   ```bash
   # Your existing frontend/API works unchanged
   ```

---

**Both systems coexist perfectly. They're built to work together, not replace each other.** 🚀