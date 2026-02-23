# ElevatedIQ Social Media Platform - Setup Script
# Cross-platform setup for development environment

param(
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$Region = "us-central1",
    [switch]$SkipGcloud,
    [switch]$SkipFirebase,
    [switch]$Development
)

# Colors for PowerShell output
$colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

function Write-Status {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor $colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $colors.Red
    exit 1
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "================================================" -ForegroundColor $colors.Cyan
    Write-Host "  $Title" -ForegroundColor $colors.Cyan
    Write-Host "================================================" -ForegroundColor $colors.Cyan
    Write-Host ""
}

# Validate prerequisites
function Test-Prerequisites {
    Write-Header "Validating Prerequisites"

    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        Write-Error "PowerShell 5.0 or higher required. Current: $($psVersion.ToString())"
    }
    Write-Success "PowerShell version: $($psVersion.ToString())"

    # Check if Node.js is installed
    try {
        $nodeVersion = node --version
        $majorVersion = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
        if ($majorVersion -lt 20) {
            Write-Error "Node.js version 20 or higher required. Current: $nodeVersion"
        }
        Write-Success "Node.js version: $nodeVersion"
    } catch {
        Write-Error "Node.js is not installed or not in PATH. Please install Node.js 20+"
    }

    # Check npm
    try {
        $npmVersion = npm --version
        Write-Success "npm version: $npmVersion"
    } catch {
        Write-Error "npm is not installed or not in PATH"
    }

    # Check gcloud (unless skipped)
    if (-not $SkipGcloud) {
        try {
            $gcloudVersion = gcloud version --format="value(Google Cloud SDK)" 2>$null
            Write-Success "gcloud CLI version: $gcloudVersion"

            # Check authentication
            $activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null | Select-Object -First 1
            if (-not $activeAccount) {
                Write-Error "Not logged into gcloud. Run: gcloud auth login"
            }
            Write-Success "gcloud authentication: $activeAccount"

        } catch {
            Write-Error "gcloud CLI is not installed or not in PATH. Install from: https://cloud.google.com/sdk"
        }
    }

    # Check Firebase CLI (unless skipped)
    if (-not $SkipFirebase) {
        try {
            $firebaseVersion = firebase --version
            Write-Success "Firebase CLI version: $firebaseVersion"
        } catch {
            Write-Warning "Firebase CLI not found. Install with: npm install -g firebase-tools"
        }
    }
}

# Setup project configuration
function Set-ProjectConfig {
    Write-Header "Project Configuration"

    # Get or validate project ID
    if (-not $ProjectId) {
        try {
            $ProjectId = gcloud config get-value project 2>$null
            if (-not $ProjectId) {
                Write-Error "No project ID found. Set with: gcloud config set project YOUR_PROJECT_ID"
            }
        } catch {
            Write-Error "Unable to get project ID from gcloud config"
        }
    }

    Write-Success "Project ID: $ProjectId"

    # Set gcloud project if needed
    if (-not $SkipGcloud) {
        $currentProject = gcloud config get-value project 2>$null
        if ($currentProject -ne $ProjectId) {
            Write-Status "Setting gcloud project to: $ProjectId"
            gcloud config set project $ProjectId
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to set project ID"
            }
        }

        Write-Success "gcloud project configured: $ProjectId"
    }

    return $ProjectId
}

# Enable required APIs
function Enable-RequiredAPIs {
    param([string]$ProjectId)

    Write-Header "Enabling Required APIs"

    $requiredAPIs = @(
        "cloudfunctions.googleapis.com",
        "firestore.googleapis.com",
        "secretmanager.googleapis.com",
        "cloudscheduler.googleapis.com"
    )

    foreach ($api in $requiredAPIs) {
        Write-Status "Checking API: $api"

        $enabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null
        if (-not $enabled) {
            Write-Status "Enabling API: $api"
            gcloud services enable $api --project=$ProjectId
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to enable API: $api"
            }
            Write-Success "API enabled: $api"
        } else {
            Write-Success "API already enabled: $api"
        }
    }
}

