# 📱 Setup Fitur Social Media Scraping (Updated)
**Dokumen ini menjelaskan cara setup API Keys dan Browser Automation.**

## 🎯 Solusi Scraping

Aplikasi mendukung 3 metode scraping:
1.  **Browser Automation (Playwright)** (🌟 Recommended) - Meniru manusia, gratis, agak lambat.
2.  **API Keys** (Official) - Cepat, stabil, tapi memerlukan biaya/verifikasi.
3.  **Mock Data** (Fallback) - Data palsu jika metode di atas gagal.

---

## 🛠 Metode 1: Browser Automation (Gratis)
Metode ini menggunakan browser "tersembunyi" untuk membuka link.

### Persyaratan
-   Install Playwright: `pip install playwright`
-   Install Browser: `playwright install chromium`
-   **PENTING**: Jika scraping gagal (login wall), Anda harus login manual sekali menggunakan `debug_real_browser.py`.

---

## 🔑 Metode 2: API Keys (Official)

Jika Anda ingin kestabilan total tanpa browser, gunakan Official API. Berikut caranya:

### 1. Twitter / X API
Twitter/X sangat ketat. Anda butuh **Bearer Token**.
1.  Buka [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).
2.  Sign up (Mungkin perlu berlangganan **Basic Tier** ~$100/bulan untuk akses baca Tweet).
3.  Buat **Project** & **App**.
4.  Copy **Bearer Token**.
5.  Set environment variable:
    ```bash
    set TWITTER_BEARER_TOKEN=Isi_Token_Anda_Disini
    ```

### 2. Instagram/Facebook API
1.  Buka [Meta for Developers](https://developers.facebook.com/).
2.  Buat Aplikasi (Business Type).
3.  Tambahkan produk **Instagram Graph API**.
4.  Dapatkan **User Access Token** (Short/Long Lived).
5.  *Catatan*: Sangat rumit untuk personal project karena butuh App Review dan Business Verification.

### 3. TikTok API
1.  Buka [TikTok for Developers](https://developers.tiktok.com/).
2.  Daftar dan buat aplikasi.
3.  Access Token untuk Research API biasanya terbatas untuk peneliti akademis.

---

## ⚠️ Kesimpulan
Untuk tugas kuliah atau proyek personal, **SANGAT DISARANKAN** menggunakan metode **Browser Playwright** atau **Mock Data** karena biaya dan kerumitan mendapatkan API Keys resmi.

---

## � Troubleshooting Playwright

Jika masih mendapatkan hasil Mock Data:
1.  Jalankan debug script: `py tests/debug_real_browser.py`
2.  Masukkan link yang bermasalah.
3.  Lihat browser yang muncul.
    -   **Jika muncul Login**: Loginlah manual di browser tersebut dengan akun tumbal. Playwright akan mencoba menyimpan sesi (cookie) jika dikonfigurasi.
    -   **Jika Captcha**: Selesaikan Captcha manual.
