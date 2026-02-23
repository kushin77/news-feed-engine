# ElevatedIQ Social Media Platform - Scripts Directory

This directory contains comprehensive deployment and management scripts for the ElevatedIQ Social Media Platform.

## 📁 Directory Structure

```
scripts/
├── deployment/           # Deployment automation
│   ├── deploy.sh        # Linux/Mac deployment script
│   └── deploy.bat       # Windows deployment script
├── setup/               # Environment setup
│   ├── setup.sh         # Linux/Mac setup script
│   └── setup.ps1        # Windows PowerShell setup script
├── config/              # Configuration management
│   ├── config.sh        # Linux/Mac config management
│   └── config.ps1       # Windows PowerShell config management
└── README.md           # This file
```bash

## 🚀 Quick Start

### 1. Initial Setup

## Linux/Mac

```bash
# Basic setup
./scripts/setup/setup.sh --project-id YOUR_PROJECT_ID

# Development setup with testing tools
./scripts/setup/setup.sh --project-id YOUR_PROJECT_ID --development
```bash

## Windows

```powershell
# Basic setup
.\scripts\setup\setup.ps1 -ProjectId YOUR_PROJECT_ID

# Development setup
.\scripts\setup\setup.ps1 -ProjectId YOUR_PROJECT_ID -Development
```bash

### 2. Configure Platform Credentials

## Interactive Configuration (Recommended)

```bash
# Linux/Mac
./scripts/config/config.sh interactive

# Windows
.\scripts\config\config.ps1 -Action interactive
```bash

## Manual Configuration

```bash
# Linux/Mac - Add Instagram token
./scripts/config/config.sh add instagram access_token --interactive

# Windows - Add Instagram token
.\scripts\config\config.ps1 -Action add -Platform instagram -SecretName access_token -Interactive
```bash

### 3. Deploy Platform

## Linux/Mac

```bash
./scripts/deployment/deploy.sh
```bash

## Windows

```powershell
.\scripts\deployment\deploy.bat
```bash

## 📋 Script Details

### Setup Scripts

**Purpose:** Initialize development environment and configure prerequisites

## Features

- ✅ Validate Node.js, gcloud CLI, and other dependencies
- ✅ Configure Google Cloud project and enable required APIs
- ✅ Create environment files and development configuration
- ✅ Install npm dependencies
- ✅ Set up local testing infrastructure

## Usage Examples

```bash
# Full development setup
./scripts/setup/setup.sh --project-id my-project --development

# CI/CD setup (skip interactive tools)
./scripts/setup/setup.sh --project-id my-project --skip-gcloud --skip-firebase

# Help
./scripts/setup/setup.sh --help
```bash

### Configuration Scripts

**Purpose:** Manage social media platform API credentials and secrets

## Supported Platforms

- 📱 Instagram (Graph API v18.0)
- 📘 Facebook (Pages API)
- 🐦 Twitter (API v2)
- 💼 LinkedIn (UGC API)
- 🎵 TikTok (Content Posting API)
- 📺 YouTube (Data API v3)
- 📌 Pinterest (API v5)
- 👻 Snapchat (Marketing API)
- 🧵 Threads (Meta API)

## Key Features

- 🔐 Secure secret management via Google Secret Manager
- 📊 Configuration validation and status checking
- 🧙‍♂️ Interactive configuration wizard
- 📤 Export/import configuration templates
- 🔄 Cross-platform compatibility

## Usage Examples

```bash
# List all platform configurations
./scripts/config/config.sh list

# Interactive setup wizard
./scripts/config/config.sh interactive

# Add specific platform credential
./scripts/config/config.sh add instagram access_token --interactive

# Validate all configurations
./scripts/config/config.sh validate

# Export configuration template
./scripts/config/config.sh export
```bash

### Deployment Scripts

**Purpose:** Deploy Cloud Functions and set up production infrastructure

## Deployment Components

- ☁️ Google Cloud Functions (schedulePost, publishScheduledPosts, analytics)
- ⏰ Cloud Scheduler for automated publishing
- 🗄️ Firestore database initialization
- 🔐 Secret Manager configuration
- 📊 Health checks and validation

## Features

- 🔍 Comprehensive pre-deployment validation
- 📦 Dependency installation and syntax checking
- 🚀 Automated function deployment with proper configuration
- ⚙️ Infrastructure setup (Firestore, Scheduler, APIs)
- 🧪 Post-deployment testing and verification
- 📋 Detailed deployment summary

