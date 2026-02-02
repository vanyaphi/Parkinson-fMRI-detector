#!/usr/bin/env python3
"""
Feature Interpretation Analysis for Parkinson's Disease fMRI Classification

This script provides multiple methods to identify and interpret the most important
features contributing to Parkinson's disease predictions, enabling biological insights.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

class FeatureInterpreter:
    """
    Class to interpret machine learning features for biological insights
    """
    
    def __init__(self, feature_names=None, roi_names=None):
        """
        Initialize with feature and ROI names for interpretability
        
        Parameters:
        feature_names: List of all feature names
        roi_names: List of ROI/brain region names
        """
        self.feature_names = feature_names
        self.roi_names = roi_names
        self.feature_importance_results = {}
        
    def create_feature_names(self, n_rois):
        """
        Create interpretable feature names based on extraction process
        """
        feature_names = []
        
        # ROI statistical features
        for roi_idx in range(n_rois):
            roi_name = f"ROI_{roi_idx:03d}" if self.roi_names is None else self.roi_names[roi_idx]
            feature_names.extend([
                f"{roi_name}_mean_activity",
                f"{roi_name}_std_activity", 
                f"{roi_name}_var_activity"
            ])
        
        # Functional connectivity features (upper triangle of correlation matrix)
        for i in range(n_rois):
            for j in range(i+1, n_rois):
                roi_i = f"ROI_{i:03d}" if self.roi_names is None else self.roi_names[i]
                roi_j = f"ROI_{j:03d}" if self.roi_names is None else self.roi_names[j]
                feature_names.append(f"FC_{roi_i}_{roi_j}")
        
        # Frequency domain features
        freq_bands = ['low_freq', 'mid_freq', 'high_freq']
        for roi_idx in range(n_rois):
            roi_name = f"ROI_{roi_idx:03d}" if self.roi_names is None else self.roi_names[roi_idx]
            for band in freq_bands:
                feature_names.append(f"{roi_name}_{band}_power")
        
        self.feature_names = feature_names
        return feature_names
    
    def analyze_feature_importance_univariate(self, X, y, k=50):
        """
        Method 1: Univariate Feature Selection using F-statistics
        Identifies features with strongest individual relationship to diagnosis
        """
        print("🔍 Analyzing univariate feature importance...")
        
        # F-statistic based selection
        selector_f = SelectKBest(score_func=f_classif, k=k)
        X_selected_f = selector_f.fit_transform(X, y)
        
        # Get feature scores and indices
        feature_scores_f = selector_f.scores_
        selected_indices_f = selector_f.get_support(indices=True)
        
        # Mutual information based selection
        selector_mi = SelectKBest(score_func=mutual_info_classif, k=k)
        X_selected_mi = selector_mi.fit_transform(X, y)
        
        feature_scores_mi = selector_mi.scores_
        selected_indices_mi = selector_mi.get_support(indices=True)
        
        # Store results
        self.feature_importance_results['univariate_f'] = {
            'scores': feature_scores_f,
            'selected_indices': selected_indices_f,
            'method': 'F-statistic'
        }
        
        self.feature_importance_results['univariate_mi'] = {
            'scores': feature_scores_mi,
            'selected_indices': selected_indices_mi,
            'method': 'Mutual Information'
        }
        
        return selected_indices_f, selected_indices_mi
    
    def analyze_model_coefficients(self, X, y):
        """
        Method 2: Linear Model Coefficients
        Uses logistic regression coefficients to identify important features
        """
        print("📊 Analyzing linear model coefficients...")
        
        # Train logistic regression with L1 regularization for feature selection
        lr_l1 = LogisticRegression(penalty='l1', solver='liblinear', C=0.1, random_state=42)
        lr_l1.fit(X, y)
        
        # Train logistic regression with L2 regularization for stable coefficients
        lr_l2 = LogisticRegression(penalty='l2', solver='liblinear', C=1.0, random_state=42)
        lr_l2.fit(X, y)
        
        # Get coefficients
        coefficients_l1 = lr_l1.coef_[0]
        coefficients_l2 = lr_l2.coef_[0]
        
        # Store results
        self.feature_importance_results['linear_l1'] = {
            'coefficients': coefficients_l1,
            'model': lr_l1,
            'method': 'Logistic Regression L1'
        }
        
        self.feature_importance_results['linear_l2'] = {
            'coefficients': coefficients_l2,
            'model': lr_l2,
            'method': 'Logistic Regression L2'
        }
        
        return coefficients_l1, coefficients_l2
    
    def analyze_tree_importance(self, X, y):
        """
        Method 3: Tree-based Feature Importance
        Uses Random Forest to identify important features
        """
        print("🌳 Analyzing tree-based feature importance...")
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        rf.fit(X, y)
        
        # Get feature importances
        feature_importances = rf.feature_importances_
        
        # Store results
        self.feature_importance_results['tree_based'] = {
            'importances': feature_importances,
            'model': rf,
            'method': 'Random Forest'
        }
        
        return feature_importances
    
    def analyze_permutation_importance(self, X, y, model=None):
        """
        Method 4: Permutation Importance
        Measures how much performance drops when each feature is randomly shuffled
        """
        print("🔄 Analyzing permutation importance...")
        
        if model is None:
            model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
            model.fit(X, y)
        
        # Calculate permutation importance
        perm_importance = permutation_importance(
            model, X, y, n_repeats=10, random_state=42, scoring='accuracy'
        )
        
        # Store results
        self.feature_importance_results['permutation'] = {
            'importances_mean': perm_importance.importances_mean,
            'importances_std': perm_importance.importances_std,
            'method': 'Permutation Importance'
        }
        
        return perm_importance.importances_mean, perm_importance.importances_std
    
    def create_importance_summary(self, top_k=20):
        """
        Create a comprehensive summary of top important features across all methods
        """
        print(f"📋 Creating summary of top {top_k} features...")
        
        summary_data = []
        
        for method_name, results in self.feature_importance_results.items():
            if method_name == 'univariate_f':
                scores = results['scores']
                top_indices = np.argsort(scores)[-top_k:][::-1]
                
                for rank, idx in enumerate(top_indices):
                    summary_data.append({
                        'method': results['method'],
                        'rank': rank + 1,
                        'feature_index': idx,
                        'feature_name': self.feature_names[idx] if self.feature_names else f'Feature_{idx}',
                        'importance_score': scores[idx],
                        'feature_type': self._categorize_feature(idx)
                    })
            
            elif method_name == 'linear_l2':
                coefficients = np.abs(results['coefficients'])  # Use absolute values
                top_indices = np.argsort(coefficients)[-top_k:][::-1]
                
                for rank, idx in enumerate(top_indices):
                    summary_data.append({
                        'method': results['method'],
                        'rank': rank + 1,
                        'feature_index': idx,
                        'feature_name': self.feature_names[idx] if self.feature_names else f'Feature_{idx}',
                        'importance_score': coefficients[idx],
                        'feature_type': self._categorize_feature(idx)
                    })
            
            elif method_name == 'tree_based':
                importances = results['importances']
                top_indices = np.argsort(importances)[-top_k:][::-1]
                
                for rank, idx in enumerate(top_indices):
                    summary_data.append({
                        'method': results['method'],
                        'rank': rank + 1,
                        'feature_index': idx,
                        'feature_name': self.feature_names[idx] if self.feature_names else f'Feature_{idx}',
                        'importance_score': importances[idx],
                        'feature_type': self._categorize_feature(idx)
                    })
            
            elif method_name == 'permutation':
                importances = results['importances_mean']
                top_indices = np.argsort(importances)[-top_k:][::-1]
                
                for rank, idx in enumerate(top_indices):
                    summary_data.append({
                        'method': results['method'],
                        'rank': rank + 1,
                        'feature_index': idx,
                        'feature_name': self.feature_names[idx] if self.feature_names else f'Feature_{idx}',
                        'importance_score': importances[idx],
                        'feature_type': self._categorize_feature(idx)
                    })
        
        self.importance_summary = pd.DataFrame(summary_data)
        return self.importance_summary
    
    def _categorize_feature(self, feature_idx):
        """
        Categorize feature type based on index position
        """
        if self.feature_names is None:
            return 'Unknown'
        
        feature_name = self.feature_names[feature_idx]
        
        if '_mean_activity' in feature_name:
            return 'ROI Mean Activity'
        elif '_std_activity' in feature_name or '_var_activity' in feature_name:
            return 'ROI Variability'
        elif 'FC_' in feature_name:
            return 'Functional Connectivity'
        elif '_freq_power' in feature_name:
            return 'Frequency Power'
        else:
            return 'Other'
    
    def plot_feature_importance_comparison(self, save_path=None):
        """
        Create visualization comparing feature importance across methods
        """
        if not hasattr(self, 'importance_summary'):
            self.create_importance_summary()
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Feature Importance Analysis - Multiple Methods', fontsize=16, fontweight='bold')
        
        methods = self.importance_summary['method'].unique()
        
        for idx, method in enumerate(methods[:4]):  # Plot up to 4 methods
            ax = axes[idx // 2, idx % 2]
            
            method_data = self.importance_summary[self.importance_summary['method'] == method]
            top_features = method_data.head(15)  # Top 15 features
            
            # Create horizontal bar plot
            bars = ax.barh(range(len(top_features)), top_features['importance_score'])
            ax.set_yticks(range(len(top_features)))
            ax.set_yticklabels([name.replace('_', ' ') for name in top_features['feature_name']], fontsize=8)
            ax.set_xlabel('Importance Score')
            ax.set_title(f'{method}\nTop Contributing Features')
            ax.invert_yaxis()
            
            # Color bars by feature type
            feature_types = top_features['feature_type'].unique()
            colors = plt.cm.Set3(np.linspace(0, 1, len(feature_types)))
            color_map = dict(zip(feature_types, colors))
            
            for bar, feature_type in zip(bars, top_features['feature_type']):
                bar.set_color(color_map[feature_type])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_biological_insights(self):
        """
        Generate biological insights from top features
        """
        if not hasattr(self, 'importance_summary'):
            self.create_importance_summary()
        
        print("\n" + "="*80)
        print("🧠 BIOLOGICAL INSIGHTS FROM FEATURE IMPORTANCE ANALYSIS")
        print("="*80)
        
        # Analyze feature types
        feature_type_importance = self.importance_summary.groupby('feature_type').agg({
            'importance_score': ['mean', 'count']
        }).round(4)
        
        print("\n📊 Feature Type Analysis:")
        print(feature_type_importance)
        
        # Top features across all methods
        top_features_overall = self.importance_summary.groupby('feature_name').agg({
            'importance_score': 'mean',
            'rank': 'mean'
        }).sort_values('importance_score', ascending=False).head(10)
        
        print("\n🏆 Top 10 Most Important Features (Average Across Methods):")
        for idx, (feature_name, row) in enumerate(top_features_overall.iterrows()):
            print(f"{idx+1:2d}. {feature_name}")
            print(f"    Average Importance: {row['importance_score']:.4f}")
            print(f"    Average Rank: {row['rank']:.1f}")
            
            # Provide biological interpretation
            interpretation = self._interpret_feature_biologically(feature_name)
            print(f"    Biological Significance: {interpretation}")
            print()
        
        # ROI-specific analysis
        self._analyze_roi_contributions()
        
        # Network-level analysis
        self._analyze_network_contributions()
    
    def _interpret_feature_biologically(self, feature_name):
        """
        Provide biological interpretation for specific features
        """
        interpretations = {
            'motor': "Motor control regions - directly affected by dopamine loss in Parkinson's",
            'basal_ganglia': "Core region affected in Parkinson's - dopaminergic neuron loss",
            'substantia_nigra': "Primary site of dopamine neuron death in Parkinson's",
            'putamen': "Part of basal ganglia - motor control and habit formation",
            'caudate': "Part of basal ganglia - executive function and movement initiation",
            'thalamus': "Relay station - altered in Parkinson's motor circuits",
            'cerebellum': "Motor coordination - compensatory changes in Parkinson's",
            'frontal': "Executive function - affected in Parkinson's cognitive symptoms",
            'FC_': "Altered brain network connectivity - hallmark of Parkinson's",
            'freq_power': "Abnormal brain oscillations - beta band changes in Parkinson's"
        }
        
        feature_lower = feature_name.lower()
        for key, interpretation in interpretations.items():
            if key in feature_lower:
                return interpretation
        
        return "May reflect disease-related changes in brain structure or function"
    
    def _analyze_roi_contributions(self):
        """
        Analyze which brain regions contribute most to classification
        """
        print("\n🧭 Brain Region Analysis:")
        
        # Extract ROI information from feature names
        roi_contributions = {}
        
        for _, row in self.importance_summary.iterrows():
            feature_name = row['feature_name']
            
            # Extract ROI name from feature
            if 'ROI_' in feature_name:
                roi_name = feature_name.split('_')[1]
                if roi_name not in roi_contributions:
                    roi_contributions[roi_name] = []
                roi_contributions[roi_name].append(row['importance_score'])
        
        # Calculate average importance per ROI
        roi_avg_importance = {roi: np.mean(scores) for roi, scores in roi_contributions.items()}
        
        # Sort and display top ROIs
        top_rois = sorted(roi_avg_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("Top 10 Most Important Brain Regions:")
        for idx, (roi, avg_importance) in enumerate(top_rois):
            print(f"{idx+1:2d}. ROI {roi}: {avg_importance:.4f}")
    
    def _analyze_network_contributions(self):
        """
        Analyze functional connectivity patterns
        """
        print("\n🔗 Functional Connectivity Analysis:")
        
        fc_features = self.importance_summary[
            self.importance_summary['feature_type'] == 'Functional Connectivity'
        ]
        
        if len(fc_features) > 0:
            print(f"Functional connectivity features represent {len(fc_features)} of top features")
            print("This suggests altered brain network communication in Parkinson's disease")
            
            # Analyze most important connections
            top_connections = fc_features.head(5)
            print("\nTop 5 Most Important Brain Connections:")
            for idx, (_, row) in enumerate(top_connections.iterrows()):
                print(f"{idx+1}. {row['feature_name']}: {row['importance_score']:.4f}")
        else:
            print("Limited functional connectivity features in top contributors")

# Example usage function
def run_feature_interpretation_analysis(X, y, feature_names=None, roi_names=None):
    """
    Complete feature interpretation analysis pipeline
    
    Parameters:
    X: Feature matrix (n_samples, n_features)
    y: Labels (n_samples,)
    feature_names: List of feature names (optional)
    roi_names: List of ROI names (optional)
    """
    
    print("🚀 Starting Feature Interpretation Analysis for Parkinson's Disease Detection")
    print("="*80)
    
    # Initialize interpreter
    interpreter = FeatureInterpreter(feature_names=feature_names, roi_names=roi_names)
    
    # Create feature names if not provided
    if feature_names is None:
        n_rois = int(np.sqrt(X.shape[1] / 6))  # Rough estimate
        interpreter.create_feature_names(n_rois)
    
    # Run all analysis methods
    interpreter.analyze_feature_importance_univariate(X, y)
    interpreter.analyze_model_coefficients(X, y)
    interpreter.analyze_tree_importance(X, y)
    interpreter.analyze_permutation_importance(X, y)
    
    # Create summary and visualizations
    interpreter.create_importance_summary()
    interpreter.plot_feature_importance_comparison('feature_importance_comparison.png')
    
    # Generate biological insights
    interpreter.generate_biological_insights()
    
    return interpreter

if __name__ == "__main__":
    print("Feature Interpretation Analysis Module")
    print("Import this module and use run_feature_interpretation_analysis() function")