# Setup development environment
function Set-DevelopmentEnvironment {
    Write-Header "Setting up Development Environment"

    # Create .env file for local development
    $envFile = ".env.local"
    $envContent = @"
# ElevatedIQ Social Media Platform - Development Environment
# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$ProjectId
GOOGLE_CLOUD_REGION=$Region

# Development Settings
NODE_ENV=development
LOG_LEVEL=debug

# Local Testing
LOCAL_FIRESTORE_EMULATOR=false
LOCAL_FUNCTIONS_EMULATOR=false

# Platform API Keys (Set these in Secret Manager for production)
# INSTAGRAM_ACCESS_TOKEN=
# FACEBOOK_ACCESS_TOKEN=
# TWITTER_API_KEY=
# LINKEDIN_ACCESS_TOKEN=
# TIKTOK_ACCESS_TOKEN=
# YOUTUBE_API_KEY=
# PINTEREST_ACCESS_TOKEN=
# SNAPCHAT_ACCESS_TOKEN=
# THREADS_ACCESS_TOKEN=

"@

    if (Test-Path $envFile) {
        Write-Warning "Environment file already exists: $envFile"
        $overwrite = Read-Host "Overwrite existing file? (y/N)"
        if ($overwrite -eq 'y' -or $overwrite -eq 'Y') {
            $envContent | Out-File -FilePath $envFile -Encoding UTF8
            Write-Success "Environment file updated: $envFile"
        }
    } else {
        $envContent | Out-File -FilePath $envFile -Encoding UTF8
        Write-Success "Environment file created: $envFile"
    }

    # Create .gitignore additions
    $gitignoreAdditions = @"

# ElevatedIQ Social Media Platform
.env.local
.env.production
functions-framework-nodejs/
firebase-debug.log
firestore-debug.log
ui-debug.log

"@

    if (Test-Path ".gitignore") {
        $existingGitignore = Get-Content ".gitignore" -Raw
        if ($existingGitignore -notlike "*ElevatedIQ Social Media Platform*") {
            Add-Content -Path ".gitignore" -Value $gitignoreAdditions
            Write-Success "Updated .gitignore with platform exclusions"
        }
    } else {
        $gitignoreAdditions | Out-File -FilePath ".gitignore" -Encoding UTF8
        Write-Success "Created .gitignore with platform exclusions"
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Header "Installing Dependencies"

    # Check if package.json exists
    if (-not (Test-Path "package.json")) {
        Write-Error "package.json not found. Run this script from the functions directory."
    }

    # Install npm dependencies
    Write-Status "Installing npm packages..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install npm dependencies"
    }
    Write-Success "npm dependencies installed"

    # Install development dependencies if in development mode
    if ($Development) {
        Write-Status "Installing development dependencies..."

        $devDependencies = @(
            "nodemon",
            "eslint",
            "prettier",
            "@google-cloud/functions-framework"
        )

        foreach ($dep in $devDependencies) {
            npm list $dep --depth=0 2>$null | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Status "Installing $dep..."
                npm install --save-dev $dep
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Installed: $dep"
                }
            }
        }
    }
}

