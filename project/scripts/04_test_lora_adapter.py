import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_DIR = "adapters/qwen_codespace_cve_lora_adapter"

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR, trust_remote_code=True)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32,
    trust_remote_code=True
)

model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
model.eval()

prompt = """### Instruction:
Extract structured vulnerability evidence from this CVE/CTI text. Return valid JSON only.

### Input:
Package express version 4.18.2 has a high severity vulnerability. A fixed version is available. No confirmed active exploitation is stated.

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.2,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))