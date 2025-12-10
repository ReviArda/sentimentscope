import logging
import sys
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
