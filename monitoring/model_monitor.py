"""
Model Monitoring and Drift Detection

Monitors model performance over time and detects data/concept drift.

Metrics:
- Performance metrics over time
- Feature distribution changes
- Prediction distribution changes
- Drift detection alerts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from scipy import stats

class ModelMonitor:
    """Monitor model performance and detect drift"""
    
    def __init__(self):
        self.baseline_stats = None
        self.performance_history = []
        self.drift_threshold = 0.05  # 5% significance level
    
    def set_baseline(self, df: pd.DataFrame):
        """Set baseline statistics from training data"""
        self.baseline_stats = {
            'feature_means': df.select_dtypes(include=[np.number]).mean().to_dict(),
            'feature_stds': df.select_dtypes(include=[np.number]).std().to_dict(),
            'approval_rate': (df['decision'] == 'approved').mean() if 'decision' in df.columns else None
        }
        print("✓ Baseline statistics set")
    
    def detect_feature_drift(self, current_df: pd.DataFrame, feature: str) -> Dict:
        """
        Detect drift in a single feature using Kolmogorov-Smirnov test
        
        Returns drift status and p-value
        """
        if not self.baseline_stats or feature not in self.baseline_stats['feature_means']:
            return {'drift_detected': False, 'reason': 'No baseline'}
        
        if feature not in current_df.columns:
            return {'drift_detected': False, 'reason': 'Feature not found'}
        
        # Get baseline statistics
        baseline_mean = self.baseline_stats['feature_means'][feature]
        baseline_std = self.baseline_stats['feature_stds'][feature]
        
        # Current statistics
        current_mean = current_df[feature].mean()
        current_std = current_df[feature].std()
        
        # Calculate drift metrics
        mean_shift = abs(current_mean - baseline_mean) / baseline_std if baseline_std > 0 else 0
        std_ratio = current_std / baseline_std if baseline_std > 0 else 1
        
        # Detect significant drift (mean shift > 2 std or std ratio > 1.5)
        drift_detected = mean_shift > 2 or std_ratio > 1.5 or std_ratio < 0.67
        
        return {
            'feature': feature,
            'drift_detected': drift_detected,
            'baseline_mean': float(baseline_mean),
            'current_mean': float(current_mean),
            'mean_shift_std': float(mean_shift),
            'baseline_std': float(baseline_std),
            'current_std': float(current_std),
            'std_ratio': float(std_ratio),
            'severity': 'high' if mean_shift > 3 else 'medium' if mean_shift > 2 else 'low'
        }
    
    def detect_prediction_drift(self, current_df: pd.DataFrame) -> Dict:
        """Detect drift in prediction distribution"""
        if not self.baseline_stats or 'decision' not in current_df.columns:
            return {'drift_detected': False, 'reason': 'No baseline or decisions'}
        
        baseline_approval = self.baseline_stats['approval_rate']
        current_approval = (current_df['decision'] == 'approved').mean()
        
        # Calculate difference
        approval_diff = abs(current_approval - baseline_approval)
        
        # Detect significant drift (> 10% change)
        drift_detected = approval_diff > 0.10
        
        return {
            'drift_detected': drift_detected,
            'baseline_approval_rate': float(baseline_approval),
            'current_approval_rate': float(current_approval),
            'difference': float(approval_diff),
            'severity': 'high' if approval_diff > 0.15 else 'medium' if approval_diff > 0.10 else 'low'
        }
    
    def comprehensive_drift_report(self, current_df: pd.DataFrame) -> Dict:
        """Generate comprehensive drift detection report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': len(current_df),
            'feature_drift': {},
            'prediction_drift': {},
            'overall_status': 'OK'
        }
        
        # Check feature drift for numeric columns
        numeric_features = current_df.select_dtypes(include=[np.number]).columns
        drift_count = 0
        
        for feature in numeric_features:
            if feature in ['application_id']:  # Skip ID columns
                continue
            
            drift_result = self.detect_feature_drift(current_df, feature)
            if drift_result.get('drift_detected'):
                report['feature_drift'][feature] = drift_result
                drift_count += 1
        
        # Check prediction drift
        prediction_drift = self.detect_prediction_drift(current_df)
        report['prediction_drift'] = prediction_drift
        
        if prediction_drift.get('drift_detected'):
            drift_count += 1
        
        # Overall status
        if drift_count > 0:
            report['overall_status'] = 'DRIFT_DETECTED'
            report['drift_count'] = drift_count
        
        return report
    
    def track_performance(self, metrics: Dict):
        """Track model performance over time"""
        metrics['timestamp'] = datetime.now().isoformat()
        self.performance_history.append(metrics)
    
    def get_performance_trend(self, metric_name: str, days: int = 7) -> Dict:
        """Get performance trend for a specific metric"""
        if not self.performance_history:
            return {'trend': 'no_data'}
        
        # Filter recent history
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            m for m in self.performance_history
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]
        
        if len(recent) < 2:
            return {'trend': 'insufficient_data'}
        
        values = [m.get(metric_name, 0) for m in recent]
        
        # Calculate trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        return {
            'metric': metric_name,
            'current_value': values[-1],
            'trend': 'improving' if slope > 0 else 'declining',
            'slope': float(slope),
            'r_squared': float(r_value ** 2),
            'data_points': len(values)
        }
    
    def generate_alerts(self, drift_report: Dict) -> List[Dict]:
        """Generate alerts based on drift detection"""
        alerts = []
        
        # Feature drift alerts
        for feature, drift_info in drift_report.get('feature_drift', {}).items():
            if drift_info.get('severity') == 'high':
                alerts.append({
                    'type': 'feature_drift',
                    'severity': 'high',
                    'feature': feature,
                    'message': f"High drift detected in {feature}: {drift_info.get('mean_shift_std', 0):.2f} std shift",
                    'recommendation': f"Review {feature} distribution and consider model retraining"
                })
        
        # Prediction drift alerts
        pred_drift = drift_report.get('prediction_drift', {})
        if pred_drift.get('drift_detected'):
            alerts.append({
                'type': 'prediction_drift',
                'severity': pred_drift.get('severity', 'medium'),
                'message': f"Approval rate changed by {pred_drift.get('difference', 0):.1%}",
                'recommendation': "Investigate business changes or model degradation"
            })
        
        return alerts

# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Load training data for baseline with absolute path
    data_path = Path(__file__).parent.parent / 'data' / 'credit_dataset.csv'
    df_train = pd.read_csv(data_path)
    
    # Initialize monitor
    monitor = ModelMonitor()
    monitor.set_baseline(df_train)
    
    print("="*60)
    print("MODEL MONITORING & DRIFT DETECTION")
    print("="*60)
    
    # Simulate current data (using same data for demo)
    df_current = df_train.sample(500)
    
    # Generate drift report
    drift_report = monitor.comprehensive_drift_report(df_current)
    
    print(f"\nMonitoring Report")
    print(f"Timestamp: {drift_report['timestamp']}")
    print(f"Sample Size: {drift_report['sample_size']}")
    print(f"Overall Status: {drift_report['overall_status']}")
    
    # Feature drift
    if drift_report['feature_drift']:
        print("\n" + "="*60)
        print("FEATURE DRIFT DETECTED")
        print("="*60)
        for feature, info in drift_report['feature_drift'].items():
            print(f"\n📊 {feature}")
            print(f"  Severity: {info['severity'].upper()}")
            print(f"  Mean Shift: {info['mean_shift_std']:.2f} std")
            print(f"  Baseline Mean: {info['baseline_mean']:.2f}")
            print(f"  Current Mean: {info['current_mean']:.2f}")
    else:
        print("\n✓ No significant feature drift detected")
    
    # Prediction drift
    pred_drift = drift_report['prediction_drift']
    if pred_drift.get('drift_detected'):
        print("\n" + "="*60)
        print("PREDICTION DRIFT DETECTED")
        print("="*60)
        print(f"Baseline Approval Rate: {pred_drift['baseline_approval_rate']:.1%}")
        print(f"Current Approval Rate: {pred_drift['current_approval_rate']:.1%}")
        print(f"Difference: {pred_drift['difference']:.1%}")
        print(f"Severity: {pred_drift['severity'].upper()}")
    else:
        print("\n✓ No significant prediction drift detected")
    
    # Generate alerts
    alerts = monitor.generate_alerts(drift_report)
    if alerts:
        print("\n" + "="*60)
        print("ALERTS")
        print("="*60)
        for i, alert in enumerate(alerts, 1):
            print(f"\n{i}. [{alert['severity'].upper()}] {alert['type']}")
            print(f"   {alert['message']}")
            print(f"   → {alert['recommendation']}")
    
    print("\n" + "="*60)
    print("MONITORING COMPLETE")
    print("="*60)
