# ============================================================
# COMPLETE FINE-TUNING SCRIPT - COPY ALL TO ONE COLAB CELL
# ============================================================

# 1. Install dependencies
print("📦 Installing dependencies...")
get_ipython().system('pip install -q transformers datasets peft bitsandbytes accelerate trl')

# 2. Import libraries
print("\n📚 Importing libraries...")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset
import json

print(f"✓ PyTorch: {torch.__version__}")
print(f"✓ CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")

# 3. Upload data files
print("\n📤 Upload training files...")
from google.colab import files
print("Upload llm_train.json:")
uploaded = files.upload()
print("Upload llm_test.json:")
uploaded = files.upload()

# 4. Load dataset
print("\n📊 Loading dataset...")
with open('llm_train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)
with open('llm_test.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print(f"✓ Train: {len(train_data)} | Test: {len(test_data)}")

# 5. Load Phi-3 model
print("\n🤖 Loading Phi-3...")
model_name = "microsoft/Phi-3-mini-4k-instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
print("✓ Model loaded")

# 6. Setup LoRA
print("\n⚙️ LoRA setup...")
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 7. Format dataset
print("\n📋 Formatting dataset...")
def format_prompt(ex):
    prompt = f"""<|system|>คุณเป็นผู้เชี่ยวชาญสินเชื่อ อธิบายชัดเจนและเป็นมิตร<|end|>
