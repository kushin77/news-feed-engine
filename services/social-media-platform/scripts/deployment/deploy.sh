#!/bin/bash

# ElevatedIQ Social Media Platform - Master Deployment Script
# Deploys all Cloud Functions and sets up the complete environment

set -e  # Exit on error

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${REGION:-"us-central1"}
FUNCTION_SOURCE="."

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

# Validate prerequisites
validate_prerequisites() {
    print_header \"Validating Prerequisites\"

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error \"gcloud CLI is not installed. Please install it first.\"
    fi
    print_success \"gcloud CLI found\"

    # Check if node is installed
    if ! command -v node &> /dev/null; then
        print_error \"Node.js is not installed. Please install Node.js 20+\"
    fi
    print_success \"Node.js found\"

    # Check Node version
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [ \"$MAJOR_VERSION\" -lt \"20\" ]; then
        print_error \"Node.js version 20 or higher required. Current: v$NODE_VERSION\"
    fi
    print_success \"Node.js version: v$NODE_VERSION\"

    # Check if logged into gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format=\"value(account)\" | head -n1 > /dev/null; then
        print_error \"Not logged into gcloud. Run: gcloud auth login\"
    fi
    print_success \"gcloud authentication verified\"

    # Get project ID if not set
    if [ -z \"$PROJECT_ID\" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z \"$PROJECT_ID\" ]; then
            print_error \"No project ID set. Set GOOGLE_CLOUD_PROJECT or run: gcloud config set project YOUR_PROJECT\"
        fi
    fi
    print_success \"Project ID: $PROJECT_ID\"

    # Check required APIs
    print_status \"Checking required APIs...\"
    REQUIRED_APIS=(
        \"cloudfunctions.googleapis.com\"
        \"firestore.googleapis.com\"
        \"secretmanager.googleapis.com\"
        \"cloudscheduler.googleapis.com\"
    )

    for API in \"${REQUIRED_APIS[@]}\"; do
        if ! gcloud services list --enabled --filter=\"name:$API\" --format=\"value(name)\" | grep -q \"$API\"; then
            print_warning \"Enabling API: $API\"
            gcloud services enable \"$API\"
        fi
        print_success \"API enabled: $API\"
    done
}

# Install dependencies
install_dependencies() {
    print_header \"Installing Dependencies\"

    if [ ! -f \"package.json\" ]; then
        print_error \"package.json not found. Run this script from the functions directory.\"
    fi

    print_status \"Installing npm dependencies...\"
    npm install
    print_success \"Dependencies installed\"
}

# Validate function code
validate_code() {
    print_header \"Validating Code\"

    # Check main function file
    if [ ! -f \"index.js\" ]; then
        print_error \"index.js not found\"
    fi
    print_success \"Main function file found\"

    # Validate syntax
    print_status \"Checking JavaScript syntax...\"
    node -e \"
        try {
            require('./index.js');
            console.log('✅ Syntax validation passed');
        } catch (e) {
            console.error('❌ Syntax error:', e.message);
            process.exit(1);
        }
    \"

    # Check platform modules
    print_status \"Validating platform modules...\"
    for platform in instagram facebook twitter linkedin tiktok youtube pinterest snapchat threads; do
        if [ -f \"platforms/$platform/index.js\" ]; then
            node -e \"
                try {
                    const platform = require('./platforms/$platform/index.js');
                    if (typeof platform.publish !== 'function') {
                        throw new Error('Missing publish method');
                    }
                    console.log('✅ $platform module valid');
                } catch (e) {
                    console.error('❌ $platform module error:', e.message);
                    process.exit(1);
                }
            \"
        fi
    done
}

# Deploy individual function
deploy_function() {
    local FUNCTION_NAME=$1
    local ENTRY_POINT=$2
    local DESCRIPTION=\"$3\"

    print_status \"Deploying $FUNCTION_NAME...\"

    gcloud functions deploy \"$FUNCTION_NAME\" \\
        --gen2 \\
        --runtime=nodejs20 \\
        --region=\"$REGION\" \\
        --source=\"$FUNCTION_SOURCE\" \\
        --entry-point=\"$ENTRY_POINT\" \\
        --trigger-http \\
        --allow-unauthenticated \\
        --memory=1GB \\
        --timeout=540s \\
        --max-instances=100 \\
        --description=\"$DESCRIPTION\" \\
        --set-env-vars=\"GOOGLE_CLOUD_PROJECT=$PROJECT_ID\"

    # Get function URL
    FUNCTION_URL=$(gcloud functions describe \"$FUNCTION_NAME\" --region=\"$REGION\" --format=\"value(serviceConfig.uri)\")
    print_success \"$FUNCTION_NAME deployed: $FUNCTION_URL\"

    # Return URL for later use
    echo \"$FUNCTION_URL\"
}

# Deploy all functions
deploy_functions() {
    print_header \"Deploying Cloud Functions\"

    # Deploy main functions
    SCHEDULE_URL=$(deploy_function \"schedulePost\" \"schedulePost\" \"Schedule posts across multiple social media platforms\")
    PUBLISH_URL=$(deploy_function \"publishScheduledPosts\" \"publishScheduledPosts\" \"Automatically publish scheduled posts\")
    ANALYTICS_URL=$(deploy_function \"analytics\" \"analytics\" \"Get social media analytics and insights\")

    # Store URLs for scheduler setup
    export SCHEDULE_URL PUBLISH_URL ANALYTICS_URL

    print_success \"All functions deployed successfully\"
}

# Set up Cloud Scheduler
setup_scheduler() {
    print_header \"Setting up Cloud Scheduler\"

    # Check if job already exists
    JOB_NAME=\"social-media-publisher\"
    SCHEDULE=\"*/5 * * * *\"  # Every 5 minutes

    if gcloud scheduler jobs describe \"$JOB_NAME\" --location=\"$REGION\" &>/dev/null; then
        print_warning \"Scheduler job '$JOB_NAME' already exists. Updating...\"
        gcloud scheduler jobs update http \"$JOB_NAME\" \\
            --location=\"$REGION\" \\
            --schedule=\"$SCHEDULE\" \\
            --uri=\"$PUBLISH_URL\" \\
            --http-method=POST \\
            --description=\"Automatically publish scheduled social media posts\"
    else
        print_status \"Creating scheduler job: $JOB_NAME\"
        gcloud scheduler jobs create http \"$JOB_NAME\" \\
            --location=\"$REGION\" \\
            --schedule=\"$SCHEDULE\" \\
            --uri=\"$PUBLISH_URL\" \\
            --http-method=POST \\
            --description=\"Automatically publish scheduled social media posts\"
    fi

    print_success \"Scheduler job configured: $JOB_NAME\"
}

# Initialize Firestore
setup_firestore() {
    print_header \"Setting up Firestore\"

    # Create posting settings document (posting disabled by default for safety)
    print_status \"Initializing Firestore collections...\"

    # Check if Firestore is already initialized
    if gcloud firestore databases describe --database=\"(default)\" &>/dev/null; then
        print_success \"Firestore database already exists\"
    else
        print_status \"Creating Firestore database...\"
        gcloud firestore databases create --location=\"$REGION\"
        print_success \"Firestore database created\"
    fi

    # Create initial configuration document
    cat << EOF > /tmp/posting_settings.json
{
    \"enabled\": false,
    \"createdAt\": \"$(date -Iseconds)\",
    \"note\": \"Posting is disabled by default for safety. Enable through admin dashboard.\"
}
EOF

    print_status \"Creating initial configuration...\"
    if command -v firebase &> /dev/null; then
        firebase firestore:set posting_settings/posting_enabled /tmp/posting_settings.json --project \"$PROJECT_ID\"
        print_success \"Initial Firestore configuration created\"
    else
        print_warning \"Firebase CLI not found. Please manually create posting_settings/posting_enabled document\"
        print_warning \"Content: $(cat /tmp/posting_settings.json)\"
    fi

    rm -f /tmp/posting_settings.json
}

# Create deployment summary
create_summary() {
    print_header \"Deployment Summary\"

    cat << EOF

🎉 ElevatedIQ Social Media Platform - Deployment Complete!

📋 Deployed Functions:
   • Schedule Posts: $SCHEDULE_URL
   • Publish Posts:  $PUBLISH_URL
   • Analytics:      $ANALYTICS_URL

⏰ Automation:
   • Scheduler Job:  $JOB_NAME (every 5 minutes)
   • Status:         $(gcloud scheduler jobs describe \"$JOB_NAME\" --location=\"$REGION\" --format=\"value(state)\" 2>/dev/null || echo \"Unknown\")

🗄️  Database:
   • Firestore:      Initialized in $REGION
   • Posting:        Disabled (safety default)

🔐 Next Steps:
   1. Configure platform credentials in Secret Manager
   2. Test with a sample post:
      curl -X POST '$SCHEDULE_URL' -H 'Content-Type: application/json' -d '{\"platforms\":[\"instagram\"],\"caption\":\"Test post\",\"imageUrl\":\"https://via.placeholder.com/1080x1080\",\"scheduledTime\":\"$(date -d \"+5 minutes\" -Iseconds)\"}'
   3. Enable posting: Update posting_settings/posting_enabled in Firestore
   4. Monitor logs: gcloud functions logs tail publishScheduledPosts

📚 Documentation:
   • Quick Start: docs/quickstart/README.md
   • Architecture: docs/architecture/README.md
   • API Reference: docs/api/README.md

🎯 Support:
   • Issues: https://github.com/kushin77/elevatedIQ/issues
   • Docs: https://docs.elevatediq.ai

EOF

    print_success \"Deployment completed successfully! 🚀\"
}

# Test deployment
test_deployment() {
    print_header \"Testing Deployment\"

    # Test schedule function
    print_status \"Testing schedule function...\"
    HTTP_STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" -X OPTIONS \"$SCHEDULE_URL\")
    if [ \"$HTTP_STATUS\" = \"204\" ]; then
        print_success \"Schedule function responding (CORS check passed)\"
    else
        print_warning \"Schedule function test failed (HTTP $HTTP_STATUS)\"
    fi

    # Test analytics function
    print_status \"Testing analytics function...\"
    HTTP_STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" \"$ANALYTICS_URL?timeframe=1d\")
    if [ \"$HTTP_STATUS\" = \"200\" ]; then
        print_success \"Analytics function responding\"
    else
        print_warning \"Analytics function test failed (HTTP $HTTP_STATUS)\"
    fi
}

# Main deployment function
main() {
    print_header \"ElevatedIQ Social Media Platform - Deployment\"

    # Run deployment steps
    validate_prerequisites
    install_dependencies
    validate_code
    deploy_functions
    setup_scheduler
    setup_firestore
    test_deployment
    create_summary
}

# Check if running as main script
if [[ \"${BASH_SOURCE[0]}\" == \"${0}\" ]]; then
    main \"$@\"
fi
