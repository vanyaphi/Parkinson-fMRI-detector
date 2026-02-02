"""
Add this code to your existing fMRI analysis notebook after model training
to get biological insights from feature importance analysis.
"""

# Add this cell after your model training is complete
# =====================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression

def analyze_top_features_for_biology(X_train, y_train, X_test, y_test, trained_models, atlas_labels=None):
    """
    Quick feature importance analysis for biological insights
    """
    
    print("🧠 ANALYZING TOP FEATURES FOR BIOLOGICAL INSIGHTS")
    print("="*60)
    
    # Method 1: Statistical significance (F-test)
    print("\n1️⃣ Statistical Significance Analysis...")
    selector = SelectKBest(score_func=f_classif, k=30)
    X_selected = selector.fit_transform(X_train, y_train)
    
    feature_scores = selector.scores_
    selected_indices = selector.get_support(indices=True)
    
    print(f"Selected {len(selected_indices)} most statistically significant features")
    
    # Method 2: Linear model coefficients
    print("\n2️⃣ Linear Model Analysis...")
    lr = LogisticRegression(penalty='l2', C=1.0, random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    
    coefficients = np.abs(lr.coef_[0])  # Use absolute values
    
    # Method 3: Permutation importance with best model
    print("\n3️⃣ Permutation Importance Analysis...")
    
    # Find best model
    best_score = 0
    best_model = None
    best_name = ""
    
    for name, model in trained_models.items():
        try:
            score = model.score(X_test, y_test)
            if score > best_score:
                best_score = score
                best_model = model
                best_name = name
        except:
            continue
    
    print(f"Using {best_name} (accuracy: {best_score:.3f}) for permutation analysis")
    
    if best_model is not None:
        perm_importance = permutation_importance(
            best_model, X_train, y_train, n_repeats=5, random_state=42
        )
        perm_scores = perm_importance.importances_mean
    else:
        perm_scores = coefficients  # Fallback to linear model
    
    # Create feature names for interpretation
    n_features = X_train.shape[1]
    
    # Estimate number of ROIs (this is approximate)
    estimated_n_rois = min(int(np.sqrt(n_features / 6)), 100)
    
    feature_names = []
    feature_types = []
    
    # ROI statistical features (mean, std, var)
    for i in range(estimated_n_rois):
        roi_name = f"ROI_{i:03d}" if atlas_labels is None else atlas_labels[i] if i < len(atlas_labels) else f"ROI_{i:03d}"
        feature_names.extend([
            f"{roi_name}_mean",
            f"{roi_name}_std", 
            f"{roi_name}_var"
        ])
        feature_types.extend(['activity', 'variability', 'variability'])
    
    # Connectivity features
    for i in range(estimated_n_rois):
        for j in range(i+1, estimated_n_rois):
            roi_i = f"ROI_{i:03d}" if atlas_labels is None else atlas_labels[i] if i < len(atlas_labels) else f"ROI_{i:03d}"
            roi_j = f"ROI_{j:03d}" if atlas_labels is None else atlas_labels[j] if j < len(atlas_labels) else f"ROI_{j:03d}"
            feature_names.append(f"FC_{roi_i}_{roi_j}")
            feature_types.append('connectivity')
    
    # Frequency features
    freq_bands = ['low', 'mid', 'high']
    for i in range(estimated_n_rois):
        roi_name = f"ROI_{i:03d}" if atlas_labels is None else atlas_labels[i] if i < len(atlas_labels) else f"ROI_{i:03d}"
        for band in freq_bands:
            feature_names.append(f"{roi_name}_{band}_freq")
            feature_types.append('frequency')
    
    # Ensure we don't exceed actual feature count
    feature_names = feature_names[:n_features]
    feature_types = feature_types[:n_features]
    
    # Combine all importance scores
    combined_scores = (
        (feature_scores / np.max(feature_scores)) * 0.3 +  # Normalize F-scores
        (coefficients / np.max(coefficients)) * 0.4 +      # Normalize coefficients  
        (perm_scores / np.max(perm_scores)) * 0.3           # Normalize permutation scores
    )
    
    # Get top features
    top_indices = np.argsort(combined_scores)[-20:][::-1]
    
    print(f"\n🏆 TOP 20 FEATURES FOR PARKINSON'S DETECTION:")
    print("="*60)
    
    results_data = []
    
    for rank, idx in enumerate(top_indices):
        feature_name = feature_names[idx] if idx < len(feature_names) else f"Feature_{idx}"
        feature_type = feature_types[idx] if idx < len(feature_types) else "unknown"
        score = combined_scores[idx]
        
        print(f"{rank+1:2d}. {feature_name}")
        print(f"    Combined Score: {score:.4f}")
        print(f"    Type: {feature_type}")
        
        # Biological interpretation
        interpretation = interpret_feature_biologically(feature_name, feature_type)
        print(f"    Biological Significance: {interpretation}")
        print()
        
        results_data.append({
            'rank': rank + 1,
            'feature_name': feature_name,
            'feature_type': feature_type,
            'combined_score': score,
            'f_score': feature_scores[idx] if idx < len(feature_scores) else 0,
            'coefficient': coefficients[idx] if idx < len(coefficients) else 0,
            'perm_importance': perm_scores[idx] if idx < len(perm_scores) else 0,
            'biological_significance': interpretation
        })
    
    # Create summary DataFrame
    results_df = pd.DataFrame(results_data)
    
    # Analyze by feature type
    print("\n📊 FEATURE TYPE ANALYSIS:")
    print("="*40)
    
    type_analysis = results_df.groupby('feature_type').agg({
        'combined_score': ['count', 'mean', 'sum']
    }).round(4)
    
    for feature_type, row in type_analysis.iterrows():
        count = int(row[('combined_score', 'count')])
        mean_score = row[('combined_score', 'mean')]
        total_score = row[('combined_score', 'sum')]
        
        print(f"{feature_type.title()}: {count} features, avg score: {mean_score:.4f}, total: {total_score:.4f}")
    
    # Generate biological insights
    print("\n🧬 BIOLOGICAL INSIGHTS:")
    print("="*40)
    
    # Analyze connectivity features
    connectivity_features = results_df[results_df['feature_type'] == 'connectivity']
    if len(connectivity_features) > 0:
        print(f"\n🔗 Network Connectivity ({len(connectivity_features)} features):")
        print("   Altered brain network communication is a hallmark of Parkinson's disease")
        for _, row in connectivity_features.head(3).iterrows():
            print(f"   • {row['feature_name']}: {row['combined_score']:.4f}")
    
    # Analyze activity features
    activity_features = results_df[results_df['feature_type'] == 'activity']
    if len(activity_features) > 0:
        print(f"\n🎯 Regional Activity ({len(activity_features)} features):")
        print("   Changes in baseline brain activity reflect dopaminergic dysfunction")
        for _, row in activity_features.head(3).iterrows():
            print(f"   • {row['feature_name']}: {row['combined_score']:.4f}")
    
    # Analyze frequency features
    frequency_features = results_df[results_df['feature_type'] == 'frequency']
    if len(frequency_features) > 0:
        print(f"\n📊 Brain Oscillations ({len(frequency_features)} features):")
        print("   Abnormal brain rhythms are associated with motor symptoms")
        for _, row in frequency_features.head(3).iterrows():
            print(f"   • {row['feature_name']}: {row['combined_score']:.4f}")
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot top features
    top_10 = results_df.head(10)
    
    plt.subplot(2, 2, 1)
    bars = plt.barh(range(len(top_10)), top_10['combined_score'])
    plt.yticks(range(len(top_10)), [name.replace('_', ' ') for name in top_10['feature_name']], fontsize=8)
    plt.xlabel('Combined Importance Score')
    plt.title('Top 10 Most Important Features')
    plt.gca().invert_yaxis()
    
    # Color by feature type
    colors = {'activity': 'red', 'connectivity': 'blue', 'frequency': 'green', 'variability': 'orange'}
    for bar, ftype in zip(bars, top_10['feature_type']):
        bar.set_color(colors.get(ftype, 'gray'))
    
    # Plot feature type distribution
    plt.subplot(2, 2, 2)
    type_counts = results_df['feature_type'].value_counts()
    plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
    plt.title('Feature Type Distribution\n(Top 20 Features)')
    
    # Plot score comparison
    plt.subplot(2, 2, 3)
    plt.scatter(results_df['f_score'], results_df['perm_importance'], 
                c=[colors.get(ft, 'gray') for ft in results_df['feature_type']], alpha=0.7)
    plt.xlabel('F-statistic Score')
    plt.ylabel('Permutation Importance')
    plt.title('Feature Importance Comparison')
    
    # Plot by brain region (if atlas available)
    plt.subplot(2, 2, 4)
    if atlas_labels is not None:
        # Extract ROI names and their importance
        roi_importance = {}
        for _, row in results_df.iterrows():
            feature_name = row['feature_name']
            if any(roi in feature_name for roi in atlas_labels[:10]):  # Check first 10 ROIs
                for roi in atlas_labels[:10]:
                    if roi in feature_name:
                        if roi not in roi_importance:
                            roi_importance[roi] = []
                        roi_importance[roi].append(row['combined_score'])
        
        if roi_importance:
            roi_avg = {roi: np.mean(scores) for roi, scores in roi_importance.items()}
            top_rois = sorted(roi_avg.items(), key=lambda x: x[1], reverse=True)[:8]
            
            rois, scores = zip(*top_rois)
            plt.barh(range(len(rois)), scores)
            plt.yticks(range(len(rois)), [roi.replace('_', ' ') for roi in rois], fontsize=8)
            plt.xlabel('Average Importance')
            plt.title('Top Brain Regions')
            plt.gca().invert_yaxis()
        else:
            plt.text(0.5, 0.5, 'ROI analysis\nnot available', ha='center', va='center', transform=plt.gca().transAxes)
    else:
        plt.text(0.5, 0.5, 'Atlas labels\nnot provided', ha='center', va='center', transform=plt.gca().transAxes)
    
    plt.tight_layout()
    plt.savefig('parkinson_feature_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n💾 Results saved:")
    print(f"   • Visualization: parkinson_feature_analysis.png")
    print(f"   • Feature analysis complete!")
    
    return results_df

def interpret_feature_biologically(feature_name, feature_type):
    """
    Provide biological interpretation for features
    """
    feature_lower = feature_name.lower()
    
    # Motor system regions
    if any(term in feature_lower for term in ['motor', 'precentral', 'postcentral']):
        return "Primary motor areas - directly affected by dopamine loss"
    
    # Basal ganglia
    elif any(term in feature_lower for term in ['putamen', 'caudate', 'pallidum', 'basal']):
        return "Basal ganglia - core region of dopaminergic dysfunction in Parkinson's"
    
    # Thalamus
    elif 'thalamus' in feature_lower or 'thalamic' in feature_lower:
        return "Thalamus - relay station in motor circuits, altered in Parkinson's"
    
    # Frontal regions
    elif any(term in feature_lower for term in ['frontal', 'prefrontal']):
        return "Executive control regions - affected in cognitive symptoms"
    
    # Connectivity
    elif feature_type == 'connectivity' or 'fc_' in feature_lower:
        return "Brain network connectivity - disrupted communication between regions"
    
    # Frequency
    elif feature_type == 'frequency' or 'freq' in feature_lower:
        return "Neural oscillations - abnormal brain rhythms in motor circuits"
    
    # Activity/variability
    elif feature_type in ['activity', 'variability']:
        return "Regional brain activity - altered baseline function or stability"
    
    else:
        return "May reflect disease-related changes in brain function"

# =====================================================
# ADD THIS TO YOUR NOTEBOOK AFTER MODEL TRAINING:
# =====================================================

# Run the feature analysis
print("Running biological feature interpretation analysis...")

# Make sure you have these variables from your previous analysis:
# X_train_scaled, y_train, X_test_scaled, y_test, trained_models
# atlas_labels (if available)

try:
    feature_results = analyze_top_features_for_biology(
        X_train_scaled, y_train, X_test_scaled, y_test, 
        trained_models, atlas_labels=atlas_labels if 'atlas_labels' in locals() else None
    )
    
    print("\n✅ Feature interpretation analysis completed!")
    print("Check the generated visualization and results above for biological insights.")
    
except Exception as e:
    print(f"❌ Error in feature analysis: {e}")
    print("Make sure you have run the model training cells first.")