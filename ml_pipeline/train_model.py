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

print(df.head())

print(df.columns)


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
    max_features=5000
)


X_train_tfidf = tfidf.fit_transform(X_train)

X_test_tfidf = tfidf.transform(X_test)



print("Training model...")


model = LogisticRegression(
    max_iter=1000
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


print("Model saved successfully 🚀")