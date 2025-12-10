# 🧠 SentimentScope - Analisis Sentimen Publik Berbasis AI

![SentimentScope Banner](https://img.shields.io/badge/Status-Active-success?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge) ![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

**SentimentScope** adalah aplikasi analisis sentimen canggih yang dirancang khusus untuk memahami nuansa Bahasa Indonesia. Dibangun menggunakan teknologi Deep Learning (**IndoBERT**), aplikasi ini mampu mendeteksi emosi di balik teks, baik itu dari ulasan produk, komentar media sosial, atau dokumen dalam jumlah besar.

---

## 👨‍💻 Pengembang

| Atribut | Detail |
| :--- | :--- |
| **Nama** | **Revi Arda Saputra** |
| **Institusi** | **UNISNU JEPARA** |
| **Proyek** | Tugas Akhir / SCERDAS |

---

## ✨ Fitur Unggulan

Aplikasi ini hadir dengan berbagai fitur powerful untuk kebutuhan analisis data Anda:

### 1. 🔍 Analisis Satuan (Real-time)
Deteksi sentimen secara instan untuk teks singkat. Cocok untuk mengecek caption, tweet, atau ulasan singkat.
- **Output:** Positif, Negatif, Netral.
- **Confidence Score:** Tingkat keyakinan model terhadap prediksi.
- **Aspek:** Mendeteksi sentimen per aspek (misal: "Makanan enak tapi mahal" -> Makanan: Positif, Harga: Negatif).

### 2. 📊 Analisis Batch (Big Data)
Hemat waktu dengan memproses ribuan data sekaligus.
- **Support:** File `.csv` dan `.xlsx`.
- **Fitur:** Download hasil lengkap.
- **Visualisasi:** Statistik instan porsi sentimen.

### 3. 📹 Social Media Intelligence (YouTube)
Tarik data langsung dari kolom komentar YouTube untuk memahami opini audiens/netizen.
- **Scraping:** Otomatis mengambil komentar terbaru.
- **Analisis:** Mengelompokkan reaksi penonton (Hujatan vs Pujian).

### 4. 🧠 Smart Training (Fine-Tuning)
Fitur tercanggih yang memungkinkan AI belajar dari data Anda sendiri.
- **Custom Dataset:** Upload data CSV Anda sendiri.
- **Adaptasi:** AI akan menyesuaikan diri dengan gaya bahasa, slang, atau konteks spesifik bisnis Anda.

---

## 🛠️ Teknologi yang Digunakan

Aplikasi ini dibangun dengan *Tech Stack* modern untuk memastikan performa dan antarmuka yang elegan.

### Backend (Otak Sistem)
- **Python**: Bahasa pemrograman utama.
- **Flask**: Web framework yang ringan dan cepat.
- **Hugging Face Transformers**: Library utama untuk memuat model AI.
- **PyTorch**: Framework Deep Learning untuk proses training.
- **Pandas**: Manipulasi dan analisis data tabular.
- **SQLAlchemy (SQLite)**: Manajemen database lokal untuk riwayat dan user.

### AI Model (Kecerdasan Buatan)
- **Base Model**: `IndoBERT` (Bidirectional Encoder Representations from Transformers).
- **Kelebihan**: Dilatih pada jutaan kata Bahasa Indonesia, sehingga paham konteks, bukan sekadar kata kunci.
- **Fine-Tuning**: Kapabilitas untuk dilatih ulang agar semakin cerdas.

### Frontend (Antarmuka Pengguna)
- **HTML5 & CSS3**: Struktur dasar web.
- **Tailwind CSS**: Framework CSS untuk desain modern dan responsif.
- **Vanilla JavaScript**: Interaktivitas tanpa bloat framework berat.
- **Chart.js**: Visualisasi grafik data yang interaktif.
- **FontAwesome**: Ikon vektor berkualitas tinggi.

---

## 🚀 Cara Instalasi & Menjalankan

Ikuti langkah ini untuk menjalankan aplikasi di komputer lokal Anda:

### 1. Prasyarat
Pastikan Anda sudah menginstal:
- Python 3.9 atau lebih baru.
- PIP (Python Package Installer).
- Koneksi internet (untuk mengunduh model pertama kali).

### 2. Instalasi Dependensi
Buka terminal/CMD di folder project dan jalankan:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
Jalankan perintah berikut:
```bash
python app.py
```
Tunggu hingga muncul pesan: `Running on http://127.0.0.1:5000`

### 4. Buka di Browser
Buka browser (Chrome/Edge) dan akses alamat:
`http://localhost:5000`

---

## 📂 Struktur Folder

```
📂 sentiment_classifier_app/
├── 📂 static/              # Aset CSS, JS, Gambar
├── 📂 templates/           # File HTML (Frontend)
├── 📂 instance/            # Database SQLite
├── 📂 fine_tuned_model/    # (Otomatis) Hasil training model
├── app.py                  # Main Server File
├── train.py                # Script Training AI
├── model_loader.py         # Logika pemuatan model
├── scraper.py              # Logika scraping YouTube
└── requirements.txt        # Daftar pustaka Python
```

---

## 📝 Catatan Penting
- **Training Model:** Proses training (Fine-Tuning) membutuhkan resource CPU/GPU yang cukup. Pastikan komputer tidak dalam kondisi heavy load saat melakukan training.
- **Data Privasi:** Semua data yang diupload diproses secara lokal (atau di server Anda), aman dan tidak dikirim ke pihak ketiga.

---

**Dibuat dengan ❤️ oleh Revi Arda Saputra @ 2024**
*Fakultas Sains dan Teknologi - UNISNU JEPARA*
