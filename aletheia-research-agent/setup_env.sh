# Backend .env configuration
cd /workspace/aletheia-research-agent/backend && cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://gueamdcmzgcngfzfbisx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1ZWFtZGNtemdjbmdmemZiaXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMTk5MDQsImV4cCI6MjA3Nzc5NTkwNH0.JptDEKXiuBz-9ppN9i4buQP2F8IHzjoHxIMLHG8TmaA
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1ZWFtZGNtemdjbmdmemZiaXN4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjIxOTkwNCwiZXhwIjoyMDc3Nzk1OTA0fQ.l83MjNCnXWDSwZ_3UpFCJ9RueaBfkPFWT0HcYQ0R_Kk

# MiniMax API (Required - configure to enable LLM)
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimax.io/anthropic

# Tavily Search API (Required - configure to enable web search)
TAVILY_API_KEY=your_tavily_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=aletheia_secret_key_change_this_in_production_2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20

# Environment
ENVIRONMENT=development
EOF
