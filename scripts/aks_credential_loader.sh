#!/bin/bash

# Simple Azure Kubernetes Credential Loader - Bash Version
# A streamlined shell script to fetch AKS credentials across subscriptions

set -euo pipefail

# Global variables
DRY_RUN=false
VERBOSE=false
SUBSCRIPTION_FILTER=()

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Azure Kubernetes Credential Loader

Usage: $0 [OPTIONS]

OPTIONS:
    --dry-run           Preview actions without executing them
    --verbose, -v       Enable verbose logging
    --subscription, -s  Process only specific subscription IDs (can be repeated)
    --help, -h          Show this help message

Examples:
    $0                                    # Process all subscriptions
    $0 --dry-run                         # Preview actions without executing
    $0 -s sub1 -s sub2                   # Process specific subscriptions
    $0 --verbose                         # Enable debug logging

EOF
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v az &> /dev/null; then
        log_error "Azure CLI (az) is not installed or not in PATH"
        exit 1
    fi

    if ! command -v kubelogin &> /dev/null; then
        log_error "kubelogin is not installed or not in PATH"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi

    # Check if user is logged in to Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged in to Azure CLI. Please run 'az login' first"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Function to execute commands (with dry-run support)
execute_command() {
    local cmd="$1"
    local description="$2"

    log_debug "About to execute: $description"
    log_debug "Command: $cmd"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would execute: $cmd"
        return 0
    fi

    if eval "$cmd"; then
        log_debug "Command succeeded: $description"
        return 0
    else
        log_error "Command failed: $description"
        return 1
    fi
}

# Process a single subscription
process_subscription() {
    local sub_id="$1"
    local sub_name="$2"

    log_info "============================================================"
    log_info "Processing subscription: $sub_name"
    log_info "Subscription ID: $sub_id"
    log_info "============================================================"

    # Set subscription context
    if ! execute_command "az account set --subscription '$sub_id'" "Set subscription context"; then
        if [[ "$DRY_RUN" != "true" ]]; then
            log_error "Failed to set subscription context, skipping..."
            return 0
        fi
    fi

    # Get AKS clusters
    local clusters_json
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would execute: az aks list --output json"
        # Sample cluster data for dry run
        clusters_json='[{"name":"sample-aks-cluster","resourceGroup":"sample-rg"}]'
    else
        if ! clusters_json=$(az aks list --output json 2>/dev/null); then
            log_warn "Failed to list AKS clusters in subscription $sub_id"
            return 0
        fi
    fi

    local cluster_count
    cluster_count=$(echo "$clusters_json" | jq '. | length')
    log_info "Found $cluster_count AKS cluster(s) in subscription $sub_name"

    if [[ "$cluster_count" -eq 0 ]]; then
        return 0
    fi

    # Process each cluster
    local total_clusters=0
    local successful_clusters=0

    while IFS= read -r cluster_info; do
        if [[ -n "$cluster_info" ]]; then
            local cluster_name resource_group
            cluster_name=$(echo "$cluster_info" | cut -d'|' -f1)
            resource_group=$(echo "$cluster_info" | cut -d'|' -f2)

            log_info "Processing cluster: $cluster_name (Resource Group: $resource_group)"

            total_clusters=$((total_clusters + 1))

            # Fetch credentials
            local get_creds_cmd="az aks get-credentials --resource-group '$resource_group' --name '$cluster_name' --overwrite-existing"
            if execute_command "$get_creds_cmd" "Get AKS credentials for $cluster_name"; then
                # Convert kubeconfig
                local kubelogin_cmd="kubelogin convert-kubeconfig -l azurecli"
                if execute_command "$kubelogin_cmd" "Convert kubeconfig for Azure CLI auth"; then
                    log_info "Successfully configured credentials for $cluster_name"
                    successful_clusters=$((successful_clusters + 1))
                else
                    log_error "Failed to convert kubeconfig for $cluster_name"
                fi
            else
                log_error "Failed to get credentials for $cluster_name"
            fi

            # Small delay to avoid overwhelming Azure API
            if [[ "$DRY_RUN" != "true" ]]; then
                sleep 1
            fi
        fi
    done < <(echo "$clusters_json" | jq -r '.[] | "\(.name)|\(.resourceGroup)"')

    echo "SUBSCRIPTION_SUMMARY:$sub_name:$total_clusters:$successful_clusters"
}

