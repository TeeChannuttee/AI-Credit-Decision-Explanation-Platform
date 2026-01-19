"""
Credit Scoring Model Training Pipeline

Trains machine learning models for credit risk assessment with explainability.

Models:
- Logistic Regression (primary - highly interpretable)
- XGBoost (optional - higher accuracy)

Features:
- Feature importance extraction
- SHAP values for explainability
- Risk band classification (Low/Medium/High)
- Model performance metrics
- Model versioning
"""

import pandas as pd
import numpy as np
import json
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import shap
import warnings
warnings.filterwarnings('ignore')

# Optional: XGBoost
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠ XGBoost not installed. Only Logistic Regression will be trained.")

class CreditScoringModel:
    """Credit scoring model with explainability"""
    
    def __init__(self, model_type='logistic'):
        """
        Initialize model
        
        Args:
            model_type: 'logistic' or 'xgboost'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_importance = None
        self.shap_explainer = None
        self.metadata = {}
        
    def prepare_features(self, df):
        """
        Prepare features for training
        
        Args:
            df: DataFrame with credit data
            
        Returns:
            X: Feature matrix
            y: Target vector
            feature_names: List of feature names
        """
        # Select features for modeling
        feature_cols = [
            'monthly_income',
            'employment_years',
            'debt_to_income',
            'existing_loans',
            'late_payment_count',
            'credit_utilization',
            'requested_amount',
            'age',
            'dependents',
            'savings_balance',
            'checking_balance',
            'credit_history_length',
            'previous_defaults'
        ]
        
        # Add categorical features (one-hot encoded)
        categorical_cols = ['employment_type', 'loan_purpose', 'education_level', 
                           'marital_status', 'home_ownership']
        
        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # Get all feature columns (numeric + encoded categorical)
        all_feature_cols = [col for col in df_encoded.columns 
                           if col not in ['application_id', 'decision', 'risk_level']]
        
        X = df_encoded[all_feature_cols]
        y = (df['decision'] == 'approved').astype(int)  # 1 = approved, 0 = rejected
        
        self.feature_names = list(X.columns)
        
        return X, y
    
    def train(self, X_train, y_train):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print(f"\nTraining {self.model_type} model...")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if self.model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'  # Handle class imbalance
            )
        elif self.model_type == 'xgboost' and XGBOOST_AVAILABLE:
            self.model = XGBClassifier(
                max_depth=5,
                learning_rate=0.1,
                n_estimators=100,
                random_state=42,
                eval_metric='logloss'
            )
        else:
            raise ValueError(f"Invalid model type: {self.model_type}")
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Extract feature importance
        if self.model_type == 'logistic':
            # For logistic regression, use absolute coefficients
            self.feature_importance = dict(zip(
                self.feature_names,
                [float(x) for x in np.abs(self.model.coef_[0])]
            ))
        elif self.model_type == 'xgboost':
            # For XGBoost, use built-in feature importance
            self.feature_importance = dict(zip(
                self.feature_names,
                [float(x) for x in self.model.feature_importances_]
            ))
        
        # Sort by importance
        self.feature_importance = dict(
            sorted(self.feature_importance.items(), 
                   key=lambda x: x[1], reverse=True)
        )
        
        print("✓ Model trained successfully")
        
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            metrics: Dictionary of performance metrics
        """
        print("\nEvaluating model...")
        
        # Scale test features
        X_test_scaled = self.scaler.transform(X_test)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'auc_roc': roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Print results
        print("\n" + "="*60)
        print("MODEL PERFORMANCE")
        print("="*60)
        print(f"Accuracy:  {metrics['accuracy']:.3f}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall:    {metrics['recall']:.3f}")
        print(f"F1 Score:  {metrics['f1_score']:.3f}")
        print(f"AUC-ROC:   {metrics['auc_roc']:.3f}")
        print(f"\nConfusion Matrix:")
        print(f"  TN: {metrics['confusion_matrix'][0][0]}  FP: {metrics['confusion_matrix'][0][1]}")
        print(f"  FN: {metrics['confusion_matrix'][1][0]}  TP: {metrics['confusion_matrix'][1][1]}")
        
        return metrics
    
    def create_shap_explainer(self, X_sample):
        """
        Create SHAP explainer for model interpretability
        
        Args:
            X_sample: Sample of training data for SHAP
        """
        print("\nCreating SHAP explainer...")
        
        X_sample_scaled = self.scaler.transform(X_sample)
        
        if self.model_type == 'logistic':
            self.shap_explainer = shap.LinearExplainer(
                self.model, X_sample_scaled, feature_names=self.feature_names
            )
        elif self.model_type == 'xgboost':
            self.shap_explainer = shap.TreeExplainer(self.model)
        
        print("✓ SHAP explainer created")
    
    def explain_prediction(self, X_instance):
        """
        Explain a single prediction using SHAP
        
        Args:
            X_instance: Single instance to explain (DataFrame row)
            
        Returns:
            shap_values: SHAP values for the instance
        """
        X_scaled = self.scaler.transform(X_instance)
        shap_values = self.shap_explainer.shap_values(X_scaled)
        
        # For binary classification, get values for positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        return dict(zip(self.feature_names, shap_values[0]))
    
    def predict_with_risk_band(self, X):
        """
        Predict with risk band classification
        
        Args:
            X: Features
            
        Returns:
            predictions: Dict with decision, probability, and risk band
        """
        X_scaled = self.scaler.transform(X)
        
        # Get probability of approval
        proba = self.model.predict_proba(X_scaled)[:, 1]
        
        # Classify into risk bands
        risk_bands = []
        for p in proba:
            if p >= 0.7:
                risk_bands.append('low')  # High approval probability = low risk
            elif p >= 0.4:
                risk_bands.append('medium')
            else:
                risk_bands.append('high')  # Low approval probability = high risk
        
        predictions = {
            'decision': ['approved' if p >= 0.5 else 'rejected' for p in proba],
            'probability': proba.tolist(),
            'risk_band': risk_bands
        }
        
        return predictions
    
    def save_model(self, version='1.0.0'):
        """
        Save model and metadata
        
        Args:
            version: Model version string
        """
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        # Save model
        model_path = models_dir / f'credit_model_v{version}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_type': self.model_type
            }, f)
        
        print(f"\n✅ Model saved to: {model_path}")
        
        # Save metadata
        metadata_path = models_dir / f'model_metadata_v{version}.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata saved to: {metadata_path}")
        
        # Save feature importance
        importance_path = models_dir / f'feature_importance_v{version}.json'
        with open(importance_path, 'w', encoding='utf-8') as f:
            json.dump(self.feature_importance, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Feature importance saved to: {importance_path}")

def main():
    """Main training pipeline"""
    
    print("="*60)
    print("CREDIT SCORING MODEL TRAINING")
    print("="*60)
    
    # Load data
    print("\nLoading dataset...")
    df = pd.read_csv('data/credit_dataset.csv')
    print(f"✓ Loaded {len(df)} records")
    
    # Initialize model
    model = CreditScoringModel(model_type='logistic')
    
    # Prepare features
    print("\nPreparing features...")
    X, y = model.prepare_features(df)
    print(f"✓ Features prepared: {X.shape[1]} features, {len(X)} samples")
    print(f"  Approval rate: {y.mean()*100:.1f}%")
    
    # Split data
    print("\nSplitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✓ Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    # Train model
    model.train(X_train, y_train)
    
    # Evaluate model
    metrics = model.evaluate(X_test, y_test)
    
    # Create SHAP explainer
    model.create_shap_explainer(X_train.sample(min(100, len(X_train))))
    
    # Print top features
    print("\n" + "="*60)
    print("TOP 10 MOST IMPORTANT FEATURES")
    print("="*60)
    for i, (feature, importance) in enumerate(list(model.feature_importance.items())[:10], 1):
        print(f"{i:2d}. {feature:30s} {importance:.4f}")
    
    # Save metadata
    model.metadata = {
        'model_id': f"credit_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'model_version': '1.0.0',
        'model_type': model.model_type,
        'training_date': datetime.now().isoformat(),
        'training_data_size': len(X_train),
        'test_data_size': len(X_test),
        'features_used': model.feature_names,
        'performance_metrics': {
            'accuracy': float(metrics['accuracy']),
            'precision': float(metrics['precision']),
            'recall': float(metrics['recall']),
            'f1_score': float(metrics['f1_score']),
            'auc_roc': float(metrics['auc_roc']),
            'confusion_matrix': metrics['confusion_matrix']
        },
        'feature_importance': model.feature_importance,
        'deployment_status': 'trained',
        'notes': 'Initial model training with synthetic data'
    }
    
    # Save model
    model.save_model(version='1.0.0')
    
    # Test prediction on sample
    print("\n" + "="*60)
    print("SAMPLE PREDICTION TEST")
    print("="*60)
    sample = X_test.iloc[[0]]
    prediction = model.predict_with_risk_band(sample)
    shap_values = model.explain_prediction(sample)
    
    print(f"Decision: {prediction['decision'][0]}")
    print(f"Probability: {prediction['probability'][0]:.3f}")
    print(f"Risk Band: {prediction['risk_band'][0]}")
    print(f"\nTop 5 Contributing Features (SHAP):")
    top_shap = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    for feature, value in top_shap:
        direction = "↑" if value > 0 else "↓"
        print(f"  {direction} {feature:30s} {value:+.4f}")
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE!")
    print("="*60)
    
    # Optional: Train XGBoost if available
    if XGBOOST_AVAILABLE:
        print("\n" + "="*60)
        print("TRAINING XGBOOST MODEL (OPTIONAL)")
        print("="*60)
        
        xgb_model = CreditScoringModel(model_type='xgboost')
        xgb_model.feature_names = model.feature_names
        xgb_model.train(X_train, y_train)
        xgb_metrics = xgb_model.evaluate(X_test, y_test)
        xgb_model.create_shap_explainer(X_train.sample(min(100, len(X_train))))
        
        xgb_model.metadata = {
            'model_id': f"credit_model_xgb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'model_version': '1.0.0',
            'model_type': 'xgboost',
            'training_date': datetime.now().isoformat(),
            'training_data_size': len(X_train),
            'test_data_size': len(X_test),
            'features_used': xgb_model.feature_names,
            'performance_metrics': {
                'accuracy': float(xgb_metrics['accuracy']),
                'precision': float(xgb_metrics['precision']),
                'recall': float(xgb_metrics['recall']),
                'f1_score': float(xgb_metrics['f1_score']),
                'auc_roc': float(xgb_metrics['auc_roc']),
                'confusion_matrix': xgb_metrics['confusion_matrix']
            },
            'feature_importance': xgb_model.feature_importance,
            'deployment_status': 'trained',
            'notes': 'XGBoost model for comparison'
        }
        
        xgb_model.save_model(version='1.0.0_xgb')
        
        print("\n✅ XGBoost model training complete!")

if __name__ == "__main__":
    main()
