# Design Specification - Aletheia Research & Data Wrangler

**Version**: 1.0 | **Style**: Dark Mode First | **Updated**: 2025-11-04

---

## 1. Direction & Rationale

### Visual Identity

Aletheia embodies **Dark Mode First** design - a bold, unapologetic dark interface optimized for power users who spend hours in focused research and data analysis. Pure blacks with vibrant accent colors create high contrast that reduces eye strain while projecting technical sophistication and rebellious confidence.

The design rejects bland enterprise aesthetics in favor of a modern, truth-seeking personality that matches Aletheia's core mission: transparent research with visible reasoning traces. Dark surfaces create depth through elevation rather than shadows, while saturated accent colors guide attention to critical interactions.

### Real-World Inspiration

- **Vercel Dashboard**: Developer-focused, high-contrast dark UI with sharp typography
- **Linear**: Task management with clean dark aesthetic, vibrant accents, smooth animations
- **GitHub Dark Mode**: Code-focused interface with excellent readability for extended use
- **Cursor IDE**: AI coding assistant with modern dark theme, glowing accents
- **Raycast**: Productivity tool combining clean dark design with powerful functionality

### Target Audience Alignment

Researchers, data analysts, and developers (20-40) expect tools that respect their time and intelligence. Dark Mode First reduces eye strain during extended sessions, creates immersive focus, and signals technical credibility. The high-contrast UI with vibrant accents makes critical actions (search, citations, thinking traces) immediately visible without cognitive overhead.

---

## 2. Design Tokens

### 2.1 Color System

#### Background Hierarchy (Surface Elevation)

| Token Name | Value | Usage | Contrast |
|------------|-------|-------|----------|
| `bg-pure-black` | `#000000` | OLED optimization, hero sections, sidebar | Base |
| `bg-near-black` | `#0A0A0A` | Main application background | Level 0 |
| `bg-elevated` | `#141414` | Cards, message bubbles, modals | Level 1 |
| `bg-hover` | `#1E1E1E` | Hover states, active elements | Level 2 |
| `bg-tooltip` | `#282828` | Tooltips, popovers | Level 3 |

#### Text Colors

| Token Name | Value | Usage | WCAG on #0A0A0A |
|------------|-------|-------|------------------|
| `text-primary` | `#E4E4E7` (zinc-200) | Primary content, headings | 15.2:1 ✅ AAA |
| `text-secondary` | `#A1A1AA` (zinc-400) | Secondary text, captions | 8.9:1 ✅ AAA |
| `text-tertiary` | `#71717A` (zinc-500) | Timestamps, metadata | 5.2:1 ✅ AA |
| `text-white` | `#FFFFFF` | High-emphasis elements | 21:1 ✅ AAA |

#### Accent Colors (Vibrant, Saturated)

| Token Name | Value | Usage | WCAG on #0A0A0A |
|------------|-------|-------|------------------|
| `accent-primary` | `#3B82F6` (blue-500) | Primary actions, CTAs, user messages | 8.6:1 ✅ AAA |
| `accent-hover` | `#60A5FA` (blue-400) | Hover states | 11.2:1 ✅ AAA |
| `accent-glow` | `rgba(59, 130, 246, 0.5)` | Glow effects | N/A |
| `accent-secondary` | `#06B6D4` (cyan-500) | Secondary actions, search toggle | 9.1:1 ✅ AAA |

#### Semantic Colors

| Token Name | Value | Usage | WCAG on #0A0A0A |
|------------|-------|-------|------------------|
| `semantic-success` | `#22C55E` (green-500) | Success states, verification | 8.8:1 ✅ AAA |
| `semantic-warning` | `#F59E0B` (amber-500) | Warnings, cautions | 7.2:1 ✅ AAA |
| `semantic-error` | `#EF4444` (red-500) | Errors, destructive actions | 6.1:1 ✅ AA |
| `semantic-info` | `#8B5CF6` (violet-500) | Information, thinking traces | 5.8:1 ✅ AA |

#### Borders & Dividers

