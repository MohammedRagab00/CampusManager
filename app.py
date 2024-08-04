from flask import Flask, render_template

app = Flask(__name__)

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route for Grade
@app.route("/grade")
def grade():
    return render_template("grade.html")

# Route for Enroll
@app.route("/enroll")
def enroll():
    return render_template("enroll.html")

# Route for Drop
@app.route("/drop")
def drop():
    return render_template("drop.html")

# Route for Profile
@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Default port is 5000; change to another port if needed
