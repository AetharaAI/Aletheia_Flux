# Aletheia Research Agent - Technical Architecture Documentation

## Overview

Aletheia is an enterprise-grade, truth-seeking research assistant built with a modern full-stack architecture. It features autonomous research capabilities with multi-step reasoning workflows, real-time web search integration, persistent conversation storage, and comprehensive source verification.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js)                      │
│                     Port 3001 | TypeScript                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  - Chat Interface with Sidebar                              │  │
│  │  - Real-time Message Streaming                              │  │
│  │  - Search Toggle (Web Search Enable/Disable)                │  │
│  │  - Conversation History (Persistent)                        │  │
│  │  - Thinking Trace Visualization                             │  │
│  │  - Source Citations                                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────┬───────────────────────────┘
                                      │ HTTP/REST + WebSocket
                                      │ Bearer Token Auth
┌─────────────────────────────────────┴───────────────────────────┐
│                         Backend (FastAPI)                        │
│                      Port 8001 | Python 3.10                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  - REST API Endpoints                                       │  │
│  │  - JWT Authentication (Supabase Compatible)                 │  │
│  │  - Research Agent Orchestration (LangGraph)                 │  │
│  │  - Web Search Integration (Tavily API)                      │  │
│  │  - LLM Integration (MiniMax-M2)                             │  │
│  │  - Rate Limiting & Error Handling                           │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────┬───────────────────────────┘
                                      │
                     ┌────────────────┼────────────────┐
                     │                │                │
        ┌────────────▼────────┐ ┌────▼────┐ ┌──────▼──────┐
        │   Supabase DB       │ │ Tavily  │ │ MiniMax-M2  │
        │  (PostgreSQL)       │ │  API    │ │     LLM     │
        │  - Conversations    │ │         │ │             │
        │  - Messages         │ │ Web     │ │ Text Gen +  │
        │  - Sources          │ │ Search  │ │ Reasoning   │
        │  - Thinking Traces  │ │         │ │             │
        └─────────────────────┘ └─────────┘ └─────────────┘
```

## Technology Stack

### Backend Stack
- **Framework**: FastAPI (Python 3.10+)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT with Supabase integration
- **Agent Orchestration**: LangGraph
- **Web Search**: Tavily API
- **LLM Provider**: MiniMax-M2
- **Caching/Rate Limiting**: Redis
- **Middleware**: Custom rate limiter, error handler, CORS

### Frontend Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **Auth**: Supabase Auth
- **HTTP Client**: Fetch API
- **UI Components**: Lucide React Icons

## Directory Structure

```
aletheia-research-agent/
├── backend/
│   ├── api/                      # API route handlers
│   │   ├── auth_routes.py        # Authentication endpoints
│   │   └── chat_routes.py        # Chat endpoints
│   ├── auth/                     # Authentication logic
│   │   └── jwt_handler.py        # JWT verification
│   ├── agents/                   # AI Agent implementations
│   │   └── research_agent.py     # LangGraph research workflow
│   ├── llm/                      # LLM client integrations
│   │   └── minimax_client.py     # MiniMax API client
│   ├── tools/                    # Tool implementations
│   │   ├── web_search.py         # Tavily web search
│   │   └── data_processor.py     # File processing
│   ├── middleware/               # FastAPI middleware
│   │   ├── rate_limiter.py       # Rate limiting
│   │   └── error_handler.py      # Error handling
│   ├── config.py                 # Configuration management
│   ├── main.py                   # FastAPI app entrypoint
│   └── .env                      # Environment variables
│
└── frontend/
    ├── app/                      # Next.js App Router
    │   ├── chat/page.tsx         # Main chat interface
    │   ├── login/page.tsx        # Login/signup page
    │   └── page.tsx              # Landing page
    ├── store/                    # State management
    │   └── chatStore.ts          # Zustand chat store
    ├── lib/                      # Utilities
    │   └── supabase.ts           # Supabase client
    └── .env.local                # Environment variables
```

## Core Components Deep Dive

### 1. Authentication System

**File**: `backend/auth/jwt_handler.py`

The authentication system supports both custom JWT tokens and Supabase tokens:

```python
def verify_token(credentials) -> dict:
    # 1. Try Supabase token first
    payload = jwt.decode(token, key=None, options={
        "verify_signature": False,
        "verify_aud": False,
        "verify_exp": False
    })

    # 2. Check for Supabase issuer
    if "supabase" in payload.get("iss", "").lower():
        return payload

    # 3. Fall back to custom JWT verification
    payload = jwt.decode(token, settings.jwt_secret_key)
    return payload
