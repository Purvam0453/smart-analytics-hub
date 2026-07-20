from fastapi import APIRouter
import pandas as pd
import os


router = APIRouter(
    tags=["Dashboard"]
)


RESULT_FILE = "results.csv"


@router.get("/dashboard-stats")
def dashboard_stats():


    if not os.path.exists(RESULT_FILE):

        return {
            "total_resumes":0,
            "average_score":0,
            "roles":{},
            "skills":{},
            "score_analysis":[]
        }



    df = pd.read_csv(RESULT_FILE)



    if df.empty:

        return {
            "total_resumes":0,
            "average_score":0,
            "roles":{},
            "skills":{},
            "score_analysis":[]
        }




    # Role Data

    roles = (

        df["predicted_role"]
        .value_counts()
        .to_dict()

    )




    # Skills Data

    skill_count = {}


    for skills in df["skills"]:

        skills = skills.replace(
            "[",
            ""
        ).replace(
            "]",
            ""
        ).replace(
            "'",
            ""
        )


        for skill in skills.split(","):

            skill = skill.strip()


            if skill:

                skill_count[skill] = (
                    skill_count.get(skill,0)+1
                )





    # Score Analysis

    score_analysis = []


    for score in df["resume_score"]:


        score_analysis.append({

            "score":str(score),

            "count":1

        })




    return {


        "total_resumes":

        len(df),



        "average_score":

        round(

            df["resume_score"].mean(),

            2

        ),



        "roles":

        roles,



        "skills":

        skill_count,



        "score_analysis":

        score_analysis

    }





@router.get("/login-stats")
def login_stats():

    return {

        "login_trend":[

            {
                "date":"Today",
                "count":1
            }

        ]

    }