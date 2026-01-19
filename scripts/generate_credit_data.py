"""
Synthetic Credit Data Generator

Generates realistic synthetic credit application data for training and testing
the AI Credit Decision Explanation Platform.

Features:
- 100% synthetic data (no real customer information)
- Realistic distributions and correlations
- Configurable dataset size
- Balanced approval/rejection rates
- Edge cases and boundary conditions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import json
import os
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

def generate_credit_dataset(n_samples=2000):
    """
    Generate synthetic credit application dataset
    
    Args:
        n_samples: Number of samples to generate (default: 2000)
    
    Returns:
        pandas.DataFrame with synthetic credit data
    """
    
    print(f"Generating {n_samples} synthetic credit applications...")
    
    data = []
    
    for i in range(n_samples):
        # Generate correlated features for realism
        
        # Age (20-70, normal distribution centered at 40)
        age = int(np.clip(np.random.normal(40, 12), 20, 70))
        
        # Employment years (0 to age-18, skewed towards longer employment)
        max_employment = age - 18
        employment_years = int(np.clip(np.random.exponential(5), 0, max_employment))
        
        # Employment type (permanent more common for longer employment)
        if employment_years > 5:
            employment_type = np.random.choice(
                ['permanent', 'contract', 'self_employed'],
                p=[0.7, 0.2, 0.1]
            )
        else:
            employment_type = np.random.choice(
                ['permanent', 'contract', 'self_employed'],
                p=[0.4, 0.5, 0.1]
            )
        
        # Monthly income (log-normal distribution, higher for permanent employees)
        if employment_type == 'permanent':
            income_mean = 50000
        elif employment_type == 'contract':
            income_mean = 40000
        else:  # self_employed
            income_mean = 60000
        
        monthly_income = np.clip(
            np.random.lognormal(np.log(income_mean), 0.5),
            15000, 500000
        )
        
        # Education level (correlated with income)
        if monthly_income > 80000:
            education_level = np.random.choice(
                ['bachelor', 'master', 'phd'],
                p=[0.5, 0.4, 0.1]
            )
        elif monthly_income > 40000:
            education_level = np.random.choice(
                ['high_school', 'bachelor', 'master'],
                p=[0.2, 0.7, 0.1]
            )
        else:
            education_level = np.random.choice(
                ['high_school', 'bachelor'],
                p=[0.6, 0.4]
            )
        
        # Marital status and dependents
        marital_status = np.random.choice(
            ['single', 'married', 'divorced', 'widowed'],
            p=[0.35, 0.50, 0.12, 0.03]
        )
        
        if marital_status == 'married':
            dependents = int(np.clip(np.random.poisson(1.5), 0, 8))
        else:
            dependents = int(np.clip(np.random.poisson(0.5), 0, 8))
        
        # Home ownership (correlated with age and income)
        if age > 40 and monthly_income > 50000:
            home_ownership = np.random.choice(
                ['own', 'mortgage', 'rent', 'family'],
                p=[0.4, 0.3, 0.2, 0.1]
            )
        else:
            home_ownership = np.random.choice(
                ['own', 'mortgage', 'rent', 'family'],
                p=[0.1, 0.2, 0.5, 0.2]
            )
        
        # Savings and checking balance (correlated with income and age)
        savings_balance = np.clip(
            monthly_income * np.random.uniform(0.5, 10) * (age / 40),
            0, 10000000
        )
        
        checking_balance = np.clip(
            monthly_income * np.random.uniform(0.1, 2),
            0, 1000000
        )
        
        # Credit history length (0 to age-18)
        credit_history_length = int(np.clip(
            np.random.exponential(8),
            0, age - 18
        ))
        
        # Existing loans (Poisson distribution)
        existing_loans = int(np.clip(np.random.poisson(1.5), 0, 10))
        
        # Debt-to-income ratio (key risk factor)
        # Lower DTI for higher income and fewer loans
        base_dti = 0.3 + (existing_loans * 0.1) - (monthly_income / 200000)
        debt_to_income = np.clip(
            np.random.normal(base_dti, 0.15),
            0.0, 2.0
        )
        
        # Late payment count (correlated with DTI)
        if debt_to_income > 0.6:
            late_payment_count = int(np.clip(np.random.poisson(2), 0, 20))
        elif debt_to_income > 0.4:
            late_payment_count = int(np.clip(np.random.poisson(0.8), 0, 20))
        else:
            late_payment_count = int(np.clip(np.random.poisson(0.3), 0, 20))
        
        # Credit utilization (correlated with DTI)
        credit_utilization = np.clip(
            debt_to_income * np.random.uniform(0.8, 1.2),
            0.0, 1.5
        )
        
        # Previous defaults (rare, correlated with late payments)
        if late_payment_count > 5:
            previous_defaults = int(np.clip(np.random.poisson(0.5), 0, 5))
        else:
            previous_defaults = 0 if np.random.random() > 0.05 else 1
        
        # Loan purpose
        loan_purpose = np.random.choice(
            ['home', 'car', 'education', 'business', 'personal'],
            p=[0.25, 0.30, 0.15, 0.10, 0.20]
        )
        
        # Requested amount (based on income and purpose)
        if loan_purpose == 'home':
            requested_amount = monthly_income * np.random.uniform(30, 80)
        elif loan_purpose == 'car':
            requested_amount = monthly_income * np.random.uniform(10, 30)
        elif loan_purpose == 'education':
            requested_amount = monthly_income * np.random.uniform(5, 20)
        elif loan_purpose == 'business':
            requested_amount = monthly_income * np.random.uniform(20, 100)
        else:  # personal
            requested_amount = monthly_income * np.random.uniform(2, 15)
        
        requested_amount = np.clip(requested_amount, 10000, 5000000)
        
        # Decision logic (rule-based + some randomness)
        # Adjusted to achieve ~60-65% approval rate
        risk_score = 0
        
        # Critical rejection criteria
        if debt_to_income > 0.65:
            risk_score += 100  # Auto-reject
        if previous_defaults > 0:
            risk_score += 100  # Auto-reject
        if monthly_income < 20000:
            risk_score += 100  # Auto-reject
        
        # High risk factors (reduced penalties for balanced approval)
        if late_payment_count >= 3:
            risk_score += 50
        elif late_payment_count == 2:
            risk_score += 20
        elif late_payment_count == 1:
            risk_score += 8
        
        if credit_utilization > 0.80:
            risk_score += 25
        elif credit_utilization > 0.60:
            risk_score += 12
        
        if employment_years < 1:
            risk_score += 15
        elif employment_years < 2:
            risk_score += 6
        
        # Medium risk factors (moderate penalties)
        if debt_to_income > 0.45:
            risk_score += 15
        elif debt_to_income > 0.35:
            risk_score += 6
        
        if existing_loans > 4:
            risk_score += 10
        elif existing_loans > 2:
            risk_score += 4
        
        if credit_history_length < 2:
            risk_score += 10
        elif credit_history_length < 3:
            risk_score += 4
        
        if requested_amount > monthly_income * 10:
            risk_score += 20
        
        if savings_balance < monthly_income * 2:
            risk_score += 6
        
        # Positive factors (stronger benefits for approval)
        if monthly_income > 100000:
            risk_score -= 20
        elif monthly_income > 80000:
            risk_score -= 12
        elif monthly_income > 50000:
            risk_score -= 6
        
        if home_ownership == 'own':
            risk_score -= 15
        
        if savings_balance > monthly_income * 10:
            risk_score -= 15
        elif savings_balance > monthly_income * 6:
            risk_score -= 8
        
        if employment_type == 'permanent' and employment_years > 10:
            risk_score -= 12
        elif employment_type == 'permanent' and employment_years > 5:
            risk_score -= 6
        
        # Add some randomness
        risk_score += np.random.randint(-10, 10)
        
        # Determine decision and risk level (adjusted thresholds for 60-65% approval)
        if risk_score >= 60:
            decision = 'rejected'
            risk_level = 'high'
        elif risk_score >= 25:
            decision = 'rejected'
            risk_level = 'medium'
        elif risk_score >= 10:
            decision = 'approved'
            risk_level = 'medium'
        else:
            decision = 'approved'
            risk_level = 'low'
        
        # Create record
        record = {
            'application_id': str(uuid.uuid4()),
            'monthly_income': round(monthly_income, 2),
            'employment_years': employment_years,
            'employment_type': employment_type,
            'debt_to_income': round(debt_to_income, 4),
            'existing_loans': existing_loans,
            'late_payment_count': late_payment_count,
            'credit_utilization': round(credit_utilization, 4),
            'requested_amount': round(requested_amount, 2),
            'loan_purpose': loan_purpose,
            'age': age,
            'education_level': education_level,
            'marital_status': marital_status,
            'dependents': dependents,
            'home_ownership': home_ownership,
            'savings_balance': round(savings_balance, 2),
            'checking_balance': round(checking_balance, 2),
            'credit_history_length': credit_history_length,
            'previous_defaults': previous_defaults,
            'decision': decision,
            'risk_level': risk_level
        }
        
        data.append(record)
        
        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1}/{n_samples} records...")
    
    df = pd.DataFrame(data)
    
    # Print statistics
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    print(f"\nTotal records: {len(df)}")
    print(f"\nDecision distribution:")
    print(df['decision'].value_counts())
    print(f"\nApproval rate: {(df['decision'] == 'approved').sum() / len(df) * 100:.1f}%")
    print(f"\nRisk level distribution:")
    print(df['risk_level'].value_counts())
    print(f"\nKey statistics:")
    print(f"  Average income: {df['monthly_income'].mean():,.0f} THB")
    print(f"  Average DTI: {df['debt_to_income'].mean():.2f}")
    print(f"  Average late payments: {df['late_payment_count'].mean():.2f}")
    print(f"  Previous defaults: {(df['previous_defaults'] > 0).sum()} ({(df['previous_defaults'] > 0).sum() / len(df) * 100:.1f}%)")
    
    return df

def validate_dataset(df):
    """Validate the generated dataset"""
    print("\n" + "="*60)
    print("DATASET VALIDATION")
    print("="*60)
    
    issues = []
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        issues.append(f"Missing values found: {missing[missing > 0]}")
    else:
        print("✓ No missing values")
    
    # Check value ranges
    if (df['monthly_income'] < 15000).any() or (df['monthly_income'] > 500000).any():
        issues.append("Income out of range")
    else:
        print("✓ Income within valid range")
    
    if (df['debt_to_income'] < 0).any() or (df['debt_to_income'] > 2).any():
        issues.append("DTI out of range")
    else:
        print("✓ DTI within valid range")
    
    if (df['age'] < 20).any() or (df['age'] > 70).any():
        issues.append("Age out of range")
    else:
        print("✓ Age within valid range")
    
    # Check logical consistency
    if (df['employment_years'] > df['age'] - 18).any():
        issues.append("Employment years exceed possible range")
    else:
        print("✓ Employment years logically consistent")
    
    # Check decision distribution (should be 55-70% approval)
    approval_rate = (df['decision'] == 'approved').sum() / len(df)
    if 0.55 <= approval_rate <= 0.70:
        print(f"✓ Approval rate balanced: {approval_rate*100:.1f}%")
    else:
        issues.append(f"Approval rate imbalanced: {approval_rate*100:.1f}%")
    
    if issues:
        print("\n⚠ VALIDATION ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ All validation checks passed!")
        return True

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✓ Data directory ready\n")
    
    # Generate dataset
    df = generate_credit_dataset(n_samples=2000)
    
    # Validate
    validate_dataset(df)
    
    # Save to CSV
    output_path = data_dir / "credit_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Dataset saved to: {output_path}")
    
    # Save sample for inspection
    sample_path = data_dir / "credit_dataset_sample.csv"
    df.head(20).to_csv(sample_path, index=False)
    print(f"✅ Sample (20 rows) saved to: {sample_path}")
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "n_samples": len(df),
        "approval_rate": float((df['decision'] == 'approved').sum() / len(df)),
        "features": list(df.columns),
        "statistics": {
            "avg_income": float(df['monthly_income'].mean()),
            "avg_dti": float(df['debt_to_income'].mean()),
            "avg_late_payments": float(df['late_payment_count'].mean()),
            "default_rate": float((df['previous_defaults'] > 0).sum() / len(df))
        }
    }
    
    metadata_path = data_dir / "dataset_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ Metadata saved to: {metadata_path}")
    
    print("\n" + "="*60)
    print("DATASET GENERATION COMPLETE!")
    print("="*60)
