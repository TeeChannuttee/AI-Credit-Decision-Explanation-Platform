"""
Generate Training Dataset for LLM Fine-tuning

Creates paired examples of credit decisions and natural Thai explanations
for fine-tuning Phi-3 or Gemma models.
"""

import json
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.decision_engine import DecisionEngine
from engine.explanation_engine import ExplanationEngine

def generate_varied_application():
    """Generate a varied credit application"""
    
    # Vary income levels
    income_levels = [25000, 35000, 45000, 55000, 65000, 75000, 85000, 100000]
    
    # Vary risk profiles
    risk_profiles = {
        'low_risk': {
            'debt_to_income': random.uniform(0.10, 0.25),
            'late_payment_count': 0,
            'credit_utilization': random.uniform(0.10, 0.30),
            'existing_loans': random.randint(0, 1),
            'previous_defaults': 0,
            'savings_balance': random.randint(200000, 500000),
        },
        'medium_risk': {
            'debt_to_income': random.uniform(0.25, 0.40),
            'late_payment_count': random.randint(0, 1),
            'credit_utilization': random.uniform(0.30, 0.50),
            'existing_loans': random.randint(1, 2),
            'previous_defaults': 0,
            'savings_balance': random.randint(100000, 300000),
        },
        'high_risk': {
            'debt_to_income': random.uniform(0.40, 0.70),
            'late_payment_count': random.randint(1, 3),
            'credit_utilization': random.uniform(0.50, 0.90),
            'existing_loans': random.randint(2, 5),
            'previous_defaults': random.randint(0, 2),
            'savings_balance': random.randint(10000, 150000),
        }
    }
    
    profile_type = random.choice(['low_risk', 'medium_risk', 'high_risk'])
    profile = risk_profiles[profile_type]
    
    application = {
        'monthly_income': random.choice(income_levels),
        'employment_years': random.randint(1, 15),
        'employment_type': random.choice(['permanent', 'contract', 'self_employed']),
        'debt_to_income': profile['debt_to_income'],
        'existing_loans': profile['existing_loans'],
        'late_payment_count': profile['late_payment_count'],
        'credit_utilization': profile['credit_utilization'],
        'requested_amount': random.choice([100000, 200000, 300000, 500000, 1000000]),
        'loan_purpose': random.choice(['car', 'home', 'education', 'business', 'personal']),
        'age': random.randint(25, 60),
        'education_level': random.choice(['high_school', 'bachelor', 'master', 'phd']),
        'marital_status': random.choice(['single', 'married', 'divorced', 'widowed']),
        'dependents': random.randint(0, 4),
        'home_ownership': random.choice(['own', 'mortgage', 'rent', 'family']),
        'savings_balance': profile['savings_balance'],
        'checking_balance': random.randint(10000, 100000),
        'credit_history_length': random.randint(1, 20),
        'previous_defaults': profile['previous_defaults']
    }
    
    return application

def format_input(application, decision_result):
    """Format application data as input text"""
    
    decision = decision_result['final_decision']
    ml_score = decision_result['ml_result']['ml_score']
    risk_level = decision_result['ml_result']['ml_risk_level']
    
    input_text = f"""ข้อมูลคำขอสินเชื่อ:
- รายได้ต่อเดือน: {application['monthly_income']:,} บาท
- อายุงาน: {application['employment_years']} ปี
- อัตราหนี้ต่อรายได้: {application['debt_to_income']:.2%}
- สินเชื่อเดิม: {application['existing_loans']} รายการ
- ชำระล่าช้า: {application['late_payment_count']} ครั้ง
- วงเงินที่ขอ: {application['requested_amount']:,} บาท
- เงินออม: {application['savings_balance']:,} บาท

ผลการประเมิน:
- การตัดสินใจ: {decision}
- คะแนน ML: {ml_score:.1%}
- ระดับความเสี่ยง: {risk_level}"""
    
    return input_text

