import requests
import os
from dotenv import load_dotenv
import pandas as pd
from scipy.stats import entropy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
LASTFM_ID = os.getenv('LASTFM_CLIENT_ID')
LASTFM_SECRET = os.getenv('LASTFM_CLIENT_SECRET')

class Artist:
    def __init__(self, name, followers, popularity, genre):
        self.name = name
        self.followers = followers
        self.popularity = popularity
        self.genre = genre
    
    def get(self):
        return {
            "name": self.name,
            "followers": self.followers,
            "popularity": self.popularity,
            "genre": self.genre,
        }

    
    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Genre: {self.genre}\n"
            f"Artist Followers: {self.followers}\n"
            f"Artist Popularity: {self.popularity}\n"
        )

class Song:
    def __init__(self, name, artists, duration, explicit, popularity, genre):
        self.name = name
        self.artists = artists
        self.duration = duration
        self.explicit = explicit
        self.popularity = popularity
        self.genre = genre

    def get(self):
        artist_names = [artist.name for artist in self.artists]
        artist_followers = [artist.followers for artist in self.artists]
        artist_popularities = [artist.popularity for artist in self.artists]

        return {
            "name": self.name,
            "artists": artist_names,
            "duration": self.duration,
            "explicit": self.explicit,
            "popularity": self.popularity,
            "genre": list(self.genre),
            "artist_followers": artist_followers,
            "artist_popularity": artist_popularities
        }

    def __str__(self):
        explicit_text = "Yes" if self.explicit else "No"
        genres = set(genre for artist in self.artists for genre in artist.genre)

        return (
            f"Song: {self.name}\n"
            f"Artists: {', '.join(artist.name for artist in self.artists)}\n"
            f"Duration: {self.duration} seconds\n"
            f"Explicit: {explicit_text}\n"
            f"Popularity: {self.popularity}\n"
            f"Genres: {', '.join(genres)}\n"
            f"Artist Followers: {', '.join(str(artist.followers) for artist in self.artists)}\n"
            f"Artist Popularity: {', '.join(str(artist.popularity) for artist in self.artists)}\n"
        )

