from flask import Flask, render_template

grades_app = Flask(__name__)

@grades_app.route("/")
def gradespage():
    return render_template("grade.html")

def grades_web():
    return 'Helow, Worlde!'
@grades_app.route("/about")
def about():
    return "About"

if __name__ == "__main__":
    grades_app.run(debug=True,port='9000')
