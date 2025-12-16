import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai_service import predict_sentiment_bert

slang_examples = [
    # Positive Slang
    ("Gokil abis videonya!", "Positif"),
    ("Mantul gan, makasih infonya", "Positif"),
    ("Kerad banget sih ini kontennya 🔥", "Positif"),
    ("Suka bgt sm penjelasannya", "Positif"),
    ("Valid no debat", "Positif"),

    # Negative Slang
    ("Gajelas lu min", "Negatif"),
    ("B aja sih menurut gw", "Netral"), # 'B aja' is slang for 'biasa aja' (neutral/negative leaning)
    ("Dih apaan sih cringe", "Negatif"),
    ("Skip dulu deh", "Negatif"),
    ("Zonk parah", "Negatif"),
    
    # Neutral/Ambiguous
    ("Nitip sendal", "Netral"),
    ("Info loker", "Netral"),
    ("Cek dm min", "Netral")
]

def run_slang_test():
    print("Running Social Media Slang Accuracy Test...")
    print(f"Model: IndoBERT (w11wo/indonesian-roberta-base-sentiment-classifier)")
    print("-" * 60)
    
    correct = 0
    
    for text, expected in slang_examples:
        try:
            sentiment, conf = predict_sentiment_bert(text)
            status = "✅" if sentiment == expected else "❌"
            if sentiment == expected: correct += 1
            
            print(f"{status} Text: '{text}'")
            print(f"   Pred: {sentiment} ({conf:.2f}) | Exp: {expected}")
            print("-" * 30)
        except Exception as e:
            print(f"Error predicting '{text}': {e}")
            
    print(f"\nAccuracy on Slang Subset: {correct}/{len(slang_examples)} ({correct/len(slang_examples):.0%})")

if __name__ == "__main__":
    run_slang_test()
