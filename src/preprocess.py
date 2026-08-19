
import re
import pandas as pd

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_data(path="data/earnings_calls.csv"):
    df = pd.read_csv(path)
    df["clean_text"] = df["call_text"].apply(clean_text)
    return df
