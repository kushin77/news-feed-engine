#!/bin/bash

# ElevatedIQ Social Media Platform - Setup Script
# Cross-platform setup for development environment

set -e  # Exit on error

# Default configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${REGION:-"us-central1"}
SKIP_GCLOUD=${SKIP_GCLOUD:-false}
SKIP_FIREBASE=${SKIP_FIREBASE:-false}
DEVELOPMENT=${DEVELOPMENT:-false}

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e \"${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}\"
}

print_success() {
    echo -e \"${GREEN}✅ $1${NC}\"
}

print_warning() {
    echo -e \"${YELLOW}⚠️  $1${NC}\"
}

print_error() {
    echo -e \"${RED}❌ $1${NC}\"
    exit 1
}

print_header() {
    echo -e \"\\n${CYAN}================================================${NC}\"
    echo -e \"${CYAN}  $1${NC}\"
    echo -e \"${CYAN}================================================${NC}\\n\"
}

# Show usage information
show_usage() {
    cat << EOF
ElevatedIQ Social Media Platform - Setup Script

Usage: $0 [OPTIONS]

Options:
    --project-id PROJECT_ID    Google Cloud Project ID
    --region REGION           Google Cloud Region (default: us-central1)
    --skip-gcloud            Skip gcloud CLI validation and setup
    --skip-firebase          Skip Firebase CLI validation
    --development            Setup development environment with testing tools
    --help                   Show this help message

Environment Variables:
    GOOGLE_CLOUD_PROJECT     Google Cloud Project ID
    REGION                   Google Cloud Region
    SKIP_GCLOUD             Skip gcloud setup (true/false)
    SKIP_FIREBASE           Skip Firebase setup (true/false)
    DEVELOPMENT             Development mode (true/false)

Examples:
    # Basic setup
    $0 --project-id my-project

    # Development setup with local testing
    $0 --project-id my-project --development

    # Setup without gcloud CLI (CI/CD environments)
    $0 --project-id my-project --skip-gcloud --skip-firebase
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID=\"$2\"
                shift 2
                ;;
            --region)
                REGION=\"$2\"
                shift 2
                ;;
            --skip-gcloud)
                SKIP_GCLOUD=true
                shift
                ;;
            --skip-firebase)
                SKIP_FIREBASE=true
                shift
                ;;
            --development)
                DEVELOPMENT=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error \"Unknown option: $1. Use --help for usage information.\"
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    print_header \"Validating Prerequisites\"

    # Check bash version
    if [ \"${BASH_VERSION%%.*}\" -lt 4 ]; then
        print_error \"Bash 4.0 or higher required. Current: $BASH_VERSION\"
    fi
    print_success \"Bash version: $BASH_VERSION\"

    # Check if node is installed
    if ! command -v node &> /dev/null; then
        print_error \"Node.js is not installed. Please install Node.js 20+\"
    fi

    # Check Node version
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [ \"$MAJOR_VERSION\" -lt \"20\" ]; then
        print_error \"Node.js version 20 or higher required. Current: v$NODE_VERSION\"
    fi
    print_success \"Node.js version: v$NODE_VERSION\"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error \"npm is not installed or not in PATH\"
    fi
    NPM_VERSION=$(npm --version)
    print_success \"npm version: $NPM_VERSION\"

    # Check gcloud (unless skipped)
    if [ \"$SKIP_GCLOUD\" != \"true\" ]; then
        if ! command -v gcloud &> /dev/null; then
            print_error \"gcloud CLI is not installed. Install from: https://cloud.google.com/sdk\"
        fi

        GCLOUD_VERSION=$(gcloud version --format=\"value(Google Cloud SDK)\" 2>/dev/null)
        print_success \"gcloud CLI version: $GCLOUD_VERSION\"

        # Check authentication
        ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format=\"value(account)\" 2>/dev/null | head -n1)
        if [ -z \"$ACTIVE_ACCOUNT\" ]; then
            print_error \"Not logged into gcloud. Run: gcloud auth login\"
        fi
        print_success \"gcloud authentication: $ACTIVE_ACCOUNT\"
    fi

    # Check Firebase CLI (unless skipped)
    if [ \"$SKIP_FIREBASE\" != \"true\" ]; then
        if ! command -v firebase &> /dev/null; then
            print_warning \"Firebase CLI not found. Install with: npm install -g firebase-tools\"
        else
            FIREBASE_VERSION=$(firebase --version)
            print_success \"Firebase CLI version: $FIREBASE_VERSION\"
        fi
    fi
}

# Setup project configuration
setup_project_config() {
    print_header \"Project Configuration\"

    # Get or validate project ID
    if [ -z \"$PROJECT_ID\" ]; then
        if [ \"$SKIP_GCLOUD\" != \"true\" ]; then
            PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
            if [ -z \"$PROJECT_ID\" ]; then
                print_error \"No project ID found. Set with: --project-id YOUR_PROJECT_ID\"
            fi
        else
            print_error \"Project ID required when skipping gcloud. Use: --project-id YOUR_PROJECT_ID\"
        fi
    fi

    print_success \"Project ID: $PROJECT_ID\"

    # Set gcloud project if needed
    if [ \"$SKIP_GCLOUD\" != \"true\" ]; then
        CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
        if [ \"$CURRENT_PROJECT\" != \"$PROJECT_ID\" ]; then
            print_status \"Setting gcloud project to: $PROJECT_ID\"
            gcloud config set project \"$PROJECT_ID\"
        fi
        print_success \"gcloud project configured: $PROJECT_ID\"
    fi
}

# Enable required APIs
enable_required_apis() {
    if [ \"$SKIP_GCLOUD\" = \"true\" ]; then
        print_warning \"Skipping API enablement (gcloud disabled)\"
        return
    fi

    print_header \"Enabling Required APIs\"

    REQUIRED_APIS=(
        \"cloudfunctions.googleapis.com\"
        \"firestore.googleapis.com\"
        \"secretmanager.googleapis.com\"
        \"cloudscheduler.googleapis.com\"
    )

    for API in \"${REQUIRED_APIS[@]}\"; do
        print_status \"Checking API: $API\"

        if ! gcloud services list --enabled --filter=\"name:$API\" --format=\"value(name)\" | grep -q \"$API\"; then
            print_status \"Enabling API: $API\"
            gcloud services enable \"$API\" --project=\"$PROJECT_ID\"
            print_success \"API enabled: $API\"
        else
            print_success \"API already enabled: $API\"
        fi
    done
}

# Setup development environment
setup_development_environment() {
    print_header \"Setting up Development Environment\"

    # Create .env file for local development
    ENV_FILE=\".env.local\"
    ENV_CONTENT=\"# ElevatedIQ Social Media Platform - Development Environment
# Generated on $(date -Iseconds)

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_REGION=$REGION

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
\"

    if [ -f \"$ENV_FILE\" ]; then
        print_warning \"Environment file already exists: $ENV_FILE\"
        read -p \"Overwrite existing file? (y/N): \" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo \"$ENV_CONTENT\" > \"$ENV_FILE\"
            print_success \"Environment file updated: $ENV_FILE\"
        fi
    else
        echo \"$ENV_CONTENT\" > \"$ENV_FILE\"
        print_success \"Environment file created: $ENV_FILE\"
    fi

    # Create .gitignore additions
    GITIGNORE_ADDITIONS=\"
# ElevatedIQ Social Media Platform
.env.local
.env.production
functions-framework-nodejs/
firebase-debug.log
firestore-debug.log
ui-debug.log
\"

    if [ -f \".gitignore\" ]; then
        if ! grep -q \"ElevatedIQ Social Media Platform\" \".gitignore\"; then
            echo \"$GITIGNORE_ADDITIONS\" >> \".gitignore\"
            print_success \"Updated .gitignore with platform exclusions\"
        fi
    else
        echo \"$GITIGNORE_ADDITIONS\" > \".gitignore\"
        print_success \"Created .gitignore with platform exclusions\"
    fi
}

# Install dependencies
install_dependencies() {
    print_header \"Installing Dependencies\"

    # Check if package.json exists
    if [ ! -f \"package.json\" ]; then
        print_error \"package.json not found. Run this script from the functions directory.\"
    fi

    # Install npm dependencies
    print_status \"Installing npm packages...\"
    npm install
    print_success \"npm dependencies installed\"

    # Install development dependencies if in development mode
    if [ \"$DEVELOPMENT\" = \"true\" ]; then
        print_status \"Installing development dependencies...\"

        DEV_DEPENDENCIES=(
            \"nodemon\"
            \"eslint\"
            \"prettier\"
            \"@google-cloud/functions-framework\"
        )

        for DEP in \"${DEV_DEPENDENCIES[@]}\"; do
            if ! npm list \"$DEP\" --depth=0 &>/dev/null; then
                print_status \"Installing $DEP...\"
                npm install --save-dev \"$DEP\"
                print_success \"Installed: $DEP\"
            fi
        done
    fi
}

# Setup local testing
setup_local_testing() {
    print_header \"Setting up Local Testing\"

    # Update package.json with test scripts
    if command -v jq &> /dev/null; then
        # Use jq if available for JSON manipulation
        jq '.scripts.\"start:local\" = \"functions-framework --target=schedulePost --port=8080\" |
            .scripts.\"test:schedule\" = \"curl -X POST http://localhost:8080 -H \\\"Content-Type: application/json\\\" -d \\\"{\\\\\\\"platforms\\\\\\\":[\\\\\\\"instagram\\\\\\\"],\\\\\\\"caption\\\\\\\":\\\\\\\"Test post\\\\\\\",\\\\\\\"imageUrl\\\\\\\":\\\\\\\"https://via.placeholder.com/1080x1080\\\\\\\"}\\\"\"' package.json > package.json.tmp && mv package.json.tmp package.json
        print_success \"Added local testing scripts to package.json\"
    else
        print_warning \"jq not found. Please manually add test scripts to package.json\"
    fi

    # Create test directory
    TEST_DIR=\"test\"
    if [ ! -d \"$TEST_DIR\" ]; then
        mkdir -p \"$TEST_DIR\"
        print_success \"Created test directory: $TEST_DIR\"
    fi

    # Sample test file
    TEST_CONTENT=\"// ElevatedIQ Social Media Platform - Sample Tests
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
\"

    TEST_FILE=\"$TEST_DIR/platform.test.js\"
    if [ ! -f \"$TEST_FILE\" ]; then
        echo \"$TEST_CONTENT\" > \"$TEST_FILE\"
        print_success \"Created sample test file: $TEST_FILE\"
    fi
}

# Create setup summary
create_setup_summary() {
    print_header \"Setup Summary\"

    cat << EOF

🎉 ElevatedIQ Social Media Platform - Setup Complete!

📋 Configuration:
   • Project ID:      $PROJECT_ID
   • Region:          $REGION
   • Environment:     $([ \"$DEVELOPMENT\" = \"true\" ] && echo \"Development\" || echo \"Production\")

📦 Dependencies:
   • Node.js:         $(node --version)
   • npm:             $(npm --version)
$([ \"$SKIP_GCLOUD\" != \"true\" ] && echo \"   • gcloud:          $(gcloud version --format='value(Google Cloud SDK)' 2>/dev/null)\")

🔧 Next Steps:
   1. Configure platform API credentials:
      • Add secrets to Google Secret Manager
      • Update .env.local for local testing

   2. Deploy the platform:
      • Run: ./scripts/deployment/deploy.sh
      • Or:  scripts\\deployment\\deploy.bat (Windows)

   3. Start local development:
      • Run: npm run start:local
      • Test: npm run test:schedule

📚 Documentation:
   • Quick Start:     docs/quickstart/README.md
   • Architecture:    docs/architecture/README.md
   • API Reference:   docs/api/README.md

🎯 Support:
   • Issues:          https://github.com/kushin77/elevatedIQ/issues
   • Documentation:   https://docs.elevatediq.ai

EOF

    print_success \"Setup completed successfully! 🚀\"
}

# Main setup function
main() {
    print_header \"ElevatedIQ Social Media Platform - Setup\"

    # Parse arguments
    parse_arguments \"$@\"

    # Validate prerequisites
    validate_prerequisites

    # Configure project
    setup_project_config

    # Enable APIs (unless skipped)
    enable_required_apis

    # Setup development environment
    setup_development_environment

    # Install dependencies
    install_dependencies

    # Setup local testing if in development mode
    if [ \"$DEVELOPMENT\" = \"true\" ]; then
        setup_local_testing
    fi

    # Show summary
    create_setup_summary
}

# Run setup if script is executed directly
if [[ \"${BASH_SOURCE[0]}\" == \"${0}\" ]]; then
    main \"$@\"
fi
