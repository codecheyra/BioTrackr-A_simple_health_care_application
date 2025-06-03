from huggingface_hub import InferenceClient
import os

# Try grabbing token from env or paste directly
client = InferenceClient(model="ritvik77/Medical_Doctor_AI_LoRA-Mistral-7B-Instruct_FullModel", token=token)

try:
    out = client.text_generation("hello", max_new_tokens=10)
    print("✅ Success:", out)
except Exception as e:
    print("❌ Error:", e)
