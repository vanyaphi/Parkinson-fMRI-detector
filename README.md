# Parkinson's Disease fMRI Detection on AWS SageMaker

This project implements a comprehensive machine learning pipeline for detecting Parkinson's disease from functional MRI (fMRI) data using AWS SageMaker. The solution includes automated infrastructure deployment, data processing, feature extraction, and multiple classification algorithms.

## 🧠 Overview

The pipeline analyzes resting-state fMRI data to distinguish between Parkinson's disease patients and healthy controls using:

- **Functional Connectivity Analysis**: Brain region correlation patterns
- **Regional Activity Measures**: Statistical properties of brain regions
- **Frequency Domain Features**: Power spectral analysis
- **Multiple ML Algorithms**: SVM, Random Forest, Logistic Regression, and Deep Neural Networks

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   S3 Bucket     │    │   SageMaker      │    │   CloudWatch    │
│                 │    │   Studio         │    │   Monitoring    │
│ ├── datasets/   │◄──►│                  │◄──►│                 │
│ ├── results/    │    │ ├── Notebooks    │    │ ├── Metrics     │
│ └── models/     │    │ ├── Processing   │    │ └── Logs        │
└─────────────────┘    │ └── Training     │    └─────────────────┘
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │   Auto-Shutdown  │
                       │   Lambda         │
                       │   (30min idle)   │
                       └──────────────────┘
```

## 📁 Project Structure

```
├── parkinson_fmri_detector_sagemaker.ipynb  # Main analysis notebook
├── fmri-sagemaker-infrastructure.yaml       # CloudFormation template
├── deploy-fmri-infrastructure.sh            # Deployment script
├── manage-auto-shutdown.sh                  # Auto-shutdown management
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
chmod +x deploy-fmri-infrastructure.sh manage-auto-shutdown.sh

# Deploy with default settings
./deploy-fmri-infrastructure.sh

# Or customize deployment
./deploy-fmri-infrastructure.sh \
    --stack-name my-parkinson-stack \
    --region us-west-2 \
    --domain-name my-fmri-domain
```

### 2. Upload Your Data

Organize your fMRI data in S3 following this structure:

```
s3://your-bucket/datasets/
├── controls/
│   ├── sub-001_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
│   └── sub-002_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
└── patients/
    ├── sub-101_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
    └── sub-102_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
```

### 3. Run Analysis

1. Access SageMaker Studio via the provided URL
2. Open the notebook: `parkinson_fmri_detector_sagemaker.ipynb`
3. Execute cells sequentially
4. Review results in the generated reports

## 🔧 Features

### Data Processing
- **Automated S3 Integration**: Seamless data loading from S3
- **ROI Extraction**: Harvard-Oxford atlas-based region extraction
- **Feature Engineering**: 1000+ features per subject including:
  - Regional time series statistics
  - Functional connectivity matrices
  - Network topology measures
  - Frequency domain characteristics

### Machine Learning
- **Multiple Algorithms**: SVM, Random Forest, Logistic Regression, Deep Neural Networks
- **Feature Selection**: Statistical significance testing and effect size analysis
- **Class Balancing**: SMOTE for handling imbalanced datasets
- **Cross-Validation**: Robust performance estimation
- **Hyperparameter Tuning**: Automated optimization

### Visualization & Reporting
- **ROC Curves**: Model performance comparison
- **Confusion Matrices**: Classification accuracy visualization
- **Feature Importance**: Top discriminative features
- **Statistical Analysis**: Group differences and effect sizes
- **Comprehensive Reports**: Automated summary generation

### Cost Optimization
- **Auto-Shutdown**: 30-minute idle timeout for notebooks
- **S3 Lifecycle**: Automatic data archiving
- **Resource Monitoring**: CloudWatch integration
- **Spot Instances**: Optional cost reduction

## 📊 Expected Results

The pipeline typically achieves:
- **Accuracy**: 75-90% depending on dataset quality
- **AUC Score**: 0.80-0.95 for well-preprocessed data
- **Processing Time**: 10-30 minutes for 50 subjects
- **Feature Count**: 500-2000 features per subject

## 🛠️ Management Commands

### Auto-Shutdown Management
```bash
# Check current status
./manage-auto-shutdown.sh status

# Disable auto-shutdown temporarily
./manage-auto-shutdown.sh disable

# Change idle timeout to 60 minutes
./manage-auto-shutdown.sh update-timeout --timeout 60

# Manually trigger shutdown check
./manage-auto-shutdown.sh trigger
```

### Infrastructure Management
```bash
# Update stack
aws cloudformation update-stack \
    --stack-name fmri-sagemaker-stack \
    --template-body file://fmri-sagemaker-infrastructure.yaml

# Delete stack (cleanup)
aws cloudformation delete-stack \
    --stack-name fmri-sagemaker-stack
```

## 🔒 Security Features

- **VPC Isolation**: SageMaker domain in private VPC
- **IAM Roles**: Principle of least privilege
- **S3 Encryption**: Server-side encryption enabled
- **HTTPS Only**: Enforced secure transport
- **Access Logging**: CloudWatch integration

## 💰 Cost Optimization

### Automatic Features
- **Idle Shutdown**: Notebooks stop after 30 minutes of inactivity
- **S3 Lifecycle**: Data transitions to cheaper storage classes
- **Resource Monitoring**: CloudWatch cost tracking

### Manual Optimization
- Use `ml.t3.medium` instances for development
- Scale to `ml.m5.large` or higher for production
- Consider Spot instances for batch processing
- Archive old results to Glacier/Deep Archive

## 🧪 Sample Data

If you don't have your own fMRI data, the notebook will automatically download sample motor task data from Neurovault for demonstration purposes.

## 📚 Scientific Background

This implementation is based on established neuroimaging research methodologies:

1. **Functional Connectivity**: Altered connectivity patterns in Parkinson's disease
2. **Basal Ganglia Networks**: Motor circuit dysfunction analysis
3. **Default Mode Network**: Resting-state network alterations
4. **Machine Learning**: Pattern recognition in neuroimaging data

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
- Check SageMaker domain status
- Verify IAM permissions
- Review CloudWatch logs

**Data loading errors**
- Verify S3 bucket permissions
- Check file naming conventions
- Ensure data is in correct format

**Out of memory errors**
- Reduce batch size
- Use larger instance type
- Process data in chunks

**Auto-shutdown not working**
- Check Lambda function logs
- Verify EventBridge rule status
- Review IAM permissions

### Support

For issues and questions:
1. Check CloudWatch logs
2. Review AWS documentation
3. Open an issue in the repository

## 🔗 References

- [fMRIPrep Documentation](https://fmriprep.org/)
- [Nilearn Documentation](https://nilearn.github.io/)
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Parkinson's Disease Neuroimaging Research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6294134/)

---

**Note**: This is a research tool and should not be used for clinical diagnosis without proper validation and regulatory approval.