"""
Train resume classification model.

Changes from original:
- De-duplicates resume texts before training
- Uses improved TF-IDF (10K features, bigrams, sublinear_tf)
- Uses class_weight='balanced' for imbalanced classes
- Saves model and vectorizer to both ml_pipeline and backend
"""
import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from processing.preprocess import clean_resume


DATA_PATH = "data/UpdatedResumeDataSet.csv"

MODEL_DIR = "trained_model"

os.makedirs(MODEL_DIR, exist_ok=True)


print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Original rows: {len(df)}")

print(df.columns)


# De-duplicate: keep first occurrence of each unique resume text
df = df.drop_duplicates(subset=["Resume"], keep="first").reset_index(drop=True)

print(f"After de-duplication: {len(df)} rows")


print("Cleaning resumes...")

df["clean_resume"] = df["Resume"].apply(
    clean_resume
)


X = df["clean_resume"]

y = df["Category"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("Creating TF-IDF...")


tfidf = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=1,
    max_df=0.95
)


X_train_tfidf = tfidf.fit_transform(X_train)

X_test_tfidf = tfidf.transform(X_test)



print("Training model...")


model = LogisticRegression(
    max_iter=1000,
    C=1.0,
    class_weight="balanced",
    solver="lbfgs"
)


model.fit(
    X_train_tfidf,
    y_train
)


prediction = model.predict(
    X_test_tfidf
)


accuracy = accuracy_score(
    y_test,
    prediction
)


print(
    "Model Accuracy:",
    accuracy * 100,
    "%"
)


print(
    classification_report(
        y_test,
        prediction
    )
)


joblib.dump(
    model,
    f"{MODEL_DIR}/model.pkl"
)


joblib.dump(
    tfidf,
    f"{MODEL_DIR}/vectorizer.pkl"
)


# Also save to backend/trained_model for inference
BACKEND_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "backend",
    "trained_model"
)

os.makedirs(BACKEND_MODEL_DIR, exist_ok=True)

joblib.dump(model, os.path.join(BACKEND_MODEL_DIR, "model.pkl"))
joblib.dump(tfidf, os.path.join(BACKEND_MODEL_DIR, "vectorizer.pkl"))


print("Model saved successfully")
print(f"  -> {MODEL_DIR}/")
print(f"  -> {BACKEND_MODEL_DIR}/")
