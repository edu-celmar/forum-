
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "min-hemliga-nyckel"


# Koppla till databasen
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="forum_farskallar"
    )


# Startsida och visa inlägg
@app.route("/", methods=["GET", "POST"])
def index():

    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        text = request.form["text"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO posts (name, text) VALUES (%s, %s)",
            (session["username"], text)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = cur.fetchall()

    conn.close()

    return render_template("index.html", posts=posts)



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()

        except mysql.connector.IntegrityError:
            conn.close()
            return "Användarnamnet finns redan!"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# Logga in
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )

        user = cur.fetchone()

        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("index"))

        return "Fel användarnamn eller lösenord!"

    return render_template("login.html")



@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
