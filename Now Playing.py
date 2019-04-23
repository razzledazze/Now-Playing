from lxml import html
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import webbrowser
import time
import urllib.request
from bs4 import BeautifulSoup

def getArtistSong(url): #Takes the url of the internet radio station and gives the currently playing song and artist
    page = requests.get(url)
    tree = html.fromstring(page.content)

    artistAndSong = tree.xpath('//p[@class="lead"]//text()')[1]
    artistAndSong = artistAndSong.split(' - ')

    artist = artistAndSong[0]
    song = artistAndSong[1]

    return artist,song

def validateCredentials(client_id, client_secret): #Validates this app with spotify API for developers, allowing the calls to be made later
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API
    return sp

def getAlbumsFromArtist(artistName,sp): #Takes in an artist name (and the sp object for searching with) and gives a list of all track names and all track uris
    result = sp.search(artistName) #search query
    artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
    sp_albums = sp.artist_albums(artist_uri, album_type='album')

    album_names = [] #will turn into a list of names as strings
    album_uris = [] #will turn into a list of uris as strings
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])

    return album_names, album_uris

def getTracksFromAlbum(album_uri,sp):
    track_names = [] #will turn into all track by the artist as a list of strings
    track_uris = [] #and the corresponding uris
    
    tracks = sp.album_tracks(album_uri) #all tracks within that album
    for trackIndex in range(len(tracks)-1): #for each track within the album
        track_names.append(tracks['items'][trackIndex]['name'])
        track_uris.append(tracks['items'][trackIndex]['uri'])
            
    return track_names, track_uris


client_id = '' # Your client id
client_secret = '' # Your secret key
sp = validateCredentials(client_id, client_secret)

url = 'https://www.internet-radio.com/station/radioparadise/' #enter any internet radio station url and this app will work with it
artist,song = getArtistSong(url) #scrapes the artist and song titles from the internet radio website

album_names, album_uris = getAlbumsFromArtist(artist,sp) #gets a list of all track names and their uris by the artist specified

song_uri = ""
for album_uri in album_uris:
    results = sp.album_tracks(album_uri)
    tracks = results['items']
    for track in tracks:
        #print(track['name']+"||||"+song)
        if song.lower() in track['name'].lower() or track['name'].lower() in song.lower(): #using in instead of == in case there's a 'remastered' or whatever at the end
            song_uri = track['uri'] #this is the song uri you are looking for

if song_uri != "": #first tries to open in spotify
    print("I found the song on Spotify here")
    webbrowser.open(song_uri)
    time.sleep(5)
else: #if it wasn't found on spotify, search youtube and give top result
    print("I couldn't find that song on Spotify, so here it is on YouTube")
    textToSearch = song+" by "+artist
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    webbrowser.open('https://www.youtube.com' + soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]['href'])
    time.sleep(5)
