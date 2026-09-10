# AI-Powered Research Gap Finder

A platform where users upload academic research papers (PDFs) and the system analyzes them to surface evidence-based candidate research gaps — underexplored areas, contradictions, and repeated limitations across the literature. This repository contains the complete frontend, built against realistic mock data and architected for a straightforward swap to a real backend.

## Features

- **Dashboard** — project stats, activity trends, topic distribution, recent gaps and activity
- **Projects** — create, browse, and manage research projects
- **Paper upload & management** — drag-and-drop upload with per-file processing status, searchable/filterable paper table
- **Paper analysis** — structured breakdown (problem, methodology, models, dataset, findings, limitations, future work) with evidence traceable back to source paper/section/page
- **Semantic search** — natural-language queries over a project's papers with AI-generated answers and cited sources
- **Research landscape** — topic distribution, method/dataset usage, ranked limitations, and future-work trends
- **Paper comparison** — side-by-side comparison across papers on shared criteria
- **Contradiction detection** — surfaces conflicting claims between papers, clearly labeled as potential (not proven) contradictions
- **Research gap finder** — the centerpiece: confidence-scored, evidence-backed candidate research gaps with suggested research questions and methodology
- **Reports** — generate and preview downloadable summary reports
- **Light/dark theme** — persisted across sessions

## Tech Stack

- **React** + **Vite** + **TypeScript** (strict mode)
- **Tailwind CSS** for styling
- **React Router DOM** for routing
- **@tanstack/react-query** for data fetching and caching
- **Axios** for HTTP requests
- **Recharts** for data visualization
- **lucide-react** for icons

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

### Build

```bash
npm run build
```

### Type Checking

```bash
npx tsc -b
```

## Environment Variables

| Variable          | Description                                                                 | Default |
| ----------------- | ---------------------------------------------------------------------------- | ------- |
| `VITE_USE_MOCK`   | When `true` (or unset), the app uses local mock data. Set to `false` to route API calls through the real backend integration. | `true`  |

Create a `.env.local` file in the project root to override:

```
VITE_USE_MOCK=false
```

## Project Structure

```
src/
  components/       # UI components, organized by feature area
    layout/         # App shell, header, sidebar, theme toggle
    common/         # Shared primitives (Button, Card, Modal, Badge, states, toasts)
    landing/        # Public landing page sections
    dashboard/       ...
    projects/        ...
    papers/          ...
    search/          ...
    landscape/       ...
    comparison/      ...
    contradictions/  ...
    gaps/            ...
    reports/         ...
  pages/            # Route-level page components
  services/         # Centralized API layer (mock/real mode switch)
  types/            # TypeScript interfaces for all domain models
  hooks/            # React Query hooks per data domain
  context/          # Theme and toast context providers
  data/             # Mock datasets
  utils/            # Formatting and shared helper utilities
```

## Routes

| Path                                    | Description                  |
| ---------------------------------------- | ----------------------------- |
| `/`                                       | Landing page                  |
| `/dashboard`                              | Dashboard                     |
| `/projects`                               | Projects list                 |
| `/projects/:projectId`                    | Project workspace (Overview)  |
| `/projects/:projectId/upload`             | Upload papers                 |
| `/projects/:projectId/papers`             | Papers list                   |
| `/projects/:projectId/search`             | Semantic search                |
| `/projects/:projectId/landscape`          | Research landscape             |
| `/projects/:projectId/compare`            | Paper comparison               |
| `/projects/:projectId/contradictions`     | Contradiction analysis         |
| `/projects/:projectId/gaps`               | Research gap finder            |
| `/papers/:paperId`                        | Paper details                  |
| `/gaps/:gapId`                            | Gap details                    |
| `/reports`                                | Reports                        |
| `*`                                       | 404                            |

## Backend Integration

This frontend is designed to swap from mock data to a real backend with minimal changes:

1. Implement the corresponding endpoints matched by `src/services/realApi.ts`.
2. Set `VITE_USE_MOCK=false` in your environment.
3. No component changes are required — all data access goes through `src/services/api.ts`, which switches between mock and real implementations based on the environment variable.

## License

This project was built as a final-year academic project.
