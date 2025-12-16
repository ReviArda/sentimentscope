# 📊 ANALISIS PROGRAM SENTIMENT CLASSIFIER APP

## 🎯 OVERVIEW

**SentimentScope** adalah aplikasi web berbasis AI untuk analisis sentimen teks Bahasa Indonesia. Aplikasi ini menggunakan model Deep Learning **IndoBERT** (Indonesian RoBERTa) untuk mengklasifikasikan sentimen menjadi tiga kategori: **Positif**, **Negatif**, dan **Netral**.

---

## 🏗️ ARSITEKTUR SISTEM

### 1. **Backend (Flask)**
- **Framework**: Flask (Python)
- **Database**: SQLite dengan SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Token) via Flask-JWT-Extended
- **Rate Limiting**: Flask-Limiter untuk mencegah abuse
- **CORS**: Enabled untuk API access

### 2. **Frontend**
- **HTML5**: Struktur halaman
- **Tailwind CSS**: Framework CSS utility-first
- **Vanilla JavaScript**: Interaktivitas tanpa framework berat
- **Chart.js**: Visualisasi data (trend chart)
- **WordCloud2.js**: Visualisasi word cloud

### 3. **AI/ML Stack**
- **Model Base**: `w11wo/indonesian-roberta-base-sentiment-classifier`
- **Library**: Hugging Face Transformers
- **Framework**: PyTorch
- **Training**: Custom fine-tuning capability

---

## 📁 STRUKTUR FILE & FUNGSI

### **File Utama Backend**

#### 1. `app.py` (Main Application)
**Fungsi Utama:**
- Entry point aplikasi Flask
- Route handlers untuk semua endpoint API
- Manajemen session dan authentication
- Error handling global

**Endpoint Utama:**
- `GET /` - Halaman utama
- `POST /api/classify` - Analisis sentimen teks
- `GET /api/history` - Riwayat analisis (per user)
- `GET /api/stats/trend` - Data trend 7 hari terakhir
- `GET /api/stats/wordcloud` - Data word frequency
- `POST /api/scrape` - Scraping komentar YouTube
- `POST /api/batch-classify` - Analisis batch dari CSV/Excel
- `POST /api/upload-train-data` - Upload data training
- `GET /api/training-status` - Status proses training
- `POST /api/feedback/<id>` - Submit koreksi user

**Fitur Keamanan:**
- Input validation (min 10, max 1000 karakter)
- Rate limiting pada auth endpoints
- JWT token verification
- SQL injection protection (via SQLAlchemy)

#### 2. `models.py` (Database Models)
**Model:**
- **User**: Tabel user dengan password hashing (Werkzeug)
- **Analysis**: Tabel riwayat analisis dengan relasi ke User

**Field Analysis:**
- `text`: Teks yang dianalisis
- `sentiment`: Hasil klasifikasi (Positif/Negatif/Netral)
- `confidence`: Skor kepercayaan (0-1)
- `correction`: Feedback user (optional)

#### 3. `auth.py` (Authentication Blueprint)
**Fungsi:**
- `POST /auth/register` - Registrasi user baru
- `POST /auth/login` - Login dan dapatkan JWT token
- `GET /auth/me` - Info user saat ini

**Keamanan:**
- Password hashing dengan Werkzeug
- Rate limiting: 5 req/min (register), 10 req/min (login)
- Validasi duplikasi username/email

#### 4. `model_loader.py` (AI Model Management)
**Fungsi Utama:**
- `load_model()` - Memuat model IndoBERT
- `reload_model()` - Reload model (setelah fine-tuning)
- `predict_sentiment_bert()` - Prediksi sentimen teks
- `predict_aspect_sentiment()` - Analisis sentimen per aspek

**Aspek yang Dideteksi:**
- **Makanan**: rasa, menu, porsi, bumbu, dll
- **Pelayanan**: pelayan, staff, ramah, lambat, dll
- **Harga**: harga, mahal, murah, biaya, dll
- **Suasana**: tempat, bersih, nyaman, musik, dll

**Algoritma Aspect Detection:**
1. Split teks berdasarkan konjungsi (tapi, namun, dan, dll)
2. Cek setiap segment terhadap keyword dictionary
3. Prediksi sentimen per segment yang match

#### 5. `train.py` (Model Training)
**Fungsi:**
- Fine-tuning model IndoBERT dengan data custom
- Support 2 sumber data:
  - CSV file (kolom: `text`, `label`)
  - Database (dari feedback user)