# Main function
main() {
    log_info "Starting Azure Kubernetes Credential Loader"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Running in DRY RUN mode - no actual changes will be made"
    fi

    check_prerequisites

    # Get subscriptions
    local subscriptions_json
    log_info "Discovering Azure subscriptions..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would execute: az account list --output json"
        subscriptions_json='[{"id":"12345678-1234-1234-1234-123456789abc","name":"mock-subscription-01"},{"id":"sample-sub-2","name":"Sample Subscription 2"}]'
    else
        if ! subscriptions_json=$(az account list --output json 2>/dev/null); then
            log_error "Failed to retrieve subscriptions"
            exit 1
        fi
    fi

    # Filter subscriptions if needed
    if [[ ${#SUBSCRIPTION_FILTER[@]} -gt 0 ]]; then
        local filter_condition=""
        for filter in "${SUBSCRIPTION_FILTER[@]}"; do
            if [[ -n "$filter_condition" ]]; then
                filter_condition="$filter_condition or "
            fi
            filter_condition="$filter_condition(.id == \"$filter\" or .name == \"$filter\")"
        done

        subscriptions_json=$(echo "$subscriptions_json" | jq "[.[] | select($filter_condition)]")
    fi

    local sub_count
    sub_count=$(echo "$subscriptions_json" | jq '. | length')
    log_info "Found $sub_count subscription(s) to process"

    if [[ "$sub_count" -eq 0 ]]; then
        log_error "No subscriptions found"
        exit 1
    fi

    # Process each subscription
    local total_subscriptions=0
    local total_clusters=0
    local total_successful=0

    while IFS= read -r sub_info; do
        if [[ -n "$sub_info" ]]; then
            local sub_id sub_name
            sub_id=$(echo "$sub_info" | cut -d'|' -f1)
            sub_name=$(echo "$sub_info" | cut -d'|' -f2)

            total_subscriptions=$((total_subscriptions + 1))

            # Process subscription and capture summary
            local result
            result=$(process_subscription "$sub_id" "$sub_name" | grep "SUBSCRIPTION_SUMMARY:" || echo "SUBSCRIPTION_SUMMARY:$sub_name:0:0")

            if [[ "$result" =~ SUBSCRIPTION_SUMMARY:(.+):([0-9]+):([0-9]+) ]]; then
                local sub_clusters="${BASH_REMATCH[2]}"
                local sub_successful="${BASH_REMATCH[3]}"
                total_clusters=$((total_clusters + sub_clusters))
                total_successful=$((total_successful + sub_successful))
            fi
        fi
    done < <(echo "$subscriptions_json" | jq -r '.[] | "\(.id)|\(.name)"')

    # Final summary
    echo
    log_info "============================================================"
    log_info "FINAL SUMMARY"
    log_info "============================================================"
    log_info "Total subscriptions processed: $total_subscriptions"
    log_info "Total AKS clusters found: $total_clusters"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN completed - no actual changes were made"
    else
        log_info "Successfully configured: $total_successful/$total_clusters clusters"
        if [[ $total_successful -lt $total_clusters ]]; then
            log_warn "Failed to configure $((total_clusters - total_successful)) cluster(s)"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --subscription|-s)
            if [[ -n "${2:-}" ]]; then
                SUBSCRIPTION_FILTER+=("$2")
                shift 2
            else
                log_error "Subscription option requires a value"
                exit 1
            fi
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run main function
main
