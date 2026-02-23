@echo off
setlocal EnableDelayedExpansion

REM ElevatedIQ Social Media Platform - Windows Deployment Script
REM Deploys all Cloud Functions and sets up the complete environment

REM Configuration
set PROJECT_ID=%GOOGLE_CLOUD_PROJECT%
if "%PROJECT_ID%"=="" (
    for /f "tokens=*" %%i in ('gcloud config get-value project 2^>nul') do set PROJECT_ID=%%i
)
set REGION=%REGION%
if "%REGION%"=="" set REGION=us-central1
set FUNCTION_SOURCE=.

echo.
echo ================================================
echo   ElevatedIQ Social Media Platform Deployment
echo ================================================
echo.

REM Function to print status messages
:print_status
echo [%date% %time%] %~1
goto :eof

:print_success
echo [92m✅ %~1[0m
goto :eof

:print_warning
echo [93m⚠️  %~1[0m
goto :eof

:print_error
echo [91m❌ %~1[0m
exit /b 1

:print_header
echo.
echo [96m================================================[0m
echo [96m  %~1[0m
echo [96m================================================[0m
echo.
goto :eof

REM Validate prerequisites
call :print_header "Validating Prerequisites"

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    call :print_error "gcloud CLI is not installed. Please install it first."
    exit /b 1
)
call :print_success "gcloud CLI found"

REM Check if node is installed
node --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Node.js is not installed. Please install Node.js 20+"
    exit /b 1
)
call :print_success "Node.js found"

REM Check Node version
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
set NODE_VERSION=%NODE_VERSION:v=%
for /f "tokens=1 delims=." %%a in ("%NODE_VERSION%") do set MAJOR_VERSION=%%a
if %MAJOR_VERSION% LSS 20 (
    call :print_error "Node.js version 20 or higher required. Current: v%NODE_VERSION%"
    exit /b 1
)
call :print_success "Node.js version: v%NODE_VERSION%"

REM Check if logged into gcloud
for /f "tokens=*" %%i in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>nul') do set ACTIVE_ACCOUNT=%%i
if "%ACTIVE_ACCOUNT%"=="" (
    call :print_error "Not logged into gcloud. Run: gcloud auth login"
    exit /b 1
)
call :print_success "gcloud authentication verified"

REM Validate project ID
if "%PROJECT_ID%"=="" (
    call :print_error "No project ID set. Set GOOGLE_CLOUD_PROJECT or run: gcloud config set project YOUR_PROJECT"
    exit /b 1
)
call :print_success "Project ID: %PROJECT_ID%"

REM Check and enable required APIs
call :print_status "Checking required APIs..."
set APIS=cloudfunctions.googleapis.com firestore.googleapis.com secretmanager.googleapis.com cloudscheduler.googleapis.com

for %%a in (%APIS%) do (
    gcloud services list --enabled --filter="name:%%a" --format="value(name)" | findstr /C:"%%a" >nul 2>&1
    if errorlevel 1 (
        call :print_warning "Enabling API: %%a"
        gcloud services enable %%a
        if errorlevel 1 (
            call :print_error "Failed to enable API: %%a"
            exit /b 1
        )
    )
    call :print_success "API enabled: %%a"
)

REM Install dependencies
call :print_header "Installing Dependencies"

if not exist "package.json" (
    call :print_error "package.json not found. Run this script from the functions directory."
    exit /b 1
)

call :print_status "Installing npm dependencies..."
call npm install
if errorlevel 1 (
    call :print_error "Failed to install dependencies"
    exit /b 1
)
call :print_success "Dependencies installed"

REM Validate code
call :print_header "Validating Code"

if not exist "index.js" (
    call :print_error "index.js not found"
    exit /b 1
)
call :print_success "Main function file found"

call :print_status "Checking JavaScript syntax..."
node -e "try { require('./index.js'); console.log('✅ Syntax validation passed'); } catch (e) { console.error('❌ Syntax error:', e.message); process.exit(1); }"
if errorlevel 1 exit /b 1

REM Check platform modules
call :print_status "Validating platform modules..."
set PLATFORMS=instagram facebook twitter linkedin tiktok youtube pinterest snapchat threads

for %%p in (%PLATFORMS%) do (
    if exist "platforms\%%p\index.js" (
        node -e "try { const platform = require('./platforms/%%p/index.js'); if (typeof platform.publish !== 'function') { throw new Error('Missing publish method'); } console.log('✅ %%p module valid'); } catch (e) { console.error('❌ %%p module error:', e.message); process.exit(1); }"
        if errorlevel 1 exit /b 1
    )
)

REM Deploy functions
call :print_header "Deploying Cloud Functions"

REM Deploy schedule function
call :print_status "Deploying schedulePost..."
gcloud functions deploy schedulePost ^
    --gen2 ^
    --runtime=nodejs20 ^
    --region=%REGION% ^
    --source=%FUNCTION_SOURCE% ^
    --entry-point=schedulePost ^
    --trigger-http ^
    --allow-unauthenticated ^
    --memory=1GB ^
    --timeout=540s ^
    --max-instances=100 ^
    --description="Schedule posts across multiple social media platforms" ^
    --set-env-vars="GOOGLE_CLOUD_PROJECT=%PROJECT_ID%"

if errorlevel 1 (
    call :print_error "Failed to deploy schedulePost function"
    exit /b 1
)

REM Get schedule function URL
for /f "tokens=*" %%i in ('gcloud functions describe schedulePost --region=%REGION% --format="value(serviceConfig.uri)"') do set SCHEDULE_URL=%%i
call :print_success "schedulePost deployed: %SCHEDULE_URL%"

REM Deploy publish function
call :print_status "Deploying publishScheduledPosts..."
gcloud functions deploy publishScheduledPosts ^
    --gen2 ^
    --runtime=nodejs20 ^
    --region=%REGION% ^
    --source=%FUNCTION_SOURCE% ^
    --entry-point=publishScheduledPosts ^
    --trigger-http ^
    --allow-unauthenticated ^
    --memory=1GB ^
    --timeout=540s ^
    --max-instances=100 ^
    --description="Automatically publish scheduled posts" ^
    --set-env-vars="GOOGLE_CLOUD_PROJECT=%PROJECT_ID%"

if errorlevel 1 (
    call :print_error "Failed to deploy publishScheduledPosts function"
    exit /b 1
)

REM Get publish function URL
for /f "tokens=*" %%i in ('gcloud functions describe publishScheduledPosts --region=%REGION% --format="value(serviceConfig.uri)"') do set PUBLISH_URL=%%i
call :print_success "publishScheduledPosts deployed: %PUBLISH_URL%"

REM Deploy analytics function
call :print_status "Deploying analytics..."
gcloud functions deploy analytics ^
    --gen2 ^
    --runtime=nodejs20 ^
    --region=%REGION% ^
    --source=%FUNCTION_SOURCE% ^
    --entry-point=analytics ^
    --trigger-http ^
    --allow-unauthenticated ^
    --memory=1GB ^
    --timeout=540s ^
    --max-instances=100 ^
    --description="Get social media analytics and insights" ^
    --set-env-vars="GOOGLE_CLOUD_PROJECT=%PROJECT_ID%"

if errorlevel 1 (
    call :print_error "Failed to deploy analytics function"
    exit /b 1
)

REM Get analytics function URL
for /f "tokens=*" %%i in ('gcloud functions describe analytics --region=%REGION% --format="value(serviceConfig.uri)"') do set ANALYTICS_URL=%%i
call :print_success "analytics deployed: %ANALYTICS_URL%"

call :print_success "All functions deployed successfully"

REM Set up Cloud Scheduler
call :print_header "Setting up Cloud Scheduler"

set JOB_NAME=social-media-publisher
set SCHEDULE=*/5 * * * *

REM Check if job exists
gcloud scheduler jobs describe %JOB_NAME% --location=%REGION% >nul 2>&1
if errorlevel 1 (
    call :print_status "Creating scheduler job: %JOB_NAME%"
    gcloud scheduler jobs create http %JOB_NAME% ^
        --location=%REGION% ^
        --schedule="%SCHEDULE%" ^
        --uri="%PUBLISH_URL%" ^
        --http-method=POST ^
        --description="Automatically publish scheduled social media posts"

    if errorlevel 1 (
        call :print_error "Failed to create scheduler job"
        exit /b 1
    )
) else (
    call :print_warning "Scheduler job '%JOB_NAME%' already exists. Updating..."
    gcloud scheduler jobs update http %JOB_NAME% ^
        --location=%REGION% ^
        --schedule="%SCHEDULE%" ^
        --uri="%PUBLISH_URL%" ^
        --http-method=POST ^
        --description="Automatically publish scheduled social media posts"

    if errorlevel 1 (
        call :print_error "Failed to update scheduler job"
        exit /b 1
    )
)

call :print_success "Scheduler job configured: %JOB_NAME%"

REM Set up Firestore
call :print_header "Setting up Firestore"

call :print_status "Initializing Firestore collections..."

REM Check if Firestore exists
gcloud firestore databases describe --database="(default)" >nul 2>&1
if errorlevel 1 (
    call :print_status "Creating Firestore database..."
    gcloud firestore databases create --location=%REGION%
    if errorlevel 1 (
        call :print_error "Failed to create Firestore database"
        exit /b 1
    )
    call :print_success "Firestore database created"
) else (
    call :print_success "Firestore database already exists"
)

REM Create initial configuration
echo {"enabled": false, "createdAt": "%date% %time%", "note": "Posting is disabled by default for safety. Enable through admin dashboard."} > temp_settings.json

REM Check if Firebase CLI is available
firebase --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Firebase CLI not found. Please manually create posting_settings/posting_enabled document"
    call :print_warning "Content: {"enabled": false, "note": "Posting disabled for safety"}"
) else (
    call :print_status "Creating initial configuration..."
    firebase firestore:set posting_settings/posting_enabled temp_settings.json --project %PROJECT_ID%
    if errorlevel 1 (
        call :print_warning "Failed to create initial config via Firebase CLI"
    ) else (
        call :print_success "Initial Firestore configuration created"
    )
)

if exist temp_settings.json del temp_settings.json

REM Test deployment
call :print_header "Testing Deployment"

call :print_status "Testing functions..."

REM Simple availability test using curl if available
curl --version >nul 2>&1
if not errorlevel 1 (
    call :print_status "Testing schedule function..."
    curl -s -o nul -w "HTTP Status: %%{http_code}" -X OPTIONS "%SCHEDULE_URL%"
    echo.

    call :print_status "Testing analytics function..."
    curl -s -o nul -w "HTTP Status: %%{http_code}" "%ANALYTICS_URL%?timeframe=1d"
    echo.
) else (
    call :print_warning "curl not available for function testing"
)

REM Deployment summary
call :print_header "Deployment Summary"

echo.
echo 🎉 ElevatedIQ Social Media Platform - Deployment Complete!
echo.
echo 📋 Deployed Functions:
echo    • Schedule Posts: %SCHEDULE_URL%
echo    • Publish Posts:  %PUBLISH_URL%
echo    • Analytics:      %ANALYTICS_URL%
echo.
echo ⏰ Automation:
echo    • Scheduler Job:  %JOB_NAME% (every 5 minutes)
for /f "tokens=*" %%i in ('gcloud scheduler jobs describe %JOB_NAME% --location=%REGION% --format="value(state)" 2^>nul') do echo    • Status:         %%i
echo.
echo 🗄️  Database:
echo    • Firestore:      Initialized in %REGION%
echo    • Posting:        Disabled (safety default)
echo.
echo 🔐 Next Steps:
echo    1. Configure platform credentials in Secret Manager
echo    2. Test with sample post (see docs/quickstart/README.md)
echo    3. Enable posting: Update posting_settings/posting_enabled in Firestore
echo    4. Monitor logs: gcloud functions logs tail publishScheduledPosts
echo.
echo 📚 Documentation:
echo    • Quick Start: docs/quickstart/README.md
echo    • Architecture: docs/architecture/README.md
echo    • API Reference: docs/api/README.md
echo.
echo 🎯 Support:
echo    • Issues: https://github.com/kushin77/elevatedIQ/issues
echo    • Docs: https://docs.elevatediq.ai
echo.

call :print_success "Deployment completed successfully! 🚀"

endlocal
pause
