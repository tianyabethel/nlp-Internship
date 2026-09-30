import pandas as pd
from collections import Counter
import re

# Load Week 1 listing sample
df = pd.read_csv("Week-1/data/processed/listing_sample.csv")

print("DATASET OVERVIEW")
print("=" * 40)
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nColumns:")
print(df.columns.tolist())

print("\nMISSING VALUES")
print("=" * 40)
print(df.isnull().sum())

print("\nREMARK LENGTH")
print("=" * 40)
df["remark_length"] = df["remarks"].astype(str).str.len()
print(df["remark_length"].describe())

print("\nTOP WORDS")
print("=" * 40)

text = " ".join(df["remarks"].dropna().astype(str).str.lower())

words = re.findall(r"\b[a-z]+\b", text)

stopwords = {
    "the", "and", "a", "to", "of", "in", "for", "with",
    "is", "this", "on", "an", "or", "that", "home", "has",
    "from", "are", "as", "be", "by", "at", "it", "you"
}

filtered_words = [word for word in words if word not in stopwords]

word_counts = Counter(filtered_words)

for word, count in word_counts.most_common(20):
    print(f"{word}: {count}")

print("\nSAMPLE REMARKS")
print("=" * 40)

for remark in df["remarks"].dropna().head(5):
    print("\n", remark)