```

**Flow**:
1. Frontend authenticates via Supabase Auth
2. Receives Supabase access token (JWT)
3. Token sent in `Authorization: Bearer <token>` header
4. Backend verifies token using Supabase issuer claim
5. Extracts `sub` field as user ID
6. Uses user_id for all database operations

### 2. Research Agent Workflow

**File**: `backend/agents/research_agent.py`

LangGraph-based multi-step reasoning workflow:

```python
class ResearchAgent:
    async def reflect(self, state) -> AgentState
    async def search(self, state) -> AgentState      # Web search
    async def verify(self, state) -> AgentState      # Cross-verify sources
    async def synthesize(self, state) -> AgentState  # Generate response
    async def suggest(self, state) -> AgentState     # Follow-up questions
```

**Workflow**:
```
reflect → search → verify → synthesize → suggest
```

Each step adds thinking trace entries:
```python
thinking_steps.append({
    "step": len(thinking_steps) + 1,
    "action": "search",
    "description": "Found 5 sources",
    "confidence": 0.85
})
```

### 3. Web Search Integration

**File**: `backend/tools/web_search.py`

Uses Tavily API for real-time web search:

```python
class WebSearchTool:
    async def search(self, query: str, max_results: int = 5):
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False
        }
```

**Returns**:
```python
[{
    "title": "Article Title",
    "url": "https://...",
    "content": "Article content...",
    "score": 0.95
}]
```

### 4. Chat API Endpoints

**File**: `backend/api/chat_routes.py`

#### POST /api/chat/send

Main chat endpoint supporting research mode:

```python
async def send_message(request: ChatRequest):
    # 1. Get or create conversation
    if not request.conversation_id:
        conv_id = create_conversation()
    else:
        conv_id = request.conversation_id

    # 2. Save user message
    save_message(conv_id, "user", message)

    # 3. Get conversation history
    history = get_history(conv_id)

    # 4. Run research agent if search enabled
    if request.enable_search:
        result = await run_research_agent(message, history)
        response = result["response"]
        sources = result["sources"]
        thinking_trace = result["thinking_trace"]
    else:
        # Direct LLM call
        response = llm_client.generate(message)

    # 5. Save assistant response
    save_message(conv_id, "assistant", response, thinking_trace, sources)

    return ChatResponse(
        message_id=msg_id,
        response=response,
        sources=sources,
        thinking_trace=thinking_trace
    )
```

#### GET /api/chat/conversations

Lists all user conversations:

```python
async def get_conversations(user_id):
    result = supabase.table("conversations")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("updated_at", desc=True)\
        .execute()

    return {"conversations": result.data}
```

#### GET /api/chat/conversations/{conversation_id}

Gets specific conversation with all messages:

```python
async def get_conversation(conversation_id, user_id):
    # Verify ownership
    conv = verify_ownership(conversation_id, user_id)

    # Get messages
    messages = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("timestamp", desc=False)\
        .execute()

    return {
        "conversation": conv.data,
        "messages": messages.data
    }
```

### 5. Database Schema

**Supabase Tables**:

#### conversations
```sql
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key → auth.users)
- title: TEXT (First 50 chars of first message)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### messages
```sql
- id: UUID (Primary Key)
- conversation_id: UUID (Foreign Key → conversations)
- role: TEXT ('user' | 'assistant' | 'system')
- content: TEXT
- thinking_trace: JSONB
- sources: JSONB
- timestamp: TIMESTAMP
```

#### sources
```sql
- id: UUID (Primary Key)
- message_id: UUID (Foreign Key → messages)
- url: TEXT
- title: TEXT
- content: TEXT
- credibility_score: FLOAT
- created_at: TIMESTAMP
```

### 6. Frontend Chat Store

**File**: `frontend/store/chatStore.ts`

Zustand store managing chat state:

```typescript
interface ChatStore {
  conversations: Conversation[]
  currentConversationId: string | null
  messages: Message[]
  isStreaming: boolean
  searchEnabled: boolean
  sidebarOpen: boolean

  // Actions
  setConversations: (convs: Conversation[]) => void
  setCurrentConversation: (id: string | null) => void
  setMessages: (msgs: Message[]) => void
  addMessage: (msg: Message) => void
  toggleSearch: () => void
  toggleSidebar: () => void
}
```

**Persistence**: `searchEnabled` and `sidebarOpen` are persisted to localStorage

### 7. Frontend Chat Interface

**File**: `frontend/app/chat/page.tsx`

Main chat components:

