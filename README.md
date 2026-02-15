# Parkinson's Disease fMRI Detection on AWS SageMaker

This project implements a comprehensive machine learning pipeline for detecting Parkinson's disease from functional MRI (fMRI) data using AWS SageMaker Notebook Instances. The solution includes automated infrastructure deployment, GitHub integration, data processing, feature extraction, and multiple classification algorithms. Most of the code is generated using Amazon Kiro.

## 🧠 Overview

The pipeline analyzes resting-state fMRI data to distinguish between Parkinson's disease patients and healthy controls using:

- **Functional Connectivity Analysis**: Brain region correlation patterns  (under development)
- **Regional Activity Measures**: Statistical properties of brain regions  (under development)
- **Frequency Domain Features**: Power spectral analysis  (under development)
- **Multiple ML Algorithms**: SVM, Random Forest, Logistic Regression, and Deep Neural Networks  (under development)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   S3 Bucket     │    │   SageMaker      │    │   CloudWatch    │
│                 │    │   Notebook       │    │   Monitoring    │
│ ├── datasets/   │◄──►│   Instance       │◄──►│                 │
│ │ └── Parkinson │    │                  │    │ ├── Metrics     │
│ │   sdisease58/ │    │ ├── GitHub Repo  │    │ └── Logs        │
│ ├── results/    │    │ ├── Auto-Shutdown│    └─────────────────┘
│ └── models/     │    │ └── fMRI Analysis│
└─────────────────┘    └──────────────────┘
```

## 📁 Project Structure

```
├── parkinson_fmri_detector_sagemaker.ipynb  # Main analysis notebook
├── fmri-notebook-infrastructure.yaml        # CloudFormation template
├── deploy-fmri-infrastructure.sh            # Deployment script
├── manage-notebook.sh                       # Notebook management script
└── README.md                                # This file
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- AWS account with SageMaker access
- fMRI data preprocessed with fMRIPrep (optional - sample data provided)

### 1. Deploy Infrastructure

```bash
# Make scripts executable
chmod +x deploy-fmri-infrastructure.sh manage-notebook.sh

# Deploy with default settings (uses public GitHub repo)
./deploy-fmri-infrastructure.sh

# Deploy with private GitHub repository access
./deploy-fmri-infrastructure.sh \
    --github-username your-github-username \
    --github-token ghp_your_personal_access_token

# Or customize deployment with all options
./deploy-fmri-infrastructure.sh \
    --stack-name my-parkinson-stack \
    --region us-west-2 \
    --notebook-name my-fmri-notebook \
    --instance-type ml.m5.large \
    --github-repo https://github.com/your-username/your-private-repo.git \
    --github-username your-username \
    --github-token ghp_your_token
```

#### GitHub Integration Options

**Public Repositories** (default):
- No credentials needed
- Repository is cloned automatically on notebook startup

**Private Repositories**:
- Provide `--github-username` and `--github-token` parameters
- GitHub personal access token is securely stored in AWS Secrets Manager
- Token requires `repo` scope for private repository access

#### Creating a GitHub Personal Access Token

For private repositories, you'll need a GitHub Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Set expiration and select scopes:
   - ✅ `repo` (Full control of private repositories)
4. Copy the generated token (starts with `ghp_`)
5. Use the token with the `--github-token` parameter

**Security Note**: The token is encrypted and stored in AWS Secrets Manager, never logged or displayed in plain text.

### 2. Upload Your Data

Organize your fMRI data in S3 following this structure for the Parkinson's disease dataset:

```
s3://your-bucket/datasets/Parkinsonsdisease58/ds004392-download/
├── sub-0203/
│   ├── func/
│   │   └── sub-0203_task-rest_bold.nii.gz
│   └── anat/
│       └── sub-0203_T1w.nii.gz
├── sub-1001/
│   ├── func/
│   │   └── sub-1001_task-rest_bold.nii.gz
│   └── anat/
│       └── sub-1001_T1w.nii.gz
└── sub-XXXX/
    └── ses-XX/
        ├── func/
        │   └── sub-XXXX_task-rest_bold.nii.gz
        └── anat/
            └── sub-XXXX_T1w.nii.gz
```

**File Naming Convention:**
- Functional data: `sub-XXXX_task-rest_bold.nii.gz`
- Anatomical data: `sub-XXXX_T1w.nii.gz`

**Subject ID Classification:**
- A separate TSV file includes classification of data into Control and Patient.

### 3. Run Analysis

1. Wait for notebook instance to be 'InService' (5-10 minutes)
2. Access the SageMaker Notebook via the provided URL
3. Navigate to the cloned GitHub repository
4. Open the notebook: `parkinson_fmri_detector_sagemaker.ipynb`
5. Execute cells sequentially
6. Review results in the generated reports

## 🔧 Features

