# ============================================================
# COMPLETE LLM FINE-TUNING - READY FOR GOOGLE COLAB
# ============================================================
# Instructions:
# 1. Open https://colab.research.google.com
# 2. Runtime > Change runtime type > T4 GPU
# 3. Copy ALL code below into ONE cell
# 4. Run and upload llm_train.json + llm_test.json when asked
# 5. Wait ~2 hours
# 6. Download fine-tuned model
# ============================================================

# Install
print("📦 Installing dependencies...")
get_ipython().system('pip install -q transformers datasets peft bitsandbytes accelerate trl')

# Import
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset
import json

print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Upload files
from google.colab import files
print("Upload llm_train.json:")
uploaded = files.upload()
print("Upload llm_test.json:")
uploaded = files.upload()

# Load data
with open('llm_train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)
print(f"✓ {len(train_data)} examples")

# Load model
model_name = "microsoft/Phi-3-mini-4k-instruct"
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, device_map="auto", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# LoRA
model = prepare_model_for_kbit_training(model)
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj","o_proj"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(model, lora_config)

# Format
def format_prompt(ex):
    return f"<|system|>ผู้เชี่ยวชาญสินเชื่อ<|end|>\n