#### Message Display
```typescript
messages.map((msg) => (
  <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
    <div className="max-w-[85%] rounded-lg p-4">
      <div className="markdown-content">{msg.content}</div>

      {msg.thinking_trace && msg.thinking_trace.length > 0 && (
        <details className="mt-4">
          <summary>Show reasoning ({msg.thinking_trace.length} steps)</summary>
          {msg.thinking_trace.map((step, idx) => (
            <div key={idx}>
              {idx + 1}. {step.description}
            </div>
          ))}
        </details>
      )}

      {msg.sources && msg.sources.length > 0 && (
        <div className="mt-4">
          {msg.sources.map((source, idx) => (
            <a key={idx} href={source.url} target="_blank">
              [{idx + 1}] {source.title}
            </a>
          ))}
        </div>
      )}
    </div>
  </div>
))
```

#### Search Toggle
```typescript
<button onClick={toggleSearch} className={
  searchEnabled
    ? "bg-accent-primary text-white"
    : "bg-bg-hover text-text-secondary"
}>
  <Search size={20} />
</button>

{searchEnabled && (
  <p>Web search enabled - responses will include verified sources</p>
)}
```

#### Conversation Sidebar
```typescript
<div className="space-y-2">
  {conversations.map((conv) => (
    <button key={conv.id} onClick={() => loadConversation(conv.id)}>
      <div>{conv.title}</div>
      <div>{new Date(conv.updated_at).toLocaleDateString()}</div>
    </button>
  ))}
</div>
```

## API Flow Examples

### Example 1: Send Message with Search Enabled

**Frontend Request**:
```typescript
const response = await fetch(`${API_URL}/api/chat/send`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${accessToken}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    message: "What's the latest in AI model updates?",
    enable_search: true,
    conversation_id: currentConversationId
  })
});

const data = await response.json();
// {
//   response: "The latest AI models include...",
//   sources: [{title: "...", url: "...", content: "..."}],
//   thinking_trace: [
//     {step: 1, action: "analyze", description: "...", confidence: 0.9},
//     {step: 2, action: "search", description: "Found 5 sources", confidence: 0.85},
//     {step: 3, action: "verify", description: "Verified 3/5 sources", confidence: 0.8},
//     {step: 4, action: "synthesize", description: "...", confidence: 0.95},
//     {step: 5, action: "suggest", description: "...", confidence: 0.8}
//   ]
// }
```

**Backend Processing**:
1. Verify Supabase JWT token
2. Extract user_id from token
3. Get or create conversation
4. Save user message
5. Check `enable_search` flag
6. Call `run_research_agent()`
7. Research agent calls Tavily API
8. Results synthesized by MiniMax-LLM
9. Save response with thinking_trace and sources
10. Return response

**Response Flow**:
1. Frontend receives response
2. Adds to local message store
3. Refreshes conversation list
4. Displays message with expandable thinking trace
5. Shows source citations

### Example 2: Load Conversation History

**Frontend Request**:
```typescript
const response = await fetch(`${API_URL}/api/chat/conversations/${id}`, {
  headers: {
    "Authorization": `Bearer ${accessToken}`
  }
});

const data = await response.json();
// {
//   conversation: {id, title, created_at, updated_at},
//   messages: [
//     {id, role: "user", content: "...", timestamp: "..."},
//     {id, role: "assistant", content: "...", thinking_trace: [...], sources: [...], timestamp: "..."}
//   ]
// }
```

**Frontend Display**:
1. Clear current messages
2. Set current conversation ID
3. Add each message to store
4. Messages render with thinking traces and sources
5. Sidebar highlights active conversation

## Environment Variables

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx

# JWT
JWT_SECRET_KEY=oaXXoG4b2F9oxo5mu2H7G0rOhI1DlCdS1qpeqQioT_8
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# APIs
MINIMAX_API_KEY=xxx
TAVILY_API_KEY=tvly-dev-xxx

# Redis
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

## Key Configuration

### CORS Configuration
**File**: `backend/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
**File**: `backend/middleware/rate_limiter.py`

- Uses Redis for distributed rate limiting
- 100 requests per minute per IP
- Returns 429 status code on limit exceeded

### Error Handling
**File**: `backend/middleware/error_handler.py`

- Sanitizes error messages
- Logs detailed errors to stderr
- Returns user-friendly error responses
- Prevents sensitive data exposure

## Security Considerations

### Authentication
- Supabase JWT tokens with RS256 algorithm
- Backend validates token signature and issuer
- Each request verified before processing
- User ID extracted from token `sub` claim

### Authorization
- All database queries filtered by `user_id`
- Ownership verified for conversation access
- No data leakage between users

### Input Validation
- All user input sanitized
- Message length validated (max 4000 chars)
- XSS prevention via input sanitization
- Rate limiting on all endpoints

### CORS
- Restricted to localhost origins
- Credentials allowed for authenticated requests
- Preflight requests handled correctly

## Deployment Architecture

### Development
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8001

# Frontend
cd frontend
npm run dev
```

