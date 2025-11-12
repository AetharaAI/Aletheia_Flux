# Aletheia Research & Data Wrangler Agent

A production-ready, full-stack AI research assistant built with truth-seeking personality and transparent reasoning.

## Overview

**Aletheia** (Greek: ἀλήθεια - "truth" or "disclosure") is an advanced research agent that combines:
- Real-time web search with source verification
- Transparent AI reasoning (thinking traces visible to users)
- Data wrangling capabilities (CSV/PDF processing)
- Agent-based orchestration using LangGraph
- Dark-mode-first, professional UI

## Architecture

### Backend (FastAPI + Python)
- **FastAPI 0.109+**: High-performance async API server
- **LangGraph 0.2+**: Agent orchestration with StateGraph workflow
- **MiniMax-M2 API**: Advanced language model integration via Anthropic SDK
- **Tavily API**: Web search with source verification
- **Supabase**: PostgreSQL database + authentication + storage
- **Redis**: Session caching and rate limiting
- **Celery**: Async task queue for background processing

### Frontend (Next.js 14 + TypeScript)
- **Next.js 14 App Router**: Modern React framework with Server Components
- **Tailwind CSS 3.4+**: Utility-first CSS with custom design tokens
- **TanStack Query v5**: Data fetching and caching
- **Zustand 4.5+**: Lightweight state management
- **Dexie.js 4.0**: IndexedDB for offline chat persistence
- **Lucide React**: SVG icon library

## Features

### 1. Conversational Research Interface
- Real-time streaming responses
- Message history with conversation management
- Auto-resizing textarea input
- File upload support (CSV, PDF)
- Web search toggle

### 2. Agent Orchestration Workflow
```
User Query → Reflect → Search → Verify → Synthesize → Suggest
```
- **Reflect**: Analyze query and plan approach
- **Search**: Perform web search (2-5 sources via Tavily API)
- **Verify**: Cross-verify sources for accessibility
- **Synthesize**: Generate comprehensive response with LLM
- **Suggest**: Provide 2-3 follow-up questions

### 3. Thinking Traces
- Visible AI reasoning process
- Step-by-step thought breakdown
- Confidence scores for each step
- Collapsible UI component

### 4. Source Verification
- Cross-check claims across 2+ sources
- Credibility scoring
- Citation system with numbered references
- External link indicators

### 5. Data Processing
- CSV file analysis with insights
- PDF text extraction
- Automated pattern detection
- Data visualization (ready for integration)

### 6. Security & Performance
- JWT authentication (access + refresh tokens)
- Input sanitization (OWASP compliance via bleach)
- Rate limiting (20 req/min per IP)
- CORS configuration
- WCAG AAA accessibility compliance
- Virtualized scrolling for large message lists

## Project Structure

```
aletheia-research-agent/
├── backend/
│   ├── agents/
│   │   └── research_agent.py          # LangGraph agent workflow
│   ├── api/
│   │   ├── auth_routes.py             # Authentication endpoints
│   │   └── chat_routes.py             # Chat API endpoints
│   ├── auth/
│   │   └── jwt_handler.py             # JWT token management
│   ├── llm/
│   │   └── minimax_client.py          # MiniMax-M2 API client
│   ├── middleware/
│   │   ├── error_handler.py           # Global error handling
│   │   └── rate_limiter.py            # Rate limiting
│   ├── tools/
│   │   ├── data_processor.py          # CSV/PDF processing
│   │   └── web_search.py              # Tavily API integration
│   ├── config.py                      # Configuration management
│   ├── main.py                        # FastAPI application
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx               # Main chat interface
│   │   ├── globals.css                # Global styles
│   │   ├── layout.tsx                 # Root layout with providers
│   │   └── page.tsx                   # Landing page
│   ├── components/
│   │   └── providers/
│   │       └── QueryProvider.tsx      # TanStack Query setup
│   ├── lib/
│   │   └── supabase.ts                # Supabase client
│   ├── store/
│   │   └── chatStore.ts               # Zustand state management
│   ├── .env.local                     # Environment variables
│   ├── package.json
│   └── tailwind.config.ts             # Tailwind with design tokens
│
├── docs/
│   ├── component-structure-plan.md    # Component architecture
│   ├── design-specification.md        # Design system (2,850 words)
│   └── design-tokens.json             # Design tokens (356 lines)
│
└── README.md
```

## Database Schema

### Tables
- **users**: User profiles (extends Supabase Auth)
- **conversations**: Chat conversations
- **messages**: Chat messages with thinking traces
- **sources**: Verified sources with credibility scores
- **search_queries**: Search query history
- **file_uploads**: Uploaded files with processing results

