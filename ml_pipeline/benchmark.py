"""
Preprocessing Consistency Benchmark
Runs the trained model on the test set using:
  (a) OLD backend inference preprocessing (no lemmatization, custom stopwords)
  (b) ML pipeline training preprocessing (with lemmatization + NLTK stopwords)
  (c) NEW shared preprocessing module (must match training exactly)
Reports accuracy for all three to quantify drift before/after fix.
"""

import os
import sys
import re
import string
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "UpdatedResumeDataSet.csv")
MODEL_PATH = os.path.join(BASE_DIR, "trained_model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "trained_model", "vectorizer.pkl")

# ============================================================
# (a) OLD backend inference preprocessing — NO lemmatization
# ============================================================
BACKEND_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
}


def old_backend_clean(text):
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\d{10,}", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    words = [w for w in text.split() if w not in BACKEND_STOP_WORDS]
    return " ".join(words)


# ============================================================
# (b) Training preprocessing — WITH lemmatization + NLTK stopwords
# ============================================================
def training_clean(text):
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\d{10,}", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    words = [lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words]
    return " ".join(words)


# ============================================================
# (c) NEW shared preprocessing module (must match training)
# ============================================================
_backend_dir = os.path.join(BASE_DIR, "..", "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_backend_dir))
from shared_preprocessing import clean_resume_text as shared_clean


def run_benchmark():
    print("=" * 70)
    print("ML PREPROCESSING CONSISTENCY BENCHMARK (BEFORE / AFTER)")
    print("=" * 70)

    # Load dataset
    print(f"\nLoading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Dataset size: {len(df)} rows, columns: {list(df.columns)}")

    X = df["Resume"]
    y = df["Category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Load model and vectorizer
    print(f"\nLoading trained model from {MODEL_PATH} ...")
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    # Benchmark (a): OLD Backend preprocessing
    print("\n--- (A) OLD backend inference (NO lemmatization, custom stopwords) ---")
    X_test_a = X_test.apply(old_backend_clean)
    pred_a = model.predict(vectorizer.transform(X_test_a))
    acc_a = accuracy_score(y_test, pred_a)
    print(f"  Accuracy: {acc_a * 100:.2f}%")

    # Benchmark (b): Training preprocessing (ground truth)
    print("\n--- (B) Training preprocessing (lemmatization + NLTK stopwords) ---")
    X_test_b = X_test.apply(training_clean)
    pred_b = model.predict(vectorizer.transform(X_test_b))
    acc_b = accuracy_score(y_test, pred_b)
    print(f"  Accuracy: {acc_b * 100:.2f}%")

    # Benchmark (c): NEW shared module
    print("\n--- (C) NEW shared_preprocessing module (should match B exactly) ---")
    X_test_c = X_test.apply(shared_clean)
    pred_c = model.predict(vectorizer.transform(X_test_c))
    acc_c = accuracy_score(y_test, pred_c)
    print(f"  Accuracy: {acc_c * 100:.2f}%")

    # Verify B and C are identical
    matches_bc = (X_test_b.tolist() == X_test_c.tolist())
    print(f"\n  Training output == Shared output: {matches_bc}")

    # Detailed report for shared preprocessing (post-fix)
    print("\n--- Classification Report (Shared / Post-Fix) ---")
    print(classification_report(y_test, pred_c))

    drift_before = acc_b - acc_a
    drift_after = acc_b - acc_c

    print("=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"  (A) OLD backend (no lemma):  {acc_a * 100:.2f}%")
    print(f"  (B) Training (ground truth): {acc_b * 100:.2f}%")
    print(f"  (C) NEW shared module:       {acc_c * 100:.2f}%")
    print(f"")
    print(f"  Drift BEFORE fix (B - A):    {drift_before * 100:+.2f}%")
    print(f"  Drift AFTER  fix (B - C):    {drift_after * 100:+.2f}%")
    print(f"  B == C identical tokens:      {matches_bc}")
    print("=" * 70)

    return {
        "old_accuracy": acc_a,
        "training_accuracy": acc_b,
        "shared_accuracy": acc_c,
        "drift_before": drift_before,
        "drift_after": drift_after,
        "tokens_identical": matches_bc,
    }


if __name__ == "__main__":
    run_benchmark()
