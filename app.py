from flask import Flask, redirect, render_template, request, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Secret"

# Database setup
con = sqlite3.connect("users.db", check_same_thread=False)
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
""")
con.commit()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/sing')
def sing():
    return render_template("register.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("Enter all fields")
            return redirect('/sing')

       
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        if user:
            flash("User already exists!")
            return redirect("/sing")

       
        hashed = generate_password_hash(password)

        cur.execute("INSERT INTO users(name,email,password) VALUES (?,?,?)",
                    (name, email, hashed))
        con.commit()

        flash("Register successful! Please login")
        return redirect('/')

    return redirect('/sing')


@app.route('/login', methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    data = cur.fetchone()

    if not data:
        flash("User not found, please register first")
        return redirect('/sing')

    db_password = data[3]

    if not check_password_hash(db_password, password):
        flash("Wrong password")
        return redirect('/')

    session['user'] = email
    flash("Login Successful!")
    return redirect("/dashboard")


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    return f"{session['user']} Welcome to Dashboard!"


if __name__ == "__main__":
    app.run(debug=True)
