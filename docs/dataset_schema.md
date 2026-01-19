# Dataset Schema Design

## Overview

This document defines the structure of all datasets used in the AI Credit Decision Explanation Platform. All data is **100% synthetic** to ensure privacy and safety.

## 1. Credit Scoring Dataset

### Purpose
Primary dataset for training ML models and making credit decisions.

### File Location
`data/credit_dataset.csv`

### Schema

| Field Name | Data Type | Range/Format | Description | Example |
|------------|-----------|--------------|-------------|---------|
| `application_id` | String | UUID | Unique identifier for each application | `a1b2c3d4-e5f6-...` |
| `monthly_income` | Float | 15,000 - 500,000 THB | Gross monthly income | 45,000.00 |
| `employment_years` | Integer | 0 - 40 years | Years in current employment | 5 |
| `employment_type` | String | Enum | Type of employment | `permanent`, `contract`, `self_employed` |
| `debt_to_income` | Float | 0.0 - 2.0 | Total debt / monthly income ratio | 0.35 |
| `existing_loans` | Integer | 0 - 10 | Number of existing loans | 2 |
| `late_payment_count` | Integer | 0 - 20 | Late payments in last 24 months | 1 |
| `credit_utilization` | Float | 0.0 - 1.5 | Credit used / credit limit | 0.45 |
| `requested_amount` | Float | 10,000 - 5,000,000 THB | Loan amount requested | 300,000.00 |
| `loan_purpose` | String | Enum | Purpose of loan | `home`, `car`, `education`, `business`, `personal` |
| `age` | Integer | 20 - 70 years | Applicant age | 35 |
| `education_level` | String | Enum | Highest education | `high_school`, `bachelor`, `master`, `phd` |
| `marital_status` | String | Enum | Marital status | `single`, `married`, `divorced`, `widowed` |
| `dependents` | Integer | 0 - 8 | Number of dependents | 2 |
| `home_ownership` | String | Enum | Housing status | `own`, `rent`, `mortgage`, `family` |
| `savings_balance` | Float | 0 - 10,000,000 THB | Total savings | 150,000.00 |
| `checking_balance` | Float | 0 - 1,000,000 THB | Checking account balance | 25,000.00 |
| `credit_history_length` | Integer | 0 - 50 years | Years of credit history | 8 |
| `previous_defaults` | Integer | 0 - 5 | Number of previous defaults | 0 |
| `decision` | String | Enum | Approval decision (target) | `approved`, `rejected` |
| `risk_level` | String | Enum | Risk classification | `low`, `medium`, `high` |

### Data Distribution Guidelines

**Income Distribution** (Log-normal)
- Mean: 50,000 THB
- Median: 40,000 THB
- Std Dev: 25,000 THB

**DTI Distribution**
- Low Risk (< 0.35): 40%
- Medium Risk (0.35 - 0.65): 40%
- High Risk (> 0.65): 20%

**Decision Distribution**
- Approved: 60-65%
- Rejected: 35-40%

### Data Quality Rules

- No missing values in required fields
- All numeric values within specified ranges
- Correlations must be realistic (e.g., higher income → lower DTI)
- Temporal consistency (employment_years ≤ age - 18)

---

## 2. Explanation Rules Dataset

### Purpose
Mapping of business rules to human-readable explanations for credit decisions.

### File Location
`data/explanation_rules.json`

### Schema

```json
{
  "rules": [
    {
      "rule_id": "string",
      "rule_name": "string",
      "condition": "string (Python expression)",
      "severity": "string (critical|high|medium|low)",
      "action": "string (approve|reject|review)",
      "reason_th": "string (Thai explanation)",
      "reason_en": "string (English explanation)",
      "recommendation_th": "string (Thai advice)",
      "recommendation_en": "string (English advice)",
      "policy_reference": "string (policy section)",
      "override_allowed": "boolean"
    }
  ]
}
```

### Example Rules

