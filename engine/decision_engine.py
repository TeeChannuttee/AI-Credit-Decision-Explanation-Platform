"""
Decision Engine

Combines ML predictions with rule-based overrides to make final credit decisions.

Features:
- Load ML model predictions
- Apply business rules
- Rule override mechanism
- Final decision determination
- Confidence scoring
"""

import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

class DecisionEngine:
    """Credit decision engine combining ML and rules"""
    
    def __init__(self, model_path='models/credit_model_v1.0.0.pkl', 
                 rules_path='data/explanation_rules.json'):
        """
        Initialize decision engine
        
        Args:
            model_path: Path to trained ML model
            rules_path: Path to business rules
        """
        # Load ML model
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
        
        # Load business rules
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
            self.rules = rules_data['rules']
        
        print(f"✓ Loaded {self.model_type} model")
        print(f"✓ Loaded {len(self.rules)} business rules")
    
    def prepare_features(self, application_data: Dict) -> pd.DataFrame:
        """
        Prepare features from application data
        
        Args:
            application_data: Dictionary with application fields
            
        Returns:
            DataFrame with features ready for model
        """
        # Create DataFrame from application
        df = pd.DataFrame([application_data])
        
        # One-hot encode categorical features
        categorical_cols = ['employment_type', 'loan_purpose', 'education_level', 
                           'marital_status', 'home_ownership']
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # Ensure all expected features are present
        for feature in self.feature_names:
            if feature not in df_encoded.columns:
                df_encoded[feature] = 0
        
        # Select only the features used in training
        X = df_encoded[self.feature_names]
        
        return X
    
    def get_ml_prediction(self, X: pd.DataFrame) -> Dict:
        """
        Get ML model prediction
        
        Args:
            X: Feature matrix
            
        Returns:
            Dictionary with ML prediction results
        """
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get prediction probability
        proba = self.model.predict_proba(X_scaled)[0, 1]
        
        # Classify into risk band
        if proba >= 0.7:
            risk_level = 'low'
        elif proba >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # ML decision (before rules)
        ml_decision = 'approved' if proba >= 0.5 else 'rejected'
        
        return {
            'ml_score': float(proba),
            'ml_risk_level': risk_level,
            'ml_decision': ml_decision,
            'confidence': float(abs(proba - 0.5) * 2)  # 0-1 scale
        }
    
    def evaluate_rules(self, application_data: Dict) -> List[Dict]:
        """
        Evaluate business rules against application
        
        Args:
            application_data: Application data dictionary
            
        Returns:
            List of triggered rules
        """
        triggered_rules = []
        
        for rule in self.rules:
            try:
                # Evaluate rule condition
                condition = rule['condition']
                
                # Create safe evaluation context
                eval_context = {
                    'debt_to_income': application_data.get('debt_to_income', 0),
                    'late_payment_count': application_data.get('late_payment_count', 0),
                    'monthly_income': application_data.get('monthly_income', 0),
                    'credit_utilization': application_data.get('credit_utilization', 0),
                    'previous_defaults': application_data.get('previous_defaults', 0),
                    'employment_years': application_data.get('employment_years', 0),
                    'existing_loans': application_data.get('existing_loans', 0),
                    'credit_history_length': application_data.get('credit_history_length', 0),
                    'requested_amount': application_data.get('requested_amount', 0),
                    'savings_balance': application_data.get('savings_balance', 0),
                    'checking_balance': application_data.get('checking_balance', 0),
                    'age': application_data.get('age', 0),
                    'dependents': application_data.get('dependents', 0),
                    'employment_type': application_data.get('employment_type', ''),
                    'loan_purpose': application_data.get('loan_purpose', ''),
                    'education_level': application_data.get('education_level', ''),
                    'home_ownership': application_data.get('home_ownership', '')
                }
                
                # Evaluate condition
                if eval(condition, {"__builtins__": {}}, eval_context):
                    triggered_rules.append(rule)
            
            except Exception as e:
                print(f"Warning: Error evaluating rule {rule['rule_id']}: {e}")
                continue
        
        return triggered_rules
    
    def combine_decision(self, ml_result: Dict, triggered_rules: List[Dict], 
                        application_data: Dict) -> Dict:
        """
        Combine ML prediction with rule-based logic
        
        Args:
            ml_result: ML prediction results
            triggered_rules: List of triggered business rules
            application_data: Original application data
            
        Returns:
            Final decision dictionary
        """
        # Sort rules by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        triggered_rules.sort(key=lambda r: severity_order.get(r['severity'], 4))
        
        # Check for critical rejection rules (non-overridable)
        critical_rejects = [r for r in triggered_rules 
                           if r['severity'] == 'critical' and r['action'] == 'reject']
        
        if critical_rejects:
            return {
                'final_decision': 'rejected',
                'decision_reason': 'critical_rule_violation',
                'primary_rule': critical_rejects[0],
                'triggered_rules': triggered_rules,
                'ml_result': ml_result,
                'override_allowed': False,
                'confidence': 1.0
            }
        
        # Check for high severity rejections
        high_rejects = [r for r in triggered_rules 
                       if r['severity'] == 'high' and r['action'] == 'reject']
        
        if high_rejects:
            return {
                'final_decision': 'rejected',
                'decision_reason': 'high_risk_factors',
                'primary_rule': high_rejects[0],
                'triggered_rules': triggered_rules,
                'ml_result': ml_result,
                'override_allowed': high_rejects[0].get('override_allowed', True),
                'confidence': 0.85
            }
        
        # Check for medium severity - requires review
        medium_risks = [r for r in triggered_rules 
                       if r['severity'] == 'medium' and r['action'] in ['reject', 'review']]
        
        if medium_risks and ml_result['ml_decision'] == 'rejected':
            return {
                'final_decision': 'rejected',
                'decision_reason': 'medium_risk_factors',
                'primary_rule': medium_risks[0],
                'triggered_rules': triggered_rules,
                'ml_result': ml_result,
                'override_allowed': True,
                'confidence': 0.7
            }
        
        # Check for positive rules
        positive_rules = [r for r in triggered_rules if r['action'] == 'approve']
        
        # ML suggests approval and no critical/high risks
        if ml_result['ml_decision'] == 'approved' and not high_rejects:
            return {
                'final_decision': 'approved',
                'decision_reason': 'low_risk_profile',
                'primary_rule': positive_rules[0] if positive_rules else None,
                'triggered_rules': triggered_rules,
                'ml_result': ml_result,
                'override_allowed': False,
                'confidence': ml_result['confidence']
            }
        
        # Default to ML decision if no strong rules
        return {
            'final_decision': ml_result['ml_decision'],
            'decision_reason': 'ml_based_decision',
            'primary_rule': None,
            'triggered_rules': triggered_rules,
            'ml_result': ml_result,
            'override_allowed': True,
            'confidence': ml_result['confidence']
        }
    
    def make_decision(self, application_data: Dict) -> Dict:
        """
        Make credit decision for application
        
        Args:
            application_data: Complete application data
            
        Returns:
            Complete decision result
        """
        # Prepare features for ML
        X = self.prepare_features(application_data)
        
        # Get ML prediction
        ml_result = self.get_ml_prediction(X)
        
        # Evaluate business rules
        triggered_rules = self.evaluate_rules(application_data)
        
        # Combine ML and rules for final decision
        decision = self.combine_decision(ml_result, triggered_rules, application_data)
        
        # Add application ID
        decision['application_id'] = application_data.get('application_id', 'unknown')
        
        return decision

# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = DecisionEngine()
    
    # Test application
    test_application = {
        'application_id': 'TEST001',
        'monthly_income': 45000,
        'employment_years': 5,
        'employment_type': 'permanent',
        'debt_to_income': 0.35,
        'existing_loans': 2,
        'late_payment_count': 0,
        'credit_utilization': 0.45,
        'requested_amount': 300000,
        'loan_purpose': 'car',
        'age': 35,
        'education_level': 'bachelor',
        'marital_status': 'married',
        'dependents': 2,
        'home_ownership': 'own',
        'savings_balance': 200000,
        'checking_balance': 50000,
        'credit_history_length': 8,
        'previous_defaults': 0
    }
    
    # Make decision
    print("\n" + "="*60)
    print("DECISION ENGINE TEST")
    print("="*60)
    
    decision = engine.make_decision(test_application)
    
    print(f"\nApplication ID: {decision['application_id']}")
    print(f"Final Decision: {decision['final_decision'].upper()}")
    print(f"Reason: {decision['decision_reason']}")
    print(f"Confidence: {decision['confidence']:.2%}")
    print(f"Override Allowed: {decision['override_allowed']}")
    
    print(f"\nML Prediction:")
    print(f"  Score: {decision['ml_result']['ml_score']:.3f}")
    print(f"  Risk Level: {decision['ml_result']['ml_risk_level']}")
    print(f"  ML Decision: {decision['ml_result']['ml_decision']}")
    
    print(f"\nTriggered Rules: {len(decision['triggered_rules'])}")
    for rule in decision['triggered_rules'][:5]:
        print(f"  - [{rule['severity'].upper()}] {rule['rule_name']}")
    
    print("\n" + "="*60)
