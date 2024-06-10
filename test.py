import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

# Test the function
client_id = '0743934039bb45d88f5e134fa081375c'
client_secret = 'c46241df84914c92aec3750c37c1d20e'
tracks = radar_korea_playlist(client_id, client_secret)
print(tracks)
