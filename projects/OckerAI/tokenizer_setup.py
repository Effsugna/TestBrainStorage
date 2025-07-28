from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
tokenizer.save_pretrained(".")

print("GPT2 tokenizer saved as tokenizer.json")

