import requests
import re
from langdetect import detect

# 1. API anahtarını buraya yaz
API_KEY = "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"  # kendi OpenRouter API anahtarını buraya yapıştır

# transcript.txt dosyasını oku
with open("transcript.txt", "r", encoding="utf-8") as f:
    lyrics = f.read()

# Temizlik (isteğe bağlı)
lyrics = re.sub(r"\[\d+\.\d+ - \d+\.\d+\]\s*", "", lyrics)

# Metnin dilini tespit et
detected_lang = detect(lyrics)
print(f"Tespit edilen dil: {detected_lang}")

# Dil bazlı prompt oluştur
if detected_lang == "tr":
    prompt = (
        "Aşağıdaki video sözlerini anlamlı, akıcı ve doğal bir paragraf halinde özetle. "
        "Sözlerin verdiği duyguyu da yansıt:\n\n" + lyrics
    )
elif detected_lang == "en":
    prompt = (
        "Summarize the following lyrics in a meaningful, fluent, and natural paragraph. "
        "Try to also reflect the emotion of the video:\n\n" + lyrics
    )
else:
    prompt = (
        f"Summarize the following text in {detected_lang} in a meaningful, fluent, and natural paragraph. "
        "Try to also reflect the emotion of the video:\n\n" + lyrics
    )

# 5. OpenRouter üzerinden Claude 3 Haiku ile API isteği yap
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openrouter.ai",  # kendi siten yoksa "https://openrouter.ai" kalabilir
    "X-Title": "Lyrics Summarizer"
}

data = {
    "model": "anthropic/claude-3-haiku",  # dilersen burayı "mistralai/mistral-7b-instruct" yapabilirsin
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=data
)

# 6. Yanıtı yazdır
reply = response.json()["choices"][0]["message"]["content"]
print("\n📌 Final Özet:\n", reply)
