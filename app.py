from flask import Flask, render_template, request, jsonify, send_file
import json, random, io
from reportlab.pdfgen import canvas

app = Flask(__name__, static_folder="static", template_folder="templates")

# Load questions once
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

@app.route("/")
def quiz():
    # Create copies and attach original index as `id` so evaluation can map answers
    randomized_questions = []
    for i, q in enumerate(QUESTIONS):
        q_copy = dict(q)
        q_copy["id"] = i
        # copy options list to avoid mutating global
        q_copy["options"] = list(q_copy.get("options", []))
        randomized_questions.append(q_copy)
    random.shuffle(randomized_questions)
    for q in randomized_questions:
        random.shuffle(q["options"])
    return render_template("quiz.html", questions=randomized_questions)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json() or {}
    score = 0
    # Evaluate against canonical QUESTIONS (order independent)
    for i, q in enumerate(QUESTIONS):
        user_ans = data.get(str(i))
        if user_ans is not None and user_ans == q.get("answer"):
            score += 1
    percent = (score / len(QUESTIONS)) * 100
    return jsonify({"score": score, "total": len(QUESTIONS), "percent": percent})

@app.route("/certificate", methods=["POST"])
def certificate():
    payload = request.get_json() or {}
    name = payload.get("name", "Anonymous")
    score = payload.get("score", 0)
    total = payload.get("total", len(QUESTIONS))
    percent = payload.get("percent", 0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(600, 800))

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(300, 740, "Certificate of Completion")

    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 700, "This is to certify that")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 670, name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 630, "has successfully completed the quiz organised by IBNUTHANI DIGITAL SERVICES.")

    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 590, f"Score: {score}/{total}")

    c.drawCentredString(300, 570, f"Percentage: {percent:.2f}%")

    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="certificate.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
