#!/bin/bash

# Deployment script for Parkinson fMRI SageMaker Notebook Infrastructure
# This script deploys the CloudFormation template with proper parameters


## Expected Data Organization

### Controls (Healthy Subjects)
# Place control subject fMRI data in: datasets/controls/
# - Filename pattern: sub-XXX_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz

# ### Patients (Parkinson's Disease)
# Place patient fMRI data in: datasets/patients/
# - Filename pattern: sub-XXX_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz

# ### Preprocessed Data
# If you have additional preprocessed data: preprocessed/

# ### Results
# Analysis results will be saved to: results/

# ### Models
# Trained models will be saved to: models/

# ## Data Requirements
# - fMRI data should be preprocessed with fMRIPrep
# - Data should be in MNI152NLin2009cAsym space
# - Resting-state or task-based fMRI is supported
# - NIfTI format (.nii.gz) required

# ## Getting Started
# 1. Upload your fMRI data to the appropriate folders
# 2. Open the Parkinson's detection notebook
# 3. Run the analysis pipeline
# 4. Review results in the generated reports


set -e

# Default values
STACK_NAME="parkinson-fmri-notebook-stack"
REGION="us-east-2"
NOTEBOOK_NAME="parkinson-fmri-detector"
INSTANCE_TYPE="ml.t3.medium"
BUCKET_NAME="fmri-dataset-bucket"
GITHUB_REPO="https://github.com/vanyaphi/Parkinson-fMRI-detector.git"
VOLUME_SIZE=20

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
        --template-file fmri-notebook-infrastructure.yaml \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides \
            NotebookInstanceName="${NOTEBOOK_NAME}" \
            InstanceType="${INSTANCE_TYPE}" \
            BucketName="${BUCKET_NAME}" \
            GitHubRepository="${GITHUB_REPO}" \
            VolumeSize="${VOLUME_SIZE}" \
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

# Function to upload the notebook (not needed since GitHub repo is cloned)
upload_notebook() {
    print_status "GitHub repository will be automatically cloned to the notebook instance..."
    
    # Get the S3 bucket name from stack outputs
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text)
    
    print_status "S3 bucket created: s3://${S3_BUCKET}/"
    print_status "GitHub repository: ${GITHUB_REPO}"
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
    echo "1. Access SageMaker Notebook Instance:"
    
    NOTEBOOK_URL=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`NotebookInstanceUrl`].OutputValue' \
        --output text)
    
    echo "   ${NOTEBOOK_URL}"
    echo ""
    echo "2. Wait for notebook instance to be 'InService' (may take 5-10 minutes)"
    echo ""
    echo "3. Upload your fMRI data to the S3 bucket:"
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text)
    
    echo "   Controls: s3://${S3_BUCKET}/datasets/controls/"
    echo "   Patients: s3://${S3_BUCKET}/datasets/patients/"
    echo ""
    echo "4. Open the cloned GitHub repository in the notebook:"
    echo "   ${GITHUB_REPO}"
    echo ""
    echo "5. Run the Parkinson's detection analysis notebook"
    echo ""
    print_status "🔧 Auto-Shutdown Features Enabled:"
    echo "   • Notebook will automatically shut down after 30 minutes of inactivity"
    echo "   • Auto-shutdown service monitors kernel activity and file modifications"
    echo "   • Cost optimization through intelligent idle detection"
    echo ""
    print_status "💰 Cost Optimization Features:"
    echo "   • S3 lifecycle policies transition data to cheaper storage classes"
    echo "   • Automatic cleanup of incomplete multipart uploads"
    echo "   • Version management with automatic deletion of old versions"
    echo "   • EBS volume optimization for notebook storage"
    echo ""
    print_status "🔒 Security Features:"
    echo "   • S3 bucket policy enforces HTTPS-only access"
    echo "   • IAM roles follow principle of least privilege"
    echo "   • Encrypted S3 storage with AES-256"
    echo ""
    print_status "📊 GitHub Integration:"
    echo "   • Repository automatically cloned to notebook instance"
    echo "   • Latest code available on notebook startup"
    echo "   • Version control integrated with development workflow"
    echo ""
    print_status "Happy analyzing! 🧠"
}

# Main execution
main() {
    echo "=========================================="
    echo "Parkinson fMRI SageMaker Notebook Deployment"
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
            --notebook-name)
                NOTEBOOK_NAME="$2"
                shift 2
                ;;
            --instance-type)
                INSTANCE_TYPE="$2"
                shift 2
                ;;
            --github-repo)
                GITHUB_REPO="$2"
                shift 2
                ;;
            --volume-size)
                VOLUME_SIZE="$2"
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
                echo "  --stack-name      CloudFormation stack name (default: parkinson-fmri-notebook-stack)"
                echo "  --region          AWS region (default: us-east-2)"
                echo "  --notebook-name   SageMaker notebook instance name (default: parkinson-fmri-detector)"
                echo "  --instance-type   Notebook instance type (default: ml.t3.medium)"
                echo "  --bucket-name     S3 bucket name prefix (default: fmri-dataset-bucket)"
                echo "  --github-repo     GitHub repository URL (default: https://github.com/vanyaphi/Parkinson-fMRI-detector.git)"
                echo "  --volume-size     EBS volume size in GB (default: 20)"
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
    echo "  Notebook Name: ${NOTEBOOK_NAME}"
    echo "  Instance Type: ${INSTANCE_TYPE}"
    echo "  Bucket Name Prefix: ${BUCKET_NAME}"
    echo "  GitHub Repository: ${GITHUB_REPO}"
    echo "  Volume Size: ${VOLUME_SIZE} GB"
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