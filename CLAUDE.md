# CLAUDE.md — TARS AI Landing Page

## Project Overview

TARS is a B2B AI-powered "Chief of Staff" service for CEOs, founders, and business leaders. This repository contains the **marketing landing page** — a single static HTML file, fully in French (`lang="fr"`).

There is no backend, no database, no build system. The entire site is one self-contained `index.html`.

## Repository Structure

```
tars-ai/
├── CLAUDE.md        # This file
└── index.html       # The entire landing page (918 lines)
```

### index.html Internal Layout

| Section    | Lines     | Contents                                                        |
|------------|-----------|-----------------------------------------------------------------|
| CSS        | 11–530    | Design tokens, component styles, responsive layout, utilities   |
| HTML       | 532–856   | Page sections: header, hero, features, pricing, FAQ, footer     |
| JavaScript | 858–916   | Scroll animations, FAQ toggle, CTA handling, header scroll effect |

## Tech Stack

- **HTML5 / CSS3 / vanilla JavaScript** — no frameworks, no libraries
- **Google Fonts** — Inter (300–700 weights), loaded via `<link>` preconnect
- **No build tools** — no npm, no bundler, no transpiler
- **No package manager** — no `package.json`, no dependencies to install
- **No tests, linting, or CI/CD**

## Development

```bash
# Serve locally (pick any)
python3 -m http.server
npx http-server
php -S localhost:8000

# Or simply open index.html in a browser
```

No install step. No environment variables. Changes to `index.html` are immediately reflected on reload.

## Design System

### CSS Custom Properties (`:root`)

| Variable                  | Value                | Purpose              |
|---------------------------|----------------------|----------------------|
| `--color-bg`              | `#0a0a0a`            | Primary background   |
| `--color-bg-secondary`    | `#111111`            | Card/section bg      |
| `--color-bg-tertiary`     | `#1a1a1a`            | Hover/alt bg         |
| `--color-text-primary`    | `#ffffff`            | Headings, body text  |
| `--color-text-secondary`  | `#a1a1aa`            | Subtitles, descriptions |
| `--color-text-muted`      | `#71717a`            | Captions, hints      |
| `--color-border`          | `#27272a`            | Default borders      |
| `--color-border-light`    | `#3f3f46`            | Lighter borders      |
| `--color-accent`          | `#3b82f6`            | Primary blue accent  |
| `--color-accent-hover`    | `#2563eb`            | Accent hover state   |
| `--color-success`         | `#10b981`            | Checkmarks, success  |
| `--color-warning`         | `#f59e0b`            | Stats highlight      |
| `--radius-sm/md/lg`       | `0.375/0.5/0.75rem`  | Border radius scale  |
| `--shadow-sm/md/lg`       | Various               | Box shadow scale     |

### Typography

Fluid type scale using `clamp()`:
- `.heading-xl` — hero title (`clamp(2.5rem, 5vw, 4rem)`)
- `.heading-lg` — section titles (`clamp(2rem, 4vw, 3rem)`)
- `.heading-md` — subsection titles (`clamp(1.5rem, 3vw, 2rem)`)
- `.text-lg` — lead paragraphs (`clamp(1.125rem, 2vw, 1.25rem)`)
- `.text-base` — body copy (`1rem`)
- `.text-sm` — small text (`0.875rem`)

### Responsive Breakpoints

- **640px** — hero CTA switches from column to row
- **768px** — grids go from 1-col to 2-col; container padding increases
- **1024px** — features grid goes to 3-col

`@media (prefers-reduced-motion: reduce)` disables scroll animations.

## CSS Conventions

- **BEM-inspired naming**: `.btn-primary`, `.feature-card`, `.pricing-card`, `.faq-item`, `.step-number`
- **Utility classes**: `.text-center`, `.text-accent`, `.text-muted`, `.mb-2`, `.mb-4`, `.mb-8`
- **Component pattern**: `.card` base class with modifier variants (`.featured`)
- All styles are embedded in a single `<style>` block — no external stylesheets

## JavaScript Patterns

All JS is in a `<script>` block at the end of `<body>`:

- **Intersection Observer** — sections start with `opacity: 0; transform: translateY(30px)` and get `.visible` class on scroll into view
- **FAQ accordion** — `toggleFaq()` toggles `.active` on `.faq-item`, closes all others first (single-open accordion)
- **CTA links** — all `href="#calendly"` links show a placeholder `alert()` (Calendly integration not yet wired)
- **Header effect** — `scroll` listener increases header background opacity past 100px scroll

## Page Sections

1. **Header** — fixed nav with logo + "Réserver une démo" CTA
2. **Hero** — headline, subtitle, primary CTA button
3. **Problem** — "2h/jour" stat with pain-point messaging
4. **Features** — 6-card grid (briefing, email triage, monitoring, tasks, multichannel, automations)
5. **How it works** — 3-step process (discovery call, 48h setup, AI operational)
6. **Pricing** — 3 tiers: Starter (149€), Pro (299€, featured), Enterprise (599€) + setup fees
7. **Testimonials** — 3 customer quotes
8. **FAQ** — 6 collapsible items
9. **Final CTA** — closing call to action
10. **Footer** — copyright line

## Guidelines for AI Assistants

- **Keep the single-file architecture** — do not split into separate CSS/JS files unless explicitly asked
- **All content must remain in French** — the site targets French-speaking executives
- **Preserve the design token system** — use existing CSS variables, don't hardcode colors or spacing
- **Respect `prefers-reduced-motion`** — any new animations must have reduced-motion fallbacks
- **Test across breakpoints** — verify changes at mobile (<640px), tablet (768px), and desktop (1024px)
- **No build tooling** — changes should work without any compilation or bundling step
- **Calendly integration is a placeholder** — CTA links currently show an alert; a real implementation will need updating
- **Footer copyright says 2024** — update if the year changes
