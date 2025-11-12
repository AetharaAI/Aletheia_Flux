# Component Structure Plan - Aletheia Research & Data Wrangler

## 1. Application Overview

**Identity**: Aletheia (Greek concept of truth and disclosure) - truth-seeking, witty, rebellious against blandness

**Target Users**: Researchers, data analysts, developers (20-40) who spend hours in focused research and data work

**Core Purpose**: Conversational research interface with real-time web search, data wrangling, source verification, and agentic workflows with transparent thinking traces

**Design Style**: Dark Mode First - Bold, unapologetic dark interface optimized for power users and extended work sessions

---

## 2. Application Architecture

**Type**: Single Page Application (SPA) with dynamic chat interface

**Reasoning**: Chat applications require real-time updates, streaming responses, and persistent UI state. SPA architecture provides the responsive, fluid experience needed for conversational interfaces while maintaining chat history and context.

---

## 3. Component Hierarchy & Structure

### Layout Structure

```
App Root
├── TopBar (Fixed, global navigation)
├── MainLayout (Flex container)
│   ├── ChatSidebar (Collapsible, conversation history)
│   └── ChatContainer (Main content area)
│       ├── ChatMessages (Virtualized scroll container)
│       │   └── MessageBubble[] (Dynamic message list)
│       │       ├── UserMessage (Right-aligned, blue accent)
│       │       └── AssistantMessage (Left-aligned, neutral)
│       │           ├── MessageContent (Markdown, code blocks)
│       │           ├── Citations (Source links)
│       │           └── ThinkingTrace (Toggleable reasoning panel)
│       └── InputBar (Fixed bottom, auto-resize)
│           ├── FileUpload (CSV, PDF support)
│           ├── TextArea (Auto-growing input)
│           └── SearchToggle (Web search activation)
└── ThemeProvider (Dark/Light mode management)
```

---

## 4. Component Specifications

### Component 1: TopBar (`/route` equivalent: Global header)

**Purpose**: Global navigation, branding, user context, and theme control

**Component Pattern**: Fixed Navigation Pattern

**Content Mapping**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Branding | Logo + Text | Static | "Aletheia" wordmark + tagline | Logo icon (truth symbol) |
| Navigation | Nav Links | Static | "Research", "History", "Settings" | - |
| User Controls | Avatar + Menu | User context | User avatar, name, menu dropdown | User profile image |
| Theme Toggle | Icon Button | Theme state | Dark/light mode switcher | Sun/moon icons |

**Interaction States**:
- Default: Semi-transparent background with backdrop blur
- Scroll: Solid background with border when scrolled >50px
- Mobile: Hamburger menu for navigation collapse

---

### Component 2: ChatSidebar (`/route` equivalent: Sidebar panel)

**Purpose**: Conversation history, new chat creation, conversation management

**Component Pattern**: Sidebar Layout with Elevated Card List

**Content Mapping**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Header | Button Group | Static | "New Chat" CTA with glow effect | Plus icon |
| Conversation List | Virtualized List | IndexedDB/Supabase | Conversation titles, timestamps, preview text | - |
| Active Indicator | Accent Highlight | Active state | Border-left accent on selected conversation | - |
| Footer | Action Buttons | Static | Settings, Sign out | Settings icon, logout icon |

**Data Structure**:
```typescript
interface Conversation {
  id: string;
  title: string;
  preview: string; // First message excerpt
  timestamp: Date;
  messageCount: number;
  isActive: boolean;
}
```

