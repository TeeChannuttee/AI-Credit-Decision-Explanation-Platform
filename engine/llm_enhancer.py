"""
LLM Explanation Enhancer - Updated with Fine-tuned Model

Uses fine-tuned Phi-3 model to generate natural Thai explanations
for credit decisions.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional

# Add project root to sys.path for direct script execution
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class LLMEnhancer:
    """Generate natural explanations using fine-tuned LLM"""
    
    def __init__(self, model_path: str = "models/fine_tuned_llm/fine_tuned_model"):
        self.model_path = Path(model_path)
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model if available
        if self.model_path.exists():
            self.load_model()
    
    def load_model(self):
        """Load fine-tuned model"""
        try:
            print(f"Loading fine-tuned model from {self.model_path}...")
            
            # Load base model
            base_model_name = "microsoft/Phi-3-mini-4k-instruct"
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Load LoRA adapter
            self.model = PeftModel.from_pretrained(base_model, str(self.model_path))
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
            
            print("✓ Fine-tuned model loaded successfully")
            
        except Exception as e:
            print(f"⚠ Could not load fine-tuned model: {e}")
            print("  Falling back to template-based explanations")
            self.model = None
            self.tokenizer = None
    
    def generate_explanation(self, 
                           application: Dict,
                           decision_result: Dict,
                           max_length: int = 512) -> str:
        """
        Generate natural explanation using fine-tuned LLM
        
        Args:
            application: Application data
            decision_result: Decision result from decision engine
            max_length: Maximum length of generated text
            
        Returns:
            Natural Thai explanation
        """
        if self.model is None or self.tokenizer is None:
            return self._fallback_explanation(decision_result)
        
        try:
            # Format input
            input_text = self._format_input(application, decision_result)
            
            # Generate
            inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                print("⏳ Generating AI explanation (CPU mode)... This usually takes 30-60 seconds.")
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=80,  # Reduced from 150 for much faster CPU response
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=False
                )
            
            # Decode
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract output part
            if "Output:" in generated_text:
                explanation = generated_text.split("Output:")[-1].strip()
            else:
                explanation = generated_text
            
            return explanation
            
        except Exception as e:
            print(f"⚠ LLM generation failed: {e}")
            return self._fallback_explanation(decision_result)
    
    def _format_input(self, application: Dict, decision_result: Dict) -> str:
        """Format input for LLM"""
        decision = decision_result['final_decision']
        ml_score = decision_result['ml_result']['ml_score']
        risk_level = decision_result['ml_result']['ml_risk_level']
        
        input_text = f"""Input: ข้อมูลคำขอสินเชื่อ:
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
- ระดับความเสี่ยง: {risk_level}

Output:"""
        
        return input_text
    
    def _fallback_explanation(self, decision_result: Dict) -> str:
        """Fallback to template-based explanation"""
        from engine.explanation_engine import ExplanationEngine
        
        engine = ExplanationEngine()
        explanation = engine.generate_explanation(
            decision_result,
            {},
            language='th',
            style='formal'
        )
        
        return explanation.get('summary', 'ไม่สามารถสร้างคำอธิบายได้')

# Example usage
if __name__ == "__main__":
    print("="*60)
    print("LLM ENHANCER TEST")
    print("="*60)
    
    enhancer = LLMEnhancer()
    
    if enhancer.model is not None:
        print("\n✓ Fine-tuned model ready!")
        print(f"  Device: {enhancer.device}")
        print(f"  Model path: {enhancer.model_path}")
        
        # Test generation
        test_app = {
            'monthly_income': 45000,
            'employment_years': 5,
            'debt_to_income': 0.35,
            'existing_loans': 2,
            'late_payment_count': 0,
            'requested_amount': 300000,
            'savings_balance': 200000
        }
        
        test_result = {
            'final_decision': 'rejected',
            'ml_result': {
                'ml_score': 0.305,
                'ml_risk_level': 'high'
            }
        }
        
        print("\n🧪 Testing LLM generation...")
        explanation = enhancer.generate_explanation(test_app, test_result)
        print("\nGenerated Explanation:")
        print(explanation)
    else:
        print("\n⚠ Fine-tuned model not available")
        print("  Using template-based explanations")
    
    print("\n" + "="*60)