class Playlist:
    def __init__(self, songs):
        self.songs = songs
        self.artists = self.extract_artists()
        

    def extract_artists(self):
        artist_data = {}

        for song in self.songs:
            song_data = song.get()

            for i, artist_name in enumerate(song_data['artists']):
                if artist_name not in artist_data:
                    artist_data[artist_name] = {
                        'followers': song_data['artist_followers'][i],
                        'popularity': song_data['artist_popularity'][i],
                        'genre': song_data['genre']
                    }

        return artist_data

    def playlist_length(self):
        return len(self.songs)    
    
    def artist_count(self):
        artists = {}

        for song in self.songs:
            for artist in song.artists:
                if artist.name in artists:
                    artists[artist.name] += 1
                else:
                    artists[artist.name] = 1
                
        return artists
    
    def artist_statistics(self):
        artist_df = pd.DataFrame(self.artists.values())

        stats = {
            'followers' : {
                'mean': artist_df['followers'].mean(),
                'median': artist_df['followers'].median(),
                'mode': artist_df['followers'].mode().tolist(),
                'std': artist_df['followers'].std(),
                'variance': artist_df['followers'].var(),
                'max' : artist_df['followers'].max(),
                'min' : artist_df['followers'].min(),
                'iqr': artist_df['followers'].quantile(0.75) - artist_df['followers'].quantile(0.25)
            },
            'popularity' : {
                'mean': artist_df['popularity'].mean(),
                'median': artist_df['popularity'].median(),
                'mode': artist_df['popularity'].mode().tolist(),
                'std': artist_df['popularity'].std(),
                'variance': artist_df['popularity'].var(),
                'max' : artist_df['popularity'].max(),
                'min' : artist_df['popularity'].min(),
                'iqr': artist_df['popularity'].quantile(0.75) - artist_df['followers'].quantile(0.25)
            }
        }

        return stats
    
    def genre_statistics(self, genres):
        genre_counts = {}

        for sublist in genres:
            if sublist:
                for genre in sublist:

                    if genre in genre_counts:
                        genre_counts[genre] += 1
                    else:
                        genre_counts[genre] = 1
        
        genre_counts = pd.Series(genre_counts)
        
        return {
            'mode': genre_counts.idxmax(),
            'frequency': genre_counts.to_dict(),
            'entropy': entropy(genre_counts)
        }
    
    def song_statistics(self):
        song_data = []

        for song in self.songs:
            song_data.append(song.get())
        
        song_df = pd.DataFrame(song_data)

        stats = {
            'duration': {
                'mean': song_df['duration'].mean(),
                'median': song_df['duration'].median(),
                'mode': song_df['duration'].mode().tolist(),
                'std': song_df['duration'].std(),
                'variance': song_df['duration'].var(),
                'max' : song_df['duration'].max(),
                'min' : song_df['duration'].min(),
                'iqr': song_df['duration'].quantile(0.75) - song_df['duration'].quantile(0.25),
                'skewness': song_df['duration'].skew(),
                'kurtosis': song_df['duration'].kurt()
            },
            'explicit' : song_df['explicit'].sum(),
            'popularity': {
                'mean': song_df['popularity'].mean(),
                'median': song_df['popularity'].median(),
                'mode': song_df['popularity'].mode().tolist(),
                'std': song_df['popularity'].std(),
                'variance': song_df['popularity'].var(),
                'max' : song_df['popularity'].max(),
                'min' : song_df['popularity'].min(),
                'iqr': song_df['popularity'].quantile(0.75) - song_df['popularity'].quantile(0.25),
                'skewness': song_df['popularity'].skew(),
                'kurtosis': song_df['popularity'].kurt()
            },
            'genre': self.genre_statistics(song_df['genre'])
        }

        return stats
    
    def print_song_statistics(self):
        stats = self.song_statistics()

        formatted_stats = (
            f"Song Statistics:\n"
            f"Duration:\n"
            f"  Mean: {stats['duration']['mean']:.2f}\n"
            f"  Median: {stats['duration']['median']:.2f}\n"
            f"  Mode: {stats['duration']['mode']}\n"
            f"  Standard Deviation: {stats['duration']['std']:.2f}\n"
            f"  Variance: {stats['duration']['variance']:.2f}\n"
            f"  Max: {stats['duration']['max']:.2f}\n"
            f"  Min: {stats['duration']['min']:.2f}\n"
            f"  IQR: {stats['duration']['iqr']:.2f}\n"
            f"  Skewness: {stats['duration']['skewness']:.2f}\n"
            f"  Kurtosis: {stats['duration']['kurtosis']:.2f}\n\n"
            f"Explicit Songs: {stats['explicit']}\n\n"
            f"Popularity:\n"
            f"  Mean: {stats['popularity']['mean']:.2f}\n"
            f"  Median: {stats['popularity']['median']:.2f}\n"
            f"  Mode: {stats['popularity']['mode']}\n"
            f"  Standard Deviation: {stats['popularity']['std']:.2f}\n"
            f"  Variance: {stats['popularity']['variance']:.2f}\n"
            f"  Max: {stats['popularity']['max']:.2f}\n"
            f"  Min: {stats['popularity']['min']:.2f}\n"
            f"  IQR: {stats['popularity']['iqr']:.2f}\n"
            f"  Skewness: {stats['popularity']['skewness']:.2f}\n"
            f"  Kurtosis: {stats['popularity']['kurtosis']:.2f}\n\n"
            f"Genre Statistics:\n"
            f"  Most Common Genre: {stats['genre']['mode']}\n"
            f"  Genre Frequency: {stats['genre']['frequency']}\n"
            f"  Genre Entropy: {stats['genre']['entropy']:.2f}\n"
        )

        print(formatted_stats)
    
    def print_artist_statistics(self):
        stats = self.artist_statistics()
        
        formatted_stats = (
            f"Artist Statistics:\n"
            f"Followers:\n"
            f"  Mean: {stats['followers']['mean']:.2f}\n"
            f"  Median: {stats['followers']['median']:.2f}\n"
            f"  Mode: {stats['followers']['mode']}\n"
            f"  Standard Deviation: {stats['followers']['std']:.2f}\n"
            f"  Variance: {stats['followers']['variance']:.2f}\n"
            f"  Max: {stats['followers']['max']:.2f}\n"
            f"  Min: {stats['followers']['min']:.2f}\n"
            f"  IQR: {stats['followers']['iqr']:.2f}\n\n"
            f"Popularity:\n"
            f"  Mean: {stats['popularity']['mean']:.2f}\n"
            f"  Median: {stats['popularity']['median']:.2f}\n"
            f"  Mode: {stats['popularity']['mode']}\n"
            f"  Standard Deviation: {stats['popularity']['std']:.2f}\n"
            f"  Variance: {stats['popularity']['variance']:.2f}\n"
            f"  Max: {stats['popularity']['max']:.2f}\n"
            f"  Min: {stats['popularity']['min']:.2f}\n"
            f"  IQR: {stats['popularity']['iqr']:.2f}\n"
        )
        
        print(formatted_stats)

