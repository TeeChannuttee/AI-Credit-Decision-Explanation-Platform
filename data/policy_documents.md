# Credit Policy Manual

**Version**: 1.0  
**Effective Date**: January 2026  
**Classification**: Internal Use Only

---

## Section 1: General Lending Principles

### 1.1 Lending Philosophy

Our institution's lending philosophy is built on three core pillars:

1. **Responsible Lending**: We provide credit to customers who demonstrate the ability and willingness to repay
2. **Risk-Based Pricing**: Interest rates and terms reflect the assessed risk level
3. **Transparency**: All decisions are explainable and based on documented criteria

### 1.2 Risk Appetite

The bank maintains a moderate risk appetite with the following parameters:

- **Target Default Rate**: < 3% annually
- **Maximum Portfolio DTI**: 45% average
- **Minimum Credit Score**: 600 (internal scale)
- **Geographic Diversification**: No single region > 30% of portfolio

### 1.3 Regulatory Compliance

All lending activities comply with:
- Bank of Thailand regulations
- Consumer Protection Act B.E. 2522
- Personal Data Protection Act B.E. 2562
- Anti-Money Laundering regulations

---

## Section 2: Eligibility Criteria

### 2.1 Minimum Requirements

#### 2.1.1 Income Requirements

**Minimum Monthly Income**: 20,000 THB (gross)

**Rationale**: This threshold ensures basic repayment capacity while accounting for living expenses in Thailand. Based on 2025 cost of living analysis, this allows for debt service while maintaining minimum quality of life.

**Income Verification**:
- Salaried employees: 3 months payslips + employment letter
- Self-employed: 2 years tax returns + bank statements
- Contract workers: Contract copy + 6 months bank statements

**Income Calculation**:
- Base salary: 100% counted
- Regular allowances: 100% counted
- Overtime: 50% counted (if consistent for 12+ months)
- Bonuses: 0% counted (too variable)
- Rental income: 70% counted (net of expenses)

#### 2.1.2 High Income Applicants

**Income > 100,000 THB/month**

Benefits:
- Expedited processing
- Higher loan amounts (up to 15x monthly income)
- Preferential interest rates
- Flexible collateral requirements

### 2.2 Employment Requirements

#### 2.2.1 Employment Stability Requirements

**Minimum Employment Duration**:
- Permanent employees: 6 months current employer
- Contract employees: 1 year current employer
- Self-employed: 2 years in business

**Employment History < 1 Year**:
- Triggers manual review
- May require additional income verification
- Co-borrower or guarantor may be required
- Loan amount may be reduced

**Rationale**: Employment stability is a strong predictor of repayment ability. Short tenure increases income volatility risk.

#### 2.2.2 Contract Employment Guidelines

Contract employees face higher income uncertainty. Additional requirements:

- **Tenure < 2 years**: Provide contract renewal history or letter of intent from employer
- **Contract expiry within loan term**: Demonstrate alternative income source or renewal probability
- **Multiple short contracts**: May be treated as self-employed

#### 2.2.3 Self-Employment Verification

Self-employed applicants require enhanced due diligence:

**Business History < 3 Years**:
- Provide business plan
- 2 years audited financial statements
- Business registration documents
- Major client contracts (if applicable)
- Higher interest rate (+ 0.5-1.0%)

**Business History ≥ 3 Years**:
- Standard documentation
- Average income over 2 years
- Seasonal businesses: use lowest quarterly income

#### 2.2.4 Long-term Employment Benefits

**Permanent Employment ≥ 10 Years**:
- Demonstrates exceptional stability
- Reduced default risk
- Eligible for:
  - Interest rate discount (-0.25%)
  - Higher loan-to-income ratio
  - Faster approval process

### 2.3 Age Requirements

#### 2.3.1 Age-Based Risk Assessment

**Minimum Age**: 20 years (legal capacity)
**Maximum Age at Loan Maturity**: 65 years

**Applicants < 25 Years**:
- Limited credit history typical
- Higher income volatility (early career)
- **Large loans (> 300,000 THB)**: Require co-borrower or guarantor
- Maximum loan term: 5 years

