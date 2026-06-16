import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_data():
    train = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "train_classical.csv"))
    val = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "val_classical.csv"))
    test = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "test_classical.csv"))
    return train, val, test

def build_tfidf(train_texts):
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2
    )
    vectorizer.fit(train_texts)
    return vectorizer

def train_and_evaluate(model, model_name, X_train, y_train, X_val, y_val):
    print(f"\n{'='*50}")
    print(f"Training: {model_name}")
    print(f"{'='*50}")
    model.fit(X_train, y_train)
    val_preds = model.predict(X_val)
    accuracy = accuracy_score(y_val, val_preds)
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_val, val_preds))
    return model, accuracy, val_preds

def save_model(model, vectorizer, model_name):
    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model, os.path.join(BASE_DIR, "models", f"{model_name}.pkl"))
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl"))
    print(f"Saved {model_name} to models/")
