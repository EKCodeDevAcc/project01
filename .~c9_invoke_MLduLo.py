import os

from flask import Flask, session, render_template, request, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
    return render_template("signup.html")

@app.route("/signUp", methods=['POST'])
def signUp():
    input_username = request.form['username']
    input_password = request.form['password']

    if input_username and input_password:
        return json.dumps({'html': '<span>All Good!</span>'})
    else:
        return json.dumps({'html': '<span>Please Enter All Required Fields.</span>'})