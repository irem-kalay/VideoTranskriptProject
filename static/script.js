//static translation

const translations = {
        tr: {
            appName: "VideoSummarizer",
            navHome: "Ana Sayfa",
            navFeatures: "Özellikler",
            navApiDocs: "API Dokümantasyonu",
            navSupport: "Destek",
            subtitle: "Yapay Zeka Destekli Video Özetleme Aracı",
            uploadLabel: "CSV Dosyası Yükle",
            dragDrop: "CSV dosyanızı buraya sürükleyin",
            clickSelect: "veya dosya seçmek için tıklayın",
            uploadSuccess: "başarıyla yüklendi",
            aiModelLabel: "AI Model Seçimi",
            startProcess: "Özetle",
            starting: "İşlem başlatılıyor...",
            showTranscripts: "Transkriptleri Göster/İndir",
            // Footer translations
            footerAbout: "VideoSummarizer Hakkında",
            footerDescription: "Gelişmiş yapay zeka teknolojileri ile videolarınızı anında özetleyen, modern ve kullanıcı dostu platformumuz.",
            footerQuickLinks: "Hızlı Bağlantılar",
            footerHome: "Ana Sayfa",
            footerFeatures: "Özellikler",
            footerPricing: "Fiyatlandırma",
            footerDocs: "Dokümantasyon",
            footerSupport: "Destek",
            footerHelp: "Yardım Merkezi",
            footerContact: "İletişim",
            footerFaq: "SSS",
            footerStatus: "Sistem Durumu",
            footerLegal: "Yasal",
            footerPrivacy: "Gizlilik Politikası",
            footerTerms: "Kullanım Koşulları",
            footerCookies: "Çerez Politikası",
            footerLicense: "Lisans",
            footerCopyright: "© 2025 VideoSummarizer. Tüm hakları saklıdır. ♥ ile yapıldı."

        },
        en: {
            appName: "VideoSummarizer",
            navHome: "Home",
            navFeatures: "Features",
            navApiDocs: "API Documentation",
            navSupport: "Support",
            subtitle: "AI-Powered Video Summarization Tool",
            uploadLabel: "Upload CSV File",
            dragDrop: "Drag your CSV file here",
            clickSelect: "or click to select a file",
            uploadSuccess: "uploaded successfully",
            aiModelLabel: "AI Model Selection",
            startProcess: "Summarise",
            starting: "Starting process...",
            showTranscripts: "Show/Download Transcripts",

            // Footer translations
            footerAbout: "About VideoSummarizer",
            footerDescription: "Our modern and user-friendly platform that instantly summarizes your videos with advanced artificial intelligence technologies.",
            footerQuickLinks: "Quick Links",
            footerHome: "Home",
            footerFeatures: "Features",
            footerPricing: "Pricing",
            footerDocs: "Documentation",
            footerSupport: "Support",
            footerHelp: "Help Center",
            footerContact: "Contact",
            footerFaq: "FAQ",
            footerStatus: "System Status",
            footerLegal: "Legal",
            footerPrivacy: "Privacy Policy",
            footerTerms: "Terms of Service",
            footerCookies: "Cookie Policy",
            footerLicense: "License",
            footerCopyright: "© 2025 VideoSummarizer. All rights reserved. Made with ♥"

        }
    };

    function setLanguage(lang) {
        document.querySelectorAll("[data-translate]").forEach(el => {
            const key = el.getAttribute("data-translate");
            el.textContent = translations[lang][key];
        });
        document.getElementById("currentLanguage").textContent = lang.toUpperCase();
        document.getElementById("currentFlag").className = `fi fi-${lang === "tr" ? "tr" : "gb"}`;
    }

    document.querySelectorAll(".dropdown-item").forEach(item => {
        item.addEventListener("click", () => {
            const lang = item.getAttribute("data-lang");
            setLanguage(lang);
        });
    });

    // Sayfa yüklenince varsayılan dil
    setLanguage("tr");

    // --- Mevcut dosya yükleme ve fetch işlemleri ---
    const fileInput = document.getElementById("csvFile");
    const fileInfo = document.getElementById("fileInfo");
    const fileNameSpan = document.getElementById("fileName");
    const processBtn = document.getElementById("processBtn");
    const showTranscriptsBtn = document.getElementById("showTranscriptsBtn");
    const transcriptBox = document.getElementById("transcriptBox");
    const resultsContainer = document.getElementById("resultsContainer");

    let uploadedFile = null;

    fileInput.addEventListener("change", (e) => {
        uploadedFile = e.target.files[0];
        if (uploadedFile) {
            fileNameSpan.textContent = uploadedFile.name;
            fileInfo.style.display = "block";
        }
    });

