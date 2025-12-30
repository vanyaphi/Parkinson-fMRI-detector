#!/bin/bash

# Script to validate CloudFormation template

set -e

TEMPLATE_FILE="fmri-notebook-infrastructure.yaml"
REGION="us-east-2"

echo "Validating CloudFormation template: ${TEMPLATE_FILE}"

# Validate template syntax
aws cloudformation validate-template \
    --template-body file://${TEMPLATE_FILE} \
    --region ${REGION}

if [ $? -eq 0 ]; then
    echo "✅ Template validation successful!"
    echo ""
    echo "Template Summary:"
    echo "- Parameters: NotebookInstanceName, InstanceType, BucketName, GitHubRepository, GitHubUsername, GitHubToken, VolumeSize"
    echo "- Resources: S3 Bucket, SageMaker Notebook Instance, Code Repository, IAM Roles, Lifecycle Config, Secrets Manager"
    echo "- Features: Auto-shutdown, GitHub integration (public/private), fMRI package installation, secure credential storage"
    echo ""
    echo "Ready for deployment with: ./deploy-fmri-infrastructure.sh"
else
    echo "❌ Template validation failed!"
    exit 1
fi