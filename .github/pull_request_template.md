## Deployment Checklist (Immutable, Ephemeral, Idempotent)

**⚠️ NOTE:** This PR does NOT trigger production deployment. Use direct-deploy after merge:
```bash
bash scripts/manual-deploy-local-key.sh main
```

### Pre-Merge Verification
- [ ] No credentials committed (SSH keys, API tokens, passwords)
- [ ] All commits are immutable (SHA verified)
- [ ] Changes are idempotent (safe to apply multiple times)
- [ ] Updated CREDENTIAL_PROVISIONING_RUNBOOK.md if adding new provisioning logic

### Credential Handling
- [ ] Secrets stored in external managers (Vault/AWS/GSM)
- [ ] No `.env` files or config with credentials committed
- [ ] Environment variables never hardcoded
- [ ] SSH keys fetched at runtime, not persisted

### Policy Compliance
- [ ] Direct-to-main push (no feature branches for production)
- [ ] Manual audit record will be appended in Issue #2072
- [ ] Deployment logs immutable (JSONL + GitHub comments)
- [ ] Rollback procedure documented in audit comment

### Testing
- [ ] Local test: `bash scripts/complete-credential-provisioning.sh --dry-run --phase 1`
- [ ] Script validation: `bash -n scripts/your-new-script.sh`
- [ ] Deployment test: `bash scripts/manual-deploy-local-key.sh staging` (if staging target exists)

---

**Deployment Principles:**
- 🔒 **Immutable:** Git bundles verified via SHA256
- 🌫️ **Ephemeral:** Credentials fetch at runtime, destroyed post-deploy
- ♻️ **Idempotent:** Deploy scripts safe to re-run without side effects
- 🚫 **No-Ops:** Fully automated via watcher + manual scripts (zero manual interventions)
- 🛡️ **Secure:** GSM/VAULT/KMS for all credentials

**See:** [`CREDENTIAL_PROVISIONING_RUNBOOK.md`](../../CREDENTIAL_PROVISIONING_RUNBOOK.md) for full policy.
