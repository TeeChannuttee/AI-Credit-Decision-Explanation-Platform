# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Generate Data (1 min)

```bash
python scripts\generate_credit_data.py
```

Expected output: `✅ Dataset saved to: data\credit_dataset.csv`

### Step 3: Train Models (2 mins)

```bash
python ml\model_training.py
```

Expected output: 
- `✅ Model saved to: models\credit_model_v1.0.0.pkl`
- `AUC-ROC: 0.901` (Logistic Regression)
- `AUC-ROC: 0.950` (XGBoost)

### Step 4: Test Decision Engine (30 sec)

```bash
python engine\decision_engine.py
```

Expected output: Decision with confidence score and triggered rules

### Step 5: Start API Server (30 sec)

```bash
uvicorn backend.main:app --reload
```

Then visit: **http://localhost:8000/docs** for interactive API documentation

---

## 📝 Quick API Test

### Using Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/decision`
3. Click "Try it out"
4. Use the example below
5. Click "Execute"

### Example Request

```json
{
  "application": {
    "monthly_income": 50000,
    "employment_years": 5,
    "employment_type": "permanent",
    "debt_to_income": 0.30,
    "existing_loans": 1,
    "late_payment_count": 0,
    "credit_utilization": 0.35,
    "requested_amount": 300000,
    "loan_purpose": "car",
    "age": 35,
    "education_level": "bachelor",
    "marital_status": "married",
    "dependents": 2,
    "home_ownership": "own",
    "savings_balance": 250000,
    "checking_balance": 50000,
    "credit_history_length": 8,
    "previous_defaults": 0
  },
  "language": "th",
  "explanation_style": "formal"
}
```

### Expected Response

```json
{
  "application_id": "APP20260119...",
  "decision": "approved",
  "confidence": 0.85,
  "ml_score": 0.82,
  "risk_level": "low",
  "explanation": {
    "summary": "คำขอสินเชื่อได้รับการอนุมัติตามเกณฑ์การประเมินความเสี่ยง",
    "reasons": [...],
    "ml_insights": {...}
  }
}
```

---

## 🎯 What You Get

✅ **2,000 synthetic credit applications**  
✅ **2 trained ML models** (Logistic Regression + XGBoost)  
✅ **30 business rules** in Thai and English  
✅ **REST API** with 8 endpoints  
✅ **Complete explanations** for every decision  
✅ **SHAP values** for feature importance  
✅ **Policy citations** for compliance  

---

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Read [WALKTHROUGH.md](WALKTHROUGH.md) for detailed guide
- Explore [docs/](docs/) for architecture and schemas
- Check [models/](models/) for trained models

---

## 🆘 Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**Model not found?**
```bash
python ml\model_training.py
```

**Data not found?**
```bash
python scripts\generate_credit_data.py
```

**API won't start?**
```bash
pip install fastapi uvicorn
uvicorn backend.main:app --reload
```

---

**Time to complete**: ~5 minutes  
**Difficulty**: Beginner-friendly  
**Requirements**: Python 3.11+
