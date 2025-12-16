import logging
import sys
import os

# Add parent directory to path to import modules from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train import train

# Configure logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

try:
    print("Starting debug run...")
    train(data_path='dummy_train.csv')
    print("Debug run completed successfully.")
except Exception as e:
    print(f"Debug run failed!")
    import traceback
    traceback.print_exc()
