from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_report(data):

    file_path = "resume_report.pdf"

    pdf = canvas.Canvas(
        file_path,
        pagesize=letter
    )


    y = 750


    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        50,
        y,
        "AI Resume Analysis Report"
    )


    y -= 50


    pdf.setFont(
        "Helvetica",
        12
    )


    pdf.drawString(
        50,
        y,
        f"Resume Score: {data['resume_score']}%"
    )


    y -= 30


    pdf.drawString(
        50,
        y,
        f"Predicted Role: {data['predicted_role']}"
    )


    y -= 40


    pdf.drawString(
        50,
        y,
        "Skills:"
    )


    y -= 25


    for skill in data["skills"]:

        pdf.drawString(
            70,
            y,
            "- " + skill
        )

        y -= 20



    y -= 20


    pdf.drawString(
        50,
        y,
        "Job Recommendations:"
    )


    y -= 25


    for job in data["recommendations"]:

        pdf.drawString(
            70,
            y,
            f"{job['job']} - {job['match']}% Match"
        )

        y -= 20



    pdf.save()


    return file_path