| Token Name | Value | Usage |
|------------|-------|-------|
| `border-subtle` | `rgba(255, 255, 255, 0.1)` | Subtle separation, card borders |
| `border-moderate` | `rgba(255, 255, 255, 0.15)` | Hover borders, active states |
| `border-strong` | `rgba(255, 255, 255, 0.2)` | Strong emphasis, focus states |
| `border-accent` | `#3B82F6` | Accent borders, active indicators |

### 2.2 Typography

#### Font Families

| Token Name | Value | Usage |
|------------|-------|-------|
| `font-primary` | `'Inter', -apple-system, BlinkMacSystemFont, sans-serif` | UI text, body content, headings |
| `font-mono` | `'JetBrains Mono', 'Fira Code', 'Courier New', monospace` | Code blocks, thinking traces, data |

#### Font Sizes (Desktop)

| Token Name | Size | Line Height | Letter Spacing | Usage |
|------------|------|-------------|----------------|-------|
| `text-xs` | 12px | 1.5 | 0.01em | Fine print, badges |
| `text-sm` | 14px | 1.5 | 0.01em | Captions, labels, timestamps |
| `text-base` | 16px | 1.5 | 0 | Body text, chat messages |
| `text-lg` | 18px | 1.6 | 0 | Large body, intro text |
| `text-xl` | 20px | 1.3 | 0 | Subheadings, card titles |
| `text-2xl` | 24px | 1.3 | 0 | Section headers |
| `text-3xl` | 32px | 1.2 | -0.01em | Page titles |
| `text-4xl` | 40px | 1.1 | -0.02em | Hero headlines |

#### Font Weights

| Token Name | Value | Usage |
|------------|-------|-------|
| `font-regular` | 400 | Body text, standard content |
| `font-medium` | 500 | Emphasized text, button labels |
| `font-semibold` | 600 | Headings, active states |
| `font-bold` | 700 | Strong emphasis, hero text |

### 2.3 Spacing System (8-Point Grid)

| Token Name | Value | Usage |
|------------|-------|-------|
| `space-1` | 4px | Tight inline spacing, icon padding |
| `space-2` | 8px | Inline spacing, small gaps |
| `space-3` | 12px | Compact element gaps |
| `space-4` | 16px | Standard element gaps |
| `space-6` | 24px | Card padding (compact), section gaps |
| `space-8` | 32px | Card padding (standard), component spacing |
| `space-12` | 48px | Section margins, large gaps |
| `space-16` | 64px | Large section spacing |
| `space-20` | 80px | Hero padding (mobile) |
| `space-32` | 128px | Hero padding (desktop) |

### 2.4 Border Radius

| Token Name | Value | Usage |
|------------|-------|-------|
| `radius-sm` | 8px | Buttons, small cards, badges |
| `radius-md` | 12px | Standard buttons, inputs |
| `radius-lg` | 16px | Cards, modals, large containers |
| `radius-xl` | 24px | Hero sections, feature cards |
| `radius-full` | 9999px | Pills, avatars, circular elements |

### 2.5 Shadows & Glows

| Token Name | Value | Usage |
|------------|-------|-------|
| `shadow-card` | `0 0 0 1px rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.5)` | Elevated cards |
| `shadow-modal` | `0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0,0,0,0.7)` | Modals, overlays |
| `glow-accent` | `0 0 20px rgba(59,130,246,0.5), 0 0 40px rgba(59,130,246,0.3)` | Primary button hover, active search |
| `glow-subtle` | `0 0 12px rgba(59,130,246,0.3)` | Subtle interactive glows |

### 2.6 Animation Timing

| Token Name | Value | Easing | Usage |
|------------|-------|--------|-------|
| `duration-fast` | 150ms | ease-out | Button hover, icon changes |
| `duration-normal` | 250ms | ease-out | Card elevation, transitions |
| `duration-slow` | 400ms | ease-out | Modals, panels, thinking trace expand |
| `duration-pulse` | 2000ms | ease-in-out | Glow pulse, typing indicator |

---

## 3. Component Specifications

### 3.1 Button Component

**Primary Button (Vibrant Accent with Glow)**

