# projects/OckerAI/train.py

from transformers import GPT2LMHeadModel, GPT2TokenizerFast, GPT2Config, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import os

# Load tokenizer
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

# Load jsonl dataset
dataset = load_dataset("json", data_files="data/seed_conversations.jsonl", split="train")

# Convert prompt+response to single string
def format(example):
    return {"text": f"User: {example['prompt']}\nAI: {example['response']}"}

dataset = dataset.map(format)

# Tokenize
def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=128)

tokenized_dataset = dataset.map(tokenize, batched=True)

# Define config + model
config = GPT2Config(
    vocab_size=tokenizer.vocab_size,
    n_positions=128,
    n_ctx=128,
    n_embd=256,
    n_layer=4,
    n_head=4,
    pad_token_id=tokenizer.eos_token_id
)

model = GPT2LMHeadModel(config)

# Training setup
training_args = TrainingArguments(
    output_dir="./models",
    overwrite_output_dir=True,
    num_train_epochs=5,
    per_device_train_batch_size=2,
    save_steps=100,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=10
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

# Train
trainer.train()

# Save model
model.save_pretrained(".")
tokenizer.save_pretrained(".")
