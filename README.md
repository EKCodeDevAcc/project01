This is Edward Kang's Project 1.

This is a web allows users to login, logout, search cities with either their name or zipcode which comes with several different features.

README.md
- Include a short writeup describing the project, what's contained in each file.

import.py
- Read csv file and insert given data into SQL table.

layout.html
- Contians common feature of websites.
- Calls bootstrap and local css files.
- Calls title and body blocks.
- When a user clicks title, 'Edward Kang's Project 1!', if a user is logged in, it redirects a user to main page.
- If not, it redirects a user to login page.

singUp.html
- A user can input username and password to create his/her account.
- Click cancel button allows a user to go back to login page.

login.html
- A user can input username and password to login to the website.
- If a user types wrong username/password combination, redirects to error page.
- Click sign up button allows a user to go to sign up page.
- If input username/password exist, redirects to main page.

error.html
- Display error messages depends on error type.
- If a user failed to login due to wrong username/password, display wrong username/password error message.
- If a user try to access to location information webpage directly without login, display no access error message.
- If username that user input already exists, display username already exists error message.
- If there is no matching results when a user input keyword for cities, display no results error message.

success.html
- Display success message when user create new username with password.

index.html
- When a user successfully login, this page would pop up as a main page.
- It display name of the page, 'main' and display welcome message with username on the right side.
- If a user clicks logout button on the right side, user can logout of the site.
- A user can search cities by typing zipcode or name of cities.
- When a user searches cities, he/she can type partial information and still find matching results.

list.html
- It display name of the page, 'main' and display welcome message with username on the right side.
- If a user clicks logout button on the right side, user can logout of the site.
- When there is matching results, this page displays a list of possible matching results.
- It displays results in table form which includes zipcode, city, state, latitude, longitude, and population columns.
- If a user clicks zipcode, it redirects user into location page.

location.html
- It display name of the page, 'main' and display welcome message with username on the right side.
- If user clicks logout button on the right side, user can logout of the site.
- This page shows more details of choosen city.
- A user can check current time, summary of weather, temperature, dew point, and humidity of choosen city.
- If a user never checked in before, user can check-in by clicking submit button.
- If a user input comment, it can save user's comment together. User can submit check-in without comment.
- Once a user submits check-in, it refreshs the page and user can see updated list of check-in comments.
- A user will not be able to see submit section after they made their submission.

application.py
- It contains most functions above that this website uses.
- One thing I didn't mention is API access which is included in this file.
- When a user goes to /api/location/<zipcode>, it displays number of check-ins, city, latitude, longitude, state, and zipcode.
- If input zipcode is invalid, it return 404 error and error message.

style.css
- It is css file for basic design of this website.