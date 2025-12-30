#!/bin/bash

# Script to manage SageMaker Notebook Instance for Parkinson fMRI detection

set -e

# Default values
STACK_NAME="parkinson-fmri-notebook-stack"
REGION="us-east-2"
ACTION=""

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

# Function to show current notebook status
show_status() {
    print_status "Checking SageMaker Notebook Instance status..."
    
    # Get notebook instance name
    NOTEBOOK_NAME=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`NotebookInstanceName`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$NOTEBOOK_NAME" ]; then
        # Get notebook instance details
        NOTEBOOK_INFO=$(aws sagemaker describe-notebook-instance \
            --notebook-instance-name "$NOTEBOOK_NAME" \
            --region "${REGION}" 2>/dev/null || echo "")
        
        if [ -n "$NOTEBOOK_INFO" ]; then
            STATUS=$(echo "$NOTEBOOK_INFO" | jq -r '.NotebookInstanceStatus')
            INSTANCE_TYPE=$(echo "$NOTEBOOK_INFO" | jq -r '.InstanceType')
            VOLUME_SIZE=$(echo "$NOTEBOOK_INFO" | jq -r '.VolumeSizeInGB')
            CREATION_TIME=$(echo "$NOTEBOOK_INFO" | jq -r '.CreationTime')
            LAST_MODIFIED=$(echo "$NOTEBOOK_INFO" | jq -r '.LastModifiedTime')
            
            print_info "Notebook Instance: ${NOTEBOOK_NAME}"
            print_info "Status: ${STATUS}"
            print_info "Instance Type: ${INSTANCE_TYPE}"
            print_info "Volume Size: ${VOLUME_SIZE} GB"
            print_info "Created: ${CREATION_TIME}"
            print_info "Last Modified: ${LAST_MODIFIED}"
            
            if [ "$STATUS" = "InService" ]; then
                NOTEBOOK_URL=$(echo "$NOTEBOOK_INFO" | jq -r '.Url')
                print_info "Notebook URL: https://${NOTEBOOK_URL}"
                print_info "Auto-shutdown: ENABLED (30 minutes idle timeout)"
            elif [ "$STATUS" = "Stopped" ]; then
                print_warning "Notebook is currently stopped"
            elif [ "$STATUS" = "Pending" ]; then
                print_info "Notebook is starting up..."
            elif [ "$STATUS" = "Stopping" ]; then
                print_info "Notebook is shutting down..."
            fi
        else
            print_warning "Notebook instance details not found"
        fi
    else
        print_warning "Notebook instance not found in stack outputs"
    fi
}

# Function to start notebook instance
start_notebook() {
    print_status "Starting SageMaker Notebook Instance..."
    
    NOTEBOOK_NAME=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`NotebookInstanceName`].OutputValue' \
        --output text)
    
    if [ -n "$NOTEBOOK_NAME" ]; then
        aws sagemaker start-notebook-instance \
            --notebook-instance-name "$NOTEBOOK_NAME" \
            --region "${REGION}"
        
        print_status "Notebook instance start initiated. It may take 5-10 minutes to be ready."
    else
        print_error "Notebook instance not found. Please deploy the stack first."
        exit 1
    fi
}

# Function to stop notebook instance
stop_notebook() {
    print_warning "Stopping SageMaker Notebook Instance..."
    
    NOTEBOOK_NAME=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`NotebookInstanceName`].OutputValue' \
        --output text)
    
    if [ -n "$NOTEBOOK_NAME" ]; then
        aws sagemaker stop-notebook-instance \
            --notebook-instance-name "$NOTEBOOK_NAME" \
            --region "${REGION}"
        
        print_warning "Notebook instance stop initiated."
    else
        print_error "Notebook instance not found."
        exit 1
    fi
}

# Function to get notebook logs
get_logs() {
    print_status "Retrieving notebook instance logs..."
    
    NOTEBOOK_NAME=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`NotebookInstanceName`].OutputValue' \
        --output text)
    
    if [ -n "$NOTEBOOK_NAME" ]; then
        # Get CloudWatch log groups for the notebook
        LOG_GROUPS=$(aws logs describe-log-groups \
            --log-group-name-prefix "/aws/sagemaker/NotebookInstances/${NOTEBOOK_NAME}" \
            --region "${REGION}" \
            --query 'logGroups[*].logGroupName' \
            --output text)
        
        if [ -n "$LOG_GROUPS" ]; then
            for LOG_GROUP in $LOG_GROUPS; do
                print_info "Log Group: $LOG_GROUP"
                aws logs describe-log-streams \
                    --log-group-name "$LOG_GROUP" \
                    --region "${REGION}" \
                    --query 'logStreams[0:3].[logStreamName,creationTime]' \
                    --output table
            done
        else
            print_warning "No log groups found for notebook instance"
        fi
    else
        print_error "Notebook instance not found."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS] ACTION"
    echo ""
    echo "Actions:"
    echo "  status              Show current notebook instance status"
    echo "  start               Start the notebook instance"
    echo "  stop                Stop the notebook instance"
    echo "  logs                Show notebook instance logs"
    echo ""
    echo "Options:"
    echo "  --stack-name NAME   CloudFormation stack name (default: parkinson-fmri-notebook-stack)"
    echo "  --region REGION     AWS region (default: us-east-2)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 logs"
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
    echo "SageMaker Notebook Instance Management"
    echo "=============================================="
    echo ""
    
    case $ACTION in
        status)
            show_status
            ;;
        start)
            start_notebook
            ;;
        stop)
            stop_notebook
            ;;
        logs)
            get_logs
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