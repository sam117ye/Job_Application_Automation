# import libraries
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["DEBUG"] = True

db = SQLAlchemy(app)
# create db
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    website = db.Column(db.String, nullable=False)
    education = db.Column(db.String, nullable=False)
    current_situation = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)

with app.app_context():
        db.create_all()

# create app
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# create routes
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        phone = request.form.get("phone")
        password = request.form.get("password")

        if not phone or not password:
            flash("All fields are required")
            return redirect("/login")

        user = Users.query.filter_by(phone=phone).first()

        if not user or not check_password_hash(user.hash, password):
            flash("Invalid phone number and/or password")
            return redirect("/login")

        session["user_id"] = user.id

        flash("Logged in successfully")

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html") 
    else:

        name = request.form.get("name")
        address = request.form.get("address")
        birthdate = request.form.get("birthdate")

        email = request.form.get("email")
        phone = request.form.get("phone")
        website = request.form.get("website")

        education = request.form.get("education")
        current_situation = request.form.get("current_situation")
        goals = request.form.get("goals")


        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not name or not address or not birthdate or not email or not phone or not website or not education or not current_situation or not goals or not password or not confirmation:
            flash("All fields are required")
            return redirect("/register")
        
        if phone.isdigit() == False:
            flash("Phone number should contain only digits")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        
        existing_user = Users.query.filter_by(phone=phone).first()
        if existing_user:
            flash("User with this phone number already exists")
            return redirect("/register")
        
        hash = generate_password_hash(password)

        try:
            new_user = Users(name=name, address=address, birthdate=birthdate, email=email, phone=phone, website=website, education=education, current_situation=current_situation, goals=goals, hash=hash)
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            

            flash("Registered successfully")

            return redirect("/")

        except Exception as e:
            print(e)
            flash("error: " + str(e))
        
        return redirect("/")
"""
*sign up
- name
- address
- birthdate
- email
- phone
- website
- education
- Current Situation
- Goals
- password

*login
*logout

"""
if __name__ == "__main__":
    app.run(debug=True)