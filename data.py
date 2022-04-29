import json
import os

def create_json(filepath = './Pink_Floyd_DB.txt'):
    DB = {}
    with open(filepath, 'r') as file:
        albm_test = file.read().split('#')[1]
        albm_test = albm_test.split('*')
        albm_test = [albm.split('::') for albm in albm_test]

        Songs = {song[0]: {'Writers': song[1], 'Duration': song[2], 'Lyrics': song[3].replace('. ', '.').split('\n')[:-1]} for song in albm_test[1:]}

        formatted_db = {albm_test[0][0]: {'Year': int(albm_test[0][1]), 'Songs': Songs}}

        # print(formatted_db)
        print(json.dumps(formatted_db, indent=5))
        with open('pink_db.json', 'w') as outfile:
            outfile.write(json.dumps(formatted_db, indent=5))





def main():
    if not os.path.exists('pink_db.json'):
        create_json()
    else:
        print('file exists!')



if __name__ == 'data':
    main()