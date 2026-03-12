Repository Actions Migration Notice

This repository has adopted a direct-deploy, direct-development model.

- All GitHub Actions workflows are deprecated. Do not re-enable them.
- Use `scripts/direct-deploy.sh` or runtime automation (systemd, cron, scheduler) to perform deploys.
- Operators must migrate secrets to GSM/Vault/KMS and avoid GitHub Actions secrets.

If you need help migrating specific workflow logic into runtime scripts, open an internal issue and tag the infra team.