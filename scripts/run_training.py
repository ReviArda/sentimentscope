import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.training_service import train

if __name__ == "__main__":
    print("Starting Training Process...")
    # Use the generated CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'social_train.csv')
    
    if os.path.exists(csv_path):
        train(data_path=csv_path)
    else:
        print(f"Error: {csv_path} not found.")
