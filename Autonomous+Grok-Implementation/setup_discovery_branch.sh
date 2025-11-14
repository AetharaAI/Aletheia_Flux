#!/bin/bash
# setup_discovery_branch.sh
# Automated setup for agent discovery system on a separate branch

set -e  # Exit on any error

echo "🚀 Agent Discovery System - Branch Setup"
echo "========================================"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this from your aletheia-flux root directory"
    exit 1
fi

# Check if aletheia-flux backend structure exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend/ directory not found"
    echo "Please run this from your aletheia-flux root directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "📍 Current branch: $(git branch --show-current)"
echo ""

# Ask for confirmation
read -p "This will create a new branch 'grok-discovery'. Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Store path to agent-discovery-system files
read -p "Enter path to extracted agent-discovery-system folder: " DISCOVERY_PATH

if [ ! -d "$DISCOVERY_PATH" ]; then
    echo "❌ Error: Directory not found: $DISCOVERY_PATH"
    exit 1
fi

echo ""
echo "✅ Found discovery system at: $DISCOVERY_PATH"
echo ""

# Create backup branch
echo "📦 Creating backup branch..."
BACKUP_BRANCH="backup-before-discovery-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BACKUP_BRANCH"
git push origin "$BACKUP_BRANCH" 2>/dev/null || echo "  (Backup created locally only)"
echo "  ✅ Backup branch: $BACKUP_BRANCH"
echo ""

# Go back to main
git checkout main
echo "📍 Switched back to main branch"
echo ""

# Create feature branch
echo "🌿 Creating grok-discovery branch..."
git checkout -b grok-discovery
echo "  ✅ Created and switched to grok-discovery"
echo ""

# Copy new files
echo "📁 Copying discovery system files..."

# Tools
echo "  → backend/tools/grok_search.py"
cp "$DISCOVERY_PATH/backend/tools/grok_search.py" backend/tools/

echo "  → backend/tools/firecrawl_scraper.py"
cp "$DISCOVERY_PATH/backend/tools/firecrawl_scraper.py" backend/tools/

# Agent
echo "  → backend/agents/discovery_agent.py"
cp "$DISCOVERY_PATH/backend/agents/discovery_agent.py" backend/agents/

# Database
echo "  → backend/database/discovery_schema.sql"
mkdir -p backend/database
cp "$DISCOVERY_PATH/backend/database/schema.sql" backend/database/discovery_schema.sql

# Documentation
echo "  → Copying documentation..."
cp "$DISCOVERY_PATH/README.md" docs/DISCOVERY_README.md 2>/dev/null || mkdir -p docs && cp "$DISCOVERY_PATH/README.md" docs/DISCOVERY_README.md
cp "$DISCOVERY_PATH/DEPLOYMENT.md" docs/DISCOVERY_DEPLOYMENT.md
cp "$DISCOVERY_PATH/IMPLEMENTATION.md" docs/DISCOVERY_IMPLEMENTATION.md

echo "  ✅ Files copied"
echo ""

# Create discovery config
echo "⚙️  Creating discovery configuration..."
mkdir -p backend/config

cat > backend/config/discovery_config.py << 'EOF'
"""
Agent Discovery System Configuration
Separate from main Aletheia config for clean separation
"""
import os
from typing import List, Dict

