import os

import psycopg
from flask import Flask, render_template, redirect, request

app = Flask(__name__)

def get_database_url():
    if os.environ.get("APP_ENV") == "PRODUCTION":
        password = os.environ.get("POSTGRES_PASSWORD")
        hostname = os.environ.get("POSTGRES_HOSTNAME")
        return f"postgres://postgres:{password}@{hostname}:5432/postgres"
    else:
        return "postgres://localhost:5432/postgres"

db_url = get_database_url()

def setup_database(url):
    connection = psycopg.connect(url)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(username VARCHAR(25), password VARCHAR(255));")
    connection.commit()
    
    
def insert_user(url, username, password):
    connection = psycopg.connect(url)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users(username, password) VALUES (%s, %s)" , (username, password))
    try:
        connection.commit()
        return 'Success'
    except Exception as e:
        return e.message
    
def find_user(url, username, password):
    connection = psycopg.connect(url)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE USERNAME = %s AND PASSWORD = %s", (username, password))
    try:
        connection.commit()
        return 'Success'
    except Exception as e:
        return e.message


@app.route("/", methods=["GET"])
def home():
    return render_template("welcome.html")

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return render_template("login.html", "Username is missing.")
        if not password:
            return render_template("login.html", "Password is missing.")
        result = insert_user(url=db_url, username=username, password=password)
        if result == "Success":
            return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        if not username:
            return render_template("login.html", "Username is missing.")
        if not password:
            return render_template("login.html", "Password is missing.")
        result = find_user(url=db_url, username=username, password=password)
        if result == "Success":
            return redirect(f"/profile/{username}")
    return render_template("login.html")

@app.route('/profile/<username>', methods=['GET'])
def profile(username):
    return render_template('profile.html', username=username)


if __name__ == "__main__":
    setup_database(db_url)
    if os.environ.get("APP_ENV") == "PRODUCTION":
        app.run(port=5000, host='0.0.0.0')
    else:
        app.run(debug=True, port="5000", host="0.0.0.0")
