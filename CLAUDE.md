# CLAUDE.md — TARS AI Landing Page

> If it won't survive the next session, write it here.

## Identity

This repository is the **marketing landing page** for TARS — a B2B AI-powered "Chief of Staff" service for CEOs, founders, and business leaders. Single static HTML file, fully in French (`lang="fr"`). No backend, no database, no build system. One self-contained `index.html`, 918 lines.

## Session Rhythm

Every session working on this codebase follows three phases:

### Orient (read before touching)
1. Read this file
2. Scan `index.html` structure — CSS (11–530), HTML (532–856), JS (858–916)
3. Identify which section is affected by the current task
4. Check if existing design tokens, classes, or patterns already solve the need

### Work (make changes)
5. Edit `index.html` — the only source file
6. Use existing CSS variables, never hardcode colors or spacing
7. Follow established naming conventions (see vocabulary below)
8. Test at all three breakpoints: mobile (<640px), tablet (768px), desktop (1024px)

### Persist (leave breadcrumbs)
9. Update this file if the change introduces new patterns, sections, or conventions
10. If a new CSS variable, class, or JS pattern was added, document it below

## Repository Structure

```
tars-ai/
├── CLAUDE.md            # This file — agent context, always read first
├── index.html           # The entire landing page (918 lines)
└── tasks/
    ├── todo.md          # Current task plan with checkboxes
    └── lessons.md       # Cumulative corrections & rules learned
```

### index.html Internal Layout

| Layer      | Lines   | What Lives Here                                                 |
|------------|---------|-----------------------------------------------------------------|
| CSS        | 11–530  | Design tokens, component styles, responsive layout, utilities   |
| HTML       | 532–856 | Page sections: header → hero → problem → features → pricing → FAQ → footer |
| JavaScript | 858–916 | Scroll animations, FAQ toggle, CTA handling, header scroll effect |

## Task Routing

Use this decision tree when you receive a request:

```
Is it a visual/styling change?
  └─ YES → Edit CSS block (lines 11–530). Use existing variables.
  └─ NO ↓

Is it a content change (text, pricing, features)?
  └─ YES → Edit HTML block (lines 532–856). Keep French. Match existing structure.
  └─ NO ↓

Is it an interaction/behavior change?
  └─ YES → Edit JS block (lines 858–916). Follow existing patterns.
  └─ NO ↓

Is it a new section?
  └─ YES → Add HTML between existing sections. Add CSS above line 530.
           Follow .section class pattern for scroll animations.
  └─ NO ↓

Is it about splitting into multiple files?
  └─ YES → Confirm with user first. Default is single-file.
```

## Tech Stack

- **HTML5 / CSS3 / vanilla JavaScript** — no frameworks, no libraries
- **Google Fonts** — Inter (300–700 weights), `<link>` preconnect
- **No build tools** — no npm, no bundler, no transpiler
- **No package manager** — no `package.json`, no dependencies
- **No tests, linting, or CI/CD**

### Development

```bash
# Serve locally (pick any)
python3 -m http.server
npx http-server
php -S localhost:8000

# Or just open index.html directly in a browser
```

No install step. No environment variables. Changes reflect on reload.

## Design System — Vocabulary

The design system is the project's vocabulary. Every visual decision routes through these tokens.

### Color Tokens (`:root`)

| Token                     | Value       | When to Use                        |
|---------------------------|-------------|------------------------------------|
| `--color-bg`              | `#0a0a0a`   | Page background                    |
| `--color-bg-secondary`    | `#111111`   | Cards, elevated sections           |
| `--color-bg-tertiary`     | `#1a1a1a`   | Hover states, alternate surfaces   |
| `--color-text-primary`    | `#ffffff`   | Headings, primary body text        |
| `--color-text-secondary`  | `#a1a1aa`   | Subtitles, feature descriptions    |
| `--color-text-muted`      | `#71717a`   | Captions, fine print, hints        |
| `--color-border`          | `#27272a`   | Section dividers, card borders     |
| `--color-border-light`    | `#3f3f46`   | Secondary button borders, hovers   |
| `--color-accent`          | `#3b82f6`   | CTAs, highlights, interactive elements |
| `--color-accent-hover`    | `#2563eb`   | Accent hover/active state          |
| `--color-success`         | `#10b981`   | Checkmarks, positive indicators    |
| `--color-warning`         | `#f59e0b`   | Statistics, attention-grabbing numbers |

### Spacing & Shape Tokens

| Token              | Value          | Purpose           |
|--------------------|----------------|-------------------|
| `--radius-sm`      | `0.375rem`     | Small elements    |
| `--radius-md`      | `0.5rem`       | Buttons, inputs   |
| `--radius-lg`      | `0.75rem`      | Cards, containers |
| `--shadow-sm/md/lg`| Various        | Elevation scale   |

