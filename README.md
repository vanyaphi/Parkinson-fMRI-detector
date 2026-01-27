# Parkinson's Disease fMRI Detection on AWS SageMaker

This project implements a comprehensive machine learning pipeline for detecting Parkinson's disease from functional MRI (fMRI) data using AWS SageMaker Notebook Instances. The solution includes automated infrastructure deployment, GitHub integration, data processing, feature extraction, and multiple classification algorithms. Most of the code is generated using Claude Code, is currently under development.

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
│   └── ses-01/
│       ├── func/
│       │   └── sub-0203_ses-01_task-rest_bold.nii.gz
│       └── anat/
│           └── sub-0203_ses-01_T1w.nii.gz
├── sub-1001/
│   └── ses-01/
│       ├── func/
│       │   └── sub-1001_ses-01_task-rest_bold.nii.gz
│       └── anat/
│           └── sub-1001_ses-01_T1w.nii.gz
└── sub-XXXX/
    └── ses-XX/
        ├── func/
        │   └── sub-XXXX_ses-XX_task-rest_bold.nii.gz
        └── anat/
            └── sub-XXXX_ses-XX_T1w.nii.gz
```

**File Naming Convention:**
- Functional data: `sub-XXXX_ses-XX_task-rest_bold.nii.gz`
- Anatomical data: `sub-XXXX_ses-XX_T1w.nii.gz`

**Subject ID Classification:**
- Subject IDs < 1000: Assumed to be healthy controls
- Subject IDs ≥ 1000: Assumed to be Parkinson's disease patients
- You can modify this logic in the notebook based on your dataset

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
- **fMRIPrep Integration**: Support for fMRIPrep preprocessed data and confound regression  (under development)
- **ROI Extraction**: Harvard-Oxford atlas-based region extraction  (under development)
- **Feature Engineering**: 1000+ features per subject (under development) including: 
  - Regional time series statistics
  - Functional connectivity matrices
  - Network topology measures
  - Frequency domain characteristics

### Machine Learning
- **Multiple Algorithms**: SVM, Random Forest, Logistic Regression, Deep Neural Networks  (under development)
- **Feature Selection**: Statistical significance testing and effect size analysis  (under development)
- **Class Balancing**: SMOTE for handling imbalanced datasets  (under development)
- **Cross-Validation**: Robust performance estimation  (under development)
- **Hyperparameter Tuning**: Automated optimization  (under development)

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
- **ROC Curves**: Model performance comparison  (under development)
- **Confusion Matrices**: Classification accuracy visualization  (under development)
- **Feature Importance**: Top discriminative features  (under development)
- **Statistical Analysis**: Group differences and effect sizes  (under development)
- **Comprehensive Reports**: Automated summary generation  (under development)

### Cost Optimization
- **Auto-Shutdown**: 30-minute idle timeout for notebook instances
- **S3 Lifecycle**: Automatic data archiving
- **Resource Monitoring**: CloudWatch integration
- **EBS Optimization**: Right-sized storage volumes

## 📊 Expected Results

The pipeline typically achieves:
- **Accuracy**: ?? depending on dataset quality
- **AUC Score**: ??for well-preprocessed data
- **Processing Time**: 10-30 minutes for 50 subjects
- **Feature Count**: 500-2000 features per subject

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

- [fMRIPrep Documentation](https://fmriprep.org/)
- [Nilearn Documentation](https://nilearn.github.io/)
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Parkinson's Disease Neuroimaging Research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6294134/)

## 🧠 fMRIPrep Integration

This project includes comprehensive support for fMRIPrep preprocessed data, which provides robust and standardized preprocessing of fMRI data. The code is currently under development and has not been tested yet.

### What is fMRIPrep?

fMRIPrep is a preprocessing pipeline that performs:
- **Motion correction**: Realignment to reference volume
- **Slice timing correction**: Temporal alignment of slices
- **Spatial normalization**: Registration to standard brain templates
- **Brain extraction**: Skull stripping using ANTs
- **ICA-AROMA**: Automatic removal of motion artifacts
- **Confound estimation**: Motion and physiological noise parameters
- **Quality control**: Comprehensive visual reports

### Using fMRIPrep with This Pipeline


#### 1. fMRIPrep Output Structure

fMRIPrep generates several important files:

```
derivatives/fmriprep/
├── sub-XXXX/
│   ├── ses-XX/
│   │   ├── func/
│   │   │   ├── sub-XXXX_ses-XX_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
│   │   │   ├── sub-XXXX_ses-XX_task-rest_desc-confounds_timeseries.tsv
│   │   │   └── sub-XXXX_ses-XX_task-rest_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz
│   │   └── anat/
│   │       └── sub-XXXX_ses-XX_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz
│   └── figures/
│       └── sub-XXXX_ses-XX_task-rest_desc-summary_bold.html
```

#### 2. Key fMRIPrep Features Used

- **MNI152NLin2009cAsym space**: Standard brain template for group analysis (under development)
- **ICA-AROMA**: Removes motion-related artifacts automatically  (under development)
- **Confound regressors**: Motion parameters, global signals, and noise components  (under development)
- **Brain masks**: Precise brain extraction for analysis  (under development)
- **Quality reports**: Visual inspection of preprocessing quality  (under development)

#### 4. Confound Regression

The notebook automatically detects and uses fMRIPrep confound files:

- **Motion parameters**: Translation and rotation in 6 directions  (under development)
- **Framewise displacement**: Summary motion metric  (under development)
- **Global signals**: Whole-brain, CSF, and white matter signals  (under development)
- **DVARS**: Temporal derivative of BOLD signal variance  (under development)
- **Physiological noise**: Respiratory and cardiac-related components  (under development)

#### 5. Quality Assessment

The pipeline provides comprehensive quality metrics:

- **Motion assessment**: Framewise displacement analysis  (under development)
- **Signal quality**: Temporal signal-to-noise ratio  (under development)
- **Artifact detection**: Identification of problematic volumes  (under development)
- **Coverage analysis**: Brain mask quality evaluation  (under development)



---

**Note**: This is a research tool and should not be used for clinical diagnosis without proper validation and regulatory approval.