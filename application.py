import os

from flask import Flask, session, render_template, request, redirect, json, url_for
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
def login():
    username = session.get('user')
    if session.get('user'):
        return render_template('index.html', message=username)
    else:
        return render_template("login.html")

@app.route("/loginPost", methods=['POST'])
def loginPost():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM members WHERE (username = :username) AND (password = :password)", {"username": username, "password": password}).rowcount != 1:
        return render_template("error.html", message="Wrong username or password. Please try again")
    else:
        session['user'] = username
        return redirect(url_for('index', message=username))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route("/signUp")
def signUp():
    name_list = db.execute("SELECT * FROM members").fetchall()
    return render_template("signUp.html", name_list=name_list)

@app.route("/signUpPost", methods=['POST'])
def signUpPost():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM members WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("error.html", message="That username already exists. Please try different username", error_title="Sign Up")

    db.execute("INSERT INTO members (username, password) VALUES (:username, :password)", {"username": username, "password": password})

    db.commit()
    return render_template("success.html")

@app.route("/index")
def index():
    username = session.get('user')
    if session.get('user'):
        return render_template('index.html', message=username)
    else:
        return render_template("error.html", message="Please login to access", error_title="Log In", error_button="/")