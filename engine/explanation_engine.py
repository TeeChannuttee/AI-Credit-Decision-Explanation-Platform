"""
Explanation Engine

Generates human-readable explanations for credit decisions.

Features:
- Combine triggered rules
- Integrate SHAP feature importance
- Generate explanations in Thai and English
- Multiple explanation styles (short/formal/advisory)
- Structured JSON output
"""

import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import shap

class ExplanationEngine:
    """Generate explanations for credit decisions"""
    
    def __init__(self, model_path='models/credit_model_v1.0.0.pkl',
                 rules_path='data/explanation_rules.json'):
        """
        Initialize explanation engine
        
        Args:
            model_path: Path to trained ML model
            rules_path: Path to business rules
        """
        # Load ML model for SHAP
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
        
        # Load rules
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
            self.rules = {r['rule_id']: r for r in rules_data['rules']}
        
        # Create SHAP explainer
        self.shap_explainer = None
        
        print("✓ Explanation engine initialized")
    
    def create_shap_explainer(self, background_data: pd.DataFrame):
        """
        Create SHAP explainer with background data
        
        Args:
            background_data: Sample data for SHAP background
        """
        X_scaled = self.scaler.transform(background_data)
        self.shap_explainer = shap.LinearExplainer(
            self.model, X_scaled, feature_names=self.feature_names
        )
        print("✓ SHAP explainer created")
    
    def get_shap_values(self, X: pd.DataFrame) -> Dict[str, float]:
        """
        Get SHAP values for instance
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Dictionary of feature: SHAP value
        """
        if self.shap_explainer is None:
            return {}
        
        X_scaled = self.scaler.transform(X)
        shap_values = self.shap_explainer.shap_values(X_scaled)
        
        # Get values for positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        return dict(zip(self.feature_names, shap_values[0]))
    
    def generate_explanation(self, decision_result: Dict, 
                           application_data: Dict,
                           X_features: pd.DataFrame = None,
                           language: str = 'th',
                           style: str = 'formal') -> Dict:
        """
        Generate complete explanation
        
        Args:
            decision_result: Result from decision engine
            application_data: Original application data
            X_features: Prepared features for SHAP
            language: 'th' or 'en'
            style: 'short', 'formal', or 'advisory'
            
        Returns:
            Complete explanation dictionary
        """
        lang_key = 'reason_th' if language == 'th' else 'reason_en'
        rec_key = 'recommendation_th' if language == 'th' else 'recommendation_en'
        
        # Get SHAP values if available
        shap_values = {}
        if X_features is not None and self.shap_explainer is not None:
            shap_values = self.get_shap_values(X_features)
        
        # Build explanation
        explanation = {
            'application_id': decision_result.get('application_id'),
            'decision': decision_result['final_decision'],
            'language': language,
            'style': style
        }
        
        # Summary
        if decision_result['final_decision'] == 'approved':
            if language == 'th':
                explanation['summary'] = self._generate_approval_summary_th(
                    decision_result, style
                )
            else:
                explanation['summary'] = self._generate_approval_summary_en(
                    decision_result, style
                )
        else:
            if language == 'th':
                explanation['summary'] = self._generate_rejection_summary_th(
                    decision_result, style
                )
            else:
                explanation['summary'] = self._generate_rejection_summary_en(
                    decision_result, style
                )
        
        # Detailed reasons from triggered rules
        explanation['reasons'] = []
        for rule in decision_result['triggered_rules'][:5]:  # Top 5 rules
            explanation['reasons'].append({
                'rule_id': rule['rule_id'],
                'severity': rule['severity'],
                'reason': rule[lang_key]
            })
        
        # Recommendations
        explanation['recommendations'] = []
        if decision_result['final_decision'] == 'rejected':
            for rule in decision_result['triggered_rules'][:3]:
                if rule['action'] in ['reject', 'review']:
                    explanation['recommendations'].append(rule[rec_key])
        
        # Feature contributions (SHAP)
        if shap_values:
            top_features = sorted(shap_values.items(), 
                                key=lambda x: abs(x[1]), reverse=True)[:5]
            
            explanation['feature_contributions'] = []
            for feature, value in top_features:
                explanation['feature_contributions'].append({
                    'feature': feature,
                    'impact': float(value),
                    'direction': 'positive' if value > 0 else 'negative'
                })
        
        # ML insights
        explanation['ml_insights'] = {
            'score': decision_result['ml_result']['ml_score'],
            'risk_level': decision_result['ml_result']['ml_risk_level'],
            'confidence': decision_result['confidence']
        }
        
        # Policy citations
        explanation['policy_citations'] = []
        for rule in decision_result['triggered_rules'][:3]:
            if 'policy_reference' in rule:
                explanation['policy_citations'].append(rule['policy_reference'])
        
        return explanation
    
    def _generate_approval_summary_th(self, decision_result: Dict, style: str) -> str:
        """Generate Thai approval summary"""
        if style == 'short':
            return "คำขอสินเชื่อได้รับการอนุมัติ"
        elif style == 'formal':
            return f"คำขอสินเชื่อได้รับการอนุมัติตามเกณฑ์การประเมินความเสี่ยง ระดับความเสี่ยง: {decision_result['ml_result']['ml_risk_level']}"
        else:  # advisory
            return f"ยินดีด้วย! คำขอสินเชื่อของคุณได้รับการอนุมัติ คุณมีโปรไฟล์ทางการเงินที่ดี (ระดับความเสี่ยง: {decision_result['ml_result']['ml_risk_level']})"
    
    def _generate_approval_summary_en(self, decision_result: Dict, style: str) -> str:
        """Generate English approval summary"""
        if style == 'short':
            return "Credit application approved"
        elif style == 'formal':
            return f"Credit application approved based on risk assessment criteria. Risk level: {decision_result['ml_result']['ml_risk_level']}"
        else:  # advisory
            return f"Congratulations! Your credit application has been approved. You have a strong financial profile (risk level: {decision_result['ml_result']['ml_risk_level']})"
    
    def _generate_rejection_summary_th(self, decision_result: Dict, style: str) -> str:
        """Generate Thai rejection summary"""
        reason = decision_result['decision_reason']
        
        if style == 'short':
            return "คำขอสินเชื่อไม่ได้รับการอนุมัติ"
        elif style == 'formal':
            if reason == 'critical_rule_violation':
                return "คำขอสินเชื่อไม่ได้รับการอนุมัติเนื่องจากไม่ผ่านเกณฑ์ความเสี่ยงที่กำหนด"
            elif reason == 'high_risk_factors':
                return "คำขอสินเชื่อไม่ได้รับการอนุมัติเนื่องจากปัจจัยความเสี่ยงสูง"
            else:
                return "คำขอสินเชื่อไม่ได้รับการอนุมัติตามผลการประเมินความเสี่ยง"
        else:  # advisory
            return "คำขอสินเชื่อของคุณไม่ได้รับการอนุมัติในครั้งนี้ กรุณาดูคำแนะนำด้านล่างเพื่อปรับปรุงโอกาสในการขอสินเชื่อครั้งต่อไป"
    
    def _generate_rejection_summary_en(self, decision_result: Dict, style: str) -> str:
        """Generate English rejection summary"""
        reason = decision_result['decision_reason']
        
        if style == 'short':
            return "Credit application declined"
        elif style == 'formal':
            if reason == 'critical_rule_violation':
                return "Credit application declined due to critical risk criteria not met"
            elif reason == 'high_risk_factors':
                return "Credit application declined due to high risk factors"
            else:
                return "Credit application declined based on risk assessment"
        else:  # advisory
            return "Your credit application was not approved at this time. Please review the recommendations below to improve your chances for future applications"
    
    def format_for_display(self, explanation: Dict) -> str:
        """
        Format explanation for console display
        
        Args:
            explanation: Explanation dictionary
            
        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 60)
        output.append("CREDIT DECISION EXPLANATION")
        output.append("=" * 60)
        output.append(f"\nApplication ID: {explanation['application_id']}")
        output.append(f"Decision: {explanation['decision'].upper()}")
        output.append(f"\n{explanation['summary']}")
        
        if explanation['reasons']:
            output.append(f"\nKey Reasons:")
            for i, reason in enumerate(explanation['reasons'], 1):
                output.append(f"  {i}. [{reason['severity'].upper()}] {reason['reason']}")
        
        if explanation.get('recommendations'):
            output.append(f"\nRecommendations:")
            for i, rec in enumerate(explanation['recommendations'], 1):
                output.append(f"  {i}. {rec}")
        
        if explanation.get('feature_contributions'):
            output.append(f"\nKey Factors:")
            for contrib in explanation['feature_contributions']:
                direction = "↑" if contrib['direction'] == 'positive' else "↓"
                output.append(f"  {direction} {contrib['feature']}: {contrib['impact']:+.3f}")
        
        output.append(f"\nML Insights:")
        output.append(f"  Score: {explanation['ml_insights']['score']:.3f}")
        output.append(f"  Risk Level: {explanation['ml_insights']['risk_level']}")
        output.append(f"  Confidence: {explanation['ml_insights']['confidence']:.1%}")
        
        if explanation.get('policy_citations'):
            output.append(f"\nPolicy References:")
            for citation in explanation['policy_citations']:
                output.append(f"  - {citation}")
        
        output.append("=" * 60)
        
        return "\n".join(output)

# Example usage
if __name__ == "__main__":
    from decision_engine import DecisionEngine
    
    # Initialize engines
    decision_engine = DecisionEngine()
    explanation_engine = ExplanationEngine()
    
    # Test application
    test_application = {
        'application_id': 'TEST002',
        'monthly_income': 25000,
        'employment_years': 2,
        'employment_type': 'contract',
        'debt_to_income': 0.55,
        'existing_loans': 3,
        'late_payment_count': 2,
        'credit_utilization': 0.75,
        'requested_amount': 500000,
        'loan_purpose': 'personal',
        'age': 28,
        'education_level': 'bachelor',
        'marital_status': 'single',
        'dependents': 0,
        'home_ownership': 'rent',
        'savings_balance': 50000,
        'checking_balance': 10000,
        'credit_history_length': 3,
        'previous_defaults': 0
    }
    
    # Make decision
    decision = decision_engine.make_decision(test_application)
    
    # Prepare features for SHAP
    X = decision_engine.prepare_features(test_application)
    
    # Load background data for SHAP
    import pandas as pd
    df = pd.read_csv('data/credit_dataset.csv').sample(100)
    X_bg = decision_engine.prepare_features(df.iloc[0].to_dict())
    explanation_engine.create_shap_explainer(X_bg)
    
    # Generate explanation (Thai, formal)
    explanation_th = explanation_engine.generate_explanation(
        decision, test_application, X, language='th', style='formal'
    )
    
    print(explanation_engine.format_for_display(explanation_th))
    
    # Generate explanation (English, advisory)
    print("\n")
    explanation_en = explanation_engine.generate_explanation(
        decision, test_application, X, language='en', style='advisory'
    )
    
    print(explanation_engine.format_for_display(explanation_en))
    
    # Save as JSON
    with open('sample_explanation.json', 'w', encoding='utf-8') as f:
        json.dump(explanation_th, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Explanation saved to sample_explanation.json")
