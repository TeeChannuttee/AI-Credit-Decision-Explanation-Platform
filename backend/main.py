"""
FastAPI Backend for AI Credit Decision Explanation Platform

Endpoints:
- POST /api/applications - Submit new application
- POST /api/decision - Get credit decision with explanation
- GET /api/cases - List all cases
- GET /api/cases/{id} - Get case details
- GET /api/health - Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from engine.decision_engine import DecisionEngine
from engine.explanation_engine import ExplanationEngine
from engine.llm_enhancer import LLMEnhancer

# Initialize FastAPI
app = FastAPI(
    title="AI Credit Decision API",
    description="Explainable AI credit decision platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
decision_engine = DecisionEngine()
explanation_engine = ExplanationEngine()
llm_enhancer = LLMEnhancer()

# Pydantic models
class CreditApplication(BaseModel):
    """Credit application request"""
    application_id: Optional[str] = None
    monthly_income: float = Field(..., gt=0, description="Monthly income in THB")
    employment_years: int = Field(..., ge=0, description="Years in current employment")
    employment_type: str = Field(..., description="permanent, contract, or self_employed")
    debt_to_income: float = Field(..., ge=0, le=2, description="Debt-to-income ratio")
    existing_loans: int = Field(..., ge=0, description="Number of existing loans")
    late_payment_count: int = Field(..., ge=0, description="Late payments in last 24 months")
    credit_utilization: float = Field(..., ge=0, le=1.5, description="Credit utilization ratio")
    requested_amount: float = Field(..., gt=0, description="Requested loan amount in THB")
    loan_purpose: str = Field(..., description="home, car, education, business, or personal")
    age: int = Field(..., ge=20, le=70, description="Applicant age")
    education_level: str = Field(..., description="high_school, bachelor, master, or phd")
    marital_status: str = Field(..., description="single, married, divorced, or widowed")
    dependents: int = Field(..., ge=0, description="Number of dependents")
    home_ownership: str = Field(..., description="own, mortgage, rent, or family")
    savings_balance: float = Field(..., ge=0, description="Savings balance in THB")
    checking_balance: float = Field(..., ge=0, description="Checking balance in THB")
    credit_history_length: int = Field(..., ge=0, description="Years of credit history")
    previous_defaults: int = Field(..., ge=0, description="Number of previous defaults")

class DecisionRequest(BaseModel):
    """Decision request with options"""
    application: CreditApplication
    language: str = Field(default="th", description="th or en")
    explanation_style: str = Field(default="formal", description="short, formal, or advisory")
    include_shap: bool = Field(default=True, description="Include SHAP values")
    use_llm: bool = Field(default=False, description="Use fine-tuned LLM for explanation")

class DecisionResponse(BaseModel):
    """Decision response"""
    application_id: str
    decision: str
    confidence: float
    ml_score: float
    risk_level: str
    explanation: Dict
    timestamp: str

# In-memory storage (replace with database in production)
applications_db = {}
decisions_db = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Credit Decision API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True
    }

@app.post("/api/applications", response_model=Dict)
async def submit_application(application: CreditApplication):
    """
    Submit a new credit application
    
    Returns application ID for tracking
    """
    # Generate ID if not provided
    if not application.application_id:
        application.application_id = f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Store application
    applications_db[application.application_id] = {
        **application.dict(),
        "submitted_at": datetime.now().isoformat(),
        "status": "submitted"
    }
    
    return {
        "application_id": application.application_id,
        "status": "submitted",
        "message": "Application received successfully"
    }

@app.post("/api/decision", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """
    Make credit decision with explanation
    
    Returns complete decision with explanation
    """
    try:
        # Convert to dict
        app_data = request.application.dict()
        
        # Generate ID if needed
        if not app_data.get('application_id'):
            app_data['application_id'] = f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Make decision
        decision_result = decision_engine.make_decision(app_data)
        
        # Prepare features for SHAP
        X = None
        if request.include_shap:
            X = decision_engine.prepare_features(app_data)
        
        # Generate explanation
        explanation = explanation_engine.generate_explanation(
            decision_result,
            app_data,
            X,
            language=request.language,
            style=request.explanation_style
        )
        
        # Add LLM enhancement if requested
        if request.use_llm:
            llm_text = llm_enhancer.generate_explanation(app_data, decision_result)
            explanation['llm_explanation'] = llm_text
            # Optional: Overwrite summary with LLM text if desired
            # explanation['summary'] = llm_text
        
        # Store decision
        decision_id = app_data['application_id']
        decisions_db[decision_id] = {
            "decision_result": decision_result,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
        # Build response
        response = DecisionResponse(
            application_id=app_data['application_id'],
            decision=decision_result['final_decision'],
            confidence=decision_result['confidence'],
            ml_score=decision_result['ml_result']['ml_score'],
            risk_level=decision_result['ml_result']['ml_risk_level'],
            explanation=explanation,
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases")
async def list_cases(
    limit: int = 10,
    offset: int = 0,
    decision: Optional[str] = None
):
    """
    List all decided cases
    
    Query parameters:
    - limit: Number of results (default 10)
    - offset: Offset for pagination (default 0)
    - decision: Filter by decision (approved/rejected)
    """
    cases = list(decisions_db.values())
    
    # Filter by decision if specified
    if decision:
        cases = [c for c in cases if c['decision_result']['final_decision'] == decision]
    
    # Sort by timestamp (newest first)
    cases.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Paginate
    total = len(cases)
    cases = cases[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "cases": cases
    }

@app.get("/api/cases/{application_id}")
async def get_case(application_id: str):
    """
    Get specific case details
    
    Returns complete decision and explanation
    """
    if application_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return decisions_db[application_id]

@app.get("/api/applications/{application_id}")
async def get_application(application_id: str):
    """
    Get application details
    """
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return applications_db[application_id]

@app.get("/api/stats")
async def get_statistics():
    """
    Get platform statistics
    """
    total_applications = len(applications_db)
    total_decisions = len(decisions_db)
    
    if total_decisions > 0:
        approved = sum(1 for d in decisions_db.values() 
                      if d['decision_result']['final_decision'] == 'approved')
        approval_rate = approved / total_decisions
    else:
        approved = 0
        approval_rate = 0
    
    return {
        "total_applications": total_applications,
        "total_decisions": total_decisions,
        "approved": approved,
        "rejected": total_decisions - approved,
        "approval_rate": approval_rate,
        "timestamp": datetime.now().isoformat()
    }

# Run with: uvicorn backend.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
