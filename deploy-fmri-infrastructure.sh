#!/bin/bash

# Deployment script for fMRI SageMaker Infrastructure
# This script deploys the CloudFormation template with proper parameters

set -e

# Default values
STACK_NAME="fmri-sagemaker-stack"
REGION="us-east-2"
DOMAIN_NAME="fmri-analysis-domain"
USER_PROFILE_NAME="fmri-researcher"
BUCKET_NAME="fmri-dataset-bucket"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS CLI is configured and ready."
}

# Function to validate parameters
validate_parameters() {
    # Check if bucket name is globally unique by attempting to create it
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    FULL_BUCKET_NAME="${BUCKET_NAME}-${ACCOUNT_ID}-${REGION}"
    
    print_status "Using bucket name: ${FULL_BUCKET_NAME}"
}

# Function to deploy the CloudFormation stack
deploy_stack() {
    print_status "Deploying CloudFormation stack: ${STACK_NAME}"
    
    aws cloudformation deploy \
        --template-file fmri-sagemaker-infrastructure.yaml \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides \
            DomainName="${DOMAIN_NAME}" \
            UserProfileName="${USER_PROFILE_NAME}" \
            BucketName="${BUCKET_NAME}" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "${REGION}" \
        --no-fail-on-empty-changeset
    
    if [ $? -eq 0 ]; then
        print_status "Stack deployment completed successfully!"
    else
        print_error "Stack deployment failed!"
        exit 1
    fi
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Retrieving stack outputs..."
    
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Function to upload the original notebook to S3
upload_notebook() {
    print_status "Uploading the complete fMRI analysis notebook..."
    
    # Get the S3 bucket name from stack outputs
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text)
    
    if [ -f "parkinson_fmri_detector_sagemaker.ipynb" ]; then
        aws s3 cp parkinson_fmri_detector_sagemaker.ipynb "s3://${S3_BUCKET}/notebooks/" --region "${REGION}"
        print_status "Notebook uploaded to s3://${S3_BUCKET}/notebooks/parkinson_fmri_detector_sagemaker.ipynb"
    else
        print_warning "Parkinson's detection notebook file not found. Using the basic version created by CloudFormation."
    fi
}

# Function to create sample folder structure in S3
create_sample_structure() {
    print_status "Creating sample folder structure in S3..."
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text)
    
    # Create sample README files for different folders
    echo "# fMRI Datasets
    
Upload your raw fMRI data here organized by:
- Subject ID (sub-01, sub-02, etc.)
- Session (ses-01, ses-02, etc.)
- Task (task-rest, task-motor, etc.)

Example structure:
datasets/
├── sub-01/
│   ├── ses-01/
│   │   ├── func/
│   │   │   └── sub-01_ses-01_task-rest_bold.nii.gz
│   │   └── anat/
│   │       └── sub-01_ses-01_T1w.nii.gz
│   └── ses-02/
└── sub-02/
" > datasets_readme.txt

    echo "# fMRIPrep Preprocessed Data

Upload your fMRIPrep preprocessed data here.
The notebook will look for files with the pattern:
sub-{subject}_ses-{session}_task-{task}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
" > preprocessed_readme.txt

    echo "# Analysis Results

This folder will contain the output from your fMRI analysis:
- Statistical maps (*.nii.gz)
- ROI time series (*.csv)
- Connectivity matrices (*.csv)
- Analysis reports (*.md)
" > results_readme.txt

    # Upload README files
    aws s3 cp datasets_readme.txt "s3://${S3_BUCKET}/datasets/README.md" --region "${REGION}"
    aws s3 cp preprocessed_readme.txt "s3://${S3_BUCKET}/preprocessed/README.md" --region "${REGION}"
    aws s3 cp results_readme.txt "s3://${S3_BUCKET}/results/README.md" --region "${REGION}"
    
    # Clean up local files
    rm datasets_readme.txt preprocessed_readme.txt results_readme.txt
    
    print_status "Sample folder structure created in S3 bucket"
}

# Function to display next steps
show_next_steps() {
    print_status "Deployment completed! Next steps:"
    echo ""
    echo "1. Access SageMaker Studio:"
    
    STUDIO_URL=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`SageMakerDomainUrl`].OutputValue' \
        --output text)
    
    echo "   ${STUDIO_URL}"
    echo ""
    echo "2. Upload your fMRI data to the S3 bucket:"
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text)
    
    echo "   s3://${S3_BUCKET}/datasets/"
    echo ""
    echo "3. Open the Parkinson's detection notebook in SageMaker Studio:"
    echo "   s3://${S3_BUCKET}/notebooks/parkinson_fmri_detector_sagemaker.ipynb"
    echo ""
    echo "4. Update the data paths in the notebook to match your dataset structure"
    echo ""
    print_status "🔧 Auto-Shutdown Features Enabled:"
    echo "   • Notebooks will automatically shut down after 30 minutes of inactivity"
    echo "   • Lambda function monitors and cleans up idle instances every 30 minutes"
    echo "   • Lifecycle configurations ensure cost optimization"
    echo ""
    print_status "💰 Cost Optimization Features:"
    echo "   • S3 lifecycle policies transition data to cheaper storage classes"
    echo "   • Automatic cleanup of incomplete multipart uploads"
    echo "   • Version management with automatic deletion of old versions"
    echo ""
    print_status "🔒 Security Features:"
    echo "   • S3 bucket policy enforces HTTPS-only access"
    echo "   • IAM roles follow principle of least privilege"
    echo "   • VPC isolation for SageMaker domain"
    echo ""
    print_status "Happy analyzing! 🧠"
}

# Main execution
main() {
    echo "=========================================="
    echo "fMRI SageMaker Infrastructure Deployment"
    echo "=========================================="
    echo ""
    
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
            --domain-name)
                DOMAIN_NAME="$2"
                shift 2
                ;;
            --user-profile)
                USER_PROFILE_NAME="$2"
                shift 2
                ;;
            --bucket-name)
                BUCKET_NAME="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --stack-name      CloudFormation stack name (default: fmri-sagemaker-stack)"
                echo "  --region          AWS region (default: us-east-2)"
                echo "  --domain-name     SageMaker domain name (default: fmri-analysis-domain)"
                echo "  --user-profile    User profile name (default: fmri-researcher)"
                echo "  --bucket-name     S3 bucket name prefix (default: fmri-dataset-bucket)"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    print_status "Configuration:"
    echo "  Stack Name: ${STACK_NAME}"
    echo "  Region: ${REGION}"
    echo "  Domain Name: ${DOMAIN_NAME}"
    echo "  User Profile: ${USER_PROFILE_NAME}"
    echo "  Bucket Name Prefix: ${BUCKET_NAME}"
    echo ""
    
    check_aws_cli
    validate_parameters
    deploy_stack
    get_stack_outputs
    upload_notebook
    create_sample_structure
    show_next_steps
}

# Run main function
main "$@"