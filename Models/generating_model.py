"""from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM

config = PeftConfig.from_pretrained("TuningAI/Llama2_7B_Cover_letter_generator")
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model = PeftModel.from_pretrained(base_model, "TuningAI/Llama2_7B_Cover_letter_generator")

generated_text = model.generate("Dear Sir/Madam, I am writing to apply for the position of Data Scientist at your company" , max_length=500, do_sample=True, temperature=0.9, top_k=50, top_p=0.95, num_return_sequences=5)

for i, text in enumerate(generated_text):
    print(f"Generated text {i+1}: {text}")

"""
import openai
from fpdf import FPDF

# import open ai to generate text
openai.api_key = "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"

response = openai.Completion.create(
    engine="gpt-3.5-turbo-instruct",
    prompt="Generate applicaton letter for the position of Data Scientist at Nestle",
    max_tokens=500,
    top_p=0.9,
    frequency_penalty=0,
    presence_penalty=0
)

# Your generated text
generated_text = response.choices[0].text


print(generated_text)

"""
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Maximum width of text (in mm)
max_width = 200
# Maximum height of text (in mm)
max_height = 250

# Current height position
current_height = 10

words = generated_text.split()
line = words.pop(0)

for word in words:
    # Check if adding the next word will exceed the max width
    if pdf.get_string_width(line + " " + word) < max_width:
        line += " " + word
    else:
        pdf.cell(200, 10, txt=line, ln=True)
        line = word
        current_height += 10
        # Check if adding the next line will exceed the max height
        if current_height > max_height:
            pdf.add_page()
            current_height = 10

# Print the last line
pdf.cell(200, 10, txt=line, ln=True)

pdf.output("h.pdf")
"""
