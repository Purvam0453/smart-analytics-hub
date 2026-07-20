import joblib
import os

from resume_parser import extract_text


# ML model paths

MODEL_PATH = "../ml_pipeline/trained_model/model.pkl"

VECTORIZER_PATH = "../ml_pipeline/trained_model/vectorizer.pkl"



# Load model

model = joblib.load(MODEL_PATH)

vectorizer = joblib.load(VECTORIZER_PATH)



def analyze_resume(text):

    # Convert text for ML

    vector = vectorizer.transform(
        [text]
    )


    # Prediction

    prediction = model.predict(
        vector
    )


    # Confidence

    probability = model.predict_proba(
        vector
    )

    confidence = max(probability[0]) * 100



    # Skill extraction

    skills_list = [

        "python",
        "sql",
        "machine learning",
        "react",
        "fastapi",
        "azure",
        "aws",
        "pyspark",
        "databricks",
        "pandas",
        "numpy"

    ]


    found_skills = []


    lower_text = text.lower()


    for skill in skills_list:

        if skill in lower_text:

            found_skills.append(skill)



    return {

    "skills": found_skills,

    "predicted_role": prediction[0],

    "resume_score": round(confidence,2),

    "recommendations": recommend_jobs(found_skills)

}
from job_recommendation import recommend_jobs