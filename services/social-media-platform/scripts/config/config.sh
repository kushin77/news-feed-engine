#!/bin/bash

# ElevatedIQ Social Media Platform - Configuration Management
# Manages secrets, environment variables, and platform credentials

set -e  # Exit on error

# Configuration
ACTION="${1:-list}"
PLATFORM="$2"
SECRET_NAME="$3"
SECRET_VALUE="$4"
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
INTERACTIVE=false
DRY_RUN=false

# Source setup functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../setup/setup.sh" 2>/dev/null || true

# Platform configuration definitions
declare -A PLATFORM_CONFIGS
PLATFORM_CONFIGS[instagram]="access_token,app_id,app_secret|Instagram Graph API v18.0|https://developers.facebook.com/docs/instagram-api"
PLATFORM_CONFIGS[facebook]="access_token,page_id,app_secret|Facebook Pages API|https://developers.facebook.com/docs/pages"
PLATFORM_CONFIGS[twitter]="api_key,api_secret,access_token,access_secret|Twitter API v2|https://developer.twitter.com/en/docs/twitter-api"
PLATFORM_CONFIGS[linkedin]="access_token,client_id,client_secret|LinkedIn UGC API|https://docs.microsoft.com/linkedin/marketing/integrations/community-management/shares/ugc-post-api"
PLATFORM_CONFIGS[tiktok]="access_token,client_key,client_secret|TikTok Content Posting API|https://developers.tiktok.com/doc/content-posting-api-get-started"
PLATFORM_CONFIGS[youtube]="api_key,client_id,client_secret,refresh_token|YouTube Data API v3|https://developers.google.com/youtube/v3"
PLATFORM_CONFIGS[pinterest]="access_token,app_id,app_secret|Pinterest API v5|https://developers.pinterest.com/docs/api/v5/"
PLATFORM_CONFIGS[snapchat]="access_token,client_id,client_secret|Snapchat Marketing API|https://marketingapi.snapchat.com/"
PLATFORM_CONFIGS[threads]="access_token,app_id,app_secret|Meta Threads API|https://developers.facebook.com/docs/threads"

show_usage() {
    cat << EOF
ElevatedIQ Social Media Platform - Configuration Management

Usage: $0 ACTION [PLATFORM] [SECRET_NAME] [SECRET_VALUE] [OPTIONS]

Actions:
    list                    List all secrets and configuration
    add PLATFORM SECRET     Add a new secret
    update PLATFORM SECRET  Update an existing secret
    delete PLATFORM SECRET  Delete a secret
    validate               Validate platform configuration
    interactive            Interactive configuration wizard
    export                 Export configuration template
    import [FILE]          Import configuration from file

Options:
    --project-id PROJECT   Google Cloud Project ID
    --interactive          Interactive mode for secure input
    --dry-run             Show what would be done without executing

Examples:
    # List all secrets
    $0 list

    # Add Instagram access token (interactive)
    $0 add instagram access_token --interactive

    # Validate all platform configurations
    $0 validate

    # Interactive configuration wizard
    $0 interactive
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --interactive)
                INTERACTIVE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            -*)
                print_error "Unknown option: $1. Use --help for usage information."
                ;;
            *)
                break
                ;;
        esac
    done
}

get_secret_name() {
    local platform=$1
    local secret_type=$2
    echo "social-media-$platform-$secret_type"
}

test_secret_exists() {
    local secret_name=$1
    gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null
}

get_secret_value() {
    local secret_name=$1
    gcloud secrets versions access latest --secret="$secret_name" --project="$PROJECT_ID" 2>/dev/null
}

set_secret_value() {
    local secret_name=$1
    local secret_value=$2
    local update=$3

    if [ "$DRY_RUN" = true ]; then
        print_status "DRY RUN: Would $([ "$update" = true ] && echo 'update' || echo 'create') secret: $secret_name"
        return 0
    fi

    if [ "$update" = true ] || test_secret_exists "$secret_name"; then
        # Update existing secret
        echo "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=- --project="$PROJECT_ID"
        print_success "Updated secret: $secret_name"
    else
        # Create new secret
        echo "$secret_value" | gcloud secrets create "$secret_name" --data-file=- --project="$PROJECT_ID"
        print_success "Created secret: $secret_name"
    fi
}

