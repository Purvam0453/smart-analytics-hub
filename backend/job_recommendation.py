jobs = {

    "Data Engineer": [
        "python",
        "sql",
        "pyspark",
        "azure",
        "databricks"
    ],

    "Data Analyst": [
        "python",
        "sql",
        "pandas",
        "numpy",
        "excel"
    ],

    "Python Developer": [
        "python",
        "fastapi",
        "django",
        "api"
    ],

    "AI Engineer": [
        "python",
        "machine learning",
        "numpy"
    ],

    "Backend Developer": [
        "python",
        "fastapi",
        "database",
        "api"
    ]

}


def recommend_jobs(skills):

    results = []

    for job, required_skills in jobs.items():

        matched = 0

        for skill in required_skills:

            if skill in skills:
                matched += 1


        score = int(
            (matched / len(required_skills)) * 100
        )


        results.append(
            {
                "job": job,
                "match": score
            }
        )


    results.sort(
        key=lambda x:x["match"],
        reverse=True
    )


    for index, item in enumerate(results):

        item["rank"] = index + 1


    return results[:5]