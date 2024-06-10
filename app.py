from flask import Flask, render_template, session, url_for, request, redirect, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

'''the re.match() function is used to validate the password against a regular expression pattern. 
This pattern requires the password to contain at least one digit (\d), one uppercase letter ([A-Z]), 
one special character ([!@#$%^&*()_+=\[{\]};:<>|./?,-]), and one lowercase letter ([a-z]), 
with a minimum length of 6 characters (.{6,}). 
If the password doesn't meet these criteria, an error message is displayed, 
and the user is redirected back to the registration page.'''

# Initialize Spotipy with your credentials
client_credentials_manager = SpotifyClientCredentials(client_id='0743934039bb45d88f5e134fa081375c', client_secret='c46241df84914c92aec3750c37c1d20e')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#function to retrieve the radar korea playlist data
def radar_korea_playlist(client_id, client_secret):
    # Initialize Spotipy client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist_id="37i9dQZF1DX9IALXsyt8zk"
    
    # Get tracks from the radar korea playlist
    try:
        radar_tracks = sp.playlist_tracks(playlist_id=playlist_id)['items']
        radar_korea_tracks = []

        for track in radar_tracks:
            track_info = {
                'name': track['track']['name'],
                'artist': ', '.join([artist['name'] for artist in track['track']['artists']]),
                'album': track['track']['album']['name'],
                'preview_url': track['track']['preview_url'],
                'external_url': track['track']['external_urls']['spotify']
            }
            radar_korea_tracks.append(track_info)

        return radar_korea_tracks

    except Exception as e:
        print("Error:", e)
        return []




# Function to retrieve the top 50 playlist data
def get_top_50_playlist():
    # Get the current top 50 playlist
    playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Example playlist ID for Top 50 Global on Spotify
    playlist_tracks = sp.playlist_tracks(playlist_id)['items']

    # Extract relevant information from each track
    playlist_data = []
    for track in playlist_tracks:
        track_name = track['track']['name']
        artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        url = track['track']['external_urls']['spotify'] if 'spotify' in track['track']['external_urls'] else None
        playlist_data.append({'name': track_name, 'artists': artists, 'url': url})

    return playlist_data


def get_trending_tracks(client_id, client_secret, country='US', limit=7):
    # Initialize Spotipy client
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Get trending tracks for the specified country
    try:
        response = sp.featured_playlists(locale=None, country=country, limit=limit)
        trending_playlists = response['playlists']['items']
        trending_tracks = []

        for playlist in trending_playlists:
            playlist_id = playlist['id']
            tracks = sp.playlist_tracks(playlist_id=playlist_id, limit=limit)['items']
            
            for track in tracks:
                track_info = {
                    'name': track['track']['name'],
                    'artist': ', '.join([artist['name'] for artist in track['track']['artists']]),
                    'album': track['track']['album']['name'],
                    'preview_url': track['track']['preview_url'],
                    'external_url': track['track']['external_urls']['spotify']
                }
                trending_tracks.append(track_info)

        return trending_tracks

    except Exception as e:
        print("Error:", e)
        return []

# Example usage:
client_id = '#####'
client_secret = '#####'
# trending_tracks = get_trending_tracks(client_id, client_secret)

# for index, track in enumerate(trending_tracks, start=1):
#     print(f"{index}. {track['name']} by {track['artist']} from the album '{track['album']}'")
#     print(f"Preview URL: {track['preview_url']}")
#     print(f"Spotify URL: {track['external_url']}")
#     print()

# create connection to database
connection = sqlite3.connect("user_data.db")
db = connection.cursor()

app = Flask(__name__)
app.secret_key = "wazzup3451"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"


@app.route("/")
def index():
    if "user_id" in session:
        trending_tracks = get_trending_tracks(client_id, client_secret)
    
    # Render a template to display trending tracks
        return render_template("home.html", trending_tracks=trending_tracks)
       
    else:
        return render_template("login.html")
    
        


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        connection = sqlite3.connect("user_data.db")
        db = connection.cursor()

        # Query the database for the username
        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = db.fetchone()

        # Check if user exists and password is correct
        if user and check_password_hash(user[2], password):
            # Store user_id in session
            session["user_id"] = user[0]
            flash("You have been successfully logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        connection = sqlite3.connect("user_data.db")
        db = connection.cursor()

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        # Check if username is already taken
        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = db.fetchone()

        if existing_user:
            flash("Username already exists, please choose another one", "error")
            return redirect(url_for("register"))
        else:
            
            if not re.match(r'^(?=.*\d)(?=.*[A-Z])(?=.*[!@#$%^&*()_+=\[{\]};:<>|./?,-])(?=.*[a-z]).{6,}$', password):
                print("Password does not meet complexity requirements")
                flash("Password must contain at least 6 characters with a number, an uppercase letter, and a special character", "error")
                return redirect(url_for("register"))
            # else:
            #     print("Password meets complexity requirements")
            
            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Insert new user into the database
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            connection.commit()

            flash("Registration successful! Please log in", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        flash("You need to log in first!", "error")
        return redirect(url_for("login"))
    # Call the function to get trending tracks
    trending_tracks = get_trending_tracks(client_id, client_secret)
    
    # Render a template to display trending tracks
    return render_template("home.html", trending_tracks=trending_tracks)
    



@app.route("/top50")
def global_top_50():
    playlist_data = get_top_50_playlist()
    return render_template("top50.html", playlist_data=playlist_data)


@app.route("/radar")
def radar():    
    return render_template("radar.html")


        

# Function to fetch top songs for a given playlist ID
def fetch_top_songs(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    songs = []
    for item in results['items']:
        song_info = {}
        track = item['track']
        song_info['song'] = track['name']
        song_info['artist'] = track['artists'][0]['name']
        song_info['preview_link'] = track['preview_url']
        song_info['spotify_link'] = track['external_urls']['spotify']
        songs.append(song_info)
    return songs

@app.route("/radar_korea", methods=["GET", "POST"])
def radar_korea():
    client_id = '0743934039bb45d88f5e134fa081375c'
    client_secret = 'c46241df84914c92aec3750c37c1d20e'
    
    try:
        radar_korea_tracks = radar_korea_playlist(client_id, client_secret)
        return render_template("radar_korea.html", radar_korea_tracks=radar_korea_tracks)
    except Exception as e:
        return f"Error: {e}"
        
@app.route("/radar_global", methods=["GET", "POST"])
def radar_global():
    client_id = '0743934039bb45d88f5e134fa081375c'
    client_secret = 'c46241df84914c92aec3750c37c1d20e'
    
    try:
        radar_korea_tracks = radar_korea_playlist(client_id, client_secret)
        return render_template("radar_global.html", radar_korea_tracks=radar_korea_tracks)
    except Exception as e:
        return f"Error: {e}"
        
        
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Flash "You have been successfully logged out!" message
    message = "You have been successfully logged out!"

    # Render logout.html template with the message
    return render_template("index.html", message=message)

    




if __name__ == "__main__":
    
    app.run(debug=True)
