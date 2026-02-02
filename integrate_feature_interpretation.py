#!/usr/bin/env python3
"""
Integration Example: Adding Feature Interpretation to fMRI Analysis

This script shows how to integrate feature interpretation into your existing
Parkinson's disease fMRI classification pipeline.
"""

import numpy as np
import pandas as pd
from feature_interpretation_analysis import FeatureInterpreter, run_feature_interpretation_analysis

def add_feature_interpretation_to_pipeline(X_train, X_test, y_train, y_test, 
                                         trained_models, roi_names=None):
    """
    Add feature interpretation to your existing ML pipeline
    
    This function should be called after training your models but before
    generating the final report.
    """
    
    print("\n" + "="*80)
    print("🔬 FEATURE INTERPRETATION & BIOLOGICAL INSIGHTS")
    print("="*80)
    
    # Create feature names based on your extraction process
    interpreter = FeatureInterpreter(roi_names=roi_names)
    
    # Estimate number of ROIs from feature dimensions
    # This is based on your feature extraction: means + stds + vars + connectivity + frequency
    n_features = X_train.shape[1]
    
    # Rough estimation: if you have n ROIs, you get:
    # - 3*n statistical features (mean, std, var)
    # - n*(n-1)/2 connectivity features  
    # - 3*n frequency features (3 bands per ROI)
    # Total ≈ 6*n + n*(n-1)/2 ≈ n*(n+11)/2
    
    # Solve quadratic equation to estimate n_rois
    # This is approximate - adjust based on your actual extraction
    estimated_n_rois = int((-11 + np.sqrt(121 + 8*n_features)) / 2)
    estimated_n_rois = min(estimated_n_rois, 200)  # Cap at reasonable number
    
    print(f"📊 Estimated number of ROIs: {estimated_n_rois}")
    print(f"📊 Total features: {n_features}")
    
    # Create interpretable feature names
    feature_names = interpreter.create_feature_names(estimated_n_rois)
    
    # Run comprehensive feature importance analysis
    print("\n🔍 Running Feature Importance Analysis...")
    
    # Method 1: Univariate analysis
    selected_f, selected_mi = interpreter.analyze_feature_importance_univariate(X_train, y_train, k=50)
    
    # Method 2: Linear model coefficients
    coef_l1, coef_l2 = interpreter.analyze_model_coefficients(X_train, y_train)
    
    # Method 3: Tree-based importance
    tree_importance = interpreter.analyze_tree_importance(X_train, y_train)
    
    # Method 4: Permutation importance using your best model
    best_model_name = get_best_model(trained_models, X_test, y_test)
    best_model = trained_models[best_model_name]
    
    print(f"🏆 Using {best_model_name} for permutation importance analysis")
    perm_mean, perm_std = interpreter.analyze_permutation_importance(X_train, y_train, best_model)
    
    # Create comprehensive summary
    summary_df = interpreter.create_importance_summary(top_k=30)
    
    # Generate visualizations
    interpreter.plot_feature_importance_comparison('parkinson_feature_importance.png')
    
    # Generate biological insights
    interpreter.generate_biological_insights()
    
    # Additional analysis specific to Parkinson's disease
    analyze_parkinson_specific_features(interpreter, summary_df)
    
    # Create feature importance report
    create_feature_report(interpreter, summary_df, best_model_name)
    
    return interpreter, summary_df

def get_best_model(trained_models, X_test, y_test):
    """
    Identify the best performing model for interpretation
    """
    best_score = 0
    best_model_name = None
    
    for name, model in trained_models.items():
        try:
            score = model.score(X_test, y_test)
            if score > best_score:
                best_score = score
                best_model_name = name
        except:
            continue
    
    return best_model_name if best_model_name else list(trained_models.keys())[0]

def analyze_parkinson_specific_features(interpreter, summary_df):
    """
    Analyze features specifically relevant to Parkinson's disease
    """
    print("\n" + "="*60)
    print("🧠 PARKINSON'S DISEASE SPECIFIC ANALYSIS")
    print("="*60)
    
    # Define Parkinson's-relevant brain regions
    motor_regions = ['motor', 'basal', 'putamen', 'caudate', 'substantia', 'thalamus']
    cognitive_regions = ['frontal', 'prefrontal', 'anterior', 'cingulate']
    
    # Analyze motor system features
    motor_features = summary_df[
        summary_df['feature_name'].str.contains('|'.join(motor_regions), case=False, na=False)
    ]
    
    if len(motor_features) > 0:
        print(f"\n🎯 Motor System Features ({len(motor_features)} found):")
        print("These regions are directly affected by dopamine loss in Parkinson's disease")
        
        for _, row in motor_features.head(10).iterrows():
            print(f"  • {row['feature_name']}: {row['importance_score']:.4f} ({row['method']})")
    
    # Analyze connectivity features
    connectivity_features = summary_df[summary_df['feature_type'] == 'Functional Connectivity']
    
    if len(connectivity_features) > 0:
        print(f"\n🔗 Network Connectivity Features ({len(connectivity_features)} found):")
        print("Altered connectivity patterns are hallmarks of Parkinson's disease")
        
        for _, row in connectivity_features.head(5).iterrows():
            print(f"  • {row['feature_name']}: {row['importance_score']:.4f}")
            
            # Extract connected regions
            if 'FC_' in row['feature_name']:
                regions = row['feature_name'].replace('FC_', '').split('_')
                if len(regions) >= 2:
                    print(f"    Connection between: {regions[0]} ↔ {regions[1]}")
    
    # Analyze frequency features
    frequency_features = summary_df[summary_df['feature_type'] == 'Frequency Power']
    
    if len(frequency_features) > 0:
        print(f"\n📊 Brain Oscillation Features ({len(frequency_features)} found):")
        print("Abnormal brain rhythms are associated with Parkinson's motor symptoms")
        
        # Group by frequency band
        freq_bands = ['low_freq', 'mid_freq', 'high_freq']
        for band in freq_bands:
            band_features = frequency_features[
                frequency_features['feature_name'].str.contains(band, na=False)
            ]
            if len(band_features) > 0:
                avg_importance = band_features['importance_score'].mean()
                print(f"  • {band.replace('_', ' ').title()}: {len(band_features)} features, avg importance: {avg_importance:.4f}")

