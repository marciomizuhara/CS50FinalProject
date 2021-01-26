import smtplib
import os
import requests
import json
import time
import datetime
import getpass

from os import environ
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Set global constants
API_KEY = '0a070746b4484a55135492be92179ac0'
USER_AGENT = 'Mizuhara'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


# Create confirmation function to shorten some coding
def is_provided(field):
    if not request.form.get(field):
        return apology(f"must provide {field}", 403)


# Index
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        find_missing_errors = is_provided("lastfmusername")
        if find_missing_errors:
            return find_missing_errors

        # Getting form data
        option = request.form.get("option")
        lastfmusername = request.form.get("lastfmusername")
        session["lastfmusername"] = lastfmusername

        # Redirect according to option chosen
        if option == "user_info":
            return redirect("/user_info")

        if option == "recently_played_tracks":
            return redirect("/recently_played_tracks")

        if option == "weekly_charts":
            return redirect("/weekly_charts")

        elif option == "all_time_top_albums":
            return redirect("/all_time_top_albums")

        elif option == "all_time_top_tracks":
            return redirect("/all_time_top_tracks")

        elif option == "all_time_top_artists":
            return redirect("/all_time_top_artists")

        else:
            pass

    else:
        return render_template("index.html")


# User Info
@app.route("/user_info", methods=["GET", "POST"])
@login_required
def user_info():

    # Set the userlastfmusername into session
    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    r = lastfm_get({'method': 'user.getinfo'})

    registered = r.json()['user'].get('registered').get('#text')

    user_information = {
        # Run the queries
        "avatar": r.json()['user']['image'][2].get('#text'),
        "realname": r.json()['user'].get('realname'),
        "country": r.json()['user'].get('country'),
        "playcount": r.json()['user'].get('playcount'),
        "registration_date": datetime.datetime.fromtimestamp(registered),
        "url": r.json()['user'].get('url')
    }

    return render_template("/user_info.html", user_information=user_information, username=username)


# recently Played Tracks
@app.route("/recently_played_tracks", methods=["GET", "POST"])
@login_required
def recently_played_tracks():
    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    # Run the queries
    r = lastfm_get({'method': 'user.getinfo'})

    avatar = r.json()['user']['image'][2].get('#text')

    r = lastfm_get({'method': 'user.getrecenttracks'})

    # cover
    recent_played_tracks_cover = []
    n = 0
    while n < 10:
        cover = r.json()['recenttracks']['track'][n]['image'][3].get('#text')
        recent_played_tracks_cover.append(cover)
        n = n + 1

    # artist
    recent_played_tracks_artist = []
    n = 0
    while n < 10:
        artist = r.json()['recenttracks']['track'][n]['artist']['#text']
        recent_played_tracks_artist.append(artist)
        n = n + 1

    # track
    recent_played_tracks_track = []
    n = 0
    while n < 10:
        track = r.json()['recenttracks']['track'][n]['name']
        recent_played_tracks_track.append(track)
        n = n + 1

    return render_template("/recently_played_tracks.html", avatar=avatar,
                           recent_played_tracks_cover=recent_played_tracks_cover,
                           recent_played_tracks_artist=recent_played_tracks_artist,
                           recent_played_tracks_track=recent_played_tracks_track,
                           username=username
                           )


