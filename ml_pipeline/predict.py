import joblib

from processing.preprocess import clean_resume


MODEL_PATH = "trained_model/model.pkl"
VECTORIZER_PATH = "trained_model/vectorizer.pkl"


# Load model

model = joblib.load(MODEL_PATH)

vectorizer = joblib.load(VECTORIZER_PATH)



def predict_role(resume_text):

    cleaned_text = clean_resume(resume_text)


    vector = vectorizer.transform(
        [cleaned_text]
    )


    prediction = model.predict(
        vector
    )


    probability = model.predict_proba(
        vector
    )


    confidence = max(probability[0]) * 100


    return {

        "predicted_role": prediction[0],

        "confidence": round(confidence,2)

    }



# Testing

if __name__ == "__main__":


    sample_resume = """

    Python developer with experience in SQL,
    Machine Learning, Data Analysis,
    Pandas, Flask and cloud technologies.

    """


    result = predict_role(sample_resume)


    print(result)