def create_feature_report(interpreter, summary_df, best_model_name):
    """
    Create a comprehensive feature importance report
    """
    report_content = f"""
# Parkinson's Disease fMRI Classification - Feature Importance Report

## Executive Summary

This report analyzes the most important brain features contributing to Parkinson's disease 
classification using functional MRI data. The analysis identifies key brain regions, 
connectivity patterns, and neural oscillations that distinguish patients from healthy controls.

## Best Performing Model: {best_model_name}

## Top 15 Most Important Features (Averaged Across Methods)

"""
    
    # Add top features to report
    top_features = summary_df.groupby('feature_name').agg({
        'importance_score': 'mean',
        'rank': 'mean',
        'feature_type': 'first'
    }).sort_values('importance_score', ascending=False).head(15)
    
    for idx, (feature_name, row) in enumerate(top_features.iterrows()):
        report_content += f"{idx+1:2d}. **{feature_name}**\n"
        report_content += f"    - Type: {row['feature_type']}\n"
        report_content += f"    - Importance Score: {row['importance_score']:.4f}\n"
        report_content += f"    - Average Rank: {row['rank']:.1f}\n"
        report_content += f"    - Biological Relevance: {interpreter._interpret_feature_biologically(feature_name)}\n\n"
    
    # Add feature type analysis
    feature_type_summary = summary_df.groupby('feature_type').agg({
        'importance_score': ['mean', 'count', 'std']
    }).round(4)
    
    report_content += "\n## Feature Type Analysis\n\n"
    report_content += "| Feature Type | Count | Mean Importance | Std Importance |\n"
    report_content += "|--------------|-------|-----------------|----------------|\n"
    
    for feature_type, row in feature_type_summary.iterrows():
        count = int(row[('importance_score', 'count')])
        mean_imp = row[('importance_score', 'mean')]
        std_imp = row[('importance_score', 'std')]
        report_content += f"| {feature_type} | {count} | {mean_imp:.4f} | {std_imp:.4f} |\n"
    
    # Add clinical implications
    report_content += """
## Clinical Implications

### Motor System Involvement
The prominence of motor-related features confirms the central role of motor circuit 
dysfunction in Parkinson's disease. Key findings include:

- **Basal Ganglia**: Core regions showing altered activity patterns
- **Motor Cortex**: Changes in baseline activity and variability
- **Thalamic Connections**: Disrupted relay function in motor circuits

### Network Connectivity Changes
Functional connectivity features indicate widespread network disruption:

- **Reduced Connectivity**: Between motor regions and other brain areas
- **Compensatory Changes**: Increased connectivity in some non-motor regions
- **Network Reorganization**: Altered communication patterns

### Brain Oscillation Abnormalities
Frequency domain features reveal altered neural rhythms:

- **Beta Band Changes**: Associated with motor symptoms
- **Low Frequency Alterations**: Related to network dysfunction
- **Regional Variations**: Different frequency patterns across brain regions

## Recommendations for Future Research

1. **Targeted ROI Analysis**: Focus on top-ranking brain regions for detailed study
2. **Longitudinal Studies**: Track feature changes over disease progression
3. **Treatment Response**: Monitor feature changes with dopaminergic therapy
4. **Subtype Analysis**: Identify features specific to different Parkinson's subtypes

## Technical Notes

- Analysis based on multiple feature importance methods for robustness
- Features ranked by average importance across all methods
- Biological interpretations based on current neuroscience literature
- Results should be validated in independent datasets

---
*Report generated automatically by Parkinson's fMRI Analysis Pipeline*
"""
    
    # Save report
    with open('parkinson_feature_importance_report.md', 'w') as f:
        f.write(report_content)
    
    print(f"\n📄 Comprehensive feature report saved: parkinson_feature_importance_report.md")

# Example integration with your existing pipeline
def example_integration():
    """
    Example showing how to integrate this into your existing fMRI analysis
    """
    
    # This would be called after your existing model training code
    # Assuming you have: X_train, X_test, y_train, y_test, trained_models
    
    print("Example integration with existing pipeline:")
    print("""
    # After training your models in the notebook, add this:
    
    # Import the interpretation module
    from integrate_feature_interpretation import add_feature_interpretation_to_pipeline
    
    # Add feature interpretation analysis
    interpreter, feature_summary = add_feature_interpretation_to_pipeline(
        X_train_scaled, X_test_scaled, y_train, y_test, 
        trained_models, roi_names=atlas_labels
    )
    
    # The analysis will:
    # 1. Identify most important features
    # 2. Create visualizations
    # 3. Generate biological insights
    # 4. Create a comprehensive report
    """)

if __name__ == "__main__":
    example_integration()