```json
{
  "rules": [
    {
      "rule_id": "R001",
      "rule_name": "High DTI Rejection",
      "condition": "debt_to_income > 0.65",
      "severity": "critical",
      "action": "reject",
      "reason_th": "อัตราส่วนหนี้สินต่อรายได้สูงเกินกว่าเกณฑ์ที่กำหนด (> 65%)",
      "reason_en": "Debt-to-income ratio exceeds acceptable threshold (> 65%)",
      "recommendation_th": "ควรลดภาระหนี้สินหรือเพิ่มรายได้ก่อนยื่นกู้ใหม่",
      "recommendation_en": "Consider reducing existing debt or increasing income before reapplying",
      "policy_reference": "Credit Policy Section 3.2.1",
      "override_allowed": false
    },
    {
      "rule_id": "R002",
      "rule_name": "Multiple Late Payments",
      "condition": "late_payment_count >= 3",
      "severity": "high",
      "action": "reject",
      "reason_th": "ประวัติการชำระหนี้ล่าช้า 3 ครั้งขึ้นไปในช่วง 24 เดือนที่ผ่านมา",
      "reason_en": "History of 3 or more late payments in the past 24 months",
      "recommendation_th": "สร้างประวัติการชำระหนี้ที่ดีอย่างน้อย 12 เดือนก่อนยื่นกู้ใหม่",
      "recommendation_en": "Establish good payment history for at least 12 months before reapplying",
      "policy_reference": "Credit Policy Section 4.1.3",
      "override_allowed": true
    },
    {
      "rule_id": "R003",
      "rule_name": "Low Income Threshold",
      "condition": "monthly_income < 20000",
      "severity": "high",
      "action": "reject",
      "reason_th": "รายได้ต่ำกว่าเกณฑ์ขั้นต่ำ (< 20,000 บาท/เดือน)",
      "reason_en": "Income below minimum threshold (< 20,000 THB/month)",
      "recommendation_th": "เพิ่มรายได้หรือพิจารณาวงเงินกู้ที่ต่ำกว่า",
      "recommendation_en": "Increase income or consider a lower loan amount",
      "policy_reference": "Credit Policy Section 2.1.1",
      "override_allowed": false
    },
    {
      "rule_id": "R004",
      "rule_name": "High Credit Utilization",
      "condition": "credit_utilization > 0.80",
      "severity": "medium",
      "action": "review",
      "reason_th": "อัตราการใช้วงเงินสูง (> 80%)",
      "reason_en": "High credit utilization (> 80%)",
      "recommendation_th": "ลดการใช้วงเงินเครดิตลงต่ำกว่า 50%",
      "recommendation_en": "Reduce credit utilization below 50%",
      "policy_reference": "Credit Policy Section 3.3.2",
      "override_allowed": true
    },
    {
      "rule_id": "R005",
      "rule_name": "Previous Default",
      "condition": "previous_defaults > 0",
      "severity": "critical",
      "action": "reject",
      "reason_th": "มีประวัติผิดนัดชำระหนี้",
      "reason_en": "History of loan default",
      "recommendation_th": "ชำระหนี้ค้างทั้งหมดและรอ 24 เดือนก่อนยื่นกู้ใหม่",
      "recommendation_en": "Clear all outstanding debts and wait 24 months before reapplying",
      "policy_reference": "Credit Policy Section 5.1.1",
      "override_allowed": false
    }
  ]
}
```

### Rule Categories

1. **Critical Rules** (cannot override): DTI > 0.65, previous defaults, fraud indicators
2. **High Severity** (officer can override): Late payments, low income
3. **Medium Severity** (auto-review): High utilization, short credit history
4. **Low Severity** (informational): Minor risk factors

---

## 3. Policy Documents Dataset

### Purpose
Knowledge base for RAG (Retrieval-Augmented Generation) to cite policies in explanations.

### File Location
`data/policy_documents.md`

### Structure

