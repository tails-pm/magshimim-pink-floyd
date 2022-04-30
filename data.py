import json
import os

def create_json(filepath : str = './Pink_Floyd_DB.txt') -> None:
    """create_json creates a JSON file from the Pink_Floyd_DB.txt.
    
    Args:
        filepath (str, optional): filepath to the Pink_Floyd_DB.txt. Defaults to './Pink_Floyd_DB.txt'.
    """    
    formatted_db = {}
    with open(filepath, 'r') as file:
        album_list = file.read().split('#')

    del album_list[0] # delete the first index as its empty due to the file starting with '#'
    # Split each album into its songs.
    album_list = [album.split('*') for album in album_list]
    # Split each song into its data.
    album_list = [[song.split('::') for song in album] for album in album_list]

    for album in album_list:
        """We create a dict of all the songs in a given album.
        song[0] is the name of the song, song[1] is a list of the writers of the song, song[2] is the duration of the song, song[3] are the lyrics of the song.
        `song[3].split('\n')` - We take the lyrics of each song and split them at the newline.
        `album[1:]` - We start from the second index because the first index contains the albums information."""
        Songs = {song[0]: {'Writers': song[1], 'Duration': song[2], 'Lyrics': song[3].split('\n')} for song in album[1:]}
        
        # We add a new key album[0][0] aka album name, and add into it a dict with its year of release `int(album[0][1])` and its songs.
        formatted_db[album[0][0]] = {'Year': int(album[0][1]), 'Songs': Songs}

    with open('pink_db.json', 'w') as outfile:
        # Convert the dict into json format and save into a file.
        outfile.write(json.dumps(formatted_db, indent=5))


def main():
    if not os.path.exists('pink_db.json'):
        create_json()
    else:
        pass



if __name__ == 'data':
    main()