def create_natural_explanation(explanation_data, style='formal'):
    """Create natural Thai explanation from structured data"""
    
    summary = explanation_data.get('summary', '')
    reasons = explanation_data.get('reasons', [])
    recommendations = explanation_data.get('recommendations', [])
    
    # Start with summary
    output = summary
    
    # Add reasons if available
    if reasons:
        output += "\n\nเหตุผลสำคัญ:\n"
        for i, reason in enumerate(reasons[:3], 1):
            output += f"{i}. {reason.get('reason', '')}\n"
    
    # Add recommendations if available
    if recommendations:
        output += "\nคำแนะนำ:\n"
        for i, rec in enumerate(recommendations[:3], 1):
            output += f"{i}. {rec}\n"
    
    return output.strip()

def generate_training_dataset(num_examples=500):
    """Generate training dataset for LLM fine-tuning"""
    
    print(f"Generating {num_examples} training examples...")
    
    # Initialize engines
    decision_engine = DecisionEngine()
    explanation_engine = ExplanationEngine()
    
    dataset = []
    
    for i in range(num_examples):
        if (i + 1) % 50 == 0:
            print(f"Generated {i + 1}/{num_examples} examples...")
        
        # Generate application
        application = generate_varied_application()
        
        # Get decision
        decision_result = decision_engine.make_decision(application)
        
        # Get explanation (vary styles)
        style = random.choice(['formal', 'advisory', 'short'])
        explanation = explanation_engine.generate_explanation(
            decision_result,
            application,
            language='th',
            style=style
        )
        
        # Format input
        input_text = format_input(application, decision_result)
        
        # Create natural output
        output_text = create_natural_explanation(explanation, style)
        
        # Add to dataset
        dataset.append({
            'input': input_text,
            'output': output_text,
            'metadata': {
                'decision': decision_result['final_decision'],
                'ml_score': decision_result['ml_result']['ml_score'],
                'risk_level': decision_result['ml_result']['ml_risk_level'],
                'style': style
            }
        })
    
    return dataset

def save_dataset(dataset, output_path):
    """Save dataset to JSON file"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset saved to: {output_file}")
    print(f"  Total examples: {len(dataset)}")
    
    # Statistics
    approved = sum(1 for d in dataset if d['metadata']['decision'] == 'approved')
    rejected = len(dataset) - approved
    
    print(f"  Approved: {approved} ({approved/len(dataset)*100:.1f}%)")
    print(f"  Rejected: {rejected} ({rejected/len(dataset)*100:.1f}%)")
    
    # Style distribution
    styles = {}
    for d in dataset:
        style = d['metadata']['style']
        styles[style] = styles.get(style, 0) + 1
    
    print(f"\n  Style distribution:")
    for style, count in styles.items():
        print(f"    {style}: {count} ({count/len(dataset)*100:.1f}%)")

def split_dataset(dataset, train_ratio=0.8):
    """Split dataset into train and test sets"""
    
    random.shuffle(dataset)
    split_idx = int(len(dataset) * train_ratio)
    
    train_set = dataset[:split_idx]
    test_set = dataset[split_idx:]
    
    return train_set, test_set

if __name__ == "__main__":
    print("="*60)
    print("LLM TRAINING DATASET GENERATION")
    print("="*60)
    
    # Generate dataset
    dataset = generate_training_dataset(num_examples=500)
    
    # Split into train/test
    train_set, test_set = split_dataset(dataset, train_ratio=0.8)
    
    # Save datasets
    data_dir = Path(__file__).parent.parent / 'data'
    save_dataset(train_set, data_dir / 'llm_train.json')
    save_dataset(test_set, data_dir / 'llm_test.json')
    
    # Show example
    print("\n" + "="*60)
    print("EXAMPLE TRAINING PAIR")
    print("="*60)
    
    example = random.choice(train_set)
    print("\nINPUT:")
    print(example['input'])
    print("\nOUTPUT:")
    print(example['output'])
    
    print("\n" + "="*60)
    print("DATASET GENERATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review data/llm_train.json and data/llm_test.json")
    print("2. Use these files in Google Colab for fine-tuning")
    print("3. Fine-tune Phi-3-mini or Gemma-2B with LoRA")
