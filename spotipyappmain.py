import requests
from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os 
import random


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

scope = "user-library-read playlist-modify-private user-read-private playlist-read-private"

SPOTIPY_CLIENT_ID = "646952c802814c1a844ff8dd9574f5d2"
SPOTIPY_CLIENT_SECRET = "c3503ee79b66498696aa6e16d45ef403"
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/'
CACHE = '.spotipyoauthcache'

sp_oauth = SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope = scope, cache_path = CACHE)

sp = spotipy.Spotify(auth_manager=sp_oauth)

loggedin =  True

app = Flask(__name__)


@app.route('/spotify', methods = ['GET', 'POST'])


def spotify_login():
    
    account_infojson = sp.current_user()
    
    user_id= account_infojson['id']

    sp_playlists = get_spotify_playlists()

    items =[]
    playlist_ids = []

    for i in sp_playlists['items']:
        items.append(i['name'])
        playlist_ids.append(i['id'])

    if request.method=='POST':
        playlist_id = request.form.get('playlistid')
        if playlist_id == 'del':
            delete_playlist(user_id)
        else:
            spotify_playlist_shuffle(user_id, playlist_id, items)

    return render_template('spotifyshuffle.html', loggedin = loggedin, spotify_username = account_infojson["display_name"], items = items, playlist_ids =playlist_ids)


def spotify_playlist_shuffle(user_id, playlist_id, items):
    track_uris = []
    shuffled_playlist_id = None
    if 'shuffled playlist' not in items:
        sp.user_playlist_create(user_id, name= 'shuffled playlist', public =False)

        sp_playlists = get_spotify_playlists()
        for i in sp_playlists['items']:
            if i['name'] == 'shuffled playlist':
                shuffled_playlist_id = i['id']

        playlist_details = sp.user_playlist_tracks(user_id, playlist_id=playlist_id)

        offset = 0
        limit = 100
        numleft = playlist_details['total']
        while numleft>0:
            for track in playlist_details['items']:
                track_uris.append(track['track']['uri'])  
            numleft -= len(track_uris)

            if 0<numleft<100:
                offset+=100
                limit = numleft
                playlist_details = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, limit=limit,offset=offset)
            elif numleft> 100:
                offset+=100
                playlist_details = sp.user_playlist_tracks
    else:
        sp_playlists = get_spotify_playlists()
        for i in sp_playlists['items']:
            if i['name'] == 'shuffled playlist':
                shuffled_playlist_id = i['id']

        playlist_details = sp.user_playlist_tracks(user_id, playlist_id=playlist_id)
        offset = 0
        limit = 100
        numleft = playlist_details['total']
        while numleft>0:
            for track in playlist_details['items']:
                track_uris.append(track['track']['uri'])  
            numleft -= len(track_uris)

            if 0<numleft<100:
                offset+=100
                limit = numleft
                playlist_details = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, limit=limit,offset=offset)
            elif numleft> 100:
                offset+=100
                playlist_details = sp.user_playlist_tracks
            
    for track in track_uris:
        random.shuffle(track_uris)
        while len(track_uris)>0:
            if len(track_uris)>100:
                sp.user_playlist_add_tracks(user_id, playlist_id = shuffled_playlist_id, tracks = track_uris[:100])
                del track_uris[:100]
            elif len(track_uris)<100:
                sp.user_playlist_add_tracks(user_id, playlist_id = shuffled_playlist_id, tracks = track_uris[:len(track_uris)])
                del track_uris[:len(track_uris)]
        

    
    return(None)

def get_spotify_playlists():
    playlists_json = sp.current_user_playlists()
    return(playlists_json)

def delete_playlist(user_id):
    sp_playlists = get_spotify_playlists()
    for i in sp_playlists['items']:
        if i['name'] == 'shuffled playlist':
            shuffled_playlist_id = i['id']
    sp.user_playlist_unfollow(user_id, playlist_id = shuffled_playlist_id)



if __name__ == '__main__':
    app.run(debug=True)
