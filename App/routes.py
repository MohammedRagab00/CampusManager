from App import app
from flask import render_template, url_for, request, redirect
import sqlite3


# Home Page route
@app.route("/")
def home():
    return render_template("home.html")


# Route for Grade
@app.route("/grade")
def grade():
    return render_template("grade.html")


@app.route("/sched")
def sched():
    return render_template("sched.html")


@app.route("/enroll", methods=["GET", "POST"])
def enroll():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    student_id = 1

    if request.method == "POST":
        selected_courses = request.form.getlist("courses")
        for cc in selected_courses:
            cursor.execute(
                "INSERT INTO registerdCourses (std_id, cc) VALUES (?, ?)",
                (student_id, cc),
            )
        conn.commit()
        conn.close()
        return redirect(url_for("enroll"))

    cursor.execute(
        """
        SELECT c.cc, c.Cname, p.precc
        FROM course c
        JOIN pre_req p ON c.cc = p.cc
        JOIN course_grade cg ON p.precc = cg.cc
        WHERE cg.std_id = ? AND cg.grade IS NOT NULL AND cg.grade != 0
        AND c.cc NOT IN (SELECT cc FROM registerdCourses WHERE std_id = ?)
    """,
        (student_id, student_id),
    )

    eligible_courses = cursor.fetchall()
    conn.close()

    return render_template("enroll.html", courses=eligible_courses)


@app.route("/drop")
def drop():
    return render_template("drop.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")
