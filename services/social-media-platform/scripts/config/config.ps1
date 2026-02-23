# ElevatedIQ Social Media Platform - Configuration Management
# Manages secrets, environment variables, and platform credentials

param(
    [string]$Action = "list",
    [string]$Platform = "",
    [string]$SecretName = "",
    [string]$SecretValue = "",
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [switch]$Interactive,
    [switch]$DryRun
)

# Import setup functions
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\setup.ps1"

function Show-ConfigUsage {
    Write-Host @"
ElevatedIQ Social Media Platform - Configuration Management

Usage: .\config.ps1 -Action ACTION [OPTIONS]

Actions:
    list                    List all secrets and configuration
    add                     Add a new secret
    update                  Update an existing secret
    delete                  Delete a secret
    validate                Validate platform configuration
    interactive             Interactive configuration wizard
    export                  Export configuration template
    import                  Import configuration from file

Options:
    -Platform PLATFORM      Platform name (instagram, facebook, etc.)
    -SecretName NAME        Secret name in Google Secret Manager
    -SecretValue VALUE      Secret value (use -Interactive for secure input)
    -ProjectId PROJECT      Google Cloud Project ID
    -Interactive            Interactive mode for secure input
    -DryRun                 Show what would be done without executing

Examples:
    # List all secrets
    .\config.ps1 -Action list

    # Add Instagram access token (interactive)
    .\config.ps1 -Action add -Platform instagram -SecretName access_token -Interactive

    # Validate all platform configurations
    .\config.ps1 -Action validate

    # Interactive configuration wizard
    .\config.ps1 -Action interactive
"@
}

# Platform configuration definitions
$platformConfigs = @{
    instagram = @{
        secrets = @("access_token", "app_id", "app_secret")
        description = "Instagram Graph API v18.0"
        docs = "https://developers.facebook.com/docs/instagram-api"
    }
    facebook = @{
        secrets = @("access_token", "page_id", "app_secret")
        description = "Facebook Pages API"
        docs = "https://developers.facebook.com/docs/pages"
    }
    twitter = @{
        secrets = @("api_key", "api_secret", "access_token", "access_secret")
        description = "Twitter API v2"
        docs = "https://developer.twitter.com/en/docs/twitter-api"
    }
    linkedin = @{
        secrets = @("access_token", "client_id", "client_secret")
        description = "LinkedIn UGC API"
        docs = "https://docs.microsoft.com/linkedin/marketing/integrations/community-management/shares/ugc-post-api"
    }
    tiktok = @{
        secrets = @("access_token", "client_key", "client_secret")
        description = "TikTok Content Posting API"
        docs = "https://developers.tiktok.com/doc/content-posting-api-get-started"
    }
    youtube = @{
        secrets = @("api_key", "client_id", "client_secret", "refresh_token")
        description = "YouTube Data API v3"
        docs = "https://developers.google.com/youtube/v3"
    }
    pinterest = @{
        secrets = @("access_token", "app_id", "app_secret")
        description = "Pinterest API v5"
        docs = "https://developers.pinterest.com/docs/api/v5/"
    }
    snapchat = @{
        secrets = @("access_token", "client_id", "client_secret")
        description = "Snapchat Marketing API"
        docs = "https://marketingapi.snapchat.com/"
    }
    threads = @{
        secrets = @("access_token", "app_id", "app_secret")
        description = "Meta Threads API"
        docs = "https://developers.facebook.com/docs/threads"
    }
}

function Get-SecretName {
    param([string]$Platform, [string]$SecretType)
    return "social-media-$Platform-$SecretType"
}

function Test-SecretExists {
    param([string]$SecretName)

    try {
        $null = gcloud secrets describe $SecretName --project=$ProjectId 2>$null
        return $true
    } catch {
        return $false
    }
}

function Get-SecretValue {
    param([string]$SecretName)

    try {
        $value = gcloud secrets versions access latest --secret=$SecretName --project=$ProjectId 2>$null
        return $value
    } catch {
        return $null
    }
}

function Set-SecretValue {
    param([string]$SecretName, [string]$SecretValue, [switch]$Update)

    if ($DryRun) {
        Write-Status "DRY RUN: Would $(if ($Update) { 'update' } else { 'create' }) secret: $SecretName"
        return $true
    }

    try {
        if ($Update -or (Test-SecretExists $SecretName)) {
            # Update existing secret
            $SecretValue | gcloud secrets versions add $SecretName --data-file=- --project=$ProjectId
            Write-Success "Updated secret: $SecretName"
        } else {
            # Create new secret
            gcloud secrets create $SecretName --data-file=- --project=$ProjectId <<< $SecretValue
            Write-Success "Created secret: $SecretName"
        }
        return $true
    } catch {
        Write-Error "Failed to set secret: $SecretName - $($_.Exception.Message)"
        return $false
    }
}

