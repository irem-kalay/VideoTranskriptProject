from pytubefix import YouTube
import whisper
import os

# YouTube video URL'si
video_url = "http://www.youtube.com/watch?v=kPa7bsKwL-c"

try:
    print("Video indiriliyor...")
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    filename = "audio.mp4"  # Geçici olarak indirilecek ses dosyasının adı
    audio_stream.download(filename=filename)
    print("Video başarıyla indirildi!")

    print("Transkript oluşturuluyor...")
    model = whisper.load_model("base")  # whisper modelini yükle
    audio_path = os.path.abspath(filename)  # Ses dosyasının tam yolu
    result = model.transcribe(audio_path)  # Transkripsiyonu yap
    full_transcript = result["text"]
    print("Transkript tamamlandı!")

    # Transkripti dosyaya yaz
    output_file = os.path.join(os.getcwd(), "transkript.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_transcript)
    print(f"Transkript başarıyla '{output_file}' dosyasına kaydedildi.")

    # Geçici ses dosyasını sil
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print("Geçici ses dosyası silindi.")

except Exception as e:
    print(f"\nBir hata oluştu: {e}")
