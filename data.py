import json
import os
from typing import Union # This module is used only for type hinting and no other purpose.

ALBUM_PREFIX = '#'
SONG_PREFIX = '*'
SONG_DATA_SEPARATOR = '::'
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

    def get_albms(self, x = None) -> list:
        """get_albms gets all album names in the database.
        
        Args:
            x: This argument is not used and is only made so we can pass an argument without error. Defaults to None.
        
        Returns:
            list: list of albums in self.pink_floyd_db.
        """        
        return ', '.join(self.pink_floyd_db.keys())

    def get_albm_songs(self, album : str) -> Union[list, None]:
        """get_albm_songs gets all songs in a given album.
        
        Args:
            album (str): the album to get the songs from.
        
        Returns:
            Union[list, None]: list: list of songs in the album.
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
        for album in self.pink_floyd_db:
            if song in self.pink_floyd_db[album]['Songs']:
                return album
        return None

    def songs_by_name(self, keyword : str) -> Union[list, None]:
        """songs_by_name finds all songs that contain the keyword in its name.
        
        Args:
            keyword (str): the keyword to find in song names.
        
        Returns:
            Union[list, None]: list: list of songs that contain the keyword.
                               None: if no songs contain the keyword in the database.
        """        
        songs = []
        for album in self.pink_floyd_db:
            for song in self.pink_floyd_db[album]['Songs']:
                if keyword.lower() in song.lower():
                    songs.append(song)

        return None if not songs else ', '.join(songs)

    def songs_by_lyr(self, keyword : str) -> Union[list, None]:
        """songs_by_lyr finds all songs that contain the keyword in their lyrics.
        
        Args:
            keyword (str): the keyword to find in songs lyrics.
        
        Returns:
            Union[list, None]: list: list of songs that contain the keyword in their lyrics.
                               None: if no songs are contain the keyword in their lyrics in the database.
        """        
        songs = []
        for album in self.pink_floyd_db:
            for song in self.pink_floyd_db[album]['Songs']:
                if keyword.lower() in self.get_song_lyr(song).lower():
                    songs.append(song)

        return None if not songs else ', '.join(songs)