// --- BU KODU EKLEYİN ---
    // AI Model Seçimi için Event Listener
    const aiOptions = document.querySelectorAll(".ai-option");

    aiOptions.forEach(option => {
        option.addEventListener("click", () => {
            // Önce tüm seçeneklerden 'selected' sınıfını kaldır
            aiOptions.forEach(opt => opt.classList.remove("selected"));

            // Sadece tıklanan seçeneğe 'selected' sınıfını ekle
            option.classList.add("selected");

            // Tıklanan kutunun içindeki radio butonu bul ve 'checked' yap
            const radio = option.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }
        });
    });

        // --- EKLEME BİTTİ ---
//Ai modeli seçerek
// Verileri saklamak için global değişkenler
let transcriptData = [];
let summaryData = [];


function updateProgressMessage(message) {
    const loadingDiv = document.querySelector('.loading-state div:last-child');
    if (loadingDiv) {
        loadingDiv.textContent = message;
    }
}

// Özetleme butonu için güncellenmiş kod
processBtn.addEventListener("click", () => {
    if (!uploadedFile)
        return alert(
            translations[document.getElementById("currentLanguage").textContent.toLowerCase()].uploadLabel
        );

    const formData = new FormData();
    formData.append("file", uploadedFile);

    const selectedAI = document.querySelector('input[name="aiModel"]:checked').value;
    formData.append("aiModel", selectedAI);

    // Yükleme durumunu göster
    transcriptBox.innerHTML = `
        <div class="loading-state">
            <i class="fas fa-spinner"></i>
            <div>Özetleme işlemi başlatılıyor...</div>
            <div class="progress-details">CSV dosyası işleniyor...</div>
        </div>
    `;
    transcriptBox.style.display = "block";

    // Artık polling YOK, direkt backend'den yanıt alacağız
    fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            transcriptBox.innerHTML = "";

            if (data.status !== "completed" || !data.results) {
                transcriptBox.innerHTML = `
                    <div class="error-item">
                        <div class="error-title">
                            <i class="fas fa-exclamation-triangle"></i>
                            İşlem Hatası
                        </div>
                        <div class="error-message">Hata: ${data.error || "Bilinmeyen hata"}</div>
                    </div>
                `;
                return;
            }

            // Özet listesini sakla
            summaryData = [...data.results];

            // Başlık ekle
            const headerDiv = document.createElement("div");
            headerDiv.className = "transcript-header";
            headerDiv.innerHTML = `<i class="fas fa-file-text"></i> Video Özetleri`;
            transcriptBox.appendChild(headerDiv);

            // Her video için kart oluştur
            data.results.forEach((item, index) => {
                const videoItem = document.createElement("div");
                videoItem.className = "video-item";
                videoItem.innerHTML = `
                    <div class="video-info">
                        <div class="video-icon">
                            <i class="fas fa-play"></i>
                        </div>
                        <div class="video-details">
                            <h4>Video ${index + 1} - Özet</h4>
                            <div class="video-url">${item.url}</div>
                        </div>
                    </div>
                    <button class="download-btn summary-download-btn">
                        <i class="fas fa-download"></i>
                        İndir
                    </button>
                `;

                // İndir butonu
                const downloadBtn = videoItem.querySelector(".summary-download-btn");
                downloadBtn.addEventListener("click", () => {
                    const summary = item.summary || "Özet bulunamadı";
                    const url = item.url;
                    const blob = new Blob([summary], { type: "text/plain;charset=utf-8" });
                    const link = document.createElement("a");
                    link.href = URL.createObjectURL(blob);
                    const fileName = url.replace(/[^a-z0-9]/gi, "_").substring(0, 50) + "_summary.txt";
                    link.download = fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(link.href);
                });

                transcriptBox.appendChild(videoItem);
            });
        })
        .catch(err => {
            transcriptBox.innerHTML = `
                <div class="error-item">
                    <div class="error-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Bağlantı Hatası
                    </div>
                    <div class="error-message">İstek hatası: ${err.message}</div>
                </div>
            `;
            console.error("Fetch hatası:", err);
        });
});

