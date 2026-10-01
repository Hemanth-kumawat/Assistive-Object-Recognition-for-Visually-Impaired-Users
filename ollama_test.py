import ollama

print("======================================")
print("       ULTRON OLLAMA TEST")
print("======================================")

response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {
            "role": "user",
            "content": (
                "You are ULTRON, an assistive AI assistant. "
                "Give a short greeting."
            )
        }
    ]
)

print()
print("🤖 ULTRON:")
print(response["message"]["content"])

print()
print("======================================")
print("       OLLAMA CONNECTION OK")
print("======================================")