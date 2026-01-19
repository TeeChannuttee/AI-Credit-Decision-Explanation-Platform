# 🤖 Fine-tune LLM สำหรับคำอธิบายสินเชื่อภาษาไทย

## 📋 สิ่งที่ต้องเตรียม:
- ✅ Google Account (สำหรับ Colab)
- ✅ ไฟล์ `data/llm_train.json` (400 ตัวอย่าง)
- ✅ ไฟล์ `data/llm_test.json` (100 ตัวอย่าง)
- ✅ เวลา 2-3 ชั่วโมง

---

## 🚀 ขั้นตอนการทำ

### 1. เปิด Google Colab
1. ไป https://colab.research.google.com
2. คลิก "New Notebook"
3. **Runtime > Change runtime type > T4 GPU** (สำคัญ!)

### 2. Copy Code ด้านล่างไปรันใน Colab

---

## 📝 CODE สำหรับ COLAB

### Cell 1: ติดตั้ง Libraries
```python
!pip install -q transformers datasets peft bitsandbytes accelerate trl
```

### Cell 2: Import และตรวจสอบ GPU
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset
import json

print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

### Cell 3: Upload ไฟล์
```python
from google.colab import files
uploaded = files.upload()  # Upload llm_train.json
uploaded = files.upload()  # Upload llm_test.json
```

### Cell 4: โหลดข้อมูล
```python
with open('llm_train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

print(f"✓ Loaded {len(train_data)} training examples")

# แสดงตัวอย่าง
print("\nExample:")
print(train_data[0]['input'][:200])
print(train_data[0]['output'][:200])
```

### Cell 5: โหลด Phi-3 Model
```python
model_name = "microsoft/Phi-3-mini-4k-instruct"

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

print("✓ Model loaded")
```

### Cell 6: Setup LoRA
```python
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
```

### Cell 7: เตรียม Dataset
```python
def format_prompt(example):
    return f"""<|system|>คุณเป็นผู้เชี่ยวชาญสินเชื่อ อธิบายชัดเจนและเป็นมิตร<|end|>
