"""
SIMPLE COLAB FINE-TUNING - WORKING VERSION
===========================================
Copy ALL to ONE Colab cell
"""

# Install with specific versions
get_ipython().system('pip install -q transformers==4.36.0 datasets peft bitsandbytes accelerate trl==0.7.4')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import json

print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Upload files
from google.colab import files
uploaded = files.upload()  # llm_train.json
uploaded = files.upload()  # llm_test.json

# Load data
with open('llm_train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)
print(f"Loaded {len(train_data)} examples")

# Load model
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

# LoRA setup
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
print(f"Trainable params: {model.print_trainable_parameters()}")

# Tokenize dataset
def tokenize_function(examples):
    texts = [f"Input: {ex['input']}\n\nOutput: {ex['output']}" for ex in examples]
    return tokenizer(texts, truncation=True, max_length=512, padding="max_length")

# Create dataset
dataset = Dataset.from_list(train_data)
tokenized_dataset = dataset.map(
    lambda x: tokenizer(
        f"Input: {x['input']}\n\nOutput: {x['output']}",
        truncation=True,
        max_length=512,
        padding="max_length"
    ),
    remove_columns=dataset.column_names
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=2,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy="epoch",
    warmup_steps=10,
    fp16=True,
    report_to="none"
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Trainer (simple version)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator
)

print("\n🚀 Starting training (this will take ~1-2 hours)...")
trainer.train()

# Save model
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

print("\n✅ DONE! Download the 'fine_tuned_model' folder")
print("Right-click folder > Download")