```markdown
# Credit Policy Manual

## Section 1: General Lending Principles
### 1.1 Lending Philosophy
[Content about bank's approach to lending...]

### 1.2 Risk Appetite
[Content about acceptable risk levels...]

## Section 2: Eligibility Criteria
### 2.1 Minimum Requirements
### 2.1.1 Income Requirements
- Minimum monthly income: 20,000 THB
- Income verification required
- Stable employment preferred

### 2.2 Age Requirements
- Minimum age: 20 years
- Maximum age at loan maturity: 65 years

## Section 3: Risk Assessment
### 3.1 Credit Scoring
### 3.2 Debt Service Ratios
### 3.2.1 Debt-to-Income (DTI)
- Maximum DTI: 65%
- Preferred DTI: < 35%
- Calculation: Total monthly debt / Gross monthly income

### 3.3 Credit Utilization
### 3.3.1 Acceptable Levels
- Optimal: < 30%
- Acceptable: 30-50%
- High Risk: > 80%

## Section 4: Payment History
### 4.1 Late Payment Evaluation
### 4.1.3 Rejection Criteria
- 3+ late payments in 24 months: Automatic rejection
- 1-2 late payments: Manual review required

## Section 5: Default and Delinquency
### 5.1 Previous Defaults
### 5.1.1 Default Impact
- Any previous default: 24-month waiting period
- Multiple defaults: Permanent rejection

## Section 6: Loan Amounts and Terms
### 6.1 Maximum Loan Amounts
- Personal loans: Up to 5,000,000 THB
- Based on income multiple (max 10x monthly income)

## Section 7: Override Procedures
### 7.1 Officer Override Authority
### 7.2 Documentation Requirements
### 7.3 Approval Hierarchy
```

### Content Requirements

- 10-20 pages of detailed policies
- Numbered sections for easy citation
- Clear thresholds and criteria
- Rationale for each policy
- Examples and edge cases

---

## 4. Audit Log Schema

### Purpose
Comprehensive logging of all decisions for compliance and debugging.

### Database Table
`audit_logs`

### Schema

| Field Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| `log_id` | UUID | No | Unique log entry ID |
| `application_id` | UUID | No | Reference to application |
| `timestamp` | DateTime | No | Decision timestamp (UTC) |
| `model_version` | String | No | ML model version used |
| `rule_version` | String | No | Rule set version used |
| `input_data` | JSON | No | All input features |
| `ml_score` | Float | No | Raw ML prediction score |
| `ml_risk_level` | String | No | ML risk classification |
| `triggered_rules` | JSON | No | List of rules that fired |
| `final_decision` | String | No | Approved/Rejected |
| `decision_reason` | String | No | Primary reason code |
| `explanation_text` | JSON | No | Full explanation (TH/EN) |
| `officer_id` | UUID | Yes | Officer who reviewed (if manual) |
| `override_applied` | Boolean | No | Was decision overridden |
| `override_reason` | String | Yes | Justification for override |
| `processing_time_ms` | Integer | No | Decision latency |
| `feature_importance` | JSON | No | SHAP values for this prediction |
| `policy_citations` | JSON | Yes | Referenced policy sections |

### Retention Policy

- Minimum retention: 7 years (regulatory requirement)
- Archived after 2 years to cold storage
- Anonymized after 10 years

---

## 5. Model Metadata Schema

### Purpose
Track model versions, performance metrics, and training details.

### File Location
`models/model_metadata.json`

### Schema

```json
{
  "model_id": "string (UUID)",
  "model_version": "string (semantic version)",
  "model_type": "string (logistic_regression|xgboost)",
  "training_date": "datetime (ISO 8601)",
  "training_data_size": "integer",
  "features_used": ["array of feature names"],
  "hyperparameters": {
    "param_name": "value"
  },
  "performance_metrics": {
    "accuracy": "float",
    "precision": "float",
    "recall": "float",
    "f1_score": "float",
    "auc_roc": "float",
    "confusion_matrix": [[int]]
  },
  "feature_importance": {
    "feature_name": "float (importance score)"
  },
  "validation_method": "string (k-fold, holdout)",
  "deployment_date": "datetime",
  "deployment_status": "string (active|deprecated|archived)",
  "notes": "string"
}
```

---

## Data Generation Strategy

### Synthetic Data Requirements

1. **Realism**: Distributions must match real-world credit data patterns
2. **Correlations**: Maintain realistic feature relationships
   - Higher income → Lower DTI
   - Longer employment → Higher approval rate
   - More late payments → Higher rejection rate

3. **Diversity**: Include edge cases and boundary conditions
4. **Balance**: Avoid extreme class imbalance (aim for 60/40 split)

### Quality Checks

- [ ] No missing values in required fields
- [ ] All values within valid ranges
- [ ] Realistic correlations between features
- [ ] Sufficient samples for each risk category
- [ ] Balanced representation across demographics
- [ ] Edge cases included (very high income, very low DTI, etc.)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-19  
**Status**: Ready for Implementation
