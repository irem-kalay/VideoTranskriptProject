#Frontend için API
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os
from urllib.parse import urlparse, parse_qs
import re, requests, time
from langdetect import detect
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import threading

# global progress tracking
progress_data = {
    "status": "idle",        # idle / processing / completed
    "current_video": None,   # video currently being processed
    "results": []            # results as they are ready
}

YOUTUBE_API_KEY = "AIzaSyAMmVryxTV1NUD-T3MhNdedWvAIhlxui2c"
youtube_api = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


#Engellenen IP'de işe yaramıyor
#proxies = {
#    "http": "http://213.233.178.137:3128",
#    "https": "http://42.119.98.66:16000"
#}

#session = requests.Session()
#session.proxies.update(proxies)


# Proxy kontrolü
#try:
 #   res = session.get("https://api.ipify.org?format=json", timeout=5)
 #   ip = res.json().get("ip")
 #   print(f"Proxy ile bağlanıyor, görünen IP: {ip}")
#except Exception as e:
 #   print(f"Proxy çalışmıyor veya erişilemiyor: {e}")


# monkeypatch YouTubeTranscriptApi içindeki requests oturumunu
#_cli.requests = session
ytt_api = YouTubeTranscriptApi()

#openrouter key https://openrouter.ai/settings/keys
API_KEY = "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"

app = Flask(__name__)
CORS(app)

#ytt_api = YouTubeTranscriptApi()

#Yardımcı Fonksiyonlar

def check_caption_exists(video_id):
    """
    Checks if the video has at least one caption track available.
    Returns True if captions exist, False otherwise.
    """
    try:
        captions = youtube_api.captions().list(
            part="id,snippet",
            videoId=video_id
        ).execute()
        return bool(captions.get("items"))
    except Exception as e:
        print(f"[YouTube API] Failed to check caption for {video_id}: {e}")
        return False


def parse_video_url_for_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/embed/')[1]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None


def summarize_text_with_ai(text, ai_model="claude"):
    """
    text: özetlenecek metin
    ai_model: frontend'den seçilen AI
    """
    text_clean = re.sub(r"\[\d+\.\d+ - \d+\.\d+\]\s*", "", text)
    detected_lang = detect(text_clean)

    if detected_lang == "tr":
        base_prompt = "Aşağıdaki metni anlamlı bir paragraf olarak özetle:\n\n" + text_clean
    else:
        base_prompt = "Summarize the following text in text's language:\n\n" + text_clean

    if ai_model == "deepseek":
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": base_prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Hata: {e}"

    elif ai_model == "gpt": #frontend'de adı gpt
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b:free",  # OpenRouterdaki ücretsiz gpt modelinin adıydı
            "messages": [{"role": "user", "content": base_prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Hata: {e}"

    elif ai_model== "mistral":
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",  # OpenRouterdaki ücretsiz gpt modelinin adıydı
            "messages": [{"role": "user", "content": base_prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Hata: {e}"

    elif ai_model== "gemini":
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.0-flash-exp:free",  # OpenRouterdaki ücretsiz gemini modelinin adıydı
            "messages": [{"role": "user", "content": base_prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Hata: {e}"

    elif ai_model== "gemma":
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemma-3-27b-it:free",  #openrouter gemma free modelin adı
            "messages": [{"role": "user", "content": base_prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Hata: {e}"


# sadece transcript çıkartıyor
def write_transcripts(csv_path):
    results = []
    try:
        df = pd.read_csv(csv_path)
        if 'url' not in df.columns or df.empty:
            raise ValueError("CSV dosyasında 'url' sütunu yok veya dosya boş")
        urls = df['url'].dropna().tolist()
    except Exception as e:
        raise RuntimeError(f"CSV okunamadı: {e}")

    for idx, youtube_url in enumerate(urls, 1):
        progress_data["status"] = "processing"
        progress_data["current_video"] = youtube_url
        progress_data["results"] = results  # update partial results

        print(f"\n{'='*60}")
        print(f"[{idx}/{len(urls)}] İşleniyor: {youtube_url}")
        print(f"{'='*60}")

        video_id = parse_video_url_for_id(youtube_url)
        if not video_id:
            results.append({"url": youtube_url, "error": "Video ID çıkarılamadı"})
            continue

        print(f"Çıkarılan Video ID: {video_id}")

        try:
            # Step 1: Check caption availability
            has_caption = check_caption_exists(video_id)
            if has_caption:
                print(f"[API] Captions exist for {video_id}, attempting fetch...")

            # Step 2: Always use youtube-transcript-api for fetching
            transcript_list = ytt_api.list(video_id)

            # Find original language transcript first
            original_transcript = next(
                (t for t in transcript_list if not t.is_translatable), None
            ) or next(
                (t for t in transcript_list if t.is_generated), None
            )

            if not original_transcript:
                raise ValueError("Orijinal dilde transkript bulunamadı")

            transcript_data = original_transcript.fetch()
            transcript_text = "\n".join(
                f"[{entry.start:.2f} - {entry.start + entry.duration:.2f}] {entry.text}"
                for entry in transcript_data
            )

            print(f"[Transcript] Retrieved for {video_id} ({original_transcript.language_code})")

            results.append({
                "url": youtube_url,
                "video_id": video_id,
                "language": original_transcript.language_code,
                "transcript": transcript_text
            })

        except Exception as e:
            error_msg = f"Hata oluştu (Video ID: {video_id}): {e}"
            print(error_msg)
            results.append({"url": youtube_url, "error": str(e)})

        # Optional: Short delay to reduce rate-limit risk
        if idx < len(urls):
            time.sleep(5)

    # Mark progress as completed
    progress_data["status"] = "completed"
    progress_data["current_video"] = None
    progress_data["results"] = results

    return results



#write_transcripts fonksiyonuyla transkripti çekiyor, summarize_text_with_ai fonksiyonuyla özet çıkartıyor
def summarize_transcript(csv_path, ai_model="openrouter"):
    transcripts_results = write_transcripts(csv_path)
    results = []

    for item in transcripts_results:
        if "error" in item:
            results.append(item)
            continue

        transcript_text = item["transcript"]
        video_id = item["video_id"]
        language_code = item["language"]

        # Özetleme
        summary = summarize_text_with_ai(transcript_text, ai_model)

        print(f"Özet oluşturuldu: {video_id} ({language_code})")

        results.append({
            "url": item["url"],
            "video_id": video_id,
            "language": language_code,
            "summary": summary
        })

        #Update progress with summaries
        progress_data["results"] = results

    #son hali
    progress_data["status"] = "completed"
    progress_data["current_video"] = None
    progress_data["results"] = results

    return results


#Ana sayfa
@app.route("/")
def home():
    return render_template("index.html")



@app.route("/progress")
def get_progress():
    return jsonify(progress_data)



#API end pointlelr
@app.route("/process", methods=["POST"])
def process_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "CSV dosyası yüklenmedi"}), 400

    file = request.files['file']
    save_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    ai_model = request.form.get("aiModel", "claude")

    results = summarize_transcript(save_path, ai_model)

    return jsonify({
        "status": "completed",
        "results": results
    })



# === Sadece Transkript Endpoint ===
@app.route("/transcripts", methods=["POST"])
def transcripts_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "CSV dosyası yüklenmedi"}), 400

    file = request.files['file']
    save_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    try:
        results = write_transcripts(save_path) #burda çağırıyorum
        return jsonify({"status": "ok", "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


