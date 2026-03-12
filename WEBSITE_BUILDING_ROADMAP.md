# Website Building Roadmap — Best Practices Framework

**Last Updated:** March 12, 2026  
**Focus:** Build ElevateIQ marketing website & product showcase frontend  
**Principles:** Immutable · Ephemeral · Idempotent · Privacy-First · No Hard-Coded Secrets

---

## 1. STRATEGIC POSITIONING

### Website Purpose (3-Tier)
```
LAYER 1: Landing Page & Lead Capture
├── Hero messaging (ElevateIQ vision)
├── Proof-of-concept demo
├── Lead magnet CTA (free trial / waitlist)
└── Async email nurture sequence

LAYER 2: Product Showcase & Platform Features
├── Agent crew visualization (8 agents running)
├── Real-time analytics dashboard
├── Integration showcase (12 platform connectors)
├── Pricing tiers & comparison
└── Customer testimonials / case studies

LAYER 3: Documentation & Knowledge Base
├── Platform architecture explainers
├── Integration guides
├── Privacy & security documentation
├── API reference & developer portal
└── FAQ & support knowledge base
```

---

## 2. TECHNOLOGY STACK (Following Repo Standards)

### Frontend
- **Framework:** React 18 + TypeScript (existing: see `services/frontend/`)
- **State:** Zustand (lightweight, no Redux boilerplate)
- **Styling:** Tailwind CSS (production-ready)
- **Build:** Vite (fast local dev + fast prod builds)
- **Testing:** Vitest + React Testing Library
- **Deployment:** Static hosting (Vercel / Netlify preferred; no containers)

### Backend (API)
- **Runtime:** Node.js 20 (Cloud Functions compatible)
- **Framework:** Express.js (microservice-oriented)
- **Email:** SendGrid (no self-hosted SMTP)
- **Database:** Supabase/Postgres (no self-managed DBs)
- **Auth:** OAuth via Supabase (no hardcoded credentials)
- **Secrets:** Google Secret Manager (GSM) - NEVER `.env` files

### Deployment
- **Branch Policy:** Direct-to-main (no feature branches)
- **CI/CD:** ⚠️ DISABLED BY POLICY — Manual local deploy via scripts
- **Immutability:** Git SHA verification on each deploy
- **Idempotency:** All scripts designed to be re-run safely
- **Credentialing:** Runtime fetch from GSM (ephemeral)
- **Monitoring:** Sentry (error tracking), DataDog (performance)

---

## 3. GITHUB ISSUES DECOMPOSITION

### Phase 0: Foundation (No Website, Just Repo Setup)
- [ ] **#15, #12:** Reorganize folder structure to mono-repo standard
  - Backend: `services/api/`
  - Frontend: `services/frontend/` (React app)
  - Shared: `packages/shared/` (TS types, utils)
  - Infrastructure: `infrastructure/` (Terraform, Docker)

- [ ] **#16, #13:** Implement documentation structure
  - `docs/ARCHITECTURE.md` — system design
  - `docs/DEPLOYMENT.md` — how to ship
  - `docs/SECURITY.md` — credential handling, OWASP
  - `docs/API.md` — backend endpoints for frontend

- [ ] **#14:** Mirror VS Code workspace configuration
  - `.code-workspace` with multi-folder setup
  - Recommended extensions (Prettier, ESLint, Thunder Client)

### Phase 1: Website MVP (Landing + Waitlist)
- [ ] **NEW: Website Landing Page**
  - Hero section with ElevateIQ tagline
  - 3-4 value propositions with icons
  - Video embed (product demo or founder intro)
  - CTA button → capture email
  - Footer with links

- [ ] **NEW: Email Capture System**
  - Backend: `POST /api/waitlist/signup` endpoint
  - Validation: email uniqueness, rate limiting
  - Service: SendGrid integration (no hardcoded API key)
  - Response: Confirmation email + webhook to automation

- [ ] **NEW: Analytics Instrumentation**
  - Segment / Plausible (privacy-focused)
  - Track: page views, CTA clicks, form submissions
  - NO Google Analytics (privacy concern)

### Phase 2: Product Showcase (Interactive Features)
- [ ] **NEW: Agent Crew Live Dashboard**
  - Show 8 agents + status (running, idle, outputting)
  - Real-time activity feed
  - Connected to backend via Server-Sent Events (SSE)
  - Demo data (no real prod data exposed)

