"""
FIXED COLAB FINE-TUNING SCRIPT
===============================
Copy ALL code below to ONE Colab cell
"""

# Install
get_ipython().system('pip install -q transformers datasets peft bitsandbytes accelerate trl')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset
import json

print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Upload
from google.colab import files
uploaded = files.upload()  # llm_train.json
uploaded = files.upload()  # llm_test.json

# Load
with open('llm_train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

# Model
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

# LoRA
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

# Format dataset - FIXED VERSION
formatted = []
for ex in train_data:
    text = f"Input: {ex['input']}\n\nOutput: {ex['output']}"
    formatted.append({"text": text})

dataset = Dataset.from_list(formatted)

# Training args
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy="epoch",
    warmup_steps=10,
    fp16=True
)

# Trainer - FIXED: removed dataset_text_field
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    max_seq_length=512,
    tokenizer=tokenizer,
    args=training_args,
    packing=False
)

print("\n🚀 Starting training...")
trainer.train()

# Save
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")
print("\n✓ Done! Download 'fine_tuned_model' folder")
