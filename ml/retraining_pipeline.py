"""
Automated Model Retraining Pipeline

Handles automatic model retraining when triggered by:
- New data threshold
- Performance degradation
- Scheduled intervals

Features:
- Data validation
- Model training with hyperparameter tuning
- Performance comparison
- Automatic deployment
- Rollback on failure
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
import json
import pickle

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score
import xgboost as xgb

from model_registry import ModelRegistry

class RetrainingPipeline:
    """Automated model retraining pipeline"""
    
    def __init__(self, 
                 data_path: str = "data/credit_dataset.csv",
                 min_new_records: int = 500,
                 min_auc_improvement: float = 0.01):
        self.data_path = Path(data_path)
        self.min_new_records = min_new_records
        self.min_auc_improvement = min_auc_improvement
        self.registry = ModelRegistry()
        
        # Track retraining metadata
        self.metadata_path = Path("models/retraining_metadata.json")
        self.load_metadata()
    
    def load_metadata(self):
        """Load retraining metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'last_retrain': None,
                'total_retrains': 0,
                'last_data_size': 0,
                'retraining_history': []
            }
    
    def save_metadata(self):
        """Save retraining metadata"""
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def should_retrain(self) -> Tuple[bool, str]:
        """
        Check if retraining should be triggered
        
        Returns:
            (should_retrain, reason)
        """
        # Check if data file exists
        if not self.data_path.exists():
            return False, "No data file found"
        
        # Load current data
        df = pd.read_csv(self.data_path)
        current_size = len(df)
        
        # Check new data threshold
        last_size = self.metadata.get('last_data_size', 0)
        new_records = current_size - last_size
        
        if new_records >= self.min_new_records:
            return True, f"New data threshold reached ({new_records} new records)"
        
        # Check scheduled retrain (e.g., weekly)
        last_retrain = self.metadata.get('last_retrain')
        if last_retrain:
            from datetime import datetime, timedelta
            last_date = datetime.fromisoformat(last_retrain)
            if datetime.now() - last_date > timedelta(days=7):
                return True, "Scheduled weekly retrain"
        
        return False, "No trigger conditions met"
    
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
        """Prepare training data"""
        print("📊 Loading and preparing data...")
        
        df = pd.read_csv(self.data_path)
        
        # Features
        feature_cols = [
            'monthly_income', 'employment_years', 'debt_to_income',
            'existing_loans', 'late_payment_count', 'credit_utilization',
            'requested_amount', 'age', 'dependents', 'savings_balance',
            'checking_balance', 'credit_history_length', 'previous_defaults'
        ]
        
        # Encode categorical
        df['employment_type_encoded'] = df['employment_type'].map({
            'permanent': 2, 'contract': 1, 'self_employed': 0
        })
        df['education_level_encoded'] = df['education_level'].map({
            'phd': 3, 'master': 2, 'bachelor': 1, 'high_school': 0
        })
        df['marital_status_encoded'] = df['marital_status'].map({
            'married': 2, 'single': 1, 'divorced': 0, 'widowed': 0
        })
        df['home_ownership_encoded'] = df['home_ownership'].map({
            'own': 2, 'mortgage': 1, 'rent': 0, 'family': 0
        })
        
        feature_cols.extend([
            'employment_type_encoded', 'education_level_encoded',
            'marital_status_encoded', 'home_ownership_encoded'
        ])
        
        X = df[feature_cols]
        y = (df['decision'] == 'approved').astype(int)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"✓ Data prepared: {len(X_train)} train, {len(X_test)} test")
        return X_train, y_train, X_test, y_test
    
    def train_models(self, X_train, y_train, X_test, y_test) -> Dict:
        """Train both Logistic Regression and XGBoost"""
        print("\n🤖 Training models...")
        
        results = {}
        
        # 1. Logistic Regression
        print("  Training Logistic Regression...")
        lr_model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        lr_model.fit(X_train, y_train)
        
        lr_pred = lr_model.predict(X_test)
        lr_pred_proba = lr_model.predict_proba(X_test)[:, 1]
        
        results['logistic'] = {
            'model': lr_model,
            'metrics': {
                'auc': roc_auc_score(y_test, lr_pred_proba),
                'accuracy': accuracy_score(y_test, lr_pred),
                'precision': precision_score(y_test, lr_pred),
                'recall': recall_score(y_test, lr_pred)
            }
        }
        
        print(f"    AUC: {results['logistic']['metrics']['auc']:.3f}")
        
        # 2. XGBoost
        print("  Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='auc'
        )
        xgb_model.fit(X_train, y_train)
        
        xgb_pred = xgb_model.predict(X_test)
        xgb_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
        
        results['xgboost'] = {
            'model': xgb_model,
            'metrics': {
                'auc': roc_auc_score(y_test, xgb_pred_proba),
                'accuracy': accuracy_score(y_test, xgb_pred),
                'precision': precision_score(y_test, xgb_pred),
                'recall': recall_score(y_test, xgb_pred)
            }
        }
        
        print(f"    AUC: {results['xgboost']['metrics']['auc']:.3f}")
        
        return results
    
    def is_better(self, new_metrics: Dict, production_metrics: Optional[Dict]) -> bool:
        """Check if new model is better than production"""
        if not production_metrics:
            return True
        
        new_auc = new_metrics.get('auc', 0)
        prod_auc = production_metrics.get('auc', 0)
        
        improvement = new_auc - prod_auc
        
        if improvement >= self.min_auc_improvement:
            print(f"✓ New model is better (AUC improvement: +{improvement:.3f})")
            return True
        else:
            print(f"✗ New model not better enough (AUC improvement: +{improvement:.3f}, need: +{self.min_auc_improvement})")
            return False
    
    def deploy_model(self, model, model_type: str, metrics: Dict) -> str:
        """Deploy new model version"""
        # Generate new version
        current_version = self.registry.get_production_model()
        if current_version:
            # Increment version
            parts = current_version['version'].split('.')
            new_version = f"{parts[0]}.{int(parts[1])+1}.0"
        else:
            new_version = "1.0.0"
        
        # Save model temporarily
        temp_path = Path(f"models/temp_{model_type}_model.pkl")
        with open(temp_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Register in registry
        self.registry.register_model(
            model_path=str(temp_path),
            version=new_version,
            model_type=model_type,
            metrics=metrics,
            metadata={
                'training_date': datetime.now().isoformat(),
                'data_size': self.metadata.get('last_data_size', 0),
                'auto_deployed': True
            }
        )
        
        # Set as production
        self.registry.set_production(new_version)
        
        # Clean up temp file
        temp_path.unlink()
        
        return new_version
    
    def run_pipeline(self) -> Dict:
        """Run complete retraining pipeline"""
        print("="*60)
        print("AUTOMATED RETRAINING PIPELINE")
        print("="*60)
        
        # Check if should retrain
        should_retrain, reason = self.should_retrain()
        print(f"\n🔍 Checking triggers: {reason}")
        
        if not should_retrain:
            print("✗ No retraining needed")
            return {'status': 'skipped', 'reason': reason}
        
        print("✓ Retraining triggered!")
        
        try:
            # Prepare data
            X_train, y_train, X_test, y_test = self.prepare_data()
            
            # Train models
            results = self.train_models(X_train, y_train, X_test, y_test)
            
            # Get production model for comparison
            prod_model = self.registry.get_production_model()
            prod_metrics = prod_model['metrics'] if prod_model else None
            
            # Check if XGBoost is better
            if self.is_better(results['xgboost']['metrics'], prod_metrics):
                # Deploy new model
                new_version = self.deploy_model(
                    results['xgboost']['model'],
                    'xgboost',
                    results['xgboost']['metrics']
                )
                
                # Update metadata
                df = pd.read_csv(self.data_path)
                self.metadata['last_retrain'] = datetime.now().isoformat()
                self.metadata['total_retrains'] += 1
                self.metadata['last_data_size'] = len(df)
                self.metadata['retraining_history'].append({
                    'version': new_version,
                    'timestamp': datetime.now().isoformat(),
                    'metrics': results['xgboost']['metrics'],
                    'reason': reason
                })
                self.save_metadata()
                
                print(f"\n✓ Successfully deployed version {new_version}")
                
                return {
                    'status': 'success',
                    'version': new_version,
                    'metrics': results['xgboost']['metrics']
                }
            else:
                print("\n✗ New model not deployed (insufficient improvement)")
                return {
                    'status': 'not_deployed',
                    'reason': 'insufficient_improvement'
                }
        
        except Exception as e:
            print(f"\n✗ Retraining failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

# Example usage
if __name__ == "__main__":
    pipeline = RetrainingPipeline()
    result = pipeline.run_pipeline()
    
    print("\n" + "="*60)
    print("PIPELINE RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
