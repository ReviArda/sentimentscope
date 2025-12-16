import pandas as pd
import random

def generate_social_dataset(output_file='social_train.csv', num_samples=200):
    """
    Generates a synthetic dataset of Indonesian social media slang.
    """
    
    # Templates for slang generation
    # {subject} {verb} {adjective} {closing}
    
    subjects = ["", "Gw sih", "Aku", "Sumpah", "Asli", "Ini", "Kontennya", "Videonya", "Min,", "Woy"]
    
    pos_adjectives = [
        "bagus banget", "mantul", "keren abis", "gokil", "juara", 
        "best", "valid no debat", "pecah", "savage", "terbaik", 
        "worth it", "enak parah", "rekomen", "daebak", "slay"
    ]
    
    neg_adjectives = [
        "jelek", "ancur", "zonk", "sampah", "cringe", 
        "gajelas", "aneh", "b aja", "biasa aja", "skip", 
        "burik", "hoax", "lebay", "norak", "ribet"
    ]
    
    neu_adjectives = [
        "biasa", "standar", "lumayan", "oke lah", "not bad",
        "cukup", "sedeng", "rata-rata"
    ]

    contexts = [
        "parah sih", "sumpah", "sih menurut gw", "banget", "asli", 
        "woi", "sih", "dong", "ya", "sih ini"
    ]
    
    # Specific slang phrases that are hard for standard models
    specific_cases = [
        ("Nitip sandal min", "Netral"),
        ("Jejak", "Netral"),
        ("Nyimak", "Netral"),
        ("Info loker gan", "Netral"),
        ("Cek DM min", "Netral"),
        ("Gacha ampas", "Negatif"),
        ("Rungkad bos", "Negatif"),
        ("Sabi lah", "Positif"),
        ("Gaskeun", "Positif"),
        ("Pantau dulu", "Netral"),
        ("Skip dulu", "Negatif"),
        ("Fyp dong", "Netral"),
        ("Meresahkan ya bund", "Negatif"),
        ("Gelay banget", "Negatif"),
        ("Kekeyi menangis melihat ini", "Negatif"),
        ("Valid", "Positif"),
        ("Mantap jiwa", "Positif"),
        ("B aja", "Negatif"), # Often negative context in slang
        ("B aja sih", "Netral"),
        ("Ygy", "Netral"), # Yan Guys Ya - context dependent, usually neutral filler
        ("Jujurly bagus", "Positif"),
        ("Jujurly kecewa", "Negatif"),
        ("Mengsedih", "Negatif"),
        ("Benar-benar membagongkan", "Negatif"), # Confusing/Negative
        ("Xixixi", "Netral"), # Laughing
        ("Wkwkwk", "Netral")
    ]

    data = []

    # 1. Generate Pattern-based samples
    # Positive
    for _ in range(int(num_samples * 0.4)):
        s = random.choice(subjects)
        adj = random.choice(pos_adjectives)
        ctx = random.choice(contexts)
        text = f"{s} {adj} {ctx}".strip()
        data.append({'text': text, 'label': 'Positif'})

    # Negative
    for _ in range(int(num_samples * 0.4)):
        s = random.choice(subjects)
        adj = random.choice(neg_adjectives)
        ctx = random.choice(contexts)
        text = f"{s} {adj} {ctx}".strip()
        data.append({'text': text, 'label': 'Negatif'})
        
    # Neutral
    for _ in range(int(num_samples * 0.1)):
        s = random.choice(subjects)
        adj = random.choice(neu_adjectives)
        text = f"{s} {adj}".strip()
        data.append({'text': text, 'label': 'Netral'})

    # 2. Add Specific Cases (Weighted)
    for text, label in specific_cases:
        # Repeat specific cases to ensure model learns them
        for _ in range(2): 
            data.append({'text': text, 'label': label})

    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    print(f"Generated {len(df)} samples.")
    print(df.head())
    
    df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    generate_social_dataset()