- [ ] **NEW: Platform Integration Showcase**
  - 12-tile grid (Instagram, TikTok, YouTube, etc.)
  - Each tile: platform icon, usage stats, case study snippet
  - Mocked data for demo

- [ ] **NEW: Pricing Table & CTA Flow**
  - 4 tiers: Starter ($497), Growth ($1,497), Pro ($3,997), Enterprise
  - Features comparison
  - CTA → Contact sales (Calendly embed or form)

- [ ] **NEW: Customer Testimonials Section**
  - Fetch from database or hardcoded JSON
  - Carousel or grid layout
  - Headshots, names, quotes, metrics ("47,200 followers", "6.2x ROAS")

### Phase 3: SEO & Content (Discovery)
- [ ] **NEW: Blog System**
  - Posts stored as MDX (Markdown + JSX)
  - Categories: Platform Updates, How-Tos, News
  - Auto-generate sitemap & RSS feed

- [ ] **NEW: SEO Metadata Framework**
  - Title tags, meta descriptions per page
  - Open Graph tags for social sharing
  - Structured data (JSON-LD for schema.org)

- [ ] **NEW: Mobile Optimization**
  - Responsive design (tested on iPhone 12, iPad Pro)
  - Touch-friendly CTAs (48px minimum)
  - Lighthouse score target: >90

---

## 4. DEVELOPMENT WORKFLOW (Best Practices)

### Local Development
```bash
# Clone & install
git clone https://github.com/kushin77/news-feed-engine
cd news-feed-engine
pnpm install

# Frontend dev server (http://localhost:3000)
cd services/frontend
pnpm dev

# Backend dev server (http://localhost:3001)
cd ../api
pnpm dev

# Run all tests
pnpm test
```

### Secret Management
```bash
# ❌ WRONG: Hardcode secrets
const API_KEY = "sk-abc123";  // SECURITY RISK

# ✅ RIGHT: Fetch from GSM at runtime
import { SecretManagerServiceClient } = require("@google-cloud/secret-manager");
const client = new SecretManagerServiceClient();
const secret = await client.accessSecretVersion({ name: "projects/123/secrets/api-key/versions/latest" });
```

### Code Ownership & Reviews
- Landing page HTML/CSS: **frontend team**
- Email signup API: **backend team**
- Infrastructure (Terraform): **ops team**
- Security: **REQUIRES CODEOWNERS approval**

---

## 5. DEPLOYMENT PIPELINE (Immutable, Ephemeral, Idempotent)

### Pre-Deploy Checklist
```bash
# 1. Verify no secrets in code
bash scripts/scan-for-secrets.sh

# 2. Run tests
pnpm test

# 3. Build locally
pnpm build

# 4. Dry-run deployment
bash scripts/deploy.sh --dry-run --target staging

# 5. If OK, deploy to production
bash scripts/deploy.sh --target production
```

### Deployment Scripts (Manual, Not CI/CD)
- **Location:** `scripts/deploy.sh`
- **Principles:**
  - Fetch credentials at runtime (ephemeral)
  - Idempotent: safe to run multiple times
  - Immutable: Git SHA verified before deploy
  - Rollback: Previous version tag stored

### Monitoring Post-Deploy
- [ ] Frontend loads in <3 seconds (Lighthouse)
- [ ] No JavaScript errors (Sentry dashboard)
- [ ] Email signup converts (SendGrid webhook)
- [ ] API latency <200ms (DataDog APM)

---

## 6. CONTENT STRATEGY

### Homepage Copy (Landing Page)
```
HERO:
"The Media OS That Runs Itself"
Subheading: "Autonomous AI agents that research, create, publish, engage, sell, and reinvest — 24 hours a day."

VALUE PROPS:
1. 8 AI Agents Running  → "Constantly working while you sleep"
2. 12 Platform Connectors → "Post to Instagram, TikTok, YouTube, LinkedIn simultaneously"
3. $XXM Revenue (YTD) → "Powered by data-driven, psychology-first growth"
4. Zero Monthly Fees (LMS model) → "Pay only for what you add to your team"

CTA: "Get Early Access" → Email capture
```