### Production
- Backend: Deploy to cloud provider (AWS, GCP, Azure)
- Frontend: Build and deploy to Vercel/Netlify
- Database: Supabase (managed PostgreSQL)
- Redis: Managed Redis instance
- CDN: CloudFlare for static assets

### Environment Variables
- Use secure secret management (AWS Secrets Manager, etc.)
- Rotate API keys regularly
- Different keys for dev/staging/prod

## Monitoring & Observability

### Health Checks
- `GET /health` - Backend health status
- Returns JSON: `{"status": "healthy"}`

### Logging
- Backend logs to stdout/stderr
- Includes request/response info
- Error stack traces captured

### Metrics to Monitor
- Request rate per endpoint
- Response time percentiles
- Error rate (4xx, 5xx status codes)
- Auth failure rate
- Research agent success rate
- Web search API usage/costs

## Performance Considerations

### Database
- Messages table indexed on `conversation_id`
- Conversations indexed on `user_id` and `updated_at`
- Regular cleanup of old conversations
- Pagination for large message histories

### Caching
- Redis for rate limiting
- Potential: Cache search results
- Potential: Cache LLM responses

### API Optimization
- Streaming responses for long generations
- Async/await for all I/O operations
- Connection pooling for database
- HTTP keep-alive enabled

## Testing Strategy

### Unit Tests
- Test all API endpoints with pytest
- Test agent workflow independently
- Test LLM client mocking
- Test authentication flow

### Integration Tests
- Test frontend-backend integration
- Test Supabase database operations
- Test Web Search API integration

### E2E Tests
- Test complete user flows
- Test conversation persistence
- Test search-enabled responses

## Extensibility

### Adding New LLM Providers
1. Create new client in `backend/llm/`
2. Implement `generate_response()` method
3. Add provider selection to config
4. Update agent to use new client

### Adding New Tools
1. Create tool in `backend/tools/`
2. Implement tool interface
3. Integrate into agent workflow
4. Add thinking trace entries

### Custom Research Workflows
1. Extend LangGraph State
2. Add new workflow nodes
3. Define node connections
4. Test with various queries

## Known Limitations

1. **Single LLM Provider**: Currently hardcoded to MiniMax-M2
2. **No Streaming**: Responses are returned as single block
3. **No File Attachments**: UI exists but backend not fully implemented
4. **No Search History**: Past searches not saved
5. **No Export**: Cannot export conversation history
6. **No Multi-language**: Frontend/backend in English only

## Future Enhancements

### High Priority
- [ ] Add conversation export (PDF, Markdown)
- [ ] Implement streaming responses
- [ ] Add citation export
- [ ] Support for file attachments

### Medium Priority
- [ ] Multi-language support
- [ ] Custom research workflows
- [ ] Team/sharing features
- [ ] Advanced search filters

### Low Priority
- [ ] Mobile responsive design
- [ ] Dark/light theme toggle
- [ ] Custom system prompts
- [ ] API for programmatic access

## Troubleshooting

### Common Issues

**401 Unauthorized**
- Check Supabase token is valid
- Verify token not expired
- Check JWT secret key

**CORS Errors**
- Verify frontend origin in `main.py`
- Check OPTIONS requests succeed
- Ensure credentials flag set

**No Search Results**
- Verify TAVILY_API_KEY configured
- Check API quota not exceeded
- Review network requests

**Slow Responses**
- Check LLM API response time
- Review database query performance
- Monitor rate limiting

**Database Errors**
- Check Supabase connection
- Verify table schema matches code
- Review RLS policies

## References

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- Supabase: https://supabase.com/docs
- LangGraph: https://python.langchain.com/docs/langgraph
- Tavily API: https://docs.tavily.com/
- MiniMax API: https://platform.minimaxi.com/

### Related Projects
- LangChain: https://github.com/langchain-ai/langchain
- Zustand: https://github.com/pmndrs/zustand
- FastAPI Users: https://fastapi-users.github.io/

---

**Document Version**: 1.0
**Last Updated**: 2025-11-13
**Maintained By**: Aletheia Development Team
