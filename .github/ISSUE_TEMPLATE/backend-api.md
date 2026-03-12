---
name: Backend API Feature
about: A new API endpoint or backend service for the website or platform
title: "[API] "
labels: ["backend", "enhancement"]
assignees: kushin77
---

## Description
<!-- What API endpoint or backend service are you building? -->

## Endpoint Details
```
METHOD: GET|POST|PUT|DELETE
Path: /api/v1/resource
Authentication: OAuth | API Key | None
Rate Limit: X requests per minute
```

## Request Body
```json
{
  "field": "type or example",
  "field2": "type or example"
}
```

## Response (Success - 200)
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "field": "value"
  }
}
```

## Response (Error - 4xx/5xx)
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

## Database Requirements
<!-- What tables, queries, or schema changes needed? -->
- [ ] Requires new table: `table_name`
- [ ] Requires new column: `table_name.column_name`
- [ ] Requires migration script

## External Service Integrations
<!-- SendGrid, GSM, Stripe, etc. -->
- [ ] Service: [SendGrid | Google Secret Manager | etc]
- [ ] Purpose: [what is it used for?]
- [ ] Authentication: [how is the secret managed?]

## Security Requirements
- [ ] Input validation (type, length, format)
- [ ] SQL injection prevention (parameterized queries)
- [ ] CORS configured correctly
- [ ] Rate limiting enforced
- [ ] No hardcoded API keys or credentials
- [ ] All secrets fetched from Google Secret Manager
- [ ] Follows OWASP Top 10 guidelines

## Testing Requirements
- [ ] Unit tests for business logic (Jest/Vitest)
- [ ] Integration tests with database
- [ ] API tests (Thunder Client / Postman collection)
- [ ] Error cases covered (400, 401, 403, 404, 500)
- [ ] Load testing for rate limits (optional)

## Monitoring & Logging
- [ ] Sentry error tracking configured
- [ ] DataDog APM instrumented (optional)
- [ ] Structured logging added (JSON format)
- [ ] Success/failure metrics tracked

## Performance Requirements
- [ ] Target latency: <200ms p95
- [ ] Database query optimized (explain plan reviewed)
- [ ] No N+1 queries
- [ ] Caching strategy defined (if applicable)

## Deployment Checklist
- [ ] All tests passing
- [ ] Code review approved
- [ ] Database migration tested (if applicable)
- [ ] Staging deployment verified
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

## Documentation
- [ ] API documentation updated
- [ ] Swagger/OpenAPI spec updated (if applicable)
- [ ] Example cURL requests included
- [ ] Error codes documented

## Related Issues
<!-- Link to related GitHub issues or PRs -->
- Part of #
- Blocked by #
- Depends on #

## Definition of Done
- [ ] Code approved by @kushin77
- [ ] All acceptance criteria met
- [ ] Tests passing (100% coverage for new code)
- [ ] Staged and verified
- [ ] Ready for production merge to main