### Messaging Framework
- **For Creators:** "Grow faster with AI agents"  
- **For Agencies:** "White-label media platform for your clients"
- **For Enterprises:** "Proprietary AI system built for your brand"

---

## 7. SECURITY CHECKLIST

### Code
- [ ] No API keys, tokens, or passwords in git history
- [ ] `.env.example` shows structure only (no real values)
- [ ] All secrets fetched from GSM at runtime
- [ ] OWASP Top 10 checked: XSS, SQLi, CSRF, etc.

### Infrastructure
- [ ] HTTPS only (SSL certificate from Let's Encrypt)
- [ ] CORS configured for trusted domains only
- [ ] Rate limiting on all APIs (prevent abuse)
- [ ] WAF (Web Application Firewall) enabled if hosted on managed platform

### Compliance
- [ ] Privacy policy published (GDPR / CCPA ready)
- [ ] Terms of service defined
- [ ] Cookie consent banner (for analytics)
- [ ] Data retention policy documented

---

## 8. ASSET INVENTORY

### Files to Create/Modify
```
services/frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx (homepage / landing)
│   │   ├── pricing.tsx
│   │   ├── features.tsx
│   │   └── blog/[slug].tsx
│   ├── components/
│   │   ├── Hero.tsx
│   │   ├── Agents.tsx (8 agent showcase)
│   │   ├── Testimonials.tsx
│   │   ├── Pricing.tsx
│   │   └── Footer.tsx
│   ├── hooks/
│   │   └── useWaitlist.ts (form logic)
│   └── styles/
│       └── globals.css (Tailwind)
├── public/
│   ├── images/ (logos, screenshots, headshots)
│   └── videos/ (demo, intro)
└── package.json (dependencies)

services/api/
├── routes/
│   └── waitlist.ts (POST /api/waitlist/signup)
├── middleware/
│   ├── auth.ts (verify API key)
│   └── validation.ts (email format, rate limit)
├── services/
│   ├── sendgrid.ts (email service)
│   └── gsm.ts (Google Secret Manager client)
└── package.json

docs/
├── WEBSITE.md (this roadmap)
├── DEPLOYMENT.md (updated with website hosting)
└── SECURITY.md (credential management)

scripts/
└── deploy.sh (manual deployment, no GitHub Actions)
```

---

## 9. SUCCESS METRICS

### Phase 1 (MVP)
- ✅ Homepage live & loads <3 seconds
- ✅ Email capture 100+ signups
- ✅ 0 security findings (Snyk scan)
- ✅ Mobile-friendly (Lighthouse >90)

### Phase 2 (Interactive)
- ✅ Agent dashboard shows live data
- ✅ Testimonials section up (5+ customer quotes)
- ✅ Pricing page converts (CTR >3%)
- ✅ No 404 errors (all links working)

### Phase 3 (Discovery)
- ✅ 10+ blog posts published
- ✅ SEO score >80 (page speed, mobile, core vitals)
- ✅ Organic traffic >500 visitors/month
- ✅ Email open rate >30% (SendGrid analytics)

---

## 10. RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| **Hardcoded secrets leaked** | Audit code with `git secrets`, use GSM only |
| **Website goes offline** | CDN + multi-region deployment, monitoring alerts |
| **Poor mobile experience** | Test on real devices, Lighthouse automated checks |
| **Email signup spam** | Rate limiting (10 signups/hour per IP), CAPTCHA |
| **No SEO ranking** | Meta tags, structured data, sitemap, blog cadence |
| **Feature scope creep** | Phase approach: MVP → showcase → content |

---

## 11. NEXT ACTIONS (This Week)

- [ ] Create GitHub issue: "Website Landing Page MVP"
- [ ] Design homepage wireframe (Figma)
- [ ] Set up React app structure (`services/frontend/`)
- [ ] Implement email capture endpoint (`services/api/routes/waitlist.ts`)
- [ ] Configure Google Secret Manager (credentials at runtime)
- [ ] Write `docs/DEPLOYMENT.md` (manual deploy process)
- [ ] Set up Sentry error tracking
- [ ] Create PR template for website changes

---

**Owner:** Frontend Team  
**Status:** Ready for Phase 1 kickoff  
**Questions?** Open an issue or mention @kushin77
