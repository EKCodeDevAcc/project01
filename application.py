import os
import requests
import datetime

from flask import Flask, session, render_template, request, redirect, json, jsonify, url_for, abort
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


# If user logged in, go to main page, 'index'
# If not, it redirects user to login page.
@app.route("/")
def login():
    username = session.get('user')
    if session.get('user'):
        return render_template('index.html', message=username)
    else:
        return render_template("login.html")


#Get input value from login.html and check if given username/password exist in db.
@app.route("/loginPost", methods=['POST'])
def loginPost():
    username = request.form.get("username")
    password = request.form.get("password")

    #If username/password does not match, return to error page with error message
    if db.execute("SELECT * FROM members WHERE (username = :username) AND (password = :password)", {"username": username, "password": password}).rowcount != 1:

        #Title that shows what kind of error occured
        error_title = "Fail to Login"

        #This is a hyperlink of button that will be shown in error page
        button_link = "/"

        #This will be a name of the error button
        button_message = "Back to Login Page"

        #Sends all information with message says detail of error. Same format for all other error pages below
        return render_template("error.html", message="Wrong username or password. Please try again", error_title=error_title, button_link=button_link, button_message=button_message)

    #If there is a user, login, and go back to main page with message which is username
    else:
        session['user'] = username
        return redirect(url_for('index', message=username))


#Logout user and redirect to '/' which in this case, login page.
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect('/')


#Simply goes to sign up page.
@app.route("/signUp")
def signUp():
    return render_template("signUp.html")


#When user input new username and password, check if it is valid.
@app.route("/signUpPost", methods=['POST'])
def signUpPost():
    username = request.form.get("username")
    password = request.form.get("password")

    #If given new username already exists in database, send error message and redirect to sign up page.
    if db.execute("SELECT * FROM members WHERE username = :username", {"username": username}).rowcount != 0:
        error_title = "Username Already Exists"
        button_link = "/signUp"
        button_message = "Back to Sign Up Page"
        return render_template("error.html", message="That username already exists. Please try different username", error_title=error_title, button_link=button_link, button_message=button_message)

    #If not, then insert new data into members table then redirect to success page.
    db.execute("INSERT INTO members (username, password) VALUES (:username, :password)", {"username": username, "password": password})

    db.commit()
    return render_template("success.html")


#This is main page that users will go to when they are logged in and direct to '/'
@app.route("/index")
def index():
    username = session.get('user')
    return render_template('index.html', message=username)


#User input keyword to seach matching results
@app.route("/search", methods=['POST'])
def search():
    username = session.get('user')
    keyword = request.form.get("search").upper()

    #If there is no matching results that either zipcode or city's substring matches with keyword, return error message.
    if db.execute("SELECT * FROM zips WHERE (zipcode ~ :keyword) OR (city ~ :keyword)", {"keyword": keyword}).rowcount == 0:
        error_title = "No Result"
        button_link = "/"
        button_message = "Back to Main Page"
        return render_template("error.html", message="No result", error_title=error_title, button_link=button_link, button_message=button_message)

    #If there is matching resutls, redirect to list page with list of information
    else:
        result_list = db.execute("SELECT * FROM zips WHERE (zipcode ~ :keyword) OR (city ~ :keyword)", {"keyword": keyword}).fetchall()
        return render_template("list.html", result_list=result_list, message=username)


