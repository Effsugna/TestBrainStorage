# projects/OckerAI/chat.py

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import torch

# Load tokenizer and model
tokenizer = GPT2TokenizerFast.from_pretrained(".")
model = GPT2LMHeadModel.from_pretrained(".")

# Ensure model is in evaluation mode
model.eval()

# Terminal-based chat loop
def chat():
    print("OckerAI Terminal Chat — type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break

        input_ids = tokenizer.encode(user_input, return_tensors="pt")

        # Clamp to model context size
        if input_ids.shape[1] > 128:
            input_ids = input_ids[:, -128:]

        # Generate reply (match max_length to n_ctx)
        output = model.generate(
            input_ids,
            max_length=128,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(input_ids)
        )

        response = tokenizer.decode(output[0], skip_special_tokens=True)
        print("OckerAI:", response.replace(user_input, "").strip())

if __name__ == "__main__":
    chat()
