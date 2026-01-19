# Testing Guide

## 🧪 Complete Testing Instructions

### Quick Test (5 minutes)

```bash
# 1. Test Data Generation
python scripts\generate_credit_data.py
# Expected: ✅ Dataset saved to: data\credit_dataset.csv

# 2. Test ML Training
python ml\model_training.py
# Expected: ✅ Model saved, AUC 0.901 (LR), 0.950 (XGB)

# 3. Test Decision Engine
python engine\decision_engine.py
# Expected: Decision output with confidence score

# 4. Test What-if Simulator
python engine\whatif_simulator.py
# Expected: Scenario simulations with impact analysis

# 5. Test RBAC
python backend\rbac.py
# Expected: Authentication and permission checks

# 6. Test Bias Detection
python monitoring\bias_detection.py
# Expected: Fairness analysis report

# 7. Test Model Monitoring
python monitoring\model_monitor.py
# Expected: Drift detection report
```

### Full System Test (10 minutes)

```bash
# Terminal 1: Start API
uvicorn backend.main:app --reload
# Expected: Server running on http://localhost:8000

# Terminal 2: Start Frontend
python frontend\serve.py
# Expected: Frontend running on http://localhost:3000

# Browser Test:
# 1. Go to http://localhost:3000
# 2. Click "Fill Example Data"
# 3. Click "Submit & Get Decision"
# 4. Verify results appear
# 5. Check "All Cases" tab
# 6. Visit http://localhost:8000/docs for API
```

### API Testing

```bash
# Health Check
curl http://localhost:8000/api/health

# Get Statistics
curl http://localhost:8000/api/stats

# Submit Decision (PowerShell)
$body = Get-Content example_application.json
Invoke-RestMethod -Uri http://localhost:8000/api/decision -Method Post -Body $body -ContentType "application/json"
```

### Expected Results

✅ **Data Generation**: 2,000 records, 54.9% approval  
✅ **ML Training**: AUC 0.901 (LR), 0.950 (XGB)  
✅ **Decision Engine**: Approved/Rejected with reasons  
✅ **What-if**: Scenario comparisons  
✅ **RBAC**: Authentication working  
✅ **Bias Detection**: Fairness metrics  
✅ **Monitoring**: Drift detection  
✅ **API**: All 8 endpoints functional  
✅ **Frontend**: Dashboard interactive  

---

## 🎯 Test Checklist

- [ ] Data generation works
- [ ] ML models train successfully
- [ ] Decision engine produces results
- [ ] What-if simulator runs
- [ ] RBAC authenticates users
- [ ] Bias detection analyzes fairness
- [ ] Monitoring detects drift
- [ ] API server starts
- [ ] Frontend dashboard loads
- [ ] Form submission works
- [ ] Results display correctly
- [ ] All cases list shows
- [ ] Swagger docs accessible

**All tests passed?** ✅ System is ready!
