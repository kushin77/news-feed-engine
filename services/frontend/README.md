# Frontend — News Feed Engine

> FAANG-grade React + TypeScript frontend with Vite, Tailwind, and comprehensive testing

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Run tests
npm run test

# Full quality check
npm run faang-check
```

## 📋 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | React 18 + TypeScript | Component-based UI with strict typing |
| **Build Tool** | Vite | Lightning-fast bundling, <100KB gzip |
| **Styling** | Tailwind CSS | Rapid utility-first style development |
| **Testing** | Vitest + React Testing Library | Unit & integration tests (>70% target) |
| **Linting** | ESLint (strict) + Prettier | Code quality & formatting (zero warnings) |
| **State** | Zustand | Lightweight state management |
| **Data Fetching** | @tanstack/react-query | Server state sync & caching |
| **Deployment** | Docker + nginx | Multi-stage production-ready build |

## 📁 Project Structure

```
src/
├── components/          # Reusable React components (Layout, etc.)
├── pages/              # Page-level components (Dashboard, etc.)
├── hooks/              # Custom React hooks
├── services/           # API clients, HTTP utilities
├── store/              # Zustand state stores
├── types/              # TypeScript interfaces & types
├── utils/              # Helper functions
├── styles/             # Global CSS + Tailwind config
├── test/               # Test setup & mocks
├── App.tsx             # Root component
└── main.tsx            # Vite entry point
```

## 🎯 FAANG Standards Checklist

- ✅ **TypeScript**: Strict mode, no `any` types, 100% coverage
- ✅ **Linting**: ESLint with security rules, zero warnings
- ✅ **Testing**: Vitest (unit) + React Testing Library (integration), >70% coverage
- ✅ **Performance**: <100KB gzip, code splitting by route
- ✅ **Security**: No hardcoded secrets, no console.logs in production
- ✅ **Accessibility**: WCAG 2.1 Level AA (Tailwind utilities)
- ✅ **Build**: Docker multi-stage, nginx reverse proxy
- ✅ **CI/CD**: GitHub Actions ready, conventional commits

## 🔧 Available Commands

### Development
```bash
npm run dev              # Start dev server with HMR
npm run type-check      # TypeScript type checking
npm run format          # Format code with Prettier
```

### Quality
```bash
npm run lint            # Check ESLint (fails on errors)
npm run lint:fix        # Auto-fix ESLint issues
npm run test            # Run Vitest  
npm run test:coverage   # Coverage report (./coverage)
npm run faang-check     # Full audit (lint + type + coverage)
```

### Build & Deploy
```bash
npm run build           # Production build (./dist)
npm run preview         # Preview production build locally
make build-docker       # Build Docker image
make docker-up          # Run Docker container
```

## 📊 Key Components

### Layout Component
Main wrapper with:
- Collapsible sidebar navigation
- Sticky header with user profile
- Responsive grid layout

### Dashboard Page
Dashboard showing:
- 4 key stat cards (posts, reach, engagement, scheduled)
- Quick action buttons (create, schedule, analytics)
- Recent activity feed placeholder

## 🧪 Testing

```bash
# Run all tests
npm run test

# Watch mode (re-run on file changes)
npm run test -- --watch

# UI mode (browser-based test dashboard)
npm run test:ui

# Coverage report (generated in ./coverage)
npm run test:coverage
```

**Coverage Target**: >70% (unit + integration)  
**Key Areas**: Core dashboarding, API integration, auth flows

## 🐳 Docker Deployment

### Build
```bash
docker build -t news-feed-frontend:latest .
```

### Run
```bash
docker run -p 80:80 news-feed-frontend:latest
```

### Image Details
- **Base**: nginx:1.27-alpine (11MB)
- **Final Size**: ~50MB
- **Health Check**: Every 30s
- **User**: nginx (non-root)

## 📦 Dependency Management

Dependencies are kept minimal and production-focused:

| Package | Version | Why |
|---------|---------|-----|
| react | ^18.3.1 | Latest, stable UI framework |
| typescript | ^5.2.2 | Strict type checking |
| vite | ^5.1.2 | Ultra-fast build tooling |
| tailwindcss | ^3.4.1 | Utility-first styling |
| zustand | ^4.4.7 | Lightweight state (< 3KB) |
| @tanstack/react-query | ^5.36.0 | Server state management |

**Zero unused dependencies** - audit with `npm audit`

## 🔐 Security

- No hardcoded secrets or API keys
- ESLint security plugin enforces best practices
- Dockerfile runs as non-root user
- Docker health checks enabled
- HTTPS-ready (configure in nginx.conf)

## 📚 Resources

- [Vite Docs](https://vitejs.dev/)
- [React TypeScript Guide](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vitest](https://vitest.dev/)
- [WCAG Accessibility](https://www.w3.org/WAI/WCAG21/quickref/)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feat/XXX-description`
2. Make changes following FAANG standards
3. Run `npm run faang-check` before committing
4. Commit with conventional message: `feat(#110): description`
5. Push and create pull request
6. Ensure CI/CD passes before merge

## 📋 Git Workflow

```bash
# Always update issues in git messages
git commit -m "feat(#110): add dashboard component"

# Push after logical units of work
git push origin feat/XXX-description

# Link commits to GitHub issues with #NUMBER
```
