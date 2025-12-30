# Troubleshooting Guide

## Common CloudFormation Deployment Issues

### 1. Property Validation Errors

**Error**: `AWS::EarlyValidation::PropertyValidation`

**Solutions**:
- Use the fixed template: `fmri-notebook-infrastructure-fixed.yaml`
- Validate template before deployment: `./validate-template.sh`
- Ensure all parameter values are within allowed ranges

### 2. S3 Bucket Name Conflicts

**Error**: `BucketAlreadyExists` or `BucketAlreadyOwnedByYou`

**Solutions**:
```bash
# Use a unique bucket name
./deploy-fmri-infrastructure.sh --bucket-name my-unique-fmri-bucket-$(date +%s)
```

### 3. IAM Permission Issues

**Error**: `AccessDenied` or insufficient permissions

**Solutions**:
- Ensure your AWS credentials have the following permissions:
  - `cloudformation:*`
  - `iam:CreateRole`, `iam:AttachRolePolicy`, `iam:PassRole`
  - `sagemaker:*`
  - `s3:CreateBucket`, `s3:PutBucketPolicy`
  - `lambda:CreateFunction`

### 4. GitHub Repository Access

**Error**: Repository clone fails in notebook

**Solutions**:
- **Public Repositories**: Ensure the repository URL is correct and accessible
- **Private Repositories**: Use GitHub credentials with deployment script:
  ```bash
  ./deploy-fmri-infrastructure.sh \
      --github-username your-username \
      --github-token ghp_your_personal_access_token
  ```
- **Token Issues**: Ensure GitHub token has `repo` scope permissions
- **Repository URL**: Check the repository exists and is accessible
- **Secrets Manager**: Verify AWS Secrets Manager permissions in IAM role

**GitHub Token Creation**:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy token (starts with `ghp_`) and use with `--github-token`

**Debugging GitHub Integration**:
```bash
# Check if code repository was created
aws sagemaker list-code-repositories

# Check secrets manager (if using private repo)
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `github`)]'

# View notebook lifecycle logs
./manage-notebook.sh logs
```

### 5. Notebook Instance Won't Start

**Error**: Notebook stuck in `Pending` state

**Solutions**:
```bash
# Check notebook status
./manage-notebook.sh status

# View CloudWatch logs
./manage-notebook.sh logs

# Try different instance type
./deploy-fmri-infrastructure.sh --instance-type ml.m5.large
```

### 6. Auto-Shutdown Not Working

**Error**: Notebook doesn't shut down after idle time

**Solutions**:
- Check if lifecycle configuration is applied
- Verify systemd service is running:
  ```bash
  # In notebook terminal
  sudo systemctl status sagemaker-auto-shutdown.service
  ```
- Check auto-shutdown logs:
  ```bash
  # In notebook terminal
  sudo journalctl -u sagemaker-auto-shutdown.service -f
  ```

## Deployment Best Practices

### 1. Pre-Deployment Checklist

```bash
# 1. Validate AWS credentials
aws sts get-caller-identity

# 2. Validate template
./validate-template.sh

# 3. Check region availability
aws sagemaker describe-notebook-instances --region us-east-2

# 4. Deploy with unique names
./deploy-fmri-infrastructure.sh --stack-name my-unique-stack-name
```

### 2. Resource Limits

- **Instance Types**: Start with `ml.t3.medium`, scale up if needed
- **Volume Size**: Minimum 5GB, recommended 20GB for fMRI data
- **Region**: Use `us-east-2` for best availability

### 3. Cost Management

```bash
# Monitor costs
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost

# Stop notebook when not in use
./manage-notebook.sh stop

# Clean up resources
aws cloudformation delete-stack --stack-name parkinson-fmri-notebook-stack
```

## Debugging Commands

### CloudFormation Events
```bash
# View stack events
aws cloudformation describe-stack-events --stack-name parkinson-fmri-notebook-stack

# Get stack status
aws cloudformation describe-stacks --stack-name parkinson-fmri-notebook-stack --query 'Stacks[0].StackStatus'
```

### SageMaker Debugging
```bash
# List notebook instances
aws sagemaker list-notebook-instances

# Get notebook details
aws sagemaker describe-notebook-instance --notebook-instance-name parkinson-fmri-detector

# View notebook logs
aws logs describe-log-groups --log-group-name-prefix "/aws/sagemaker/NotebookInstances"
```

### S3 Debugging
```bash
# List buckets
aws s3 ls

# Check bucket contents
aws s3 ls s3://your-bucket-name --recursive

# Test bucket access
aws s3 cp test.txt s3://your-bucket-name/test.txt
```

## Recovery Procedures

### 1. Stack Rollback
```bash
# If deployment fails, CloudFormation will automatically rollback
# To manually rollback:
aws cloudformation cancel-update-stack --stack-name parkinson-fmri-notebook-stack
```

### 2. Resource Cleanup
```bash
# Delete failed stack
aws cloudformation delete-stack --stack-name parkinson-fmri-notebook-stack

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name parkinson-fmri-notebook-stack

# Redeploy
./deploy-fmri-infrastructure.sh
```

### 3. Manual Resource Cleanup
If CloudFormation fails to delete resources:

```bash
# Stop notebook instance
aws sagemaker stop-notebook-instance --notebook-instance-name parkinson-fmri-detector

# Delete notebook instance
aws sagemaker delete-notebook-instance --notebook-instance-name parkinson-fmri-detector

# Delete S3 bucket (empty it first)
aws s3 rm s3://your-bucket-name --recursive
aws s3 rb s3://your-bucket-name

# Delete IAM roles
aws iam delete-role --role-name parkinson-fmri-detector-execution-role
```

## Getting Help

### 1. AWS Support
- Use AWS Support Center for account-specific issues
- Check AWS Service Health Dashboard for regional issues

### 2. Community Resources
- AWS CloudFormation documentation
- SageMaker developer guide
- GitHub issues for this project

### 3. Logs and Monitoring
- CloudWatch Logs: `/aws/sagemaker/NotebookInstances/`
- CloudFormation Events in AWS Console
- SageMaker notebook instance logs in Jupyter terminal

## Contact Information

For issues specific to this fMRI detection pipeline:
1. Check this troubleshooting guide
2. Review CloudWatch logs
3. Open an issue in the GitHub repository
4. Include relevant error messages and AWS region information