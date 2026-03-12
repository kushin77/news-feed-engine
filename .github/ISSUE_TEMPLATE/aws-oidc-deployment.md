## Overview

This issue tracks the deployment of AWS OIDC Federation integration, replacing long-lived AWS access keys with temporary STS credentials.

## Deployment Details

- **Phase**: Tier 2 - AWS Credential Management
- **Status**: ✋ In Progress
- **Deployment Method**: Terraform + GitHub Actions
- **Target**: AWS Account `{{ AWS_ACCOUNT_ID }}`
- **GitHub Repository**: `kushin77/self-hosted-runner`

## Pre-Deployment Checklist

- [ ] AWS account access verified
- [ ] Terraform installed and configured
- [ ] GitHub CLI installed (`gh`)
- [ ] Required AWS permissions:
  - [ ] `iam:CreateOpenIDConnectProvider`
  - [ ] `iam:CreateRole`
  - [ ] `iam:PutRolePolicy`
  - [ ] `iam:CreateServiceLinkedRole`
- [ ] GitHub token available (for API updates)
- [ ] No existing OIDC provider conflicts

<!-- rest of the template truncated for brevity -->
