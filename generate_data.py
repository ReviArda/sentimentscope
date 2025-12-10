import csv
import random

# Word lists for generation
subjects = [
    "Pelayanan", "Makanan", "Minuman", "Tempat", "Suasana", "Harga", "Aplikasi", "Fitur", 
    "Koneksi", "Pengiriman", "Admin", "Produk", "Kualitas", "Desain", "Warna", "Ukuran", 
    "Bahan", "Kamera", "Baterai", "Sinyal", "Hotel", "Kamar", "AC", "Kasur", "Kamar mandi",
    "Staff", "Security", "Parkiran", "Website", "Interface", "Tombol", "Loading", "Film",
    "Musik", "Buku", "Game", "Sepatu", "Baju", "Celana", "Tas", "Jam tangan", "Laptop",
    "HP", "Tablet", "Headset", "Mouse", "Keyboard", "Monitor", "Printer", "Scanner",
    "Meja", "Kursi", "Lampu", "AC", "Kipas", "Jendela", "Pintu", "Lantai", "Dinding",
    "Atap", "Taman", "Kolam", "Gym", "Spa", "Lobby", "Resepsionis", "Lift", "Tangga",
    "Toilet", "Wastafel", "Shower", "Handuk", "Sabun", "Sampo", "Sikat gigi", "Odol",
    "Sprei", "Bantal", "Guling", "Selimut", "Lemari", "Kulkas", "TV", "Remote", "Wifi",
    "Sinyal", "Kuota", "Pulsa", "Listrik", "Air", "Gas", "Bensin", "Parkir", "Tiket",
    "Antrian", "Kasir", "Pelayan", "Koki", "Satpam", "Supir", "Kurir", "Admin"
]

verbs_pos = [
    "sangat memuaskan", "luar biasa", "keren banget", "mantap", "oke punya", "juara", 
    "terbaik", "bikin nagih", "worth it", "recommended", "patut dicoba", "sangat membantu",
    "mudah digunakan", "cepat", "responsif", "ramah", "bersih", "nyaman", "indah", "elegan",
    "mewah", "eksklusif", "premium", "berkelas", "modern", "canggih", "inovatif", "kreatif",
    "unik", "estetik", "instagramable", "fotogenik", "luas", "lega", "sejuk", "harum",
    "rapi", "tertata", "terawat", "higienis", "steril", "aman", "tenang", "damai"
]

verbs_neg = [
    "sangat mengecewakan", "buruk sekali", "parah", "tidak layak", "hancur", "gagal",
    "bikin emosi", "lambat", "lelet", "kasar", "kotor", "bau", "berisik", "mahal", 
    "tidak sesuai", "rusak", "cacat", "palsu", "penipuan", "merugikan", "membosankan",
    "aneh", "jelek", "kusam", "sempit", "pengap", "panas", "gelap", "seram", "angker",
    "berantakan", "jorok", "menjijikkan", "berdebu", "berkarat", "usang", "kuno", "jadul",
    "norak", "kampungan", "alay", "lebay", "ribet", "susah", "membingungkan"
]

verbs_neu = [
    "biasa saja", "standar", "cukup", "lumayan", "sesuai harga", "not bad", "average",
    "perlu ditingkatkan", "masih oke", "bisa dimaklumi", "sedang-sedang saja", "normal",
    "tidak ada yang spesial", "seperti biasa", "cukup baik", "agak kurang", "terlalu biasa",
    "standar pabrik", "sesuai deskripsi", "cukup membantu", "cukup memadai", "cukup lengkap",
    "cukup bersih", "cukup nyaman", "cukup luas", "cukup terang", "cukup dingin", "cukup panas",
    "cukup cepat", "cukup ramah", "cukup responsif", "cukup aman", "cukup tenang"
]

contexts = [
    "banget", "sekali", "sungguh", "benar-benar", "asli", "sumpah", "pokoknya", "dijamin",
    "pastinya", "memang", "ternyata", "rupanya", "akhirnya", "awalnya", "tadinya",
    "jujur", "serius", "beneran", "yakin", "pasti", "tentu", "jelas", "nyata"
]

# Generate 2500 entries
new_data = []

# Positive (approx 850)
for _ in range(850):
    sub = random.choice(subjects)
    verb = random.choice(verbs_pos)
    ctx = random.choice(contexts)
    text = f"{sub} di sini {verb} {ctx}!"
    if random.random() > 0.5:
        text = f"{ctx} {sub}-nya {verb}."
    new_data.append([text, "Positif"])

# Negative (approx 850)
for _ in range(850):
    sub = random.choice(subjects)
    verb = random.choice(verbs_neg)
    ctx = random.choice(contexts)
    text = f"{sub} {verb} {ctx}, kecewa."
    if random.random() > 0.5:
        text = f"Gak nyangka {sub}-nya bakal {verb} gini."
    new_data.append([text, "Negatif"])

# Neutral (approx 800)
for _ in range(800):
    sub = random.choice(subjects)
    verb = random.choice(verbs_neu)
    text = f"{sub} {verb} sih menurutku."
    if random.random() > 0.5:
        text = f"Buat {sub}-nya {verb}, gak lebih."
    new_data.append([text, "Netral"])

random.shuffle(new_data)

# Append to CSV
try:
    with open('dummy_train.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(new_data)
    print(f"Successfully appended {len(new_data)} rows to dummy_train.csv")
except Exception as e:
    print(f"Error: {e}")
