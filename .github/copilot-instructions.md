# GitHub Copilot Instructions

This repository uses GitHub Copilot for assistance when writing code and documentation.  When interacting with Copilot, keep the following guidelines in mind:

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