def get_access_token(client_id, client_secret):
    url = url = 'https://accounts.spotify.com/api/token'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
         'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    data = response.json()
    return data['access_token']

def get_playlist(access_token, playlist_id, next_url = None):
    url = next_url if next_url else f'https://api.spotify.com/v1/playlists/{playlist_id}'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_artist(access_token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_genre(name, artists):
    known_genres = [
        'pop', 'rock', 'hip hop', 'rap', 'jazz', 'classical', 'electronic', 'folk', 'country',
        'blues', 'reggae', 'metal', 'punk', 'soul', 'funk', 'disco', 'house', 'techno', 'trance',
        'dubstep', 'bossa nova', 'indie', 'alternative', 'r&b', 'latin', 'world', 'ska', 'ambient',
        'grunge', 'opera', 'gospel', 'bluegrass', 'swing', 'synthpop', 'new wave', 'edm', 
        'video game music', 'trap', 'lo-fi', 'dance', 'electro', 'hardstyle', 'glitch hop', 'vaporwave',
        'chiptune', 'progressive house', 'deep house',
        'k-pop', 'j-pop', 'j-rock', 'j-rap', 'jazz fusion', 'enka', 'kayokyoku',
        'mandopop', 'cantopop', 'thai-pop', 'v-pop', 'thai pop', 'indian pop',
        'bhangra', 'qawwali', 'filmi', 'arab pop', 'rai', 'turkish pop', 'greek pop',
        'afrobeat', 'highlife', 'juj music', 'kizomba', 'kuduro', 'kwaito', 'flamenco', 'tango',
        'samba', 'reggaeton', 'merengue', 'bachata', 'cumbia', 'vallenato', 'fado', 'klezmer',
        'schlager', 'zouk', 'soukus', 'mbalax', 'kaseko', 'maloya', 'funana', 'sega', 'calypso', 
        'soca', 'mento', 'salsa', 'chicha', 'huayno', 'forro', 'brega', 'axé', 'frevo', 'pagode',
        'tropicalia', 'celtic', 'traditional irish', 'eurobeat'
    ]

    artist_list = []

    for artist in artists:
        artist_list.append(artist.get()['name'])
    
    if not name or not artist_list:
        raise ValueError("Song dictionary must contain 'name' and 'artists' keys.")

    artist_name = ', '.join(artist_list)
    
    url = 'http://ws.audioscrobbler.com/2.0/'

    params = {
        'method': 'track.getInfo',
        'api_key': LASTFM_ID,
        'artist': artist_name,
        'track': name,
        'format': 'json'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'track' in data and 'toptags' in data['track']:
        tags = data['track']['toptags']['tag']

        genres = [tag['name'].lower() for tag in tags if tag['name'].lower() in known_genres]

        if not genres and tags:
            genres = [tags[0]['name'].lower()]

        return genres
    else:
        return []

def visualization(playlist):
    song_stats = playlist.song_statistics()
    genre_stats = song_stats['genre']
    duration_stats = song_stats['duration']
    popularity_stats = song_stats['popularity']
    artist_stats = playlist.artist_statistics()

    max_followers_artist = max(playlist.artists, key=lambda x: playlist.artists[x]['followers'])
    min_followers_artist = min(playlist.artists, key=lambda x: playlist.artists[x]['followers'])

    genre_counts = genre_stats['frequency']
    genres, counts = zip(*genre_counts.items())

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(x=genres, y=counts, hue=genres, palette='viridis', edgecolor='black', ax=ax, dodge=False, legend=False)

    plt.title('Spotify Playlist Data Analysis', fontsize=16, weight='bold')
    plt.xlabel('Genre', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.subplots_adjust(bottom=0.4)

    textstr1 = '\n'.join((
        f"Most Popular Genre: {genre_stats['mode']}",
        f"Genre Entropy: {genre_stats['entropy']:.2f}",
        f"No. of Songs: {playlist.playlist_length()}"
    ))

    textstr2 = '\n'.join((
        f"Avg. Duration: {duration_stats['mean']:.2f}s",
        f"Longest Duration: {duration_stats['max']:.2f}s",
        f"Shortest Duration: {duration_stats['min']:.2f}s",
        f"Duration Std: {duration_stats['std']:.2f}"
    ))

    textstr3 = '\n'.join((
        f"Avg. Popularity: {popularity_stats['mean']:.2f}",
        f"Popularity Std: {popularity_stats['std']:.2f}",
        f"Popularity Skewness: {popularity_stats['skewness']:.2f}",
        f"Popularity Kurtosis: {popularity_stats['kurtosis']:.2f}"
    ))

    textstr4 = '\n'.join((
        f"Avg. Followers: {artist_stats['followers']['mean']:.2f}",
        f"Largest Followers: {artist_stats['followers']['max']} ({max_followers_artist})",
        f"Lowest Followers: {artist_stats['followers']['min']} ({min_followers_artist})",
        f"Followers IQR: {artist_stats['followers']['iqr']:.2f}"
    ))

    def diversity_level(entropy):
        if entropy < 1.5:
            return "Very Low"
        elif entropy < 2.5:
            return "Low"
        elif entropy < 3.5:
            return "Moderate"
        elif entropy < 4.5:
            return "High"
        else:
            return "Very High"

    def popularity_preference(mean, std):
        if mean > 70 and std < 10:
            return "Very High"
        elif mean > 60:
            return "High"
        else:
            return "Moderate"

    def artist_popularity_level(mean, std):
        if mean > 1e6 and std < 1e5:
            return "Very High"
        elif mean > 5e5:
            return "High"
        elif mean > 1e5:
            return "Moderate"
        else:
            return "Low"

    def song_length_preference(mean):
        if mean > 240:
            return "Long"
        elif mean > 180:
            return "Moderate"
        else:
            return "Short"

    textstr5 = f"Diversity Level:\n{diversity_level(genre_stats['entropy'])}"
    textstr6 = f"Popularity Preference:\n{popularity_preference(popularity_stats['mean'], popularity_stats['std'])}"
    textstr7 = f"Artist Popularity Level:\n{artist_popularity_level(artist_stats['followers']['mean'], artist_stats['followers']['std'])}"
    textstr8 = f"Song Length Preference:\n{song_length_preference(duration_stats['mean'])}"

    def add_text_box(ax, textstr, x, y, colour, fontsize, alignment):
        ax.text(x, y, textstr, transform=ax.transAxes, fontsize=fontsize, bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor=colour, alpha=0.7,),
                verticalalignment='top',  horizontalalignment=alignment)

    add_text_box(ax, textstr1, 0.00, -0.5, 'lightgrey', 12, 'left')
    add_text_box(ax, textstr2, 0.20, -0.5, 'lightgrey', 12, 'left')
    add_text_box(ax, textstr3, 0.40, -0.5, 'lightgrey', 12, 'left')
    add_text_box(ax, textstr4, 0.60, -0.5, 'lightgrey', 12, 'left')
    add_text_box(ax, textstr5, 0.20, -0.75, 'lightblue', 16, 'center')
    add_text_box(ax, textstr6, 0.40, -0.75, 'lightblue', 16, 'center')
    add_text_box(ax, textstr7, 0.60, -0.75, 'lightblue', 16, 'center')
    add_text_box(ax, textstr8, 0.80, -0.75, 'lightblue', 16, 'center')

    plt.tight_layout()
    plt.show()

def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    playlist_link = input("Enter Spotify Playlist Link: ")
    playlist_id = playlist_link.split('/')[-1].split('?')[0]

    data = get_playlist(access_token, playlist_id)
    playlist_data = data['tracks']['items']

    next_url = data['tracks']['next']

    if next_url != None:
         data = get_playlist(access_token, playlist_id, next_url)
         playlist_data.extend(data['items'])

    songs = []

    for s in playlist_data:

        name = s['track']['name']
        artists = []
        duration = s['track']['duration_ms'] / 1000
        explicit = s['track']['explicit']
        popularity = s['track']['popularity']

        artist_data = s['track']['artists']

        for a in artist_data:
            skip = False

            if a['id'] is None:
                skip = True

        if skip:
            continue

        for a in artist_data:
            artist_id = a['id']
            profile = get_artist(access_token, artist_id)

            artist_name = profile['name']
            artist_followers = profile['followers']['total']
            artist_popularity = profile['popularity']
            artist_genres = profile['genres']

            artist = Artist(artist_name, artist_followers, artist_popularity, artist_genres)
            artists.append(artist)
        
        genre = get_genre(name, artists)

        if len(genre) <= 0 or genre == []:
            genre = artists[0].get()['genre']

        song = Song(name, artists, duration, explicit, popularity, genre)
        songs.append(song)
        
    playlist = Playlist(songs)
    
    if playlist.playlist_length() <= 1:
        print(playlist.playlist_length())
        return False
    else:
        visualization(playlist)
        return True
    
if __name__ == '__main__':
    run = main()

    while not run:
        print("Playlist has less than 2 songs - Try another playlist or adding more songs")
        run = main()