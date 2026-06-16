import re
import spacy
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
import pandas as pd

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))


def strip_placeholders(text):
    """Remove {{placeholder}} patterns from Bitext dataset"""
    return re.sub(r'\{\{.*?\}\}', '', text).strip()


def clean_text_classical(text):
    """
    Full cleaning for classical ML models (TF-IDF + Logistic Regression/SVM).
    Lowercase, remove punctuation, remove stopwords, lemmatize.
    """
    text = strip_placeholders(text)
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)

    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc
        if token.text not in stop_words
        and len(token.text) > 1
        and not token.is_space
    ]
    return " ".join(tokens)


def clean_text_bert(text):
    """
    Light cleaning for DistilBERT.
    BERT handles its own tokenization - only strip placeholders
    and normalize whitespace. Keep punctuation and stopwords.
    """
    text = strip_placeholders(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_dataframe(df, mode='bert'):
    """
    Apply preprocessing to the Bitext dataframe.
    
    mode='bert'      → light cleaning for DistilBERT
    mode='classical' → full cleaning for TF-IDF models
    """
    df = df.copy()
    
    # Rename columns first
    df = df.rename(columns={
        'instruction': 'text',
        'intent': 'label'
    })

    if mode == 'bert':
        df['text_clean'] = df['text'].apply(clean_text_bert)
    else:
        df['text_clean'] = df['text'].apply(clean_text_classical)

    # Keep only what we need
    # 'label' is the renamed 'intent', keep 'category' as broad reference
    df = df[['text', 'text_clean', 'label', 'category', 'response']]
    
    return df


def create_splits(df, test_size=0.15, val_size=0.15, random_state=42):
    """
    Create stratified train/val/test splits.
    Default: 70% train, 15% val, 15% test
    """
    train_df, temp_df = train_test_split(
        df,
        test_size=(test_size + val_size),
        stratify=df['label'],
        random_state=random_state
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=temp_df['label'],
        random_state=random_state
    )
    return train_df, val_df, test_df