### Storage
- **aletheia-files**: 50MB file size limit, supports CSV/PDF

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+ (Supabase)
- Redis 7.2+

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment** (`.env`):
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# API Keys (REQUIRED for full functionality)
MINIMAX_API_KEY=your_minimax_api_key
TAVILY_API_KEY=your_tavily_api_key

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your_secret_key_change_this
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
```

3. **Run the server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
pnpm install
```

2. **Configure environment** (`.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run development server**:
```bash
pnpm dev
```

4. **Build for production**:
```bash
pnpm build
pnpm start
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user
- `POST /api/auth/signin` - Sign in user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/signout` - Sign out user
- `GET /api/auth/me` - Get current user

### Chat
- `POST /api/chat/send` - Send message (non-streaming)
- `POST /api/chat/stream` - Send message (streaming)
- `POST /api/chat/upload` - Upload file (CSV/PDF)
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation messages
- `DELETE /api/chat/conversations/{id}` - Delete conversation

## Design System

### Color Palette (Dark Mode First)
- **Background**: Pure blacks (#000, #0A0A0A) for OLED optimization
- **Elevation**: Layered grays (#141414, #1E1E1E, #282828)
- **Text**: High-contrast zinc colors (15.2:1 ratio, WCAG AAA)
- **Accents**: Electric blue (#3B82F6), cyan (#06B6D4)
- **Glow Effects**: Box shadows instead of traditional shadows

### Typography
- **Primary**: Inter (UI, body text)
- **Monospace**: JetBrains Mono (code, thinking traces)
- **Sizes**: 12px - 40px with optimal line heights

### Components
- **Buttons**: Glow effects on hover, 48px touch targets
- **Cards**: Elevated surfaces with subtle borders
- **MessageBubble**: Rounded corners with role-based styling
- **ThinkingTrace**: Collapsible panel with confidence indicators

## API Key Configuration

### Required APIs

1. **MiniMax API**
   - Sign up at: https://api.minimax.io
   - Model: `claude-3-5-sonnet-20241022` (MiniMax-M2)
   - Base URL: `https://api.minimax.io/anthropic`

2. **Tavily API**
   - Sign up at: https://tavily.com
   - Search depth: "advanced" for research quality
   - Max results: 5 sources per query

### Fallback Behavior
- Without MINIMAX_API_KEY: Basic responses without LLM enhancement
- Without TAVILY_API_KEY: Mock search results with warning message
- Frontend displays clear instructions for setup

## Testing

### Backend Tests (pytest)
```bash
cd backend
pytest tests/
```

### Frontend Tests (Jest + RTL)
```bash
cd frontend
pnpm test
```

### Integration Tests
```bash
# Start both servers
cd backend && uvicorn main:app &
cd frontend && pnpm dev &

# Run e2e tests
pnpm test:e2e
```

## Performance Targets

- **Latency**: <2s end-to-end response time
- **Concurrent Users**: 500+ via Redis caching
- **Message Rendering**: Virtualized for 1000+ messages
- **Code Splitting**: Heavy components lazy-loaded

## Accessibility

- **WCAG AAA Compliance**: All text 7:1+ contrast
- **Keyboard Navigation**: Full support with shortcuts
- **Screen Readers**: Semantic HTML with ARIA labels
- **Focus Management**: Visible focus rings, skip links
- **Reduced Motion**: Respects prefers-reduced-motion

## Production Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
  
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
```

### Environment Variables Checklist
- [ ] SUPABASE_URL
- [ ] SUPABASE_ANON_KEY
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] MINIMAX_API_KEY (required for LLM)
- [ ] TAVILY_API_KEY (required for search)
- [ ] JWT_SECRET_KEY (generate secure random string)
- [ ] REDIS_URL
- [ ] NEXT_PUBLIC_SUPABASE_URL
- [ ] NEXT_PUBLIC_SUPABASE_ANON_KEY
- [ ] NEXT_PUBLIC_API_URL

## License

MIT License - see LICENSE file for details

## Credits

- **Design Inspiration**: Vercel, Linear, GitHub, Cursor IDE, Raycast
- **LLM**: MiniMax-M2 via Anthropic SDK
- **Search**: Tavily API
- **Database**: Supabase (PostgreSQL + Auth + Storage)

---

**Note**: This application requires valid API credentials (MINIMAX_API_KEY, TAVILY_API_KEY) for full functionality. The system will operate in degraded mode with clear user feedback when credentials are missing.