remove_secret() {
    local secret_name=$1

    if [ "$DRY_RUN" = true ]; then
        print_status "DRY RUN: Would delete secret: $secret_name"
        return 0
    fi

    gcloud secrets delete "$secret_name" --project="$PROJECT_ID" --quiet
    print_success "Deleted secret: $secret_name"
}

show_all_secrets() {
    print_header "Platform Configuration Status"

    for platform in $(echo "${!PLATFORM_CONFIGS[@]}" | tr ' ' '\\n' | sort); do
        local config="${PLATFORM_CONFIGS[$platform]}"
        local secrets=$(echo "$config" | cut -d'|' -f1)
        local description=$(echo "$config" | cut -d'|' -f2)
        local docs=$(echo "$config" | cut -d'|' -f3)

        echo ""
        echo -e "${CYAN}📱 ${platform^^}${NC}"
        echo "   Description: $description"
        echo "   Documentation: $docs"
        echo ""

        local all_configured=true
        IFS=',' read -ra SECRET_ARRAY <<< "$secrets"
        for secret_type in "${SECRET_ARRAY[@]}"; do
            local secret_name=$(get_secret_name "$platform" "$secret_type")

            if test_secret_exists "$secret_name"; then
                echo -e "   • $secret_type: ${GREEN}✅ Configured${NC}"
            else
                echo -e "   • $secret_type: ${RED}❌ Missing${NC}"
                all_configured=false
            fi
        done

        if [ "$all_configured" = true ]; then
            echo -e "   Status: ${GREEN}✅ Ready${NC}"
        else
            echo -e "   Status: ${YELLOW}⚠️  Incomplete${NC}"
        fi
    done

    echo ""
}

add_platform_secret() {
    local platform=$1
    local secret_type=$2
    local value=$3

    if [ -z "${PLATFORM_CONFIGS[$platform]:-}" ]; then
        print_error "Unknown platform: $platform. Available: $(echo "${!PLATFORM_CONFIGS[@]}" | tr ' ' ', ')"
        return 1
    fi

    local config="${PLATFORM_CONFIGS[$platform]}"
    local secrets=$(echo "$config" | cut -d'|' -f1)

    if [[ ",$secrets," != *",$secret_type,"* ]]; then
        print_error "Invalid secret type '$secret_type' for $platform. Available: $secrets"
        return 1
    fi

    local secret_name=$(get_secret_name "$platform" "$secret_type")

    if [ "$INTERACTIVE" = true ] || [ -z "$value" ]; then
        print_status "Enter $secret_type for $platform:"
        read -s value
        echo
    fi

    if [ -z "$value" ]; then
        print_error "Secret value is required"
        return 1
    fi

    local update=false
    if test_secret_exists "$secret_name"; then
        update=true
    fi

    set_secret_value "$secret_name" "$value" "$update"
}

remove_platform_secret() {
    local platform=$1
    local secret_type=$2

    if [ -z "${PLATFORM_CONFIGS[$platform]:-}" ]; then
        print_error "Unknown platform: $platform"
        return 1
    fi

    local secret_name=$(get_secret_name "$platform" "$secret_type")

    if ! test_secret_exists "$secret_name"; then
        print_warning "Secret does not exist: $secret_name"
        return 0
    fi

    read -p "Delete secret '$secret_name'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        remove_secret "$secret_name"
    fi
}

