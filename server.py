"""Movie Ratings."""

from flask.helpers import url_for
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session 
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.sql.functions import user

from model import connect_to_db, db, User, Rating, Movie

from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')

@app.route('/users')
def user_list():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/user/<user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    return render_template('user.html', user=user)

@app.route('/register')
def register_user():

    return render_template('register.html')

@app.route('/registration')
def registration():
    email = request.args.get("email")
    password = request.args.get("password")
    age = request.args.get("age")
    zipcode = request.args.get("zipcode")

    passhash = generate_password_hash(password)
    user_id = db.session.query(func.max(User.user_id) + 1)
    new_user = User(user_id=user_id, email=email, password=passhash, age=age, zipcode=zipcode)

    db.session.add(new_user)
    db.session.commit()
    flash("User added successfully")

    return redirect(url_for("login"))

@app.route('/login')
def login():

    return render_template('login.html')

@app.route('/loginuser')
def login_user():
    email = request.args.get("email")
    password = request.args.get("password")
    users = User.query.all()

    for user in users:
        if user.email == email and check_password_hash(user.password, password):
            session['logged_in_user_id'] = user.user_id
            logged_in_user_id = user.user_id
            break
    
    if 'logged_in_user_id' in session.keys():
        user = User.query.get(logged_in_user_id)
        flash(f"Logged in user with user id: {logged_in_user_id}")
    else:
        flash("No user found for that email.")
        return redirect('/login')
    return render_template("user.html", user=user)

@app.route('/logout')
def logout():
    session.pop("logged_in_user_id", None)
    flash("Logged out user.")
    return redirect('/')

@app.route('/movies')
def show_all_movies():
    movies = Movie.query.all()

    return render_template("movies.html", movies=movies)

@app.route('/movie/<movie_id>')
def show_movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    reviews = Rating.query.filter_by(movie_id=movie.movie_id)

    return render_template("movie.html", movie=movie, reviews=reviews)
    

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    app.run(port=5000, host='0.0.0.0')
