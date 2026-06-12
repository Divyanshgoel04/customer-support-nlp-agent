import re
import spacy
from nltk.corpus import stopwords

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))

def replace_placeholder(text, product):
    """Replace {product_purchased} with actual product name"""
    return text.replace("{product_purchased}", product)

def clean_text(text):
    """Lowercase, remove punctuation/numbers, remove stopwords, lemmatize"""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # remove punctuation/numbers
    
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc 
              if token.text not in stop_words and len(token.text) > 1]
    
    return " ".join(tokens)

def preprocess_dataframe(df):
    """Apply full preprocessing to the dataframe"""
    df = df.copy()
    
    # Step 1: Replace placeholder
    df['Description_Clean'] = df.apply(
        lambda row: replace_placeholder(row['Ticket Description'], row['Product Purchased']),
        axis=1
    )
    
    # Step 2: Clean text
    df['Description_Clean'] = df['Description_Clean'].apply(clean_text)
    
    return df