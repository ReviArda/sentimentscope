import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

from models import Analysis
import pandas as pd

# Configuration
MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"
OUTPUT_DIR = "./fine_tuned_model"

# Configure logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train(data_path=None):
    """
    Fine-tune the model using user corrections from the database or a CSV file.
    Args:
        data_path (str, optional): Path to CSV file containing 'text' and 'label' columns.
    """
    logger.info("Starting Fine-Tuning Process...")
    
    # 1. Load Data
    texts = []
    labels = []

    if data_path:
        logger.info(f"Loading training data from {data_path}...")
        try:
            df = pd.read_csv(data_path)
            # Check columns
            if 'text' not in df.columns or 'label' not in df.columns:
                logger.error("Error: CSV must contain 'text' and 'label' columns.")
                return
            
            # Limit to 500 rows for performance (MVP constraint)
            # Limit to 500 rows for performance (MVP constraint)
            if len(df) > 500:
                logger.warning("Warning: Limiting dataset to 500 rows for performance.")
                df = df.head(500)
                
            texts = df['text'].astype(str).tolist()
            labels = df['label'].astype(str).tolist()
            logger.info(f"Loaded {len(texts)} samples from CSV.")
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return
            
    else:
        # Load from Database
        from app import app, db
        with app.app_context():
            # Fetch analyses that have a correction
            corrected_data = Analysis.query.filter(Analysis.correction.isnot(None)).all()
            
            if not corrected_data:
                logger.warning("No corrected data found. Please provide feedback via the web UI first.")
                return

            logger.info(f"Found {len(corrected_data)} corrected samples from Database.")
            
            texts = [item.text for item in corrected_data]
            labels = [item.correction for item in corrected_data]

    # 2. Prepare Dataset
    # Map labels to integers
    label_map = {'Positif': 0, 'Netral': 1, 'Negatif': 2}
    try:
        numeric_labels = [label_map[l] for l in labels]
    except KeyError as e:
        logger.error(f"Error: Invalid label found in database: {e}")
        return

    dataset = Dataset.from_dict({'text': texts, 'label': numeric_labels})
    
    # Split dataset (80% train, 20% test) if enough data
    if len(dataset) > 5:
        dataset = dataset.train_test_split(test_size=0.2)
        train_dataset = dataset['train']
        eval_dataset = dataset['test']
    else:
        logger.warning("Warning: Not enough data for split. Training on all data.")
        train_dataset = dataset
        eval_dataset = dataset

    # 3. Tokenization
    logger.info("Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

    # 4. Load Model
    logger.info("Loading Model...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3)

    # 5. Training Arguments
    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch" if len(dataset) > 5 else "no",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="no",        # Disable saving checkpoints every epoch
        save_total_limit=1,        # Only keep the last checkpoint if saved
        logging_dir='./logs',
        logging_steps=10,
        load_best_model_at_end=False,
    )

    # 6. Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval if len(dataset) > 5 else None,
    )

    # 7. Train
    logger.info("Training...")
    trainer.train()

    # 8. Save Model
    # 8. Save Model
    logger.info(f"Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    logger.info("Fine-tuning complete!")

if __name__ == "__main__":
    train()