# Weekly Top Charts
@app.route("/weekly_charts", methods=["GET", "POST"])
@login_required
def weeklytopartists():

    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    # Run the queries
    r = lastfm_get({'method': 'user.getinfo'})

    avatar = r.json()['user']['image'][2].get('#text')

    # WEEKLY TOP TRACKS
    r = lastfm_get({'method': 'user.getWeeklyTrackChart'})

    # track
    weekly_tracks_track = []
    n = 0
    while n < 10:
        artist = r.json()['weeklytrackchart']['track'][n].get('name')
        weekly_tracks_track.append(artist)
        n = n + 1

    # artist
    weekly_tracks_artist = []
    n = 0
    while n < 10:
        artist = r.json()['weeklytrackchart']['track'][n]['artist'].get('#text')
        weekly_tracks_artist.append(artist)
        n = n + 1

    # playcount
    weekly_tracks_playcount = []
    n = 0
    while n < 10:
        artist = r.json()['weeklytrackchart']['track'][n].get('playcount')
        weekly_tracks_playcount.append(artist)
        n = n + 1

    # WEEKLY TOP ARTISTS
    r = lastfm_get({
        'method': 'user.getWeeklyArtistChart'

    })

    # artist
    weekly_artists_artist = []
    n = 0
    while n < 10:
        artist = r.json()['weeklyartistchart']['artist'][n]['name']
        weekly_artists_artist.append(artist)
        n = n + 1

    # playcount
    weekly_artists_playcount = []
    n = 0
    while n < 10:
        artist = r.json()['weeklyartistchart']['artist'][n]['playcount']
        weekly_artists_playcount.append(artist)
        n = n + 1

    # WEEKLY TOP ALBUMS
    r = lastfm_get({'method': 'user.getWeeklyAlbumChart'})

    # album
    weekly_albums_album = []
    n = 0
    while n < 20:
        album = r.json()['weeklyalbumchart']['album'][n].get('name')
        weekly_albums_album.append(album)
        n = n + 1

    # artist
    weekly_albums_artist = []
    n = 0
    while n < 10:
        artist = r.json()['weeklyalbumchart']['album'][n]['artist'].get('#text')
        weekly_albums_artist.append(artist)
        n = n + 1

    # playcount
    weekly_albums_playcount = []
    n = 0
    while n < 10:
        playcount = r.json()['weeklyalbumchart']['album'][n].get('playcount')
        weekly_albums_playcount.append(playcount)
        n = n + 1

    return render_template("/weekly_charts.html", avatar=avatar,
                           weekly_tracks_track=weekly_tracks_track, weekly_tracks_artist=weekly_tracks_artist,
                           weekly_tracks_playcount=weekly_tracks_playcount, weekly_artists_artist=weekly_artists_artist,
                           weekly_artists_playcount=weekly_artists_playcount, weekly_albums_album=weekly_albums_album,
                           weekly_albums_artist=weekly_albums_artist, weekly_albums_playcount=weekly_albums_playcount,
                           username=username
                           )


# All Time Top Tracks
@app.route("/all_time_top_tracks", methods=["GET", "POST"])
@login_required
def alltimetoptracks():

    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    # Run the queries
    r = lastfm_get({
        'method': 'user.getinfo'

    })

    avatar = r.json()['user']['image'][2].get('#text')

    r = lastfm_get({
        'method': 'user.getTopTracks'

    })

    # Track name
    all_time_top_tracks_track = []
    n = 0
    while n < 50:
        tracks = r.json()['toptracks']['track'][n].get('name')
        all_time_top_tracks_track.append(tracks)
        n = n + 1

    # Track artist
    all_time_top_tracks_artist = []
    n = 0
    while n < 50:
        artist = r.json()['toptracks']['track'][n].get('artist').get('name')
        all_time_top_tracks_artist.append(artist)
        n = n + 1

    # Track playcount
    all_time_top_tracks_playcount = []
    n = 0
    while n < 50:
        playcount = r.json()['toptracks']['track'][n].get('playcount')
        all_time_top_tracks_playcount.append(playcount)
        n = n + 1

    return render_template("/all_time_top_tracks.html", avatar=avatar,
                           all_time_top_tracks_track=all_time_top_tracks_track,
                           all_time_top_tracks_artist=all_time_top_tracks_artist,
                           all_time_top_tracks_playcount=all_time_top_tracks_playcount,
                           username=username
                           )