function Remove-Secret {
    param([string]$SecretName)

    if ($DryRun) {
        Write-Status "DRY RUN: Would delete secret: $SecretName"
        return $true
    }

    try {
        gcloud secrets delete $SecretName --project=$ProjectId --quiet
        Write-Success "Deleted secret: $SecretName"
        return $true
    } catch {
        Write-Error "Failed to delete secret: $SecretName - $($_.Exception.Message)"
        return $false
    }
}

function Show-AllSecrets {
    Write-Header "Platform Configuration Status"

    foreach ($platform in $platformConfigs.Keys | Sort-Object) {
        $config = $platformConfigs[$platform]

        Write-Host ""
        Write-Host "📱 $($platform.ToUpper())" -ForegroundColor Cyan
        Write-Host "   Description: $($config.description)"
        Write-Host "   Documentation: $($config.docs)"
        Write-Host ""

        $allConfigured = $true
        foreach ($secretType in $config.secrets) {
            $secretName = Get-SecretName -Platform $platform -SecretType $secretType
            $exists = Test-SecretExists -SecretName $secretName

            $status = if ($exists) { "✅ Configured" } else { "❌ Missing"; $allConfigured = $false }
            $color = if ($exists) { "Green" } else { "Red" }

            Write-Host "   • $secretType`: " -NoNewline
            Write-Host $status -ForegroundColor $color
        }

        $overallStatus = if ($allConfigured) { "✅ Ready" } else { "⚠️  Incomplete" }
        $overallColor = if ($allConfigured) { "Green" } else { "Yellow" }
        Write-Host "   Status: " -NoNewline
        Write-Host $overallStatus -ForegroundColor $overallColor
    }

    Write-Host ""
}

function Add-PlatformSecret {
    param([string]$Platform, [string]$SecretType, [string]$Value)

    if (-not $platformConfigs.ContainsKey($Platform)) {
        Write-Error "Unknown platform: $Platform. Available: $($platformConfigs.Keys -join ', ')"
        return
    }

    $config = $platformConfigs[$Platform]
    if ($SecretType -notin $config.secrets) {
        Write-Error "Invalid secret type '$SecretType' for $Platform. Available: $($config.secrets -join ', ')"
        return
    }

    $secretName = Get-SecretName -Platform $Platform -SecretType $SecretType

    if ($Interactive -or -not $Value) {
        Write-Status "Enter $SecretType for $Platform:"
        $Value = Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText
    }

    if (-not $Value) {
        Write-Error "Secret value is required"
        return
    }

    $exists = Test-SecretExists -SecretName $secretName
    Set-SecretValue -SecretName $secretName -SecretValue $Value -Update:$exists
}

function Remove-PlatformSecret {
    param([string]$Platform, [string]$SecretType)

    if (-not $platformConfigs.ContainsKey($Platform)) {
        Write-Error "Unknown platform: $Platform"
        return
    }

    $secretName = Get-SecretName -Platform $Platform -SecretType $SecretType

    if (-not (Test-SecretExists -SecretName $secretName)) {
        Write-Warning "Secret does not exist: $secretName"
        return
    }

    $confirm = Read-Host "Delete secret '$secretName'? (y/N)"
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        Remove-Secret -SecretName $secretName
    }
}

function Test-PlatformConfiguration {
    Write-Header "Validating Platform Configuration"

    $issues = @()

    foreach ($platform in $platformConfigs.Keys | Sort-Object) {
        $config = $platformConfigs[$platform]
        Write-Status "Checking $platform configuration..."

        $missing = @()
        foreach ($secretType in $config.secrets) {
            $secretName = Get-SecretName -Platform $platform -SecretType $secretType
            if (-not (Test-SecretExists -SecretName $secretName)) {
                $missing += $secretType
            }
        }

        if ($missing.Count -eq 0) {
            Write-Success "$platform: All secrets configured"
        } else {
            $message = "$platform: Missing secrets: $($missing -join ', ')"
            Write-Warning $message
            $issues += $message
        }
    }

    Write-Host ""
    if ($issues.Count -eq 0) {
        Write-Success "All platform configurations are complete! 🎉"
    } else {
        Write-Warning "Configuration issues found:"
        foreach ($issue in $issues) {
            Write-Host "  • $issue" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "Use 'config.ps1 -Action interactive' to configure missing secrets" -ForegroundColor Cyan
    }
}

function Start-InteractiveConfiguration {
    Write-Header "Interactive Platform Configuration"

    Write-Host "This wizard will help you configure API credentials for all platforms." -ForegroundColor Cyan
    Write-Host "You can skip platforms by pressing Enter without a value." -ForegroundColor Yellow
    Write-Host ""

    foreach ($platform in $platformConfigs.Keys | Sort-Object) {
        $config = $platformConfigs[$platform]

        Write-Host "📱 Configuring $($platform.ToUpper())" -ForegroundColor Cyan
        Write-Host "   $($config.description)"
        Write-Host "   Documentation: $($config.docs)"
        Write-Host ""

        $skip = Read-Host "Configure $platform? (Y/n)"
        if ($skip -eq 'n' -or $skip -eq 'N') {
            Write-Host "   Skipped $platform" -ForegroundColor Yellow
            Write-Host ""
            continue
        }

        foreach ($secretType in $config.secrets) {
            $secretName = Get-SecretName -Platform $platform -SecretType $secretType
            $exists = Test-SecretExists -SecretName $secretName

            $prompt = "   Enter $secretType"
            if ($exists) {
                $prompt += " (exists, press Enter to keep current)"
            }
            $prompt += ": "

            $value = Read-Host $prompt -AsSecureString | ConvertFrom-SecureString -AsPlainText

            if ($value) {
                Set-SecretValue -SecretName $secretName -SecretValue $value -Update:$exists
            } elseif ($exists) {
                Write-Host "   Keeping existing value for $secretType" -ForegroundColor Yellow
            } else {
                Write-Host "   Skipped $secretType" -ForegroundColor Yellow
            }
        }

        Write-Host ""
    }

    Write-Success "Interactive configuration completed!"
    Write-Host ""
    Write-Host "Run 'config.ps1 -Action validate' to verify your configuration" -ForegroundColor Cyan
}

function Export-ConfigurationTemplate {
    Write-Header "Exporting Configuration Template"

    $template = @{
        project_id = $ProjectId
        region = $Region
        platforms = @{}
    }

    foreach ($platform in $platformConfigs.Keys | Sort-Object) {
        $config = $platformConfigs[$platform]
        $template.platforms[$platform] = @{
            description = $config.description
            documentation = $config.docs
            secrets = @{}
        }

        foreach ($secretType in $config.secrets) {
            $template.platforms[$platform].secrets[$secretType] = "YOUR_${platform.ToUpper()}_${secretType.ToUpper()}"
        }
    }

    $templateFile = "config-template.json"
    $template | ConvertTo-Json -Depth 10 | Out-File $templateFile -Encoding UTF8

    Write-Success "Configuration template exported to: $templateFile"
    Write-Host "Edit the template with your values and use 'config.ps1 -Action import' to apply" -ForegroundColor Cyan
}

function Import-ConfigurationFromFile {
    param([string]$ConfigFile = "config.json")

    if (-not (Test-Path $ConfigFile)) {
        Write-Error "Configuration file not found: $ConfigFile"
        return
    }

    Write-Header "Importing Configuration from $ConfigFile"

    try {
        $config = Get-Content $ConfigFile | ConvertFrom-Json

        foreach ($platformName in $config.platforms.PSObject.Properties.Name) {
            $platformConfig = $config.platforms.$platformName

            Write-Status "Importing $platformName configuration..."

            foreach ($secretType in $platformConfig.secrets.PSObject.Properties.Name) {
                $secretValue = $platformConfig.secrets.$secretType

                if ($secretValue -and $secretValue -notlike "YOUR_*") {
                    $secretName = Get-SecretName -Platform $platformName -SecretType $secretType
                    $exists = Test-SecretExists -SecretName $secretName

                    Set-SecretValue -SecretName $secretName -SecretValue $secretValue -Update:$exists
                } else {
                    Write-Warning "Skipping placeholder value for $platformName.$secretType"
                }
            }
        }

        Write-Success "Configuration imported successfully!"

    } catch {
        Write-Error "Failed to import configuration: $($_.Exception.Message)"
    }
}

# Main configuration function
function Start-Configuration {
    # Validate prerequisites
    if (-not $ProjectId) {
        try {
            $ProjectId = gcloud config get-value project 2>$null
        } catch {
            Write-Error "No project ID found. Set GOOGLE_CLOUD_PROJECT or use -ProjectId"
            return
        }
    }

    # Execute requested action
    switch ($Action.ToLower()) {
        "list" {
            Show-AllSecrets
        }
        "add" {
            if (-not $Platform -or -not $SecretName) {
                Write-Error "Platform and SecretName required for add action"
                Show-ConfigUsage
                return
            }
            Add-PlatformSecret -Platform $Platform -SecretType $SecretName -Value $SecretValue
        }
        "update" {
            if (-not $Platform -or -not $SecretName) {
                Write-Error "Platform and SecretName required for update action"
                Show-ConfigUsage
                return
            }
            Add-PlatformSecret -Platform $Platform -SecretType $SecretName -Value $SecretValue
        }
        "delete" {
            if (-not $Platform -or -not $SecretName) {
                Write-Error "Platform and SecretName required for delete action"
                Show-ConfigUsage
                return
            }
            Remove-PlatformSecret -Platform $Platform -SecretType $SecretName
        }
        "validate" {
            Test-PlatformConfiguration
        }
        "interactive" {
            Start-InteractiveConfiguration
        }
        "export" {
            Export-ConfigurationTemplate
        }
        "import" {
            $configFile = if ($Platform) { $Platform } else { "config.json" }
            Import-ConfigurationFromFile -ConfigFile $configFile
        }
        default {
            Write-Error "Unknown action: $Action"
            Show-ConfigUsage
        }
    }
}

# Run configuration if script is executed directly
if ($MyInvocation.InvocationName -ne '.') {
    Start-Configuration
}