### Data Processing
- **GitHub Integration**: Automatic repository cloning with support for private repositories
- **Secure Credentials**: GitHub tokens stored in AWS Secrets Manager
- **Automated S3 Integration**: Seamless data loading from S3
- **fMRI Visualization**: Comprehensive visualization of the first control subject's data
- **ROI Extraction**: Harvard-Oxford atlas-based region extraction 
- **Feature Engineering**: 1000+ features per subject  including: 
  - Regional time series statistics
  - Functional connectivity matrices
  - Frequency domain characteristics

### Machine Learning
- **Multiple Algorithms**: SVM, Random Forest, Logistic Regression  
- **Feature Selection**: Statistical significance testing and effect size analysis 
- **Class Balancing**: SMOTE for handling imbalanced datasets  
- **Cross-Validation**: Robust performance estimation 

### Visualization & Reporting
- **fMRI Data Visualization**: Comprehensive multi-panel visualization including:
  - Mean fMRI images in sagittal, coronal, and axial views
  - Time series plots from central voxels
  - Signal intensity distribution histograms
  - Temporal signal-to-noise ratio (tSNR) maps
  - Motion estimation plots
  - Power spectrum analysis
  - Brain mask visualization
  - Data quality assessment metrics
- **ROC Curves**: Model performance comparison
- **Confusion Matrices**: Classification accuracy visualization
- **Feature Importance**: Top discriminative features
- **Statistical Analysis**: Group differences and effect sizes
- **Comprehensive Reports**: Automated summary generation

### Cost Optimization
- **Auto-Shutdown**: 30-minute idle timeout for notebook instances

## 📊 Expected Results

The pipeline typically achieves:
- **Accuracy**: 60% depending on dataset quality
- **Processing Time**: 1-2 hours for 58 subjects
- **Feature Count**: 1400 features per subject

## 🛠️ Management Commands

### Notebook Instance Management
```bash
# Check notebook status
./manage-notebook.sh status

# Start notebook instance
./manage-notebook.sh start

# Stop notebook instance
./manage-notebook.sh stop

# View notebook logs
./manage-notebook.sh logs
```

### Infrastructure Management
```bash
# Update stack
aws cloudformation update-stack \
    --stack-name parkinson-fmri-notebook-stack \
    --template-body file://fmri-notebook-infrastructure.yaml

# Delete stack (cleanup)
aws cloudformation delete-stack \
    --stack-name parkinson-fmri-notebook-stack
```


## 💰 Cost Optimization

### Automatic Features
- **Idle Shutdown**: Notebooks stop after 30 minutes of inactivity
- **S3 Lifecycle**: Data transitions to cheaper storage classes

### Manual Optimization
- Use `ml.t3.medium` instances for development
- Scale to `ml.m5.large` or higher for production datasets
- Monitor usage with CloudWatch metrics
- Archive old results to Glacier/Deep Archive

## 🧪 Sample Data

If you don't have your own fMRI data, the notebook will automatically download sample motor task data from Neurovault for demonstration purposes.

## 📚 Scientific Background

This implementation is based on established neuroimaging research methodologies:

1. **Functional Connectivity**: Altered connectivity patterns in Parkinson's disease  (under development)
2. **Basal Ganglia Networks**: Motor circuit dysfunction analysis  (under development)
3. **Default Mode Network**: Resting-state network alterations  (under development)
4. **Machine Learning**: Pattern recognition in neuroimaging data  (under development)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Notebook won't start**
- Check notebook instance status with `./manage-notebook.sh status`
- Verify IAM permissions
- Review CloudWatch logs with `./manage-notebook.sh logs`

**GitHub repository not cloned**
- Verify repository URL is accessible
- For private repositories, ensure GitHub credentials are provided
- Check that GitHub token has `repo` scope permissions
- Review notebook instance lifecycle configuration logs
- Verify AWS Secrets Manager permissions for private repositories

**Data loading errors**
- Verify S3 bucket permissions
- Check file naming conventions
- Ensure data is in correct format

**fMRIPrep preprocessing errors**
- Verify BIDS format compliance
- Check FreeSurfer license availability
- Ensure sufficient memory and disk space
- Review fMRIPrep logs for specific errors

**Out of memory errors**
- Reduce batch size in notebook
- Use larger instance type (ml.m5.large or higher)
- Process data in smaller chunks

**Auto-shutdown not working**
- Check notebook instance logs
- Verify lifecycle configuration is applied
- Review systemd service status

### Support

For issues and questions:
1. Check CloudWatch logs
2. Review AWS documentation

## 🔗 References

- [Nilearn Documentation](https://nilearn.github.io/)
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Parkinson's Disease Neuroimaging Research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6294134/)



---

**Note**: This is a research tool and should not be used for clinical diagnosis without proper validation and regulatory approval.