# All Time Top Artists
@app.route("/all_time_top_artists", methods=["GET", "POST"])
@login_required
def alltimetoptartists():

    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    # Run the queries
    r = lastfm_get({
        'method': 'user.getinfo'

    })

    avatar = r.json()['user']['image'][2].get('#text')

    r = lastfm_get({
        'method': 'user.getTopArtists'

    })

    # Artist Name
    all_time_top_artists_name = []
    n = 0
    while n < 50:
        artist = r.json()['topartists']['artist'][n].get('name')
        all_time_top_artists_name.append(artist)
        n = n + 1

    # Artist playcount
    all_time_top_artists_playcount = []
    n = 0
    while n < 50:
        playcount = r.json()['topartists']['artist'][n].get('playcount')
        all_time_top_artists_playcount.append(playcount)
        n = n + 1

    return render_template("/all_time_top_artists.html", avatar=avatar,
                           all_time_top_artists_name=all_time_top_artists_name,
                           all_time_top_artists_playcount=all_time_top_artists_playcount,
                           username=username
                           )


# All Time Top Albums
@app.route("/all_time_top_albums", methods=["GET", "POST"])
@login_required
def alltimetopalbums():

    if "lastfmusername" not in session:
        session["lastfmusername"] = session["userlastfmusername"]

    username = session["lastfmusername"]

    def lastfm_get(payload):
        # Define headers and URL
        headers = {'user-agent': USER_AGENT}
        url = 'http://ws.audioscrobbler.com/2.0/'

        # Add API Key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        payload['user'] = username

        response = requests.get(url, headers=headers, params=payload)
        return response

    # Run the queries
    r = lastfm_get({
        'method': 'user.getinfo'

    })

    avatar = r.json()['user']['image'][2].get('#text')

    r = lastfm_get({
        'method': 'user.getTopAlbums'

    })

    # Cover
    all_time_top_albums_cover = []
    n = 0
    while n < 21:
        cover = r.json()['topalbums']['album'][n]['image'][2].get('#text')
        all_time_top_albums_cover.append(cover)
        n = n + 1

    # Album Name
    all_time_top_albums_name = []
    n = 0
    while n < 21:
        name = r.json()['topalbums']['album'][n]['name']
        all_time_top_albums_name.append(name)
        n = n + 1

    # Album Artist
    all_time_top_albums_artist = []
    n = 0
    while n < 21:
        artist = r.json()['topalbums']['album'][n]['artist'].get('name')
        all_time_top_albums_artist.append(artist)
        n = n + 1

    # Album Playcount
    all_time_top_albums_playcount = []
    n = 0
    while n < 21:
        playcount = r.json()['topalbums']['album'][n].get('playcount')
        all_time_top_albums_playcount.append(playcount)
        n = n + 1

    return render_template("/all_time_top_albums.html", avatar=avatar,
                           all_time_top_albums_cover=all_time_top_albums_cover,
                           all_time_top_albums_artist=all_time_top_albums_artist,
                           all_time_top_albums_name=all_time_top_albums_name,
                           all_time_top_albums_playcount=all_time_top_albums_playcount,
                           username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result_checks = is_provided("username") or is_provided("password") or is_provided("confirmation") or \
                        is_provided("userlastfmusername")
        if result_checks:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match")

        try:
            primary_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                                     username=request.form.get("username"),
                                     hash=generate_password_hash(request.form.get("password")))
        except:
            return apology("username already exists", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        db.execute("INSERT INTO user_data (user_id, email, userlastfmusername) "
                   "VALUES (:user_id, :email, :userlastfmusername)",
                   user_id=session["user_id"],
                   email=request.form.get("email"),
                   userlastfmusername=request.form.get("userlastfmusername")
                   )

        rows2 = db.execute("SELECT * FROM user_data WHERE user_id = :user_id",
                           user_id=session["user_id"])

        session["email"] = rows2[0]["email"]
        session["userlastfmusername"] = rows2[0]["userlastfmusername"]
        session["registered"] = rows2[0]["registered"]

        if primary_key is None:
            return apology("registration error", 403)

        session["user_id"] = primary_key

        flash(f"Welcome aboard, {session['username']}!")
        return redirect("/")

    else:
        return render_template("register.html")

    # """Register user"""
    # return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        result_checks = is_provided("username") or is_provided("password")
        if result_checks is not None:
            return result_checks

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        # session["password"] = rows[0]["hash"]

        rows2 = db.execute("SELECT * FROM user_data WHERE user_id = :user_id",
                           user_id=session["user_id"]
                           )

        session["email"] = rows2[0]["email"]
        session["userlastfmusername"] = rows2[0]["userlastfmusername"]
        session["registered"] = rows2[0]["registered"]

        flash(f"Welcome back, {session['username']}!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


# Account Settings
@app.route("/account_settings", methods=["GET", "POST"])
@login_required
def account_settings():

    # username = session["username"]

    if request.method == "POST":
        option = request.form.get("option")

        if option == "change_password":
            return redirect("/change_password")

        elif option == "change_email":
            return redirect("/change_email")

        elif option == "change_lastfmusername":
            return redirect("/change_lastfmusername")

    else:
        return render_template("account_settings.html")


# Change Password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":

        if request.form.get("newpassword") != request.form.get("confirmation"):
            return apology("passwords must match")

        user_id = session["user_id"]

        try:
            db.execute("UPDATE users SET hash = :hash WHERE id = :user_id",
                       hash=generate_password_hash(request.form.get("newpassword")),
                       user_id=user_id)

            flash('Password successfully changed!')

            return redirect("/account_settings")
        except:
            return apology("algo deu errado")
    else:
        return render_template("change_password.html")


# Change Last.fm Username
@app.route("/change_lastfmusername", methods=["GET", "POST"])
@login_required
def change_lastfmusername():

    username = session["username"]

    if request.method == "POST":

        newuserlastfmusername = request.form.get("newuserlastfmusername")
        user_id = session["user_id"]

        try:
            db.execute("UPDATE user_data SET userlastfmusername = :newuserlastfmusername WHERE user_id = :user_id",
                       newuserlastfmusername=newuserlastfmusername,
                       user_id=user_id
                       )

            rows2 = db.execute("SELECT * FROM user_data WHERE user_id = :user_id",
                               user_id=session["user_id"]
                               )

            session["userlastfmusername"] = rows2[0]["userlastfmusername"]

            flash('Last.fm username successfully changed!')
            return redirect("/account_settings")

        except:
            return apology(" Nao Deu")

    else:
        return render_template("change_lastfmusername.html")


# Change Email
@app.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email():

    username = session["username"]

    if request.method == "POST":

        if request.form.get("newemail") != request.form.get("confirmation"):
            return apology("emails must match")

        newemail = request.form.get("newemail")
        user_id = session["user_id"]

        try:
            db.execute("UPDATE user_data SET email = :newemail WHERE user_id = :user_id",
                       newemail=newemail,
                       user_id=user_id
                       )

            rows2 = db.execute("SELECT * FROM user_data WHERE user_id = :user_id",
                               user_id=session["user_id"]
                               )

            session["email"] = rows2[0]["email"]

            flash('E-mail successfully changed!')

            return redirect("/account_settings")
        except:
            return apology(" Nao Deu")

    else:
        return render_template("change_email.html")


# About
@app.route("/about", methods=["GET", "POST"])
@login_required
def about():

    username = session["username"]

    if request.method == "POST":
        pass

    else:
        return render_template("about.html")


# Feedback
@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "POST":

        username = session["username"]

        name = request.form.get("name")
        user_email = request.form.get("email")
        server_email = "marciomizu@gmail.com"
        password = environ.get('PASSWORD')

        feedback = request.form.get("feedback")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("marciomizu@gmail.com", password)

        server.sendmail(user_email, server_email, feedback)

        flash("Your feedback has been sent!")
        redirect("/")
        server.quit()

    else:
        return render_template("feedback.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
