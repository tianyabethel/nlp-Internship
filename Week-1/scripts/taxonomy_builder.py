import pandas as pd
import nltk
from collections import Counter
from nltk.util import ngrams

# Download tokenizer if needed
nltk.download("punkt")

# Load Week 1 listing sample
df = pd.read_csv("Week-1/data/processed/listing_sample.csv")

# Combine listing remarks
all_text = " ".join(
    df["remarks"].dropna().astype(str).str.lower()
)

# Tokenize
tokens = nltk.word_tokenize(all_text)

# Extract bigrams
bigrams = list(ngrams(tokens, 2))

# Count frequency
freq = Counter(bigrams)

# Display the 200 most common phrases
print("\nTop 200 real-estate phrases:\n")

for i, (bigram, count) in enumerate(freq.most_common(200), start=1):
    phrase = " ".join(bigram)
    print(f"{i}. {phrase}: {count}")
