import sys
print(f"Python version: {sys.version}")

import pandas as pd
print(f"pandas: {pd.__version__}")

import torch
print(f"PyTorch: {torch.__version__}")

import transformers
print(f"Transformers: {transformers.__version__}")

import sklearn
print(f"scikit-learn: {sklearn.__version__}")

import spacy
nlp = spacy.load("en_core_web_sm")
print(f"spaCy: {spacy.__version__}")

import langchain
print(f"LangChain: {langchain.__version__}")

import chromadb
print(f"ChromaDB: {chromadb.__version__}")

import fastapi
print(f"FastAPI: {fastapi.__version__}")

import streamlit
print(f"Streamlit: {streamlit.__version__}")

# Check new dataset
df = pd.read_csv("data/raw/Bitext_support.csv")
print(f"\nDataset loaded successfully")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Categories: {df['category'].unique()}")
print(f"Sample instruction:\n{df['instruction'].iloc[0]}")
print(f"Sample response:\n{df['response'].iloc[0]}")