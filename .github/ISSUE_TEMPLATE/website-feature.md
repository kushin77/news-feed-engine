---
name: Website Feature
about: A new feature, page, or component for the ElevateIQ marketing website
title: "[WEBSITE] "
labels: ["website", "enhancement"]
assignees: kushin77
---

## Description
<!-- Clear, concise description of what you're building for the website -->

## User Story
<!-- Optional: Describe from the user's perspective -->
- As a [user type], I want [action], so that [benefit]

## Acceptance Criteria
<!-- What needs to be true for this issue to be "done"? -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Details
<!-- How should this be implemented? Any API requirements, data sources, etc. -->

### Frontend Components
<!-- React components needing to be built -->
- [ ] Component 1
- [ ] Component 2

### Backend Requirements
<!-- API endpoints, database queries, integrations -->
- [ ] Endpoint: `POST /api/...`
- [ ] Database: `table_name`

### External Services
<!-- SendGrid, Sentry, GSM, etc. -->
- [ ] Service: purpose

## Design / Mockup
<!-- Link to Figma, screenshot, or description of visual design -->

## Security Checklist
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] All secrets fetched from Google Secret Manager at runtime
- [ ] No `.env` files committed
- [ ] Input validation on all forms (XSS prevention)
- [ ] Rate limiting applied to API endpoints

## Testing Requirements
- [ ] Unit tests written (Jest/Vitest)
- [ ] Component tests in React Testing Library
- [ ] Manual testing on desktop + mobile
- [ ] Lighthouse score check (target: >90)

## Deployment Checklist
- [ ] Changes are idempotent (safe to apply multiple times)
- [ ] No database migrations required (or rollback plan documented)
- [ ] Monitoring alerts configured (Sentry error tracking)
- [ ] Tested on staging environment first

## Related Issues
<!-- Link to related GitHub issues or PRs -->
- Relates to #
- Blocked by #

## Definition of Done
- [ ] Code review approved by @kushin77
- [ ] All acceptance criteria met
- [ ] Tests passing (Vitest + React Testing Library)
- [ ] Documentation updated (if applicable)
- [ ] Deployed to staging and verified
- [ ] Ready for production merge to main
