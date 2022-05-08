import json
import os
import datetime as dt
from typing import Union # This module is used only for type hinting and no other purpose.

ALBUM_PREFIX = '#'
SONG_PREFIX = '*'
SONG_DATA_SEPARATOR = '::'
TIME_ZERO = dt.datetime.strptime('00:00:00', '%H:%M:%S') # Used when calculating time sum.
TOP_COMMON_COUNT = 50

class data(): # Approval from elinor.
    """data class manages a db of pink_floyd with data from Pink_Floyd_DB.txt"""    
    def __init__(self):
        # Check if the json file exists.
        if not os.path.exists('pink_db.json'):
            self.create_json()

        with open('pink_db.json', 'r') as src_db:
            self.pink_floyd_db = json.load(src_db)

    def create_json(self, filepath : str = './Pink_Floyd_DB.txt') -> None:
        """create_json creates a JSON file from the Pink_Floyd_DB.txt.
        
        Args:
            filepath (str, optional): filepath to the Pink_Floyd_DB.txt. Defaults to './Pink_Floyd_DB.txt'.

        Raises:
            FileNotFoundError: error is raised whenever the database file has not been found.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError("Database hasn't been found in the path listed (Defaults to './Pink_Floyd_DB.txt'.")

        formatted_db = {}
        with open(filepath, 'r') as file:
            # Split the files data based on '#' that is the prefix of each album.
            album_list = sorted(file.read().split(ALBUM_PREFIX))

        del album_list[0] # delete the first index as its empty due to the file starting with '#'

        # Split each album into its songs based on '*' that is the prefix of each songs.
        album_list = [album.split(SONG_PREFIX) for album in album_list]
        # Split each song into its data based on '::' that seperates each data from one another.
        album_list = [[song.split(SONG_DATA_SEPARATOR) for song in album] for album in album_list]

        for album in album_list:
            """We create a dict of all the songs in a given album.
            song[0] is the name of the song, song[1] is a list of the writers of the song, song[2] is the duration of the song, song[3] are the lyrics of the song.
            `song[3].split('\n')` - We take the lyrics of each song and split them at the newline.
            `album[1:]` - We start from the second index because the first index contains the albums information."""
            Songs = {song[0]: {'Writers': song[1], 'Duration': song[2], 'Lyrics': song[3].split('\n')} for song in sorted(album[1:])}
            
            # We add a new key album[0][0] aka album name, and add into it a dict with its year of release `int(album[0][1])` and its songs.
            formatted_db[album[0][0]] = {'Year': int(album[0][1]), 'Songs': Songs}

        with open('pink_db.json', 'w') as outfile:
            # Convert the dict into json format and save into a file.
            outfile.write(json.dumps(formatted_db, indent=5))

    def get_albms(self, x = None) -> str:
        """get_albms gets all album names in the database.
        
        Args:
            x: This argument is not used and is only made so we can pass an argument without error. Defaults to None.
        
        Returns:
            str: str of albums in self.pink_floyd_db.
        """        
        return ', '.join(self.pink_floyd_db.keys())

    def get_albm_songs(self, album : str) -> Union[str, None]:
        """get_albm_songs gets all songs in a given album.
        
        Args:
            album (str): the album to get the songs from.
        
        Returns:
            Union[str, None]: str: all songs in the album.
                               None: if the album is not found in the database.
        """        
        return ', '.join(self.pink_floyd_db[album]['Songs'].keys()) if album in self.pink_floyd_db else None

    def get_sng_dur(self, song : str) -> Union[str, None]:
        """get_sng_dur gets a songs duration from a given song.
        
        Args:
            song (str): the song to find and get the duration from.
        
        Returns:
            Union[str, None]: str: the duration of the song.
                              None: if the song is not found in the database.
        """        
        album = self.find_songs_albm(song)
        return self.pink_floyd_db[album]['Songs'][song]['Duration'] if album is not None else None

    def get_song_lyr(self, song : str) -> Union[str, None]:
        """get_song_lyr gets a songs lyrics from a given song.

        Args:
            song (str): the song to find and get the lyrics from.
        
        Returns:
            Union[str, None]: str: the lyrics of the song.
                              None: if the song is not found in the database.
        """        
        album = self.find_songs_albm(song)

        if album is not None:
            # Get the lyrics and convert it to a string.
            lyrics = self.pink_floyd_db[album]['Songs'][song]['Lyrics']
            return '\n'.join(lyrics) 
        else:
            return None

    def find_songs_albm(self, song : str) -> Union[str, None]:
        """find_songs_albm find the album for a given song.
        
        Args:
            song (str): the song to find its associated album.
        
        Returns:
            Union[str, None]: str: the album name.
                              None: if the song is not found associated to an album in the database.
        """
        # Go over each song in each album.
        for album in self.pink_floyd_db:
            # Check if the song exists in the album.
            if song in self.pink_floyd_db[album]['Songs']:
                return album
        return None

    def songs_by_name(self, keyword : str) -> Union[str, None]:
        """songs_by_name finds all songs that contain the keyword in its name.
        
        Args:
            keyword (str): the keyword to find in song names.
        
        Returns:
            Union[str, None]: str: str of songs that contain the keyword.
                               None: if no songs contain the keyword in the database.
        """        
        songs = []
        # Go over the name of each song in each album.
        for album in self.pink_floyd_db:
            for song in self.pink_floyd_db[album]['Songs']:
                # Check if the name contain the keyword.
                if keyword.lower() in song.lower():
                    songs.append(song)

        return None if not songs else ', '.join(songs)

    def songs_by_lyr(self, keyword : str) -> Union[str, None]:
        """songs_by_lyr finds all songs that contain the keyword in their lyrics.
        
        Args:
            keyword (str): the keyword to find in songs lyrics.
        
        Returns:
            Union[str, None]: str: str of songs that contain the keyword in their lyrics.
                               None: if no songs are contain the keyword in their lyrics in the database.
        """        
        songs = []
        # Go over the lyrics of each song in each album.
        for album in self.pink_floyd_db:
            for song in self.pink_floyd_db[album]['Songs']:
                # Check if the lyrics contain the keyword.
                if keyword.lower() in self.get_song_lyr(song).lower():
                    songs.append(song)

        return None if not songs else ', '.join(songs)

    def fifty_most_common(self, x = None) -> str:
        """fifty_most_common find the fifty most common words in each song in each album in the database.
        
        Args:
            x: This argument is not used and is only made so we can pass an argument without error. Defaults to None.
        
        Returns:
            str: fifty most common words the lyrics of all songs in pink_floyd_db, format '<rank>. <word>:<occurence>'.
        """     
        common_words = {}
        # Go over each word in each lyrics of each song in each album.
        for album in self.pink_floyd_db:
            for song, song_data in self.pink_floyd_db[album]['Songs'].items():
                for line in song_data['Lyrics']:
                    for word in line.split(' '):
                        # Continue if the word is not alphanumeric.
                        if not word.isalpha():
                            continue
                        # Try to add one to a key, if KeyError was raised set that key as one.
                        try:
                            common_words[word.lower()] += 1
                        except KeyError:
                            common_words[word.lower()] = 1
        # Sort ascending the dictionary based on size of values.
        top_50_common = dict(sorted(common_words.items(), key=lambda item: item[1], reverse=True)[:TOP_COMMON_COUNT])
        
        db_msg = [] # List of each ranking of words, used later to add easily the newlines.
        # Create ranking msg for each word.
        for cnt, (word, occur) in enumerate(top_50_common.items()):
           db_msg += ['{0}. {1}: {2}'.format(cnt + 1, word, occur)]
        return '\n'.join(db_msg) # Add the newline between each ranking.
    
    def albm_by_dur(self, x = None) -> str:
        """albm_by_dur gets each albums total duration and sorts them by size.
        
        Args:
            x: This argument is not used and is only made so we can pass an argument without error. Defaults to None.
        
        Returns:
            str: ranking of each album based on duration, format '<rank>. <album>:<duration>'.
        """        
        album_durations = {}
        # Go over the duration of each song in each album
        for album in self.pink_floyd_db:
            album_time = dt.datetime.strptime('00:00:00', '%H:%M:%S') # Empty the timestamp for the album.
            for song, song_data in self.pink_floyd_db[album]['Songs'].items():
                # Convert the duration to time() object.
                cur_time = dt.datetime.strptime(song_data['Duration'], '%M:%S')
                # Convert the time() object back to a string but with a new format.
                cur_time = cur_time.strftime('%H:%M:%S')
                # Convert the new string format back to a time() object.
                cur_time = dt.datetime.strptime(cur_time, '%H:%M:%S')
                
                # Add the duration to the current duration sum of the album.
                album_time = (album_time - TIME_ZERO + cur_time)
            album_durations[album] = album_time # Add the album duration to the dict with its name as the key.
        
        # Sort ascending the dictionary based on size of values
        album_durations = dict(sorted(album_durations.items(), key=lambda item: item[1], reverse=True))
        
        db_msg = []# List of each ranking of words, used later to add easily the newlines.
        # Create ranking msg for each word.
        for cnt, (album, album_dur) in enumerate(album_durations.items()):
            db_msg += ['{0}. {1}: {2}'.format(cnt + 1, album, album_dur.strftime('%H:%M:%S'))]
        return '\n'.join(db_msg) # Add the newline between each ranking.