**Rationale**: Young applicants have less established careers and credit history, increasing repayment uncertainty.

#### 2.3.2 Senior Applicant Guidelines

**Applicants > 60 Years**:
- Retirement income verification required
- **Large loans (> 1,000,000 THB)**: 
  - Verify pension/retirement income
  - Maximum loan term: Age 70 minus current age
  - May require life insurance assignment

**Rationale**: Ensure loan maturity before retirement or significant income reduction.

### 2.4 Education Level

#### 2.4.1 Education-Income Correlation

While not a direct criterion, education correlates with income stability:

**Advanced Degree (Master/PhD) + High Income (> 80,000 THB)**:
- Positive risk indicator
- Reflects specialized skills and career investment
- Lower default rates historically

**Note**: Education alone is not sufficient; must be combined with income and employment stability.

### 2.5 Dependent Impact

#### 2.5.1 Dependent Impact Assessment

**Many Dependents (≥ 4) + Income < 60,000 THB**:
- Triggers review
- Higher living expenses reduce disposable income
- May require:
  - Reduced loan amount
  - Co-borrower income
  - Proof of additional support (e.g., spouse income)

**Calculation**: Assume 5,000 THB/month per dependent for living expenses.

---

## Section 3: Risk Assessment

### 3.1 Credit Scoring

Our proprietary credit scoring model combines:
- **ML Model**: Logistic Regression / XGBoost (70% weight)
- **Business Rules**: Policy-based overrides (30% weight)
- **External Data**: Credit bureau score (if available)

**Score Range**: 0-100
- 0-30: Low risk (auto-approve if no rule violations)
- 31-70: Medium risk (manual review)
- 71-100: High risk (likely reject)

### 3.2 Debt Service Ratios

#### 3.2.1 Maximum Debt-to-Income Ratio

**Maximum DTI**: 65%

**Calculation**:
```
DTI = (Total Monthly Debt Payments) / (Gross Monthly Income)
```

**Total Monthly Debt Payments includes**:
- Existing loan installments
- Credit card minimum payments (3% of outstanding balance)
- Proposed new loan installment

**DTI > 65%**: Automatic rejection (non-overridable)

**Rationale**: DTI > 65% leaves insufficient income for living expenses, dramatically increasing default risk. Based on 10 years of portfolio analysis showing default rate > 15% above this threshold.

#### 3.2.2 Elevated DTI Guidelines

**DTI 45-65%**: Elevated risk zone
- Triggers manual review
- Loan amount may be reduced
- Higher interest rate may apply
- Require proof of:
  - Stable employment (> 2 years)
  - Emergency savings (≥ 3 months expenses)
  - No recent late payments

#### 3.2.3 Optimal DTI Standards

**DTI < 30%**: Optimal range
- Indicates strong financial health
- Sufficient buffer for unexpected expenses
- Historically < 1% default rate
- Eligible for best rates and terms

### 3.3 Credit Utilization

#### 3.3.1 Acceptable Levels

Credit utilization = (Total Credit Used) / (Total Credit Limit)

**Optimal**: < 30%
**Acceptable**: 30-50%
**Concerning**: 50-80%
**High Risk**: > 80%

#### 3.3.2 Credit Utilization Standards

**Utilization > 80%**: High risk indicator
- Suggests financial stress
- May indicate over-reliance on credit
- Triggers manual review
- May require:
  - Explanation letter
  - Plan to reduce utilization
  - Reduced loan amount

**Rationale**: High utilization correlates with financial distress and increased default probability.

#### 3.3.3 Optimal Credit Usage

**Utilization < 30% + Credit History ≥ 3 years**:
- Demonstrates responsible credit management
- Strong positive indicator
- Reflects financial discipline
- Eligible for preferential terms

#### 3.3.4 Moderate Utilization Guidelines

**Utilization 50-80%**:
- Borderline acceptable
- Monitor for increasing trend
- Recommend customer reduce usage
- May approve with conditions

### 3.4 Multiple Loans

#### 3.4.1 Multiple Loan Assessment