**Proses Training:**
1. Load data (max 500 rows untuk performa)
2. Map label ke integer (Positif=0, Netral=1, Negatif=2)
3. Split dataset (80% train, 20% test)
4. Tokenization dengan max_length=128
5. Training dengan hyperparameter:
   - Learning rate: 2e-5
   - Batch size: 8
   - Epochs: 3
   - Weight decay: 0.01
6. Save model ke `./fine_tuned_model/`

**Catatan:**
- Training berjalan di background thread (non-blocking)
- Status training dapat di-poll via API

#### 6. `scraper.py` (YouTube Scraper)
**Fungsi:**
- Mengambil komentar dari video YouTube
- Library: `youtube-comment-downloader`
- Limit: 20 komentar (untuk performa)
- Sort: Newest comments

#### 7. `extensions.py` (Flask Extensions)
**Initialization:**
- SQLAlchemy (database)
- JWTManager (authentication)
- Limiter (rate limiting)

---

### **File Frontend**

#### 1. `templates/index.html`
**Struktur:**
- Single Page Application (SPA) dengan tab navigation
- 5 Tab utama:
  1. **Analisis** - Input teks dan hasil
  2. **Dashboard** - Grafik trend & word cloud (login required)
  3. **Social** - Scraping YouTube comments
  4. **Batch** - Upload CSV/Excel untuk analisis massal
  5. **Training** - Upload data untuk fine-tuning

**Komponen UI:**
- Glass morphism design
- Responsive layout (mobile-friendly)
- Animated background blobs
- Modal untuk login & feedback

#### 2. `static/js/script.js`
**Fungsi Utama:**
- **Auth Management**: Login, logout, token management
- **API Communication**: Fetch ke semua endpoint
- **UI Updates**: Dynamic content rendering
- **Chart Rendering**: Chart.js untuk trend chart
- **Word Cloud**: WordCloud2.js integration
- **File Handling**: Drag & drop untuk upload

**State Management:**
- LocalStorage: JWT token, user info
- SessionStorage: History untuk non-login user

---

## 🔄 ALUR KERJA APLIKASI

### **1. Analisis Sentimen (Single Text)**

```
User Input Text
    ↓
Validasi (10-1000 karakter)
    ↓
predict_sentiment_bert(text)
    ↓
IndoBERT Model Processing
    ↓
Return: (sentiment, confidence)
    ↓
predict_aspect_sentiment(text) [Optional]
    ↓
Return: [{aspect, sentiment, text}, ...]
    ↓
Save to DB (if logged in)
    ↓
Display Result + Update Stats
```

### **2. Batch Analysis**

```
Upload CSV/Excel
    ↓
Detect Text Column (text/review/komentar)
    ↓
Limit to 1000 rows
    ↓
Loop: predict_sentiment_bert() per row
    ↓
Aggregate Statistics
    ↓
Return Results + Download Option
```

### **3. Training Process**

```
Upload Training CSV (text, label)
    ↓
Save to uploads/training_data.csv
    ↓
Start Background Thread
    ↓
train.py: Fine-tuning Process
    ↓
Save Model to fine_tuned_model/
    ↓
reload_model() - Load new weights
    ↓
Update Training Status
```

### **4. YouTube Scraping**

```
User Input YouTube URL
    ↓
scraper.py: get_youtube_comments()
    ↓
Extract 20 comments
    ↓
Loop: predict_sentiment_bert() per comment
    ↓
Return: Results + Statistics
```

---

## 🔐 KEAMANAN & VALIDASI

### **Input Validation**
- ✅ Min length: 10 karakter
- ✅ Max length: 1000 karakter
- ✅ Content-Type: application/json
- ✅ File type: CSV/Excel only
- ✅ File size: Implicit limit (1000 rows)

### **Authentication**
- ✅ JWT token-based
- ✅ Password hashing (Werkzeug)
- ✅ Rate limiting pada auth endpoints
- ✅ Token expiration: 1 hari

### **Database**
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Foreign key constraints
- ✅ User ownership verification

### **Error Handling**
- ✅ Try-catch di semua endpoint
- ✅ Logging ke file (`app.log`)
- ✅ User-friendly error messages
- ✅ Graceful degradation

---

## 📊 FITUR ANALISIS

### **1. Sentiment Classification**
- **3 Kategori**: Positif, Negatif, Netral
- **Confidence Score**: 0-1 (ditampilkan sebagai persentase)
- **Model**: IndoBERT (pre-trained + fine-tunable)