## Usage Examples

```bash
# Standard deployment
./scripts/deployment/deploy.sh

# Windows deployment
.\scripts\deployment\deploy.bat

# Check deployment logs
gcloud functions logs tail publishScheduledPosts --region=us-central1
```bash

## 🛠️ Advanced Configuration

### Environment Variables

## Setup Scripts

```bash
GOOGLE_CLOUD_PROJECT=your-project     # Google Cloud Project ID
REGION=us-central1                    # Deployment region
SKIP_GCLOUD=false                     # Skip gcloud CLI validation
SKIP_FIREBASE=false                   # Skip Firebase CLI validation
DEVELOPMENT=false                     # Enable development tools
```bash

## Config Scripts

```bash
GOOGLE_CLOUD_PROJECT=your-project     # Google Cloud Project ID
```bash

## Deploy Scripts

```bash
GOOGLE_CLOUD_PROJECT=your-project     # Google Cloud Project ID
REGION=us-central1                    # Deployment region
```bash

### Cross-Platform Support

All scripts are designed to work across different operating systems:

- **Linux/Mac:** Bash scripts (`.sh` files)
- **Windows:** Batch (`.bat`) and PowerShell (`.ps1`) scripts
- **CI/CD:** Support for headless automation

### Error Handling

Scripts include comprehensive error handling:

- 🔍 Pre-flight validation checks
- 🚨 Clear error messages with suggested fixes
- 🔄 Rollback capabilities where applicable
- 📊 Status reporting and progress tracking

## 🔧 Troubleshooting

### Common Issues

## 1. Permission Errors

```bash
# Fix script permissions (Linux/Mac)
chmod +x scripts/setup/setup.sh
chmod +x scripts/config/config.sh
chmod +x scripts/deployment/deploy.sh
```bash

## 2. gcloud Authentication

```bash
# Login to gcloud
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```bash

## 3. Node.js Version

```bash
# Check Node.js version (requires 20+)
node --version

# Install via nvm (recommended)
nvm install 20
nvm use 20
```bash

## 4. Missing Dependencies

```bash
# Install missing tools
npm install -g firebase-tools
npm install -g @google-cloud/functions-framework
```bash

### Debug Mode

Enable verbose output for troubleshooting:

## Linux/Mac

```bash
set -x  # Enable debug mode
./scripts/setup/setup.sh --project-id YOUR_PROJECT_ID
```bash

## Windows

```powershell
$VerbosePreference = "Continue"
.\scripts\setup\setup.ps1 -ProjectId YOUR_PROJECT_ID -Verbose
```bash

### Log Files

Scripts generate logs in:

- 📁 `./logs/` (if created)
- 📋 Console output (all platforms)
- ☁️ Google Cloud Logging (after deployment)

## 🎯 Best Practices

### Security

- 🔐 Always use interactive mode for entering secrets
- 🚫 Never commit API keys to version control
- ✅ Validate configurations before deployment
- 🔄 Rotate credentials regularly

### Development Workflow

1. **Setup:** Run setup script with `--development` flag
2. **Configure:** Use interactive configuration wizard
3. **Test:** Use local testing scripts
4. **Deploy:** Deploy to staging environment first
5. **Validate:** Run post-deployment tests
6. **Monitor:** Check logs and metrics

### Production Deployment

1. **Validate:** Ensure all configurations are complete
2. **Backup:** Export current configuration
3. **Deploy:** Use production deployment settings
4. **Monitor:** Watch deployment logs
5. **Test:** Verify all functions are working
6. **Document:** Update deployment records

## 📚 Additional Resources

- **Architecture Documentation:** `../docs/architecture/README.md`
- **API Reference:** `../docs/api/README.md`
- **Quick Start Guide:** `../docs/quickstart/README.md`
- **Platform Guidelines:** `../docs/platforms/`

## 🆘 Support

If you encounter issues:

1. **Check Prerequisites:** Ensure all required tools are installed
2. **Review Logs:** Check script output for error messages
3. **Validate Configuration:** Run `config.sh validate` or `config.ps1 -Action validate`
4. **Documentation:** Review platform-specific documentation
5. **Issues:** Create issue at <https://github.com/kushin77/elevatedIQ/issues>

---

**ElevatedIQ Social Media Platform** | **Deployment Made Simple** 🚀
