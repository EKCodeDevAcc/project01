import os
import requests
import datetime

from flask import Flask, session, render_template, request, redirect, json, jsonify, url_for
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
        error_title = "Fail to Login"
        button_link = "/"
        button_message = "Back to Login Page"
        return render_template("error.html", message="Wrong username or password. Please try again", error_title=error_title, button_link=button_link, button_message=button_message)
    else:
        session['user'] = username
        return redirect(url_for('index', message=username))


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route("/signUp")
def signUp():
    return render_template("signUp.html")


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
    return render_template('index.html', message=username)


@app.route("/search", methods=['POST'])
def search():

    username = session.get('user')
    keyword = request.form.get("search").upper()

    if db.execute("SELECT * FROM zips WHERE (zipcode ~ :keyword) OR (city ~ :keyword)", {"keyword": keyword}).rowcount == 0:
        return render_template("error.html", message="No result")
    else:
        result_list = db.execute("SELECT * FROM zips WHERE (zipcode ~ :keyword) OR (city ~ :keyword)", {"keyword": keyword}).fetchall()
        return render_template("list.html", result_list=result_list, message=username)


@app.route("/location/<string:select_zip>")
def location(select_zip):
    username = session.get('user')

    if session.get('user'):
        if db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip}).rowcount == 1:
            location_list = db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip})

            comment_list = db.execute("SELECT * FROM comments WHERE zipcode = :zipcode", {"zipcode": select_zip})

            current_latitude = str(db.execute("SELECT latitude FROM zips WHERE (zipcode = :zipcode)", {"zipcode": select_zip}).fetchone()[0])
            current_longitude = str(db.execute("SELECT longitude FROM zips WHERE (zipcode = :zipcode)", {"zipcode": select_zip}).fetchone()[0])

            weather = requests.get("https://api.darksky.net/forecast/f9f349f903f5d2f2f93565b27de10eb9/" + current_latitude + "," + current_longitude).json()
            weather_time = datetime.datetime.fromtimestamp(int(weather["currently"]["time"]-4*60*60)).strftime('%Y-%m-%d %H:%M:%S')
            weather_summary = weather["currently"]["summary"]
            weather_temperature = weather["currently"]["temperature"]
            weather_dewPoint = weather["currently"]["dewPoint"]
            weather_humidity = weather["currently"]["humidity"] * 100

            if db.execute("SELECT * FROM comments WHERE (zipcode = :zipcode) AND (username = :username)", {"zipcode": select_zip, "username": username}).rowcount == 1:
                check_list = "yes"
                return render_template("location.html", location_list=location_list, check_list=check_list, weather_time=weather_time, weather_summary=weather_summary,
                weather_temperature=weather_temperature, weather_dewPoint=weather_dewPoint, weather_humidity=weather_humidity, message=username, current_zipcode=select_zip, comment_list=comment_list)
            else:
                check_list = "no"
                return render_template("location.html", location_list=location_list, check_list=check_list, weather_time=weather_time, weather_summary=weather_summary,
                weather_temperature=weather_temperature, weather_dewPoint=weather_dewPoint, weather_humidity=weather_humidity, message=username, current_zipcode=select_zip, comment_list=comment_list)
        else:
            error_title = "No Result"
            button_link = "/"
            button_message = "Back to Main Page"
            return render_template("error.html", message="No Result", error_title=error_title, button_link=button_link, button_message=button_message)
    else:
        error_title = "No Access"
        button_link = "/"
        button_message = "Back to Login Page"
        return render_template("error.html", message="You have no access. Please login and try again", error_title=error_title, button_link=button_link, button_message=button_message)




@app.route("/commentPost", methods=['POST'])
def commentPost():

    username = session.get('user')
    zipcode = request.form.get("zipcode")
    comment = request.form.get("comment")

    db.execute("INSERT INTO comments (username, zipcode, comment) VALUES (:username, :zipcode, :comment)", {"username": username, "zipcode": zipcode, "comment": comment})

    db.commit()
    return redirect("/location/" + zipcode)


@app.route("/api/location/<string:select_zip>")
def location_api(select_zip):
    if db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip}).rowcount == 0:
        return jsonify({"error: zipcode does not exist."}), 442
    else:
        result_list = db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip}).fetchone()
        comment_number = db.execute("SELECT COUNT(comments.zipcode) FROM comments WHERE zipcode = :zipcode", {"zipcode": select_zip}).fetchone()
        return jsonify({
            "zip": result_list[0],
            "city": result_list[1],
            "state": result_list[2],
            "latitude": str(result_list[3]),
            "longitude": str(result_list[4]),
            "population": str(result_list[5]),
            "check_ins": str(comment_number[0])
        })