**Existing Loans > 4**:
- Indicates complex debt structure
- Higher administrative burden for borrower
- Increased risk of missed payments
- Triggers review

**Recommendation**: Debt consolidation
- Simplifies repayment
- May reduce total interest
- Improves cash flow management

### 3.5 Credit History

#### 3.5.1 Credit History Length Standards

**Credit History < 2 Years**:
- Limited track record
- Higher uncertainty
- May require:
  - Co-borrower with longer history
  - Additional documentation
  - Conservative loan amount

**Credit History ≥ 5 Years**:
- Sufficient track record
- Reliable predictor of behavior
- Preferred applicant profile

### 3.6 Savings and Liquidity

#### 3.6.1 Savings Requirements for Large Loans

**Large Loan (> 500,000 THB) + Savings < 3x Monthly Income**:
- Insufficient emergency buffer
- Risk of default if income disruption
- May require:
  - Reduced loan amount
  - Collateral
  - Life/income insurance

**Recommended Savings**: 6 months expenses minimum

#### 3.6.2 Liquidity Requirements

**Low Checking Balance (< 0.5x Monthly Income) + Large Loan**:
- Poor cash flow management indicator
- May struggle with installment timing
- Triggers review

**Optimal**: Checking balance ≥ 1x monthly income

### 3.7 Asset Ownership

#### 3.7.1 Asset-Based Advantages

**Home Ownership + Savings > 6x Monthly Income**:
- Strong financial security
- Collateral available if needed
- Lower default risk
- Eligible for:
  - Larger loan amounts
  - Better interest rates
  - Flexible terms

#### 3.7.2 Housing Status Risk Assessment

**Renter + Large Loan (> 1,000,000 THB)**:
- No asset base
- Higher financial vulnerability
- May require:
  - Collateral (vehicle, investments)
  - Guarantor
  - Higher down payment
  - Reduced loan amount

---

## Section 4: Payment History

### 4.1 Late Payment Evaluation

#### 4.1.1 Payment History Importance

Payment history is the single strongest predictor of future payment behavior.

**Evaluation Period**: 24 months
**Data Sources**: 
- Internal records
- Credit bureau reports
- Utility payment history (if available)

#### 4.1.2 Minor Payment Issues

**1 Late Payment**:
- Low severity
- May be isolated incident
- Triggers review
- Require explanation
- No automatic rejection

**Mitigation**:
- Maintain perfect record for 6+ months
- Provide explanation (medical emergency, etc.)
- Demonstrate improved financial management

#### 4.1.3 Late Payment Evaluation Criteria

**3+ Late Payments in 24 Months**:
- High severity
- Strong default predictor
- **Automatic rejection** (overridable by senior officer)

**Override Criteria**:
- All late payments > 18 months ago
- Perfect payment record since
- Documented extenuating circumstances
- Significant income increase
- Senior credit officer approval required

**Rationale**: Pattern of late payments indicates chronic cash flow issues or poor financial discipline.

### 4.2 Excellent Payment History

#### 4.2.1 Excellent Payment History

**No Late Payments + Credit History ≥ 5 Years**:
- Exceptional track record
- Lowest default risk category
- Eligible for:
  - Premium interest rates
  - Highest loan amounts
  - Expedited processing
  - Flexible terms

---

## Section 5: Default and Delinquency

### 5.1 Previous Defaults

#### 5.1.1 Default Impact Assessment

**Any Previous Default**: Automatic rejection (non-overridable)

**Definition of Default**:
- 90+ days past due
- Charge-off
- Repossession
- Foreclosure
- Bankruptcy
- Debt settlement < 100%

**Waiting Period**: 24 months minimum from default resolution

**Rationale**: Default indicates fundamental inability or unwillingness to honor obligations. Historical data shows 40%+ re-default rate within 24 months.

**Post-Waiting Period Requirements**:
- All defaulted debts fully paid
- 24 months perfect payment history
- Explanation letter
- Proof of income stability
- Higher interest rate (+2-3%)
- Lower loan amount (max 5x monthly income)
- Collateral required