// Transkript gösterme butonu için güncellenmiş kod
showTranscriptsBtn.addEventListener("click", () => {
    if (!uploadedFile)
        return alert(
            translations[document.getElementById("currentLanguage").textContent.toLowerCase()].uploadLabel
        );

    const formData = new FormData();
    formData.append("file", uploadedFile);

    // Yükleme durumunu göster
    transcriptBox.innerHTML = `
        <div class="loading-state">
            <i class="fas fa-spinner"></i>
            <div>Transkript işlemi başlatılıyor...</div>
            <div class="progress-details">CSV dosyası işleniyor...</div>
        </div>
    `;
    transcriptBox.style.display = "block";

    // Timeout destekli fetch
    const fetchWithTimeout = (url, options, timeout = 180000) => {
        return Promise.race([
            fetch(url, options),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error("Fetch isteği zaman aşımına uğradı")), timeout)
            )
        ]);
    };

    fetchWithTimeout("http://127.0.0.1:5000/transcripts", {
        method: "POST",
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            transcriptBox.innerHTML = "";

            //Global değişken
            transcriptData = data.results || [];


            const headerDiv = document.createElement("div");
            headerDiv.className = "transcript-header";
            headerDiv.innerHTML = `
                <i class="fas fa-file-alt"></i>
                Video Transkriptleri
            `;
            transcriptBox.appendChild(headerDiv);

            if (data.status === "ok" && data.results) {
                data.results.forEach((item, index) => {
                    const videoItem = document.createElement("div");

                    if (item.error) {
                        videoItem.className = "error-item";
                        videoItem.innerHTML = `
                            <div class="error-title">
                                <i class="fas fa-exclamation-triangle"></i>
                                Video ${index + 1}
                            </div>
                            <div class="video-url">${item.url}</div>
                            <div class="error-message">Hata: ${item.error}</div>
                        `;
                    } else {
                        videoItem.className = "video-item";
                        videoItem.innerHTML = `
                            <div class="video-info">
                                <div class="video-icon">
                                    <i class="fas fa-play"></i>
                                </div>
                                <div class="video-details">
                                    <h4>Video ${index + 1} - Transkript</h4>
                                    <div class="video-url">${item.url}</div>
                                </div>
                            </div>
                            <button class="download-btn transcript-download-btn" data-index="${index}">
                                <i class="fas fa-download"></i>
                                İndir
                            </button>
                        `;

                        //İndir butonunu bağlama
                        const downloadBtn = videoItem.querySelector('.transcript-download-btn');
                        downloadBtn.addEventListener("click", () => {
                            const transcript = transcriptData[index].transcript || "Transkript bulunamadı";
                            const url = transcriptData[index].url;

                            const blob = new Blob([transcript], { type: "text/plain;charset=utf-8" });
                            const link = document.createElement("a");
                            link.href = URL.createObjectURL(blob);
                            const fileName = url.replace(/[^a-z0-9]/gi, "_").substring(0, 50) + "_transcript.txt";
                            link.download = fileName;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            URL.revokeObjectURL(link.href);
                        });
                    }

                    transcriptBox.appendChild(videoItem);
                });
            } else {
                const errorDiv = document.createElement("div");
                errorDiv.className = "error-item";
                errorDiv.innerHTML = `
                    <div class="error-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        İşlem Hatası
                    </div>
                    <div class="error-message">Hata: ${data.error || "Bilinmeyen hata"}</div>
                `;
                transcriptBox.appendChild(errorDiv);
            }
        })
        .catch(err => {
            transcriptBox.innerHTML = `
                <div class="error-item">
                    <div class="error-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Bağlantı Hatası
                    </div>
                    <div class="error-message">İstek hatası: ${err.message}</div>
                </div>
            `;
            console.error("Fetch hatası:", err);
        });
});
