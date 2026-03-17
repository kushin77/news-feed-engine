# GitHub Copilot Instructions

This repository uses GitHub Copilot for assistance when writing code and documentation. When interacting with Copilot, keep the following guidelines in mind:

## 🔴 NON-NEGOTIABLE REQUIREMENTS (Every Prompt — Exception: Brainstorming)

**These apply to ALL work unless explicitly marked as "brainstorming only":**

1. **Always Update Issues**
   - Link work to GitHub issues (#number references)
   - Update issue with progress comments
   - Add labels: `in-progress`, `faang`, `security`, `testing`, `frontend`, etc.
   - Close issues when work is complete with brief summary
   - Comment reasoning for any issue skipping/blocking

2. **Always Commit & Push**
   - Commit after every logical unit of work
   - Use conventional commits: `feat(frontend): add React scaffold`, `fix(security): update deps`, `docs(testing): add coverage guide`
   - Push to feature branch immediately after each commit
   - Never leave uncommitted work — every change must be tracked
   - Include issue number in commit: `feat(#110): add vitest setup`

3. **FAANG-Level Quality Standards (Every Output)**
   - **Code**: TypeScript strict mode, no `any`, full type coverage
   - **Testing**: >70% coverage minimum (aim 80%+), unit + integration tests
   - **Security**: No hardcoded secrets, no console.logs in prod, ESLint security rules enforced
   - **Performance**: Lighthouse 90+, <3s LCP, <100ms FID, bundle <100KB (gzip)
   - **Accessibility**: WCAG 2.1 Level AA minimum
   - **Documentation**: Every function/component has JSDoc with examples
   - **Linting**: Zero warnings in ESLint, Prettier formatted, Husky pre-commit hooks
   - **CI/CD**: Green status on all checks, no merge without approval

---

## 🎯 EPIC COMPLETION CHECKLIST (End of Sprint / Epic Close)

**REQUIRED FOR ALL EPICS:** When completing an epic or major work milestone, verify:

### 📋 Process & Reinforcement
- [ ] All work tracked to GitHub issues with #number references
- [ ] Each commit includes issue reference (feat(#110): ...)
- [ ] Feature branch workflow followed (no direct-to-main)
- [ ] Immutable/ephemeral/idempotent principles applied
- [ ] No manual interventions in any script
- [ ] Audit trail recorded (JSONL + GitHub comments)

### 🏃 Speed & Automation
- [ ] Deployment fully automated (bash infrastructure/deploy/{env}.sh)
- [ ] Zero manual configuration steps documented
- [ ] Rollback automated and tested
- [ ] Health checks automatic with clear pass/fail
- [ ] No prerequisites beyond env variables
- [ ] Deployment succeeds on first attempt, every time
- [ ] Post-deployment verification automated

### 🔄 Consistency
- [ ] All environment variables use ELEVATEDIQ_{SERVICE}_{SETTING} format
- [ ] All services follow same folder structure (cmd/, internal/, config/, tests/)
- [ ] No duplicate code (reusable logic in /shared folder)
- [ ] All services follow same deployment pattern
- [ ] All services use same logging/telemetry approach
- [ ] All config loaded from environment or Secret Manager
- [ ] All services follow README.md template

### 🔒 Security
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] All secrets in external manager (GCP Secret Manager, Vault, or KMS)
- [ ] No console.logs that expose sensitive data
- [ ] ESLint security rules pass with zero warnings
- [ ] Credentials ephemeral (fetch at runtime, expire after use)
- [ ] TLS/SSL enabled for all network communication
- [ ] Rate limiting implemented on all public endpoints
- [ ] JWT validation enforced on protected routes
- [ ] Service accounts follow naming convention (elevatediq-sa)
- [ ] Least privilege RBAC enforced

### 🔍 Gap Analysis & Overlaps
- [ ] All code duplication identified and documented
- [ ] Shared code extracted to /shared folder
- [ ] No TODO comments remaining (all actionable items tracked as issues)
- [ ] No hardcoded values (all configurable via env vars)
- [ ] No multiple implementations of same functionality
- [ ] Architecture documented in ARCHITECTURE.md

### ☑️ Enforcement & Governance
- [ ] CODEOWNERS file valid and enforced
- [ ] Code review approval required (via GitHub)
- [ ] All status checks passing (tests, linting, security)
- [ ] Pre-commit hooks enforce standards (no secrets, no console.logs, lint)
- [ ] Pre-push hooks verify test coverage and build success
- [ ] Dependabot configured and monitored
- [ ] Security scanning enabled (secret patterns, vulnerability scan)

### 👥 Service Accounts & Naming
- [ ] All services follow naming: elevatediq-{function} (e.g., elevatediq-feed)
- [ ] All GCP service accounts follow naming: elevatediq-{env}-sa
- [ ] All Kubernetes service accounts follow naming: elevatediq-{service}
- [ ] All database users follow naming: elevatediq_{env}_{service}
- [ ] All S3 buckets follow naming: elevatediq-{region}-{purpose}
- [ ] All DNS entries follow naming: {service}.elevatediq.ai
- [ ] Service account permissions verified (least privilege)
- [ ] Key rotation policies enforced (>30 days max age)

### 📊 Optimization
- [ ] Frontend bundle size <100KB gzipped (verify: npm run build && du -sh dist)
- [ ] Lighthouse scores 90+ in all categories
- [ ] Backend response time <100ms p99
- [ ] Database queries <50ms average
- [ ] Memory footprint documented and reasonable
- [ ] CPU usage profiled and optimized
- [ ] No memory leaks (long-running stability verified)

### 🏛️ Portal (Admin Dashboard)
- [ ] Appsmith/Admin portal integrated with backend
- [ ] Read-only dashboards for monitoring
- [ ] User management with RBAC
- [ ] SSO configured (Google OAuth / Entra ID)
- [ ] Audit logging enabled
- [ ] On-call alerts configured
- [ ] Runbooks linked in portal

### 🔗 Backend Integration
- [ ] API contracts formalized (OpenAPI spec or Postman collection)
- [ ] All endpoints documented with curl examples
- [ ] All database schemas documented
- [ ] All error codes standardized and documented
- [ ] All async workflows documented (webhooks, callbacks)
- [ ] Health check endpoints working (/health, /ready, /metrics)
- [ ] Metrics exposed on Prometheus endpoint
- [ ] Tracing configured (OTLP collector)

### 🧪 Testing & Quality
- [ ] Unit test coverage >70% across all services
- [ ] Integration tests pass (end-to-end flow)
- [ ] Performance tests documented (load, latency, memory)
- [ ] Security tests pass (OWASP Top 10 scan)
- [ ] Manual QA checklist completed
- [ ] Staging environment identical to production

### 📝 Documentation
- [ ] README.md updated with latest changes
- [ ] API documentation current (OpenAPI spec or Postman)
- [ ] Deployment runbook updated
- [ ] On-call runbook created
- [ ] Known issues documented
- [ ] Example configurations provided (.env.template)
- [ ] Troubleshooting guide created

### 🚀 Git Workflow
- [ ] Feature branch commits follow conventional commit format
- [ ] All commits include issue reference (#XXX)
- [ ] Code review approved by CODEOWNERS
- [ ] PR template completed and verified
- [ ] Signed commits enabled (GPG or SSH)
- [ ] Merge to main (no fast-forward: --no-ff)
- [ ] Feature branch deleted (local and remote)
- [ ] Release tags created for versions

### ✅ Pre-Go-Live (If applicable)
- [ ] All resources in production environment verified
- [ ] Database backups configured and tested
- [ ] Monitoring and alerting active and tested
- [ ] SSL certificates valid and not expiring soon
- [ ] On-call team trained and available
- [ ] Incident response procedure documented
- [ ] Rollback procedure tested and verified
- [ ] 99.95% SLA infrastructure in place
- [ ] Auto-scaling policies tested
- [ ] CDN cache headers optimized
- [ ] Load balancing configured

### 📊 Issue Closure
- [ ] All blocked issues unblocked or documented
- [ ] All related tickets closed or reclassified
- [ ] Completion summary added to issue (5-10 bullet points)
- [ ] PR linked from issue
- [ ] Performance metrics updated (if applicable)
- [ ] Follow-up work tracked in new issues

---

1. **No GitHub Actions**
   - The project enforces a strict "NO GITHUB ACTIONS" policy. All CI, deployment, and release automation runs on trusted hosts or scheduled timers. Do not suggest, create, or modify workflows under `.github/workflows/`.
   - If you see a workflow file you believe is necessary, open an issue instead of committing it.

2. **Deployment & Credential Handling**
   - Deployments follow the immutable/ephemeral/idempotent principles described in `.github/pull_request_template.md`.
   - Secrets must be stored in external managers (Vault/GSM/KMS); never hardcode them or create `.env` files.

3. **Code Ownership & Reviews**
   - Refer to `CODEOWNERS` for review requirements; changes to infrastructure, docs, or security must be approved by the ops/platform team.

4. **Dependency Management**
   - Dependabot configuration is defined in `.github/dependabot.yml`. Keep dependencies up-to-date and follow the weekly PRs.

5. **Secret Scanning**
   - Custom patterns defined in `.github/secret-scanning-patterns.yml` help detect sensitive data. Avoid introducing new patterns without review.

6. **Issue Templates & Project Management**
   - Use existing templates in `.github/ISSUE_TEMPLATE/` when opening new issues. Tailor descriptions to provide clear context and steps.

7. **General Best Practices**
   - Write clear, maintainable code and documentation.
   - Follow the existing style of the repository (Go for core services, Python for processor, etc.).
   - When unsure, ask a human reviewer—contributors and maintainers are listed in the CODEOWNERS file.

These instructions are intended to help Copilot generate suggestions that align with project policies and workflows. If you’re unsure whether a suggestion complies with these rules, consult the repository maintainers or open an issue for clarification.