class DiscoveryConfig:
    """Configuration for the agent discovery system"""
    
    # API Keys (required)
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # Feature Flag
    ENABLED = os.getenv("DISCOVERY_ENABLED", "false").lower() == "true"
    
    # Discovery Settings
    MAX_RESULTS_PER_RUN = int(os.getenv("DISCOVERY_MAX_RESULTS", "50"))
    AUTO_VERIFY_THRESHOLD = float(os.getenv("DISCOVERY_AUTO_VERIFY_THRESHOLD", "0.9"))
    
    # Scheduling
    SCHEDULE_ENABLED = os.getenv("DISCOVERY_SCHEDULE_ENABLED", "false").lower() == "true"
    SCHEDULE_HOUR = int(os.getenv("DISCOVERY_SCHEDULE_HOUR", "2"))
    SCHEDULE_MINUTE = int(os.getenv("DISCOVERY_SCHEDULE_MINUTE", "0"))
    
    # Default Discovery Sources
    DISCOVERY_SOURCES = {
        "directories": [
            "https://github.com/topics/ai-agents",
            "https://huggingface.co/models",
            "https://www.langchain.com/",
            "https://www.crewai.com/",
            "https://autogpt.net/",
        ],
        "frameworks": [
            "https://python.langchain.com/docs",
            "https://docs.crewai.com/",
        ]
    }
    
    SEARCH_KEYWORDS = [
        "AI agent",
        "LangChain agent",
        "autonomous agent",
        "research agent",
        "coding agent"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.ENABLED:
            return True  # Config not needed if disabled
        
        if not cls.GROK_API_KEY:
            print("⚠️  Warning: GROK_API_KEY not set")
            return False
        
        if not cls.FIRECRAWL_API_KEY:
            print("⚠️  Warning: FIRECRAWL_API_KEY not set")
            return False
        
        return True

discovery_config = DiscoveryConfig()
EOF

echo "  ✅ Created backend/config/discovery_config.py"
echo ""

# Update requirements.txt
echo "📦 Updating requirements.txt..."
if [ -f requirements.txt ]; then
    echo "" >> requirements.txt
    echo "# Agent Discovery System Dependencies" >> requirements.txt
    cat "$DISCOVERY_PATH/requirements.txt" | grep -E "^(firecrawl|schedule|apscheduler)" >> requirements.txt
    echo "  ✅ Updated requirements.txt"
else
    echo "  ⚠️  requirements.txt not found, skipping"
fi
echo ""

# Create .env.example additions
echo "🔐 Creating .env additions..."
cat > .env.discovery.example << 'EOF'
# =============================================================================
# AGENT DISCOVERY SYSTEM
# =============================================================================

# Feature Flag - Set to true to enable discovery system
DISCOVERY_ENABLED=false

# API Keys (required when DISCOVERY_ENABLED=true)
GROK_API_KEY=your-grok-api-key-here          # Get from https://x.ai
FIRECRAWL_API_KEY=your-firecrawl-key-here    # Get from https://firecrawl.dev

# Discovery Settings
DISCOVERY_MAX_RESULTS=50
DISCOVERY_AUTO_VERIFY_THRESHOLD=0.9

# Scheduling (optional)
DISCOVERY_SCHEDULE_ENABLED=false
DISCOVERY_SCHEDULE_HOUR=2
DISCOVERY_SCHEDULE_MINUTE=0
EOF

echo "  ✅ Created .env.discovery.example"
echo "  ℹ️  Add these to your backend/.env file"
echo ""

# Stage all files
echo "📝 Staging files for commit..."
git add backend/tools/grok_search.py
git add backend/tools/firecrawl_scraper.py
git add backend/agents/discovery_agent.py
git add backend/database/discovery_schema.sql
git add backend/config/discovery_config.py
git add requirements.txt 2>/dev/null || true
git add docs/ 2>/dev/null || true
git add .env.discovery.example

echo "  ✅ Files staged"
echo ""

# Create commit
echo "💾 Creating commit..."
git commit -m "feat: Add agent discovery system

Components:
- Grok search tool for fast web discovery
- Firecrawl scraper for deep content extraction  
- Discovery agent with 7-phase workflow
- Database schema for discovered agents
- Configuration with feature flag (disabled by default)
- Documentation and deployment guides

Features:
- Autonomous agent discovery
- Structured data storage
- Outreach generation
- Conversion tracking

Integration:
- Extends Aletheia Flux without modifying existing code
- Feature flag controlled (DISCOVERY_ENABLED)
- Separate configuration and routes
- Independent database tables

Setup:
1. Add API keys to .env (see .env.discovery.example)
2. Run database migration (discovery_schema.sql)
3. Set DISCOVERY_ENABLED=true
4. Test with: POST /api/discovery/run

Docs: See docs/DISCOVERY_*.md for details"

echo "  ✅ Commit created"
echo ""

# Summary
echo "✨ Setup Complete!"
echo "=================="
echo ""
echo "📌 Current branch: $(git branch --show-current)"
echo "📌 Backup branch: $BACKUP_BRANCH"
echo ""
echo "Next steps:"
echo ""
echo "1. Get API keys:"
echo "   - Grok: https://x.ai"
echo "   - Firecrawl: https://firecrawl.dev"
echo ""
echo "2. Update backend/.env with keys from .env.discovery.example"
echo ""
echo "3. Run database migration:"
echo "   psql \$DATABASE_URL -f backend/database/discovery_schema.sql"
echo ""
echo "4. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "5. Test the discovery system:"
echo "   python backend/agents/discovery_agent.py"
echo ""
echo "6. Enable in production:"
echo "   Set DISCOVERY_ENABLED=true in .env"
echo ""
echo "7. When ready to merge:"
echo "   git checkout main"
echo "   git merge grok-discovery"
echo ""
echo "📚 Documentation:"
echo "   - Overview: docs/DISCOVERY_README.md"
echo "   - Deployment: docs/DISCOVERY_DEPLOYMENT.md"
echo "   - Technical: docs/DISCOVERY_IMPLEMENTATION.md"
echo ""
echo "🔄 To switch between branches:"
echo "   git checkout main          # Back to main (discovery disabled)"
echo "   git checkout grok-discovery  # Discovery features"
echo ""
echo "Happy discovering! 🚀"