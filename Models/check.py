"""
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("kwanyick/llama-2-7b-cover-letter")
model = AutoModelForCausalLM.from_pretrained("kwanyick/llama-2-7b-cover-letter")

generated_text = model.generate("Dear Sir/Madam, I am writing to apply for the position of Data Scientist at your company" , max_length=500, do_sample=True, temperature=0.9, top_k=50, top_p=0.95, num_return_sequences=5)

print(generated_text)
"""

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="kwanyick/llama-2-7b-cover-letter")

generated_text = pipe("Dear Sir/Madam, I am writing to apply for the position of Data Scientist at your company", max_length=500, do_sample=True, temperature=0.9, top_k=50, top_p=0.95, num_return_sequences=5)

print(generated_text)