"""
Bias Detection and Fairness Monitoring

Analyzes model decisions for potential bias across demographic groups.

Metrics:
- Approval rate by group
- False positive/negative rates
- Disparate impact ratio
- Statistical parity difference
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from collections import defaultdict

class BiasDetector:
    """Detect and monitor bias in credit decisions"""
    
    def __init__(self):
        self.protected_attributes = ['age', 'marital_status', 'education_level']
        self.metrics_history = []
    
    def calculate_approval_rate(self, df: pd.DataFrame, group_col: str) -> Dict:
        """Calculate approval rate by group"""
        if group_col not in df.columns:
            return {}
        
        rates = {}
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group]
            if len(group_data) > 0:
                approval_rate = (group_data['decision'] == 'approved').sum() / len(group_data)
                rates[str(group)] = {
                    'count': len(group_data),
                    'approved': (group_data['decision'] == 'approved').sum(),
                    'approval_rate': float(approval_rate)
                }
        
        return rates
    
    def calculate_disparate_impact(self, rates: Dict) -> Dict:
        """
        Calculate disparate impact ratio
        
        Ratio should be >= 0.8 to avoid adverse impact (80% rule)
        """
        if not rates or len(rates) < 2:
            return {}
        
        # Find highest and lowest approval rates
        max_rate = max(r['approval_rate'] for r in rates.values())
        min_rate = min(r['approval_rate'] for r in rates.values())
        
        if max_rate == 0:
            return {'ratio': 0, 'passes_80_rule': False}
        
        ratio = min_rate / max_rate
        
        return {
            'ratio': float(ratio),
            'passes_80_rule': ratio >= 0.8,
            'max_rate': float(max_rate),
            'min_rate': float(min_rate)
        }
    
    def calculate_statistical_parity(self, rates: Dict) -> Dict:
        """
        Calculate statistical parity difference
        
        Difference should be close to 0 for fairness
        """
        if not rates or len(rates) < 2:
            return {}
        
        approval_rates = [r['approval_rate'] for r in rates.values()]
        max_diff = max(approval_rates) - min(approval_rates)
        
        return {
            'max_difference': float(max_diff),
            'is_fair': max_diff <= 0.1  # 10% threshold
        }
    
    def analyze_age_bias(self, df: pd.DataFrame) -> Dict:
        """Analyze bias by age groups"""
        # Create age groups
        df_copy = df.copy()
        df_copy['age_group'] = pd.cut(
            df_copy['age'],
            bins=[0, 30, 40, 50, 100],
            labels=['<30', '30-40', '40-50', '50+']
        )
        
        rates = self.calculate_approval_rate(df_copy, 'age_group')
        disparate_impact = self.calculate_disparate_impact(rates)
        statistical_parity = self.calculate_statistical_parity(rates)
        
        return {
            'attribute': 'age',
            'group_rates': rates,
            'disparate_impact': disparate_impact,
            'statistical_parity': statistical_parity
        }
    
    def analyze_marital_status_bias(self, df: pd.DataFrame) -> Dict:
        """Analyze bias by marital status"""
        rates = self.calculate_approval_rate(df, 'marital_status')
        disparate_impact = self.calculate_disparate_impact(rates)
        statistical_parity = self.calculate_statistical_parity(rates)
        
        return {
            'attribute': 'marital_status',
            'group_rates': rates,
            'disparate_impact': disparate_impact,
            'statistical_parity': statistical_parity
        }
    
    def analyze_education_bias(self, df: pd.DataFrame) -> Dict:
        """Analyze bias by education level"""
        rates = self.calculate_approval_rate(df, 'education_level')
        disparate_impact = self.calculate_disparate_impact(rates)
        statistical_parity = self.calculate_statistical_parity(rates)
        
        return {
            'attribute': 'education_level',
            'group_rates': rates,
            'disparate_impact': disparate_impact,
            'statistical_parity': statistical_parity
        }
    
    def comprehensive_bias_report(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive bias report"""
        report = {
            'total_applications': len(df),
            'overall_approval_rate': float((df['decision'] == 'approved').sum() / len(df)),
            'bias_analysis': {}
        }
        
        # Analyze each protected attribute
        if 'age' in df.columns:
            report['bias_analysis']['age'] = self.analyze_age_bias(df)
        
        if 'marital_status' in df.columns:
            report['bias_analysis']['marital_status'] = self.analyze_marital_status_bias(df)
        
        if 'education_level' in df.columns:
            report['bias_analysis']['education'] = self.analyze_education_bias(df)
        
        # Overall fairness assessment
        fairness_issues = []
        for attr, analysis in report['bias_analysis'].items():
            if 'disparate_impact' in analysis:
                if not analysis['disparate_impact'].get('passes_80_rule', True):
                    fairness_issues.append(f"{attr}: Fails 80% rule")
            if 'statistical_parity' in analysis:
                if not analysis['statistical_parity'].get('is_fair', True):
                    fairness_issues.append(f"{attr}: High statistical parity difference")
        
        report['fairness_assessment'] = {
            'has_issues': len(fairness_issues) > 0,
            'issues': fairness_issues,
            'overall_status': 'PASS' if len(fairness_issues) == 0 else 'REVIEW_NEEDED'
        }
        
        return report
    
    def generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on bias analysis"""
        recommendations = []
        
        for attr, analysis in report.get('bias_analysis', {}).items():
            disparate_impact = analysis.get('disparate_impact', {})
            
            if not disparate_impact.get('passes_80_rule', True):
                recommendations.append(
                    f"Review {attr} impact: Approval rate ratio is {disparate_impact.get('ratio', 0):.2f} "
                    f"(should be >= 0.8)"
                )
            
            statistical_parity = analysis.get('statistical_parity', {})
            if not statistical_parity.get('is_fair', True):
                recommendations.append(
                    f"Address {attr} disparity: Difference is {statistical_parity.get('max_difference', 0):.1%} "
                    f"(should be <= 10%)"
                )
        
        if not recommendations:
            recommendations.append("✓ No significant bias detected across protected attributes")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Load dataset with absolute path
    data_path = Path(__file__).parent.parent / 'data' / 'credit_dataset.csv'
    df = pd.read_csv(data_path)
    
    # Initialize detector
    detector = BiasDetector()
    
    print("="*60)
    print("BIAS DETECTION & FAIRNESS ANALYSIS")
    print("="*60)
    
    # Generate report
    report = detector.comprehensive_bias_report(df)
    
    print(f"\nTotal Applications: {report['total_applications']}")
    print(f"Overall Approval Rate: {report['overall_approval_rate']:.1%}")
    
    print("\n" + "="*60)
    print("BIAS ANALYSIS BY PROTECTED ATTRIBUTES")
    print("="*60)
    
    for attr, analysis in report['bias_analysis'].items():
        print(f"\n📊 {attr.upper()}")
        print("-" * 60)
        
        # Group rates
        print("Approval Rates by Group:")
        for group, stats in analysis['group_rates'].items():
            print(f"  {group:20s}: {stats['approval_rate']:6.1%} ({stats['approved']}/{stats['count']})")
        
        # Disparate impact
        di = analysis.get('disparate_impact', {})
        if di:
            status = "✓ PASS" if di.get('passes_80_rule') else "✗ FAIL"
            print(f"\nDisparate Impact Ratio: {di.get('ratio', 0):.3f} {status}")
            print(f"  (Min: {di.get('min_rate', 0):.1%} / Max: {di.get('max_rate', 0):.1%})")
        
        # Statistical parity
        sp = analysis.get('statistical_parity', {})
        if sp:
            status = "✓ FAIR" if sp.get('is_fair') else "✗ REVIEW"
            print(f"Statistical Parity Diff: {sp.get('max_difference', 0):.1%} {status}")
    
    print("\n" + "="*60)
    print("FAIRNESS ASSESSMENT")
    print("="*60)
    
    assessment = report['fairness_assessment']
    print(f"\nOverall Status: {assessment['overall_status']}")
    
    if assessment['has_issues']:
        print("\n⚠ Issues Found:")
        for issue in assessment['issues']:
            print(f"  - {issue}")
    else:
        print("\n✓ No significant fairness issues detected")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    recommendations = detector.generate_recommendations(report)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")
    
    print("\n" + "="*60)
    print("BIAS DETECTION COMPLETE")
    print("="*60)