---

## Section 6: Loan Amounts and Terms

### 6.1 Maximum Loan Amounts

#### 6.1.1 General Loan Limits

**Personal Loans**: 10,000 - 5,000,000 THB

**Income-Based Limits**:
- Standard: Up to 8x monthly income
- High income (> 100,000): Up to 15x monthly income
- Excellent credit: Up to 12x monthly income

#### 6.1.2 Maximum Loan Amount Guidelines

**Requested Amount > 10x Monthly Income**:
- Exceeds prudent lending limits
- High risk of over-leverage
- **Rejection** (overridable)

**Override Criteria**:
- Significant assets (> loan amount)
- Multiple income sources
- Exceptional credit history
- Collateral provided
- Business purpose with solid plan

### 6.2 Loan Purpose

#### 6.2.1 Business Loan Requirements

**Business Loan + Self-Employed + Experience < 5 Years**:
- High risk combination
- Requires:
  - Detailed business plan
  - 3 years financial statements
  - Industry analysis
  - Major contracts/purchase orders
  - Personal guarantee
  - Business asset collateral

**Approval Rate**: ~30% (vs 60% for personal loans)

---

## Section 7: Approval Criteria

### 7.1 Premium Applicants

#### 7.1.1 Premium Applicant Criteria

**Excellent Overall Profile**:
- DTI < 25%
- No late payments
- Income > 60,000 THB
- Credit utilization < 30%

**Benefits**:
- Auto-approval (up to 2M THB)
- Best interest rates (-0.5% from standard)
- Flexible terms
- Dedicated relationship manager
- Annual credit limit review

**Target Segment**: Top 15% of applicants

---

## Section 8: Override Procedures

### 8.1 Officer Override Authority

**Credit Officers** may override:
- Medium severity rules
- Low severity rules
- Some high severity rules (with justification)

**Cannot Override**:
- Critical rules (DTI > 65%, previous defaults, minimum income)
- Regulatory requirements
- Fraud indicators

### 8.2 Documentation Requirements

All overrides must include:
1. **Reason Code**: Specific justification category
2. **Written Explanation**: Detailed rationale (minimum 100 characters)
3. **Supporting Evidence**: Documents justifying override
4. **Risk Mitigation**: How risk will be managed
5. **Officer ID**: Accountability trail

### 8.3 Approval Hierarchy

**Override Authority Levels**:
- **Junior Officer**: Low severity only, < 500K THB
- **Senior Officer**: Low + Medium severity, < 2M THB
- **Credit Manager**: Low + Medium + some High, < 5M THB
- **Chief Credit Officer**: All overridable rules, any amount

**Audit**: All overrides reviewed quarterly for patterns and outcomes

---

## Section 9: Model Governance

### 9.1 Model Validation

ML models are validated:
- **Annually**: Full revalidation
- **Quarterly**: Performance monitoring
- **Monthly**: Drift detection

**Validation Criteria**:
- AUC > 0.75
- Precision > 70%
- Recall > 65%
- Demographic parity < 10% difference

### 9.2 Model Updates

Models may be updated when:
- Performance degrades below thresholds
- Significant market changes
- Regulatory requirements change
- New data sources available

**Approval Required**: Chief Risk Officer + Chief Credit Officer

### 9.3 Explainability Requirements

Every decision must include:
- Primary reason (rule or score)
- Contributing factors (top 3-5)
- Policy citations
- Recommendations for improvement
- Available in Thai and English

---

## Appendix A: Glossary

**DTI (Debt-to-Income Ratio)**: Total monthly debt payments divided by gross monthly income

**Credit Utilization**: Total credit used divided by total credit limit

**Default**: Failure to repay loan resulting in charge-off, 90+ days delinquency, or bankruptcy

**Late Payment**: Payment received > 30 days after due date

**Override**: Manual approval of application that would otherwise be rejected by automated rules

---

**Document Control**:
- **Version**: 1.0
- **Approved By**: Chief Credit Officer
- **Next Review**: July 2026
- **Distribution**: Credit Officers, Risk Management, Compliance