**Interaction States**:
- Collapsed (Mobile): Hidden by default, slide-in overlay
- Expanded (Desktop): 280px fixed width sidebar
- Conversation hover: Background elevation change (#141414 → #1e1e1e)

---

### Component 3: ChatMessages (`/route` equivalent: Main chat area)

**Purpose**: Display conversation messages with virtualized scrolling for performance

**Component Pattern**: Virtualized Scroll Container with Message List

**Content Mapping**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Messages Container | Virtualized List | Chat state | Dynamic message array | - |
| User Messages | Right-aligned Bubble | User input | Text, files, timestamps | - |
| Assistant Messages | Left-aligned Bubble | Agent responses | Markdown, code, citations, thinking traces | - |
| Loading State | Typing Indicator | Streaming state | Animated dots or pulse | - |
| Empty State | Centered Card | Initial state | Welcome message, suggested prompts | Aletheia logo |

**Virtualization Strategy**:
- Use React Virtual or similar library for >100 messages
- Render buffer: 5 messages above/below viewport
- Maintain scroll position during streaming

---

### Component 4: MessageBubble (`/route` equivalent: Individual message component)

**Purpose**: Display individual messages with rich content, citations, and thinking traces

**Component Pattern**: Elevated Card with Nested Content Sections

**Content Mapping for User Messages**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Message Body | Text Block | User input | Plain text or formatted input | - |
| Attachments | File Preview | Uploaded files | CSV/PDF file names, sizes, icons | File type icons |
| Timestamp | Caption Text | Message metadata | Formatted time (e.g., "2:30 PM") | - |

**Content Mapping for Assistant Messages**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Message Content | Markdown Renderer | Agent response | Headers, lists, bold, italic, links | - |
| Code Blocks | Syntax Highlighter | Code content | Language-specific highlighting, copy button | Code icon |
| Citations | Link List | Source verification | Numbered source links, URLs, titles | External link icon |
| Thinking Trace | Collapsible Panel | Agent reasoning | Step-by-step thought process, confidence scores | Brain icon |
| Data Visualizations | Chart Embed | CSV analysis | Charts, tables, statistics | - |

**Data Structure**:
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: FileAttachment[];
  citations?: Citation[];
  thinkingTrace?: ThinkingStep[];
  isStreaming?: boolean;
}

interface Citation {
  id: string;
  title: string;
  url: string;
  snippet: string;
}

interface ThinkingStep {
  step: number;
  description: string;
  confidence: number;
}
```

**Visual States**:
- User Message: Right-aligned, blue accent background (#3b82f6), white text
- Assistant Message: Left-aligned, elevated dark surface (#141414), zinc-200 text
- Streaming: Animated gradient border on active message
- Thinking Trace Collapsed: Subtle indicator with "Show reasoning" text
- Thinking Trace Expanded: Full panel with step-by-step breakdown

---

### Component 5: InputBar (`/route` equivalent: Fixed bottom input area)

**Purpose**: User input with file upload, auto-resizing, and search toggle

**Component Pattern**: Fixed Bottom Bar with Auto-resize Textarea

**Content Mapping**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| File Upload | Icon Button | File input state | Upload icon, file count badge | Upload icon, file icons |
| Textarea | Auto-resize Input | User input | Multi-line text input (1-8 lines) | - |
| Search Toggle | Toggle Button | Search state | "Web Search" indicator (on/off) | Search icon with glow when active |
| Submit Button | Primary Button | Input state | Send icon or arrow | Send icon |

**Interaction States**:
- Default: 1 line height, gray border
- Typing: Auto-expand (max 8 lines), accent border glow
- File Attached: File preview chips above textarea
- Search Active: Search toggle glows with accent color
- Disabled: Gray out when assistant is responding

**Constraints**:
- Max height: 8 lines (~200px) before scroll
- Mobile: Full-width with 16px padding
- Desktop: Max-width 900px, centered

---

### Component 6: ThinkingTrace (Nested in MessageBubble)

**Purpose**: Display agent's reasoning process transparently

**Component Pattern**: Collapsible Panel with Step List

**Content Mapping**:

| Section | Component Pattern | Data Source | Content Elements | Visual Assets |
|---------|------------------|-------------|------------------|---------------|
| Trigger | Button/Link | Thinking data | "Show reasoning" / "Hide reasoning" toggle | Chevron icon |
| Steps Container | Ordered List | Thinking steps | Numbered steps with descriptions | - |
| Confidence Bars | Progress Indicators | Confidence scores | Visual bars showing certainty (0-100%) | - |
| Metadata | Caption Text | Trace metadata | Duration, tokens used, model info | - |

**Visual Treatment**:
- Background: Slightly darker than message (#0a0a0a)
- Border-left: 2px accent color stripe
- Steps: Subtle numbering with monospace font
- Animation: Smooth expand/collapse (300ms)

---

## 5. State Management Considerations

### Global State (Chat Context)

**Conversation State**:
- Current conversation ID
- Message array (user + assistant)
- Streaming status
- File attachments

**UI State**:
- Sidebar collapsed/expanded
- Theme (dark/light)
- Active conversation
- Input focus state

**Persistence**:
- IndexedDB: Chat history (offline-first)
- Supabase: Cloud sync, authentication
- Local Storage: Theme preference, UI preferences

### Component-Level State

**ChatMessages**:
- Scroll position
- Virtualization window
- Loading states

**InputBar**:
- Textarea value
- File uploads
- Search toggle state

**MessageBubble**:
- Thinking trace expanded/collapsed
- Code block copy state

---

## 6. Data Flow Patterns

### Message Streaming Flow

```
User Input → InputBar
  ↓