# Setup local testing
function Set-LocalTesting {
    Write-Header "Setting up Local Testing"

    # Create test script in package.json
    $packageJson = Get-Content "package.json" | ConvertFrom-Json

    if (-not $packageJson.scripts) {
        $packageJson | Add-Member -Type NoteProperty -Name scripts -Value @{}
    }

    $packageJson.scripts | Add-Member -Type NoteProperty -Name "start:local" -Value "functions-framework --target=schedulePost --port=8080" -Force
    $packageJson.scripts | Add-Member -Type NoteProperty -Name "test:schedule" -Value "curl -X POST http://localhost:8080 -H 'Content-Type: application/json' -d '{\"platforms\":[\"instagram\"],\"caption\":\"Test post\",\"imageUrl\":\"https://via.placeholder.com/1080x1080\"}'" -Force

    $packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
    Write-Success "Added local testing scripts to package.json"

    # Create local test files
    $testDir = "test"
    if (-not (Test-Path $testDir)) {
        New-Item -ItemType Directory -Path $testDir | Out-Null
        Write-Success "Created test directory: $testDir"
    }

    # Sample test file
    $testContent = @"
// ElevatedIQ Social Media Platform - Sample Tests
// Run with: npm test

const assert = require('assert');
const { schedulePost, analytics } = require('../index.js');

describe('Social Media Platform', () => {
    describe('Schedule Post', () => {
        it('should validate required parameters', async () => {
            // Add your test cases here
            assert(true, 'Test placeholder');
        });
    });

    describe('Analytics', () => {
        it('should return analytics data', async () => {
            // Add your test cases here
            assert(true, 'Test placeholder');
        });
    });
});
"@

    $testFile = "$testDir/platform.test.js"
    if (-not (Test-Path $testFile)) {
        $testContent | Out-File -FilePath $testFile -Encoding UTF8
        Write-Success "Created sample test file: $testFile"
    }
}

# Create deployment summary
function Write-SetupSummary {
    param([string]$ProjectId)

    Write-Header "Setup Summary"

    Write-Host ""
    Write-Host "🎉 ElevatedIQ Social Media Platform - Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Configuration:" -ForegroundColor Cyan
    Write-Host "   • Project ID:      $ProjectId"
    Write-Host "   • Region:          $Region"
    Write-Host "   • Environment:     $(if ($Development) { 'Development' } else { 'Production' })"
    Write-Host ""
    Write-Host "📦 Dependencies:" -ForegroundColor Cyan
    Write-Host "   • Node.js:         $(node --version)"
    Write-Host "   • npm:             $(npm --version)"
    if (-not $SkipGcloud) {
        Write-Host "   • gcloud:          $(gcloud version --format='value(Google Cloud SDK)' 2>$null)"
    }
    Write-Host ""
    Write-Host "🔧 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Configure platform API credentials:"
    Write-Host "      • Add secrets to Google Secret Manager"
    Write-Host "      • Update .env.local for local testing"
    Write-Host ""
    Write-Host "   2. Deploy the platform:"
    Write-Host "      • Run: .\scripts\deployment\deploy.ps1"
    Write-Host "      • Or: bash scripts/deployment/deploy.sh"
    Write-Host ""
    Write-Host "   3. Start local development:"
    Write-Host "      • Run: npm run start:local"
    Write-Host "      • Test: npm run test:schedule"
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Cyan
    Write-Host "   • Quick Start:     docs/quickstart/README.md"
    Write-Host "   • Architecture:    docs/architecture/README.md"
    Write-Host "   • API Reference:   docs/api/README.md"
    Write-Host ""
    Write-Host "🎯 Support:" -ForegroundColor Cyan
    Write-Host "   • Issues:          https://github.com/kushin77/elevatedIQ/issues"
    Write-Host "   • Documentation:   https://docs.elevatediq.ai"
    Write-Host ""

    Write-Success "Setup completed successfully! 🚀"
}

# Main setup function
function Start-Setup {
    Write-Header "ElevatedIQ Social Media Platform - Setup"

    # Validate prerequisites
    Test-Prerequisites

    # Configure project
    $configuredProjectId = Set-ProjectConfig

    # Enable APIs (unless skipped)
    if (-not $SkipGcloud) {
        Enable-RequiredAPIs -ProjectId $configuredProjectId
    }

    # Setup development environment
    Set-DevelopmentEnvironment

    # Install dependencies
    Install-Dependencies

    # Setup local testing if in development mode
    if ($Development) {
        Set-LocalTesting
    }

    # Show summary
    Write-SetupSummary -ProjectId $configuredProjectId
}

# Run setup if script is executed directly
if ($MyInvocation.InvocationName -ne '.') {
    Start-Setup
}