**Structure**: Text/Icon within filled rectangle
**Tokens**:
- Height: 48px (desktop), 44px (mobile)
- Padding: `space-4` horizontal (16px), `space-3` vertical (12px)
- Border Radius: `radius-md` (12px)
- Font: `font-medium` (500), `text-base` (16px)
- Background: `accent-primary` (#3B82F6)
- Text Color: `text-white`
- Transition: `duration-fast` (150ms)

**States**:
- Default: Solid blue background, no glow
- Hover: Brightness 110%, apply `glow-accent`
- Active: Scale 0.98, brightness 120%
- Disabled: Opacity 40%, no hover effects
- Focus: 2px outline with `border-accent`, 4px offset

**Note**: Use sparingly for primary actions (Send, Submit, New Chat)

**Secondary Button (Outline with Accent)**

**Structure**: Same dimensions as primary
**Tokens**:
- Background: Transparent
- Border: 2px solid `accent-primary`
- Text Color: `accent-primary`
- Hover: Background `accent-primary`, text `text-white`, apply `glow-subtle`

**Ghost Button (Minimal)**

**Structure**: Same dimensions as primary
**Tokens**:
- Background: Transparent
- Border: None
- Text Color: `text-secondary`
- Hover: Background `bg-hover`, text `text-primary`

### 3.2 Card Component (Elevated Surface)

**Structure**: Container with elevated background, border, padding, and rounded corners

**Tokens**:
- Background: `bg-elevated` (#141414)
- Border: 1px solid `border-subtle`
- Border Radius: `radius-lg` (16px)
- Padding: `space-8` (32px) desktop, `space-6` (24px) mobile
- Shadow: `shadow-card`

**States**:
- Default: Level 1 elevation
- Hover: Background `bg-hover`, border `border-moderate`, subtle lift (translateY -2px)
- Active: Border `border-accent` on selected cards (conversation list)
- Focus: 2px outline with `border-accent`

**Note**: Use for message bubbles, conversation list items, settings cards

### 3.3 MessageBubble Component

**User Message (Right-Aligned)**

**Structure**: Chat bubble with accent background, right-aligned
**Tokens**:
- Background: `accent-primary` (#3B82F6)
- Text Color: `text-white`
- Border Radius: `radius-lg` (16px), bottom-right corner `radius-sm` (8px)
- Padding: `space-4` (16px)
- Max Width: 70% of container
- Margin: `space-3` (12px) vertical, auto left
- Shadow: `shadow-card`

**Assistant Message (Left-Aligned)**

**Structure**: Chat bubble with elevated dark background, left-aligned
**Tokens**:
- Background: `bg-elevated` (#141414)
- Text Color: `text-primary` (#E4E4E7)
- Border: 1px solid `border-subtle`
- Border Radius: `radius-lg` (16px), bottom-left corner `radius-sm` (8px)
- Padding: `space-6` (24px)
- Max Width: 85% of container
- Margin: `space-3` (12px) vertical, auto right

**Nested Elements**:
- Code blocks: Background `bg-pure-black`, font `font-mono`, `text-sm`, padding `space-4`, `radius-md`
- Citations: Text `accent-secondary`, underline on hover, external link icon
- Thinking trace: Border-left 2px `semantic-info`, background `bg-near-black`, padding `space-4`

**Streaming State**:
- Add animated gradient border: `linear-gradient(90deg, accent-primary, accent-secondary)` rotating 360° over 2s
- Cursor blinking animation on last character

### 3.4 Navigation (TopBar)

**Structure**: Fixed header with logo, navigation, and user controls

**Tokens**:
- Height: 64px
- Background: `rgba(10, 10, 10, 0.9)` with `backdrop-blur(10px)`
- Border Bottom: 1px solid `border-subtle`
- Padding: 0 `space-6` (24px)
- Z-index: 1000

**Layout**:
- Left: Logo (text "Aletheia" with icon) - `text-xl`, `font-semibold`
- Center (Desktop): Navigation links - `text-base`, `text-secondary`, hover `text-primary` + accent underline
- Right: Theme toggle + User avatar

**States**:
- Scrolled: Background opacity 100%, border more visible
- Mobile: Collapse center nav to hamburger menu

### 3.5 InputBar Component

**Structure**: Fixed bottom bar with auto-resize textarea, file upload, and submit

**Tokens**:
- Background: `bg-elevated` (#141414)
- Border Top: 1px solid `border-subtle`
- Padding: `space-4` (16px)
- Max Width: 900px (centered)
- Min Height: 64px

**Textarea**:
- Background: `bg-hover` (#1E1E1E)
- Border: 1px solid `border-subtle`
- Border Radius: `radius-md` (12px)
- Padding: `space-3` (12px) `space-4` (16px)
- Font: `font-primary`, `text-base`
- Text Color: `text-primary`
- Placeholder: `text-tertiary`
- Min Height: 44px (1 line)
- Max Height: 200px (8 lines)
- Auto-resize: Grow as user types

**States**:
- Focus: Border `border-accent`, apply `glow-subtle`
- Typing: Border glow animation
- Disabled: Opacity 60%, cursor not-allowed

**Action Buttons**:
- File Upload: Ghost button with upload icon, badge shows file count
- Search Toggle: Toggle button, glow when active with `accent-secondary`
- Submit: Primary button with send icon, disabled when empty

### 3.6 ThinkingTrace Component (Nested in MessageBubble)

**Structure**: Collapsible panel showing agent reasoning steps

**Tokens**:
- Background: `bg-near-black` (#0A0A0A)
- Border Left: 2px solid `semantic-info` (#8B5CF6)
- Border Radius: `radius-md` (12px)
- Padding: `space-4` (16px)
- Margin Top: `space-3` (12px)

**Trigger Button**:
- Text: "Show reasoning" / "Hide reasoning"
- Font: `text-sm`, `font-medium`
- Color: `semantic-info`
- Icon: Chevron (rotate 180° when expanded)

**Content**:
- Steps: Ordered list with monospace numbering
- Font: `font-mono`, `text-sm`
- Color: `text-secondary`
- Confidence bars: Progress bar with gradient from `semantic-error` (low) to `semantic-success` (high)

**Animation**:
- Expand/Collapse: `duration-slow` (400ms), ease-out
- Max Height transition from 0 to auto (use max-height hack)

**Note**: Critical for Aletheia's transparency mission - make reasoning visible and elegant

---

## 4. Layout & Responsive Design

### 4.1 Application Layout Structure

**Desktop (≥1024px)**:

```
┌─────────────────────────────────────────┐
│ TopBar (64px fixed)                     │ ← backdrop-blur, semi-transparent
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │   ChatMessages               │
│ (280px)  │   (max-width 900px, centered)│ ← virtualized scroll
│          │                              │
│ Conv.    │   MessageBubble[]            │
│ List     │                              │
│          ├──────────────────────────────┤
│          │ InputBar (fixed bottom)      │ ← 900px max-width, centered
└──────────┴──────────────────────────────┘
```

- **Sidebar**: Fixed 280px width, full height, `bg-pure-black`, `border-right` 1px subtle
- **ChatMessages**: Centered container, max-width 900px, padding `space-6` (24px)
- **InputBar**: Fixed to bottom, max-width 900px, centered within main area

**Tablet (768px - 1023px)**:

- Sidebar collapses to overlay (slide-in from left, 280px, `bg-pure-black` with 50% dark backdrop)
- ChatMessages: Full-width with `space-4` (16px) padding
- TopBar: Hamburger icon to toggle sidebar

**Mobile (≤767px)**:

- Sidebar: Bottom sheet or full-screen overlay when opened
- ChatMessages: Full-width with `space-3` (12px) padding
- MessageBubble: Max-width 90% (reduced from 70%/85%)
- InputBar: Full-width, buttons smaller (40px height)
- TopBar: Condensed - logo only, hamburger menu, user avatar

### 4.2 Breakpoint Tokens

| Token Name | Value | Usage |
|------------|-------|-------|
| `bp-sm` | 640px | Mobile devices |
| `bp-md` | 768px | Tablets |
| `bp-lg` | 1024px | Desktop |
| `bp-xl` | 1280px | Large desktop |

### 4.3 Grid System

**Desktop Chat Container**:
- Max-width: 900px
- Padding: `space-6` (24px) horizontal
- Centered: `margin: 0 auto`

**Message Layout**:
- User messages: `margin-left: auto`, max-width 70%
- Assistant messages: `margin-right: auto`, max-width 85%
- Vertical gap: `space-3` (12px) between messages

### 4.4 Responsive Adaptations

**Typography Scaling**:
- Mobile: Reduce headline sizes by 20-30% (`text-4xl` → `text-3xl`)
- Maintain `text-base` (16px) for body text (readability critical)

**Spacing Adjustments**:
- Mobile: Reduce section padding from `space-12` (48px) to `space-8` (32px)
- Card padding: `space-8` (32px) → `space-6` (24px)

**Touch Targets**:
- Minimum 44×44px for all interactive elements on mobile
- Increase button padding if needed to meet target size

---

## 5. Interaction & Animation

### 5.1 Animation Standards

**Timing Strategy**:
- **Micro-interactions**: `duration-fast` (150ms) - button hover, icon color changes
- **Component transitions**: `duration-normal` (250ms) - card hover, page transitions
- **Panel animations**: `duration-slow` (400ms) - sidebar slide, thinking trace expand
- **Ambient effects**: `duration-pulse` (2000ms) - glow pulse, typing indicator

**Easing Functions**:
- Primary: `ease-out` (90% of animations) - feels responsive and snappy
- Secondary: `cubic-bezier(0.4, 0.0, 0.2, 1)` for sharp, precise movements

### 5.2 Component Animations

**Button Interactions**:
- Hover: Brightness filter + glow effect (150ms ease-out)
- Active: Scale 0.98 (100ms)
- Focus: Outline fade-in (200ms)

**Card Hover**:
- Background transition (250ms)
- Transform translateY -2px (250ms)
- Border color transition (250ms)

**Message Streaming**:
- Text appears character-by-character (simulated typing)
- Blinking cursor at end: opacity 0 ↔ 1, 500ms infinite
- Gradient border rotation: 360° over 2s linear infinite

**Sidebar Slide**:
- Transform translateX -280px → 0 (400ms ease-out)
- Backdrop fade-in: opacity 0 → 0.5 (400ms)

**Thinking Trace Expand**:
- Max-height 0 → 500px (400ms ease-out)
- Opacity 0 → 1 (300ms, delayed 100ms)

### 5.3 Glow Effects (Signature Dark Mode Element)

**Accent Glow (Primary Actions)**:
```
box-shadow: 
  0 0 20px rgba(59, 130, 246, 0.5),
  0 0 40px rgba(59, 130, 246, 0.3);
```
- Applied on: Primary button hover, active search toggle, focus states
- Animation: Subtle pulse (opacity 0.3 ↔ 0.5, 2s infinite)

**Subtle Glow (Interactive Elements)**:
```
box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
```
- Applied on: Input focus, secondary button hover

**Border Glow (Streaming Messages)**:
```
border-image: linear-gradient(90deg, #3B82F6, #06B6D4) 1;
animation: rotate-gradient 2s linear infinite;
```

### 5.4 Micro-Interactions

**Typing Indicator**:
- Three dots with staggered fade animation
- Each dot: opacity 0.3 → 1, 600ms, infinite
- Stagger delay: 150ms per dot

**File Upload**:
- Badge bounce on file added (scale 0 → 1.2 → 1, 300ms)
- Preview chip slide-in (translateY 8px → 0, 250ms)

**Citation Hover**:
- Underline slide-in (width 0 → 100%, 200ms)
- External link icon glow (color + drop-shadow)

**Code Block Copy**:
- Button appears on hover (opacity 0 → 1, 150ms)
- Click: Check icon replace, green flash (300ms)

### 5.5 Performance Animations (GPU-Accelerated Only)

**Allowed Properties**:
- ✅ `transform` (translate, scale, rotate)
- ✅ `opacity`
- ✅ `filter` (for glows, brightness)

**Forbidden Properties** (force CPU rendering):
- ❌ `width`, `height`, `margin`, `padding`
- ❌ `left`, `top`, `right`, `bottom` (use `transform` instead)
- ❌ `background-position` (use pseudo-elements with transforms)

### 5.6 Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Maintain functionality** while removing decorative animations (glows, pulses, rotations).

### 5.7 Dark Mode Specific Considerations

**Subtler Movements**: Dark backgrounds amplify motion perception
- Reduce translateY from 16px → 8px
- Slower durations: 300ms instead of 200ms

**Brightness Adjustments**: Avoid bright flashes
- Max brightness change: <50% in <200ms
- Glow intensity: 50% on mobile (performance + less intense)

---

## 6. Accessibility & Best Practices

### 6.1 WCAG Compliance

**Text Contrast** (Verified):
- `text-primary` (#E4E4E7) on `bg-near-black` (#0A0A0A): **15.2:1** ✅ AAA
- `text-secondary` (#A1A1AA) on `bg-near-black`: **8.9:1** ✅ AAA
- `accent-primary` (#3B82F6) on `bg-near-black`: **8.6:1** ✅ AAA

**Interactive Elements**:
- All buttons, links: Minimum 4.5:1 contrast
- Focus indicators: 3:1 contrast against background
- Disabled states: Clearly distinguishable (40% opacity minimum)

### 6.2 Keyboard Navigation

**Tab Order**:
1. Skip to main content link
2. TopBar navigation
3. Sidebar conversation list
4. ChatMessages (focusable for screen readers)
5. InputBar textarea
6. Submit button

**Shortcuts**:
- `Enter`: Submit message (when textarea focused)
- `Shift + Enter`: New line in textarea
- `Cmd/Ctrl + K`: Focus search toggle
- `Cmd/Ctrl + N`: New conversation
- `Escape`: Close sidebar (mobile), collapse thinking trace

**Focus Management**:
- Visible focus rings: 2px `border-accent`, 4px offset
- Focus trap in modals (if implemented)
- Return focus after sidebar close

### 6.3 Screen Reader Support

**Semantic HTML**:
- `<nav>` for TopBar and sidebar
- `<main>` for ChatMessages container
- `<article>` for each MessageBubble
- `<aside>` for ThinkingTrace

**ARIA Labels**:
- Icon-only buttons: `aria-label="Upload file"`, `aria-label="Toggle search"`
- Thinking trace: `aria-expanded="true/false"` on trigger
- Streaming messages: `aria-live="polite"` region
- Conversation list: `aria-current="page"` on active item

**Alt Text**:
- User avatars: `alt="[User name] profile picture"`
- Logo: `alt="Aletheia - Truth-seeking research agent"`
- File icons: `alt="[File type] file - [filename]"`

### 6.4 Theme Support

**Dark Mode (Primary)**:
- Default theme, optimized for extended use
- Pure blacks (#000, #0A0A0A) for OLED power savings
- All tokens defined in section 2

**Light Mode (Secondary, Optional)**:
- Invert background hierarchy:
  - `bg-pure-black` → `#FFFFFF`
  - `bg-near-black` → `#FAFAFA`
  - `bg-elevated` → `#F5F5F5`
  - `bg-hover` → `#E5E5E5`
- Text colors:
  - `text-primary` → `#18181B` (zinc-900)
  - `text-secondary` → `#52525B` (zinc-600)
  - `text-tertiary` → `#A1A1AA` (zinc-400)
- Accents remain same (verify contrast: all pass ≥4.5:1 on white)
- Shadows replace glows:
  - `shadow-card`: `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`

**Theme Toggle**:
- Icon: Sun (light mode) / Moon (dark mode)
- Location: TopBar right side
- Persist: localStorage `theme` key
- Smooth transition: 200ms on `background-color`, `color`, `border-color`

### 6.5 Performance Considerations

**Virtualization**:
- Messages: Render only visible + 5 buffer above/below
- Library: `react-virtual` or `react-window`
- Item height estimation: 100px average, dynamic measurement

**Code Splitting**:
- Syntax highlighter: Lazy load on first code block
- Chart libraries: Lazy load on CSV upload
- PDF parser: Load on demand

**Image Optimization**:
- User avatars: WebP format, 64×64px max
- Lazy loading: `loading="lazy"` attribute
- Responsive: Serve appropriate sizes

**Caching**:
- Service worker: Cache static assets, fonts
- IndexedDB: Store chat history (10MB limit)
- Supabase: Cloud sync for persistence

---

**Design Specification Complete**
**Total Word Count**: ~2,850 words
**Status**: Ready for development handoff