Submit → API Call (Supabase Edge Function)
  ↓
Streaming Response → WebSocket/SSE
  ↓
ChatMessages Update (Progressive)
  ↓
MessageBubble Renders (Partial Content)
  ↓
Complete → Final State + Citations
```

### File Upload Flow

```
User Selects File → InputBar
  ↓
Preview Display → File Chips
  ↓
Submit → Upload to Supabase Storage
  ↓
Process → Backend Analysis (CSV/PDF parsing)
  ↓
Return → Structured Data + Visualization
  ↓
MessageBubble → Display Results
```

### Citation Flow

```
Agent Response → Source URLs Detected
  ↓
Backend Verification → Fetch Metadata
  ↓
Return → Citation Objects
  ↓
MessageBubble → Numbered Links
  ↓
User Click → Open in New Tab
```

---

## 7. Responsive Behavior

### Desktop (≥1024px)
- Sidebar: 280px fixed width, always visible
- Chat: Centered, max-width 900px
- TopBar: Full navigation visible

### Tablet (768px - 1023px)
- Sidebar: Collapsible overlay
- Chat: Full-width with 24px padding
- TopBar: Condensed navigation

### Mobile (≤767px)
- Sidebar: Bottom sheet or slide-in overlay
- Chat: Full-width with 16px padding
- TopBar: Hamburger menu
- InputBar: Full-width, smaller buttons

---

## 8. Accessibility Considerations

**Keyboard Navigation**:
- Tab through messages, input, buttons
- Enter to submit, Shift+Enter for new line
- Arrow keys to navigate conversation history

**Screen Readers**:
- Semantic HTML (nav, main, article for messages)
- ARIA labels for icon buttons
- Live regions for streaming messages

**Focus States**:
- Visible focus rings with accent color
- Skip to main content link
- Focus trap in modals (if any)

**Color Contrast**:
- All text ≥7:1 contrast (WCAG AAA)
- Interactive elements clearly distinguishable
- Accent colors tested against backgrounds

---

## 9. Performance Optimization

**Virtualization**:
- Render only visible messages (5 buffer above/below)
- Lazy load conversation history

**Code Splitting**:
- Lazy load syntax highlighter
- Lazy load chart libraries
- Separate bundles for PDF/CSV processors

**Image Optimization**:
- Lazy load user avatars
- WebP format with fallback
- Responsive image sizes

**Caching**:
- Cache API responses
- Service worker for offline support
- IndexedDB for chat persistence

---

## 10. Content Analysis

**Information Density**: High
- Chat applications have dynamic, high-volume content (100+ messages)
- Real-time streaming requires responsive rendering
- Complex nested components (markdown, code, citations, thinking traces)

**Content Balance**:
- Text: 70% (conversational content, markdown)
- Data/Charts: 20% (CSV analysis, visualizations)
- Interactive Elements: 10% (buttons, toggles, inputs)
- Content Type: Mixed (text-heavy with data-driven components)

**Interaction Intensity**: Very High
- Continuous user input and streaming responses
- Real-time state updates
- File uploads and processing
- Toggle states (thinking traces, search, sidebar)
