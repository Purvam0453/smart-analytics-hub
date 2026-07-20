from fastapi import APIRouter
import pandas as pd
import os


router = APIRouter(

    prefix="/analytics",

    tags=["Analytics"]

)


CSV_FILE = "results.csv"



@router.get("/summary")
def analytics_summary():


    if not os.path.exists(CSV_FILE):

        return {
            "message": "No data available"
        }



    df = pd.read_csv(CSV_FILE)



    if df.empty:

        return {
            "message": "No resume analyzed yet"
        }




    df["resume_score"] = pd.to_numeric(

        df["resume_score"],

        errors="coerce"

    )



    df = df.dropna(

        subset=["resume_score"]

    )



    highest_score = df.loc[

        df["resume_score"].idxmax()

    ]



    best_user = df["username"].value_counts().idxmax()



    df["date_time"] = pd.to_datetime(

        df["date_time"]

    )



    daily_accuracy = (

        df.groupby(

            df["date_time"].dt.date

        )["resume_score"]

        .mean()

        .reset_index()

    )



    daily_accuracy.columns = [

        "date",

        "average_score"

    ]



    return {


        "total_resumes":

        len(df),



        "average_score":

        round(

            df["resume_score"].mean(),

            2

        ),



        "highest_score_resume":{


            "filename":

            highest_score["filename"],



            "score":

            highest_score["resume_score"],



            "role":

            highest_score["predicted_role"]

        },



        "best_user":

        best_user,



        "daily_accuracy":

        daily_accuracy.to_dict(

            orient="records"

        )

    }