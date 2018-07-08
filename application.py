import os

from flask import Flask, session, render_template, request, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app._static_folder = "static"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def displayLogin():
    return render_template("login.html")

@app.route("/displaySignUp")
def displaySignUp():
    name_list = db.execute("SELECT * FROM members").fetchall()
    return render_template("signUp.html", name_list=name_list)

@app.route("/sign", methods=['POST'])
def sign():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM members WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("error.html", message="That username already exists. Please try different username")

    db.execute("INSERT INTO members (username, password) VALUES (:username, :password)", {"username": username, "password": password})

    db.commit()
    return render_template("success.html")