#Return information of certain city where its zipcode is select_zip
@app.route("/location/<string:select_zip>")
def location(select_zip):
    username = session.get('user')

    #There are 3 steps
    #First, check if this end user is logged in, if the user is logged in, moving on. But if he/she isn't logged in, go to last else statement.
    if session.get('user'):

        #Then check if there is a city with given zipcode, select_zip. If there is, go to the last step
        if db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip}).rowcount == 1:

            #If user is logged in and zipcode is valid, then get information of location and list of comments belong to this city.
            location_list = db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip})
            comment_list = db.execute("SELECT * FROM comments WHERE zipcode = :zipcode", {"zipcode": select_zip})

            #get latitude of longitude of city which will be used to get information from darksky
            current_latitude = str(db.execute("SELECT latitude FROM zips WHERE (zipcode = :zipcode)", {"zipcode": select_zip}).fetchone()[0])
            current_longitude = str(db.execute("SELECT longitude FROM zips WHERE (zipcode = :zipcode)", {"zipcode": select_zip}).fetchone()[0])

            #get time, summary, temp, dewPoint, and humidity
            weather = requests.get("https://api.darksky.net/forecast/f9f349f903f5d2f2f93565b27de10eb9/" + current_latitude + "," + current_longitude).json()

            #subtract 4 hours from GMT
            weather_time = datetime.datetime.fromtimestamp(int(weather["currently"]["time"]-4*60*60)).strftime('%Y-%m-%d %H:%M:%S')
            weather_summary = weather["currently"]["summary"]
            weather_temperature = weather["currently"]["temperature"]
            weather_dewPoint = weather["currently"]["dewPoint"]

            #Multiply 100 to display it as %
            weather_humidity = weather["currently"]["humidity"] * 100

            #this checks if the current user already checked in about current location. If he/she already checked in, return check_list as yes
            if db.execute("SELECT * FROM comments WHERE (zipcode = :zipcode) AND (username = :username)", {"zipcode": select_zip, "username": username}).rowcount == 1:

                #If check_list is yes, in location page, comment submit form will be hidden
                check_list = "yes"
                return render_template("location.html", location_list=location_list, check_list=check_list, weather_time=weather_time, weather_summary=weather_summary,
                weather_temperature=weather_temperature, weather_dewPoint=weather_dewPoint, weather_humidity=weather_humidity, message=username, current_zipcode=select_zip, comment_list=comment_list)

            #If not, return check_list as no.  Return all information we got from db and darksky together
            else:

                #If check_list is no, in location page, comment submit form will be shown
                check_list = "no"
                return render_template("location.html", location_list=location_list, check_list=check_list, weather_time=weather_time, weather_summary=weather_summary,
                weather_temperature=weather_temperature, weather_dewPoint=weather_dewPoint, weather_humidity=weather_humidity, message=username, current_zipcode=select_zip, comment_list=comment_list)

        #If there is no such city where its zipcode is select_zip, go to error message and notify there is no city with select_zipcode
        else:
            error_title = "No Result"
            button_link = "/"
            button_message = "Back to Main Page"
            return render_template("error.html", message="No Result", error_title=error_title, button_link=button_link, button_message=button_message)

    #If user isn't logged in, go to error page and says user has no access and tells he/she has to log in first
    else:
        error_title = "No Access"
        button_link = "/"
        button_message = "Back to Login Page"
        return render_template("error.html", message="You have no access. Please login and try again", error_title=error_title, button_link=button_link, button_message=button_message)


#If user click submit button in location page, this function works
@app.route("/commentPost", methods=['POST'])
def commentPost():

    #get current username, zipcode, and comment the user left(this can be blank), submit the information into comments table
    username = session.get('user')
    zipcode = request.form.get("zipcode")
    comment = request.form.get("comment")

    db.execute("INSERT INTO comments (username, zipcode, comment) VALUES (:username, :zipcode, :comment)", {"username": username, "zipcode": zipcode, "comment": comment})

    db.commit()

    #then redirect to current location page with updated information
    return redirect("/location/" + zipcode)


#this allows users to access to API
@app.route("/api/location/<string:select_zip>")
def location_api(select_zip):

    #If typed zipcode does not exist, return 404 error response code
    if db.execute("SELECT * FROM zips WHERE zipcode = :zipcode", {"zipcode": select_zip}).rowcount == 0:
        return jsonify({"error": "404 Not Found - zipcode does not exist."}), 404

    #If not, return resulting JSON with all information about the city and number of comments belong to the city
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