### **2. Aspect-Based Sentiment**
- Deteksi sentimen per aspek dalam satu teks
- Contoh: "Makanan enak tapi pelayanan lambat"
  - Makanan: Positif
  - Pelayanan: Negatif

### **3. Statistics Dashboard**
- **Trend Chart**: 7 hari terakhir (Chart.js)
- **Word Cloud**: Top 50 kata (WordCloud2.js)
- **Session Stats**: Real-time percentage bars

### **4. Batch Processing**
- Support CSV & Excel
- Auto-detect text column
- Limit 1000 rows untuk performa
- Download hasil sebagai CSV

---

## ⚙️ KONFIGURASI & SETTINGS

### **Environment Variables** (Hardcoded - perlu diubah untuk production)
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///sentiment.db'
JWT_SECRET_KEY = 'super-secret-key-change-this-in-production'  # ⚠️ PERLU DIUBAH!
```

### **Model Configuration**
```python
MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"
FINE_TUNED_DIR = "./fine_tuned_model"
MAX_TEXT_LENGTH = 1000
MIN_TEXT_LENGTH = 10
```

### **Training Configuration**
```python
Learning Rate: 2e-5
Batch Size: 8
Epochs: 3
Max Length: 128 tokens
Max Rows: 500 (training), 1000 (batch)
```

---

## 🚨 MASALAH & REKOMENDASI

### **Masalah yang Ditemukan**

1. **Security Issues:**
   - ⚠️ JWT secret key hardcoded (perlu environment variable)
   - ⚠️ No HTTPS enforcement
   - ⚠️ SQLite untuk production (sebaiknya PostgreSQL/MySQL)

2. **Performance Issues:**
   - ⚠️ Model loading blocking (perlu lazy loading)
   - ⚠️ No caching mechanism
   - ⚠️ Training di thread (sebaiknya Celery/Redis)

3. **Code Quality:**
   - ⚠️ Beberapa magic numbers (perlu constants)
   - ⚠️ Error messages dalam bahasa Indonesia (perlu i18n)
   - ⚠️ No unit tests

4. **User Experience:**
   - ⚠️ No loading indicators di beberapa tempat
   - ⚠️ No pagination untuk history (hanya 10 per page)
   - ⚠️ No export history feature

### **Rekomendasi Perbaikan**

1. **Security:**
   ```python
   # Gunakan environment variables
   import os
   JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-key')
   ```

2. **Performance:**
   - Implement Redis untuk caching
   - Use Celery untuk background tasks
   - Add database indexing

3. **Testing:**
   - Unit tests untuk model functions
   - Integration tests untuk API endpoints
   - E2E tests untuk user flows

4. **Monitoring:**
   - Add logging levels (DEBUG, INFO, WARNING, ERROR)
   - Implement health checks
   - Add metrics collection

---

## 📈 METRIK & STATISTIK

### **Database Schema**
- **Users**: id, username, email, password_hash, created_at
- **Analyses**: id, user_id, text, sentiment, confidence, correction, created_at

### **API Response Times** (Estimated)
- `/api/classify`: ~200-500ms (tergantung model loading)
- `/api/batch-classify`: ~1-5 detik (1000 rows)
- `/api/scrape`: ~2-10 detik (tergantung YouTube)
- `/api/upload-train-data`: Immediate (background process)

---

## 🎓 KESIMPULAN

**SentimentScope** adalah aplikasi yang **well-structured** dengan fitur lengkap untuk analisis sentimen Bahasa Indonesia. Aplikasi ini menggunakan teknologi modern dan best practices dalam pengembangan web application.

### **Kelebihan:**
✅ Arsitektur yang jelas (MVC pattern)
✅ Fitur lengkap (single, batch, social, training)
✅ UI modern dan responsive
✅ Support fine-tuning untuk custom domain
✅ Error handling yang baik

### **Area Perbaikan:**
⚠️ Security hardening (environment variables, HTTPS)
⚠️ Performance optimization (caching, async)
⚠️ Testing coverage
⚠️ Production readiness (database, deployment)

### **Overall Rating: 8/10**
Aplikasi ini sangat baik untuk project akademik dan dapat dikembangkan lebih lanjut untuk production dengan beberapa perbaikan di atas.

---

**Dianalisis oleh:** AI Assistant  
**Tanggal:** 2025  
**Versi Aplikasi:** 1.0.0

