import csv
import os


CSV_FILE = "results/prediction_result.csv"



def add_resume(data):
    """
    Dummy function for compatibility.
    Data already gets saved in CSV.
    """
    pass



def get_dashboard_stats():

    resumes = []


    if os.path.exists(CSV_FILE):

        with open(
            CSV_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                skills = row["Skills"].replace('"', "").split(",")

                skills = [
                    skill.strip()
                    for skill in skills
                    if skill.strip()
                ]


                resumes.append({

                    "role": row["Role"],

                    "score": float(row["Resume Score"]),

                    "skills": skills

                })



    total = len(resumes)

    roles = {}

    skills_count = {}

    total_score = 0



    for resume in resumes:

        total_score += resume["score"]


        role = resume["role"]

        roles[role] = roles.get(role,0) + 1



        for skill in resume["skills"]:

            skills_count[skill] = skills_count.get(skill,0)+1



    average_score = 0


    if total > 0:

        average_score = round(
            total_score / total,
            2
        )



    return {

        "total_resumes": total,

        "average_score": average_score,

        "roles": roles,

        "skills": skills_count,

        "recent_resumes": resumes[-5:]

    }