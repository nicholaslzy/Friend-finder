import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmation")
        username = request.form.get("username")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmpassword:
            return apology("must confirm password", 400)
        elif password != confirmpassword:
            return apology("passwords must match", 400)


        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already exists", 400)

        password_hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
            new_user = db.execute("SELECT id FROM users WHERE username = ?", username)
            user_id = new_user[0]["id"]
            # remembers user as user_id next time website is visited
            session["user_id"] = user_id
            flash("Registered successfully!", 'success')
            return redirect("/")
        except Exception as e:
            return apology("error occurred during registration", 400)

    else:
        return render_template("register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Show account information"""
    user_id = session["user_id"]
    if request.method == "GET":

        # get username to display on account page
        user = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        return render_template("account.html", username=user[0]['username'])

    if request.method == "POST":

        # get password hash from data base and convert it to text, compare it against the fields
        plain_text_password = request.form.get("password")
        hashed_password = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
        hashed_password = hashed_password[0]['hash']
        if not check_password_hash( hashed_password, plain_text_password):
            return apology("wrong password", 400)
        elif len(request.form.get("newpassword")) < 3:
            return apology("password is too short", 400)
        elif request.form.get("newpassword") != request.form.get("confirmnewpassword"):
            return apology("passwords do not match", 400)
        else:
            new_password = request.form.get("newpassword")
            new_hashed_password = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hashed_password, user_id)
            flash('Password changed successfully', 'success')
            return redirect("index.html")

@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
    user_id = session["user_id"]
    if request.method == "GET":

        user = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        user_info = db.execute("SELECT * FROM users_info WHERE user_id = ?", user_id)
        if user_info:
            user_info = user_info[0]
        else:
            user_info = {}
        return render_template("info.html", username=user[0]['username'], user_info=user_info)

    if request.method == "POST":
        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        school = request.form.get("school")
        course = request.form.get("course")
        if (db.execute("SELECT * FROM users_info WHERE user_id = ?", user_id)):
            db.execute("UPDATE users_info SET name = ?, age = ?, gender = ?, school = ?, course = ? WHERE user_id = ?", name, age, gender, school, course, user_id)
            flash('Information updated successfully!', 'success')
            return redirect('/')

        else:
            db.execute("INSERT INTO users_info (user_id, name, age, gender, school, course) VALUES (?, ?, ?, ?, ?, ?)", user_id, name, age, gender, school, course)
            flash('Information added successfully!', 'success')
            return redirect('/')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/requests", methods=["GET", "POST"])
@login_required
def requests():
    user_id = session["user_id"]
    if request.method == "GET":
        friend_requests = db.execute(
            "SELECT u.*, fr.status "
            "FROM users_info u "
            "JOIN friend_requests fr ON u.user_id = fr.receiver_id "
            "WHERE fr.sender_id = ? AND fr.status = 'pending'",
            user_id
        )

        return render_template("requests.html", friend_requests=friend_requests)



@app.route("/declineFriendRequest", methods=["POST"])
@login_required
def declineFriendRequest():
    user_id = session["user_id"]
    if request.method == "POST":
        friend_id_decline = request.form.get("friend_id_decline")
        if friend_id_decline:
        # Ensure user_id is always less than friend_id to avoid duplicate entries
            sender_id, receiver_id = user_id, int(friend_id_decline)
        if sender_id > receiver_id:
                sender_id, receiver_id = receiver_id, sender_id
        try:
            db.execute("UPDATE friend_requests SET status = 'Declined' WHERE sender_id = ? AND receiver_id = ?", sender_id, receiver_id)
            return 'Friend request declined', 200
        except Exception as e:
            return "An error occurred", 500

@app.route("/acceptFriendRequest", methods=["POST"])
@login_required
def acceptFriendRequest():
    user_id = session["user_id"]
    if request.method == "POST":
        friend_id_accept = request.form.get("friend_id_accept")
        if friend_id_accept:
            # Ensure user_id is always less than friend_id to avoid duplicate entries
            sender_id, receiver_id = user_id, int(friend_id_accept)
        if sender_id > receiver_id:
            sender_id, receiver_id = receiver_id, sender_id
        try:
            db.execute("UPDATE friend_requests SET status = 'Accepted' WHERE sender_id = ? AND receiver_id = ?", sender_id, receiver_id)
            db.execute("INSERT INTO relationships (user_id, friend_id) VALUES (?, ?)", sender_id, receiver_id)
            return 'Friend request Accepted', 200
        except Exception as e:
            return "An error occurred", 500


@app.route("/findfriends", methods=["GET", "POST"])
@login_required
def findfriends():
    user_id = session["user_id"]
    if request.method == "POST":
        friend_id = request.form.get("friend_id")

        if friend_id:
            # Ensure user_id is always less than friend_id to avoid duplicate entries
            sender_id, receiver_id = user_id, int(friend_id)
            if sender_id > receiver_id:
                sender_id, receiver_id = receiver_id, sender_id

            existing_request = db.execute("SELECT * FROM friend_requests WHERE sender_id = ? AND receiver_id = ? AND status = 'pending'", sender_id, receiver_id)
            if not existing_request:
                db.execute("INSERT INTO friend_requests (sender_id, receiver_id, status) VALUES (?, ?, 'pending')", sender_id, receiver_id)

            return "Success", 200

    if request.method == "GET":
        user_list = db.execute(
            "SELECT users_info.*, friend_requests.status FROM users_info "
            "LEFT JOIN friend_requests ON ((users_info.user_id = friend_requests.receiver_id AND friend_requests.sender_id = ?) "
            "OR (users_info.user_id = friend_requests.sender_id AND friend_requests.receiver_id = ?)) "
            "WHERE users_info.user_id != ? AND (friend_requests.status IS NULL OR friend_requests.status = 'pending')",
            user_id, user_id, user_id
        )
        print(user_list)
        return render_template("findfriends.html", user_list=user_list)


@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    user_id = session["user_id"]
    if request.method == "GET":
        friends = db.execute(
            "SELECT u.* "
            "FROM users_info u "
            "JOIN relationships r ON (u.user_id = r.friend_id AND r.user_id = ?) "
            "OR (u.user_id = r.user_id AND r.friend_id = ?)",
            user_id, user_id
        )
        print(friends)
        return render_template("index.html", friends=friends)