validate_platform_configuration() {
    print_header "Validating Platform Configuration"

    local issues=()

    for platform in $(echo "${!PLATFORM_CONFIGS[@]}" | tr ' ' '\\n' | sort); do
        local config="${PLATFORM_CONFIGS[$platform]}"
        local secrets=$(echo "$config" | cut -d'|' -f1)

        print_status "Checking $platform configuration..."

        local missing=()
        IFS=',' read -ra SECRET_ARRAY <<< "$secrets"
        for secret_type in "${SECRET_ARRAY[@]}"; do
            local secret_name=$(get_secret_name "$platform" "$secret_type")
            if ! test_secret_exists "$secret_name"; then
                missing+=("$secret_type")
            fi
        done

        if [ ${#missing[@]} -eq 0 ]; then
            print_success "$platform: All secrets configured"
        else
            local message="$platform: Missing secrets: $(IFS=','; echo "${missing[*]}")"
            print_warning "$message"
            issues+=("$message")
        fi
    done

    echo ""
    if [ ${#issues[@]} -eq 0 ]; then
        print_success "All platform configurations are complete! 🎉"
    else
        print_warning "Configuration issues found:"
        for issue in "${issues[@]}"; do
            echo "  • $issue"
        done
        echo ""
        echo -e "${CYAN}Use '$0 interactive' to configure missing secrets${NC}"
    fi
}

interactive_configuration() {
    print_header "Interactive Platform Configuration"

    echo -e "${CYAN}This wizard will help you configure API credentials for all platforms.${NC}"
    echo -e "${YELLOW}You can skip platforms by pressing Enter without a value.${NC}"
    echo ""

    for platform in $(echo "${!PLATFORM_CONFIGS[@]}" | tr ' ' '\\n' | sort); do
        local config="${PLATFORM_CONFIGS[$platform]}"
        local secrets=$(echo "$config" | cut -d'|' -f1)
        local description=$(echo "$config" | cut -d'|' -f2)
        local docs=$(echo "$config" | cut -d'|' -f3)

        echo -e "${CYAN}📱 Configuring ${platform^^}${NC}"
        echo "   $description"
        echo "   Documentation: $docs"
        echo ""

        read -p "Configure $platform? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            echo -e "   ${YELLOW}Skipped $platform${NC}"
            echo ""
            continue
        fi

        IFS=',' read -ra SECRET_ARRAY <<< "$secrets"
        for secret_type in "${SECRET_ARRAY[@]}"; do
            local secret_name=$(get_secret_name "$platform" "$secret_type")
            local exists=false

            if test_secret_exists "$secret_name"; then
                exists=true
            fi

            local prompt="   Enter $secret_type"
            if [ "$exists" = true ]; then
                prompt+=" (exists, press Enter to keep current)"
            fi
            prompt+=": "

            echo -n "$prompt"
            read -s value
            echo

            if [ -n "$value" ]; then
                set_secret_value "$secret_name" "$value" "$exists"
            elif [ "$exists" = true ]; then
                echo -e "   ${YELLOW}Keeping existing value for $secret_type${NC}"
            else
                echo -e "   ${YELLOW}Skipped $secret_type${NC}"
            fi
        done

        echo ""
    done

    print_success "Interactive configuration completed!"
    echo ""
    echo -e "${CYAN}Run '$0 validate' to verify your configuration${NC}"
}

export_configuration_template() {
    print_header "Exporting Configuration Template"

    local template_file="config-template.json"

    cat > "$template_file" << EOF
{
  "project_id": "$PROJECT_ID",
  "region": "$REGION",
  "platforms": {
EOF

    local first_platform=true
    for platform in $(echo "${!PLATFORM_CONFIGS[@]}" | tr ' ' '\\n' | sort); do
        local config="${PLATFORM_CONFIGS[$platform]}"
        local secrets=$(echo "$config" | cut -d'|' -f1)
        local description=$(echo "$config" | cut -d'|' -f2)
        local docs=$(echo "$config" | cut -d'|' -f3)

        if [ "$first_platform" = false ]; then
            echo "," >> "$template_file"
        fi
        first_platform=false

        cat >> "$template_file" << EOF
    "$platform": {
      "description": "$description",
      "documentation": "$docs",
      "secrets": {
EOF

        local first_secret=true
        IFS=',' read -ra SECRET_ARRAY <<< "$secrets"
        for secret_type in "${SECRET_ARRAY[@]}"; do
            if [ "$first_secret" = false ]; then
                echo "," >> "$template_file"
            fi
            first_secret=false

            echo "        \"$secret_type\": \"YOUR_${platform^^}_${secret_type^^}\"" >> "$template_file"
        done

        echo "      }" >> "$template_file"
        echo -n "    }" >> "$template_file"
    done

    cat >> "$template_file" << EOF

  }
}
EOF

    print_success "Configuration template exported to: $template_file"
    echo -e "${CYAN}Edit the template with your values and use '$0 import' to apply${NC}"
}

import_configuration_from_file() {
    local config_file=${1:-"config.json"}

    if [ ! -f "$config_file" ]; then
        print_error "Configuration file not found: $config_file"
        return 1
    fi

    print_header "Importing Configuration from $config_file"

    if ! command -v jq &> /dev/null; then
        print_error "jq is required for importing configuration. Install with: apt-get install jq"
        return 1
    fi

    # Extract platforms from JSON
    local platforms=$(jq -r '.platforms | keys[]' "$config_file")

    for platform in $platforms; do
        print_status "Importing $platform configuration..."

        # Get secrets for this platform
        local platform_secrets=$(jq -r ".platforms.$platform.secrets | keys[]" "$config_file")

        for secret_type in $platform_secrets; do
            local secret_value=$(jq -r ".platforms.$platform.secrets.$secret_type" "$config_file")

            if [ -n "$secret_value" ] && [[ "$secret_value" != YOUR_* ]]; then
                local secret_name=$(get_secret_name "$platform" "$secret_type")
                local exists=false

                if test_secret_exists "$secret_name"; then
                    exists=true
                fi

                set_secret_value "$secret_name" "$secret_value" "$exists"
            else
                print_warning "Skipping placeholder value for $platform.$secret_type"
            fi
        done
    done

    print_success "Configuration imported successfully!"
}

# Main configuration function
main() {
    # Parse additional arguments
    parse_arguments "$@"

    # Shift parsed arguments
    while [[ $# -gt 0 && "$1" =~ ^-- ]]; do
        shift
        [ $# -gt 0 ] && shift
    done

    # Update action and parameters after parsing
    ACTION="${1:-$ACTION}"
    PLATFORM="${2:-$PLATFORM}"
    SECRET_NAME="${3:-$SECRET_NAME}"
    SECRET_VALUE="${4:-$SECRET_VALUE}"

    # Validate prerequisites
    if [ -z "$PROJECT_ID" ]; then
        if command -v gcloud &> /dev/null; then
            PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        fi

        if [ -z "$PROJECT_ID" ]; then
            print_error "No project ID found. Set GOOGLE_CLOUD_PROJECT or use --project-id"
            return 1
        fi
    fi

    # Execute requested action
    case "${ACTION,,}" in
        list)
            show_all_secrets
            ;;
        add)
            if [ -z "$PLATFORM" ] || [ -z "$SECRET_NAME" ]; then
                print_error "Platform and SecretName required for add action"
                show_usage
                return 1
            fi
            add_platform_secret "$PLATFORM" "$SECRET_NAME" "$SECRET_VALUE"
            ;;
        update)
            if [ -z "$PLATFORM" ] || [ -z "$SECRET_NAME" ]; then
                print_error "Platform and SecretName required for update action"
                show_usage
                return 1
            fi
            add_platform_secret "$PLATFORM" "$SECRET_NAME" "$SECRET_VALUE"
            ;;
        delete)
            if [ -z "$PLATFORM" ] || [ -z "$SECRET_NAME" ]; then
                print_error "Platform and SecretName required for delete action"
                show_usage
                return 1
            fi
            remove_platform_secret "$PLATFORM" "$SECRET_NAME"
            ;;
        validate)
            validate_platform_configuration
            ;;
        interactive)
            interactive_configuration
            ;;
        export)
            export_configuration_template
            ;;
        import)
            local config_file=${PLATFORM:-"config.json"}
            import_configuration_from_file "$config_file"
            ;;
        *)
            print_error "Unknown action: $ACTION"
            show_usage
            return 1
            ;;
    esac
}

# Run configuration if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
