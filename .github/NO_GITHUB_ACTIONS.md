NO GITHUB ACTIONS POLICY
=========================

This repository enforces a strict "NO GITHUB ACTIONS" policy.

- All CI, deployment, and release automation must run from trusted hosts  
  (direct-deploy) or scheduled systemd timers. GitHub Actions workflows are  
  disallowed in this org/project.
- If a workflow file is ever added under `.github/workflows/` it will be  
  removed by the maintenance automation and flagged for review.

To remove workflows locally, run: `scripts/remove_github_workflows.sh`