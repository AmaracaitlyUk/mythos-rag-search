import os
import requests

key = os.environ.get("GROQ_API_KEY")
print("Key loaded:", repr(key))

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Say hi in 3 words."}],
        "max_tokens": 20,
    },
)
print(r.status_code)
print(r.json())