### Typography Scale

Fluid sizing via `clamp()` — never use fixed `font-size` for headings:

| Class          | Size                            | Use For              |
|----------------|---------------------------------|----------------------|
| `.heading-xl`  | `clamp(2.5rem, 5vw, 4rem)`     | Hero title only      |
| `.heading-lg`  | `clamp(2rem, 4vw, 3rem)`       | Section titles       |
| `.heading-md`  | `clamp(1.5rem, 3vw, 2rem)`     | Subsection titles    |
| `.text-lg`     | `clamp(1.125rem, 2vw, 1.25rem)`| Lead paragraphs      |
| `.text-base`   | `1rem`                          | Body copy            |
| `.text-sm`     | `0.875rem`                      | Small text, captions |

### Responsive Breakpoints

| Breakpoint | What Changes                                      |
|------------|---------------------------------------------------|
| `640px`    | Hero CTA: column → row                            |
| `768px`    | Grids: 1-col → 2-col; container padding increases |
| `1024px`   | Features grid: 2-col → 3-col                      |

`@media (prefers-reduced-motion: reduce)` disables all scroll animations.

## Naming Conventions

### CSS Classes — Pattern Reference

| Pattern              | Examples                                         | Rule                              |
|----------------------|--------------------------------------------------|-----------------------------------|
| Component            | `.card`, `.btn`, `.header`, `.nav`                | Noun, singular                    |
| Component + modifier | `.btn-primary`, `.btn-secondary`, `.card.featured`| Hyphenated modifier               |
| Section-scoped       | `.feature-card`, `.pricing-card`, `.faq-item`     | Section prefix + component        |
| Sub-element          | `.feature-icon`, `.pricing-price`, `.step-number` | Parent prefix + role              |
| Utility              | `.text-center`, `.text-accent`, `.mb-4`           | Property-value, no section prefix |

### Adding New Classes

1. Check if an existing class already covers the need
2. If section-specific → prefix with section name (e.g., `.testimonial-*`)
3. If reusable → add as utility in the utilities block (line ~523)
4. Never create a class used only once — use inline styles for one-offs

## JavaScript Patterns

All JS lives in a single `<script>` block at end of `<body>` (lines 858–916):

| Pattern                | Implementation                        | How to Extend                        |
|------------------------|---------------------------------------|--------------------------------------|
| Scroll animation       | `IntersectionObserver` + `.visible`   | Add `.section` class to new sections |
| FAQ accordion          | `toggleFaq()` → `.active` toggle      | Add `.faq-item` with same structure  |
| CTA handling           | `href="#calendly"` → `alert()` placeholder | Replace alert with real integration |
| Header scroll effect   | `scroll` listener → opacity change    | Modify threshold (currently 100px)   |

### Adding New Interactions

1. Use vanilla JS only — no jQuery, no framework imports
2. Attach listeners inside `DOMContentLoaded`
3. Use `classList` operations for state changes
4. Respect `prefers-reduced-motion` for any animation

## Page Sections — Content Map

| #  | Section        | HTML Lines | Key Classes             | Content                          |
|----|----------------|------------|-------------------------|----------------------------------|
| 1  | Header         | 534–539    | `.header`, `.nav`       | Logo + demo CTA                  |
| 2  | Hero           | 542–562    | `.hero`, `.hero-content` | Headline, subtitle, CTA         |
| 3  | Problem        | 565–578    | `.problem`              | "2h/jour" stat + pain point      |
| 4  | Features       | 581–635    | `.features-grid`        | 6 cards with emoji icons         |
| 5  | How it works   | 638–670    | `.steps`                | 3-step process                   |
| 6  | Pricing        | 673–732    | `.pricing-grid`         | 3 tiers (149€/299€/599€)        |
| 7  | Testimonials   | 735–770    | `.testimonials-grid`    | 3 customer quotes                |
| 8  | FAQ            | 773–835    | `.faq-list`             | 6 collapsible items              |
| 9  | Final CTA      | 838–849    | `.final-cta`            | Closing call to action           |
| 10 | Footer         | 852–856    | `.footer`               | Copyright (currently says 2024)  |

## Common Pitfalls

These are the failure modes specific to this project. Avoid them:

| Pitfall                              | Why It Happens                           | What to Do Instead                              |
|--------------------------------------|------------------------------------------|-------------------------------------------------|
| Hardcoded colors                     | Grabbing hex values instead of variables | Always use `var(--color-*)` tokens              |
| Breaking mobile layout               | Testing only at desktop width            | Check all 3 breakpoints after every change      |
| Adding English text                  | Defaulting to English                    | All user-facing text must be in French           |
| Splitting files without asking       | Instinct to separate concerns            | Keep single-file unless user explicitly requests |
| Fixed font sizes for headings        | Using `px` or `rem` directly             | Use `clamp()` pattern matching existing scale    |
| Forgetting reduced-motion            | Adding CSS animations                    | Always add `prefers-reduced-motion` fallback     |
| Adding npm/build dependencies        | Instinct to install packages             | This is a zero-dependency project — keep it that |
| Duplicating existing patterns        | Not checking what already exists         | Search CSS block first for existing classes      |
| Inline styles for recurring patterns | Quick fix that doesn't scale             | Create a class following naming conventions      |
| Modifying `:root` without documenting| Adding a token and forgetting this file  | Update this CLAUDE.md when adding design tokens  |

## Evolution Signals

Update this file when any of these occur:

- A new CSS variable is added to `:root`
- A new reusable class pattern is introduced
- A new page section is created
- The JS architecture changes (e.g., new observer, new event pattern)
- External dependencies are introduced (fonts, scripts, APIs)
- The file is split into multiple files
- Calendly placeholder is replaced with real integration

## Workflow — How the Agent Works

These rules govern how the AI agent operates on this project. They are adapted to the reality of TARS AI: a single `index.html`, zero build system, visual output only.

### 1. Plan Before Touching

- Enter plan mode for any task involving **3+ edits** or **cross-layer changes** (CSS + HTML + JS)
- Write the plan to `tasks/todo.md` with checkable items before starting
- If something breaks mid-task → **STOP**, re-read this file, re-plan. Don't push through blindly
- For single-layer, single-section changes (e.g., changing one text string) → skip planning, just do it

### 2. Subagent Strategy

- Use subagents to **explore `index.html`** without flooding main context (918 lines is a lot to hold)
- Offload to subagents: "find all uses of `--color-accent`", "check all breakpoint behavior for `.pricing-grid`"
- One task per subagent — don't bundle unrelated searches
- Main context stays focused on the actual edit

### 3. Learn From Corrections

- After ANY correction from the user → add the pattern to `tasks/lessons.md`
- Format: `| What went wrong | Why | Rule to follow |`
- Review `tasks/lessons.md` at session start — don't repeat mistakes
- Lessons are cumulative: they survive across sessions

### 4. Verify Before Declaring Done

- Never say "c'est fait" without checking:
  - **Tokens**: no hardcoded colors/spacing? Uses `var(--color-*)` and `var(--radius-*)`?
  - **French**: all new text in French?
  - **Responsive**: works at 640px, 768px, 1024px?
  - **Reduced motion**: new animations have `prefers-reduced-motion` fallback?
  - **Single file**: nothing was split?
- Ask yourself: "Would someone reviewing this landing page spot anything broken?"

### 5. Demand Elegance (When It Matters)

- For visual/structural changes: pause and ask "is there a simpler way using existing tokens/classes?"
- If a fix requires more than 3 new CSS rules → check if existing patterns already solve it
- If something feels hacky (inline styles, magic numbers, `!important`) → refactor using the design system
- For trivial text changes → don't overthink it, just edit

### 6. Autonomous Problem Solving

- When given a bug report (broken layout, wrong color, misaligned element) → just fix it
- Read the relevant section of `index.html`, identify root cause, apply fix
- Don't ask "which line is it on?" — use the Content Map above to locate it
- Zero hand-holding required from the user

### 7. Track Progress

1. Write plan to `tasks/todo.md` with `- [ ]` checkboxes
2. Mark items `- [x]` as completed — don't batch, mark immediately
3. At task end: add a `## Review` section to `tasks/todo.md` summarizing what changed
4. Update `tasks/lessons.md` if any correction was received

### Core Principles

| Principle | Applied to TARS AI |
|-----------|--------------------|
| **Simplicity First** | One file. Existing tokens. Minimal edits. Don't add complexity. |
| **No Laziness** | Find root causes in CSS/HTML/JS. No `!important` hacks, no inline-style band-aids. |
| **Minimal Impact** | Touch only the lines that need changing. Don't refactor adjacent code "while you're there". |

## Constraints — Non-Negotiable

1. **French only** — all user-visible content in French (`lang="fr"`)
2. **Single file** — do not split without explicit user request
3. **Zero dependencies** — no npm, no CDN scripts (Google Fonts is the sole external resource)
4. **Design tokens** — never hardcode colors, radii, or shadows
5. **Accessibility** — respect `prefers-reduced-motion`, maintain semantic HTML
6. **Responsive** — every change must work at mobile, tablet, and desktop
