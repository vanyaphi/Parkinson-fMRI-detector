#!/bin/bash

# Script to manage auto-shutdown settings for fMRI SageMaker infrastructure

set -e

# Default values
STACK_NAME="fmri-sagemaker-stack"
REGION="us-east-2"
ACTION=""
IDLE_TIME_MINUTES=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to show current auto-shutdown status
show_status() {
    print_status "Checking auto-shutdown status..."
    
    # Get Lambda function details
    FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`IdleShutdownFunctionArn`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$FUNCTION_NAME" ]; then
        # Get function configuration
        FUNCTION_CONFIG=$(aws lambda get-function-configuration \
            --function-name "$FUNCTION_NAME" \
            --region "${REGION}" 2>/dev/null || echo "")
        
        if [ -n "$FUNCTION_CONFIG" ]; then
            CURRENT_IDLE_TIME=$(echo "$FUNCTION_CONFIG" | jq -r '.Environment.Variables.IDLE_TIME_MINUTES // "30"')
            print_info "Auto-shutdown Lambda function: ACTIVE"
            print_info "Current idle timeout: ${CURRENT_IDLE_TIME} minutes"
        else
            print_warning "Auto-shutdown Lambda function: NOT FOUND"
        fi
    else
        print_warning "Auto-shutdown Lambda function: NOT DEPLOYED"
    fi
    
    # Check EventBridge rule
    RULE_NAME="${STACK_NAME}-idle-shutdown-schedule"
    RULE_STATUS=$(aws events describe-rule \
        --name "$RULE_NAME" \
        --region "${REGION}" \
        --query 'State' \
        --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$RULE_STATUS" = "ENABLED" ]; then
        print_info "EventBridge schedule: ENABLED (runs every 30 minutes)"
    elif [ "$RULE_STATUS" = "DISABLED" ]; then
        print_warning "EventBridge schedule: DISABLED"
    else
        print_warning "EventBridge schedule: NOT FOUND"
    fi
    
    # Check running SageMaker apps
    DOMAIN_ID=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`SageMakerDomainId`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$DOMAIN_ID" ]; then
        print_info "Checking running SageMaker apps..."
        
        APPS=$(aws sagemaker list-apps \
            --domain-id-equals "$DOMAIN_ID" \
            --region "${REGION}" \
            --query 'Apps[?Status==`InService`].[AppName,AppType,UserProfileName,Status]' \
            --output table 2>/dev/null || echo "")
        
        if [ -n "$APPS" ] && [ "$APPS" != "None" ]; then
            echo "$APPS"
        else
            print_info "No running SageMaker apps found"
        fi
    fi
}

# Function to update idle timeout
update_timeout() {
    print_status "Updating idle timeout to ${IDLE_TIME_MINUTES} minutes..."
    
    FUNCTION_ARN=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`IdleShutdownFunctionArn`].OutputValue' \
        --output text)
    
    if [ -n "$FUNCTION_ARN" ]; then
        aws lambda update-function-configuration \
            --function-name "$FUNCTION_ARN" \
            --environment "Variables={DOMAIN_ID=$(aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" --query 'Stacks[0].Outputs[?OutputKey==`SageMakerDomainId`].OutputValue' --output text),IDLE_TIME_MINUTES=${IDLE_TIME_MINUTES}}" \
            --region "${REGION}"
        
        print_status "Idle timeout updated successfully!"
    else
        print_error "Lambda function not found. Please deploy the stack first."
        exit 1
    fi
}

# Function to enable auto-shutdown
enable_shutdown() {
    print_status "Enabling auto-shutdown..."
    
    RULE_NAME="${STACK_NAME}-idle-shutdown-schedule"
    aws events enable-rule \
        --name "$RULE_NAME" \
        --region "${REGION}"
    
    print_status "Auto-shutdown enabled!"
}

# Function to disable auto-shutdown
disable_shutdown() {
    print_warning "Disabling auto-shutdown..."
    
    RULE_NAME="${STACK_NAME}-idle-shutdown-schedule"
    aws events disable-rule \
        --name "$RULE_NAME" \
        --region "${REGION}"
    
    print_warning "Auto-shutdown disabled! Remember to manually stop instances to avoid charges."
}

# Function to manually trigger shutdown check
trigger_shutdown_check() {
    print_status "Manually triggering shutdown check..."
    
    FUNCTION_ARN=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`IdleShutdownFunctionArn`].OutputValue' \
        --output text)
    
    if [ -n "$FUNCTION_ARN" ]; then
        RESULT=$(aws lambda invoke \
            --function-name "$FUNCTION_ARN" \
            --region "${REGION}" \
            --payload '{}' \
            /tmp/lambda-response.json)
        
        print_status "Shutdown check triggered. Response:"
        cat /tmp/lambda-response.json
        rm -f /tmp/lambda-response.json
    else
        print_error "Lambda function not found."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS] ACTION"
    echo ""
    echo "Actions:"
    echo "  status              Show current auto-shutdown status"
    echo "  enable              Enable auto-shutdown"
    echo "  disable             Disable auto-shutdown"
    echo "  update-timeout      Update idle timeout (use with --timeout)"
    echo "  trigger             Manually trigger shutdown check"
    echo ""
    echo "Options:"
    echo "  --stack-name NAME   CloudFormation stack name (default: fmri-sagemaker-stack)"
    echo "  --region REGION     AWS region (default: us-east-2)"
    echo "  --timeout MINUTES   Idle timeout in minutes (default: 30)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 update-timeout --timeout 60"
    echo "  $0 disable"
    echo "  $0 enable"
    echo "  $0 trigger"
}

# Main execution
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --stack-name)
                STACK_NAME="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --timeout)
                IDLE_TIME_MINUTES="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            status|enable|disable|update-timeout|trigger)
                ACTION="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    if [ -z "$ACTION" ]; then
        print_error "No action specified"
        show_help
        exit 1
    fi
    
    echo "=============================================="
    echo "fMRI SageMaker Auto-Shutdown Management"
    echo "=============================================="
    echo ""
    
    case $ACTION in
        status)
            show_status
            ;;
        enable)
            enable_shutdown
            ;;
        disable)
            disable_shutdown
            ;;
        update-timeout)
            update_timeout
            ;;
        trigger)
            trigger_shutdown_check
            ;;
        *)
            print_error "Unknown action: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"