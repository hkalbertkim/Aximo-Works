import requests
import json

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "deepseek-coder:6.7b"

def generate(prompt: str):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]

if __name__ == "__main__":
    test_prompt = """
You are Aximo Engine.
Write a minimal Python function that adds two numbers.
Only output code.
"""
    output = generate(test_prompt)
    print("\n=== LLM OUTPUT ===\n")
    print(output)
