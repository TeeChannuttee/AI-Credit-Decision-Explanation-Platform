"""
What-if Simulation Engine

Allows users to adjust application parameters and see how decisions change in real-time.

Features:
- Parameter adjustment
- Real-time decision recalculation
- Side-by-side comparison
- Impact analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, List
from copy import deepcopy
from engine.decision_engine import DecisionEngine
from engine.explanation_engine import ExplanationEngine

class WhatIfSimulator:
    """What-if simulation for credit decisions"""
    
    def __init__(self):
        """Initialize simulator"""
        self.decision_engine = DecisionEngine()
        self.explanation_engine = ExplanationEngine()
        print("✓ What-if simulator initialized")
    
    def simulate(self, original_application: Dict, 
                 modifications: Dict) -> Dict:
        """
        Simulate decision with modified parameters
        
        Args:
            original_application: Original application data
            modifications: Dictionary of field: new_value to change
            
        Returns:
            Simulation result with comparison
        """
        # Get original decision
        original_decision = self.decision_engine.make_decision(original_application)
        
        # Create modified application
        modified_application = deepcopy(original_application)
        modified_application.update(modifications)
        
        # Get modified decision
        modified_decision = self.decision_engine.make_decision(modified_application)
        
        # Compare results
        comparison = self._compare_decisions(
            original_decision, 
            modified_decision,
            modifications
        )
        
        return {
            'original': original_decision,
            'modified': modified_decision,
            'modifications': modifications,
            'comparison': comparison
        }
    
    def _compare_decisions(self, original: Dict, modified: Dict, 
                          changes: Dict) -> Dict:
        """
        Compare two decisions
        
        Args:
            original: Original decision result
            modified: Modified decision result
            changes: Applied modifications
            
        Returns:
            Comparison analysis
        """
        decision_changed = original['final_decision'] != modified['final_decision']
        
        score_delta = (modified['ml_result']['ml_score'] - 
                      original['ml_result']['ml_score'])
        
        confidence_delta = modified['confidence'] - original['confidence']
        
        risk_changed = (original['ml_result']['ml_risk_level'] != 
                       modified['ml_result']['ml_risk_level'])
        
        return {
            'decision_changed': decision_changed,
            'decision_direction': self._get_direction(
                original['final_decision'], 
                modified['final_decision']
            ),
            'score_delta': float(score_delta),
            'score_change_pct': float(score_delta / original['ml_result']['ml_score'] * 100),
            'confidence_delta': float(confidence_delta),
            'risk_level_changed': risk_changed,
            'risk_level_direction': self._get_risk_direction(
                original['ml_result']['ml_risk_level'],
                modified['ml_result']['ml_risk_level']
            ),
            'modified_fields': list(changes.keys()),
            'impact_summary': self._generate_impact_summary(
                decision_changed, score_delta, risk_changed
            )
        }
    
    def _get_direction(self, original: str, modified: str) -> str:
        """Get decision change direction"""
        if original == modified:
            return 'unchanged'
        elif original == 'rejected' and modified == 'approved':
            return 'improved'
        else:
            return 'worsened'
    
    def _get_risk_direction(self, original: str, modified: str) -> str:
        """Get risk level change direction"""
        risk_order = {'low': 0, 'medium': 1, 'high': 2}
        
        if original == modified:
            return 'unchanged'
        elif risk_order[modified] < risk_order[original]:
            return 'reduced'
        else:
            return 'increased'
    
    def _generate_impact_summary(self, decision_changed: bool, 
                                 score_delta: float, 
                                 risk_changed: bool) -> str:
        """Generate human-readable impact summary"""
        if decision_changed:
            if score_delta > 0:
                return "Significant improvement - Decision changed to APPROVED"
            else:
                return "Significant decline - Decision changed to REJECTED"
        elif abs(score_delta) > 0.1:
            return f"Moderate impact - Score changed by {abs(score_delta):.1%}"
        elif risk_changed:
            return "Minor impact - Risk level changed"
        else:
            return "Minimal impact - No significant changes"
    
    def batch_simulate(self, original_application: Dict, 
                      scenarios: List[Dict]) -> List[Dict]:
        """
        Run multiple what-if scenarios
        
        Args:
            original_application: Base application
            scenarios: List of modification dictionaries
            
        Returns:
            List of simulation results
        """
        results = []
        
        for i, scenario in enumerate(scenarios):
            result = self.simulate(original_application, scenario)
            result['scenario_id'] = i + 1
            result['scenario_name'] = scenario.get('_name', f'Scenario {i+1}')
            results.append(result)
        
        return results
    
    def suggest_improvements(self, application: Dict, 
                           decision: Dict) -> List[Dict]:
        """
        Suggest parameter changes to improve approval chances
        
        Args:
            application: Current application
            decision: Current decision result
            
        Returns:
            List of suggested improvements
        """
        suggestions = []
        
        # If already approved, no suggestions needed
        if decision['final_decision'] == 'approved':
            return [{
                'message': 'Application already approved',
                'suggestions': []
            }]
        
        # Analyze triggered rules for suggestions
        for rule in decision['triggered_rules']:
            if rule['severity'] in ['critical', 'high', 'medium']:
                suggestion = self._rule_to_suggestion(rule, application)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions[:5]  # Top 5 suggestions
    
    def _rule_to_suggestion(self, rule: Dict, application: Dict) -> Dict:
        """Convert triggered rule to actionable suggestion"""
        rule_id = rule['rule_id']
        
        # Map rules to suggestions
        if 'DTI' in rule_id or 'debt_to_income' in rule['condition']:
            current_dti = application.get('debt_to_income', 0)
            target_dti = 0.35
            return {
                'field': 'debt_to_income',
                'current_value': current_dti,
                'suggested_value': target_dti,
                'reason': 'Reduce debt-to-income ratio to below 35%',
                'priority': 'high'
            }
        
        elif 'late_payment' in rule['condition']:
            return {
                'field': 'late_payment_count',
                'current_value': application.get('late_payment_count', 0),
                'suggested_value': 0,
                'reason': 'Maintain perfect payment history for 12 months',
                'priority': 'high'
            }
        
        elif 'income' in rule['condition']:
            current_income = application.get('monthly_income', 0)
            return {
                'field': 'monthly_income',
                'current_value': current_income,
                'suggested_value': current_income * 1.2,
                'reason': 'Increase monthly income or add co-applicant',
                'priority': 'medium'
            }
        
        elif 'savings' in rule['condition']:
            current_savings = application.get('savings_balance', 0)
            target_savings = application.get('monthly_income', 50000) * 3
            return {
                'field': 'savings_balance',
                'current_value': current_savings,
                'suggested_value': target_savings,
                'reason': 'Build emergency fund (3-6 months of income)',
                'priority': 'medium'
            }
        
        return None

# Example usage
if __name__ == "__main__":
    import json
    
    # Initialize simulator
    simulator = WhatIfSimulator()
    
    # Test application (rejected)
    test_application = {
        'application_id': 'WHATIF001',
        'monthly_income': 30000,
        'employment_years': 2,
        'employment_type': 'contract',
        'debt_to_income': 0.55,
        'existing_loans': 3,
        'late_payment_count': 2,
        'credit_utilization': 0.75,
        'requested_amount': 400000,
        'loan_purpose': 'personal',
        'age': 28,
        'education_level': 'bachelor',
        'marital_status': 'single',
        'dependents': 0,
        'home_ownership': 'rent',
        'savings_balance': 30000,
        'checking_balance': 10000,
        'credit_history_length': 3,
        'previous_defaults': 0
    }
    
    print("="*60)
    print("WHAT-IF SIMULATION DEMO")
    print("="*60)
    
    # Get original decision
    original_decision = simulator.decision_engine.make_decision(test_application)
    print(f"\nOriginal Decision: {original_decision['final_decision'].upper()}")
    print(f"ML Score: {original_decision['ml_result']['ml_score']:.3f}")
    print(f"Risk Level: {original_decision['ml_result']['ml_risk_level']}")
    
    # Scenario 1: Reduce DTI
    print("\n" + "="*60)
    print("SCENARIO 1: Reduce Debt-to-Income Ratio")
    print("="*60)
    
    scenario1 = simulator.simulate(test_application, {
        'debt_to_income': 0.30
    })
    
    print(f"Modified Decision: {scenario1['modified']['final_decision'].upper()}")
    print(f"ML Score: {scenario1['modified']['ml_result']['ml_score']:.3f}")
    print(f"Score Change: {scenario1['comparison']['score_delta']:+.3f} ({scenario1['comparison']['score_change_pct']:+.1f}%)")
    print(f"Impact: {scenario1['comparison']['impact_summary']}")
    
    # Scenario 2: Improve payment history + increase savings
    print("\n" + "="*60)
    print("SCENARIO 2: Perfect Payment History + Higher Savings")
    print("="*60)
    
    scenario2 = simulator.simulate(test_application, {
        'late_payment_count': 0,
        'savings_balance': 150000,
        'debt_to_income': 0.30
    })
    
    print(f"Modified Decision: {scenario2['modified']['final_decision'].upper()}")
    print(f"ML Score: {scenario2['modified']['ml_result']['ml_score']:.3f}")
    print(f"Score Change: {scenario2['comparison']['score_delta']:+.3f} ({scenario2['comparison']['score_change_pct']:+.1f}%)")
    print(f"Impact: {scenario2['comparison']['impact_summary']}")
    
    # Get improvement suggestions
    print("\n" + "="*60)
    print("IMPROVEMENT SUGGESTIONS")
    print("="*60)
    
    suggestions = simulator.suggest_improvements(test_application, original_decision)
    for i, suggestion in enumerate(suggestions, 1):
        if 'field' in suggestion:
            print(f"\n{i}. {suggestion['reason']}")
            print(f"   Current: {suggestion['current_value']}")
            print(f"   Target: {suggestion['suggested_value']}")
            print(f"   Priority: {suggestion['priority'].upper()}")
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
