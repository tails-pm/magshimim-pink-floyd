import socket as sock
import re
#TODO: 1. orgenize code and consts and reformat var names 2. debug code.

SERVER_ADDRESS = ('127.0.0.1', 7160)

# Base commands in ASIB without data as we just want to test if the server received them and identifies them appropriately.
ASIB_COMMAND_FORMATS = ['200:ABMLIST',
                         '207:SNGINABM&{0}',
                         '214:SNGDUR&{0}',
                         '221:SNGLYR&{0}',
                         '228:ABMFROMSNG&{0}',
                         '235:SNGBYNAME&{0}',
                         '242:SNGBYLYR&{0}',
                         '249:EXIT']

CHOICE_MENU = """Please choose one of the following actions:
[1] - Get list of albums.
[2] - Get list of all songs in an album.
[3] - Get the duration of a song.
[4] - Get the lyrics of a song.
[5] - Get the album of a song.
[6] - Get all songs' names that include the specified word.
[7] - Get all songs that include the specified word in its lyrics.
[8] - Exit."""

RESULT_PRINT_FORMAT = {
    'ABMLIST': 'Pink Floyd list of albums:\n{Res}.',
    'SNGINABM': 'All songs in {Req} are:\n{Res}.',
    'SNGDUR': "{Req}'s duration is: {Res}.",
    'SNGLYR': "{Req}'s lyrics are:\n{Res}",
    'ABMFROMSNG': '{Req} is in the album:\n{Res}.',
    'SNGBYNAME': 'All songs that include keyword {Req} are:\n{Res}.',
    'SNGBYLYR': 'All songs that include keyword {Req} in its lyrics are:\n{Res}.',
}

EXIT_ACTION = 8

CHOICE_ALBM_INPUT = (2,)
CHOICE_SONG_INPUT = (3, 4, 5)
CHOICE_KEYWORD_INPUT = (6, 7)

"""The pattern will match to a string if it has the following pattern:
        First capturing group `(\d{3})`:
            \d{3}` three digit number.
        `:ERROR:` matches the characters ':ERROR:' (case sensitive)
        Second capturing group `([A-Z]+)`:
            `[A-Z]+` one or more uppercase letters (case sensitive).
        `:` matches the character ':'.
        Third capturing group `(.*)`:
            `.` matches any single character zero or unlimted times.
"""
ERROR_PTRN = re.compile(r'(\d{3}):ERROR:([A-Z]+):(.*)')
"""The pattern will match to a string if it has the following pattern:
        `OK:` matches the characters 'OK:' (case sensitive)
        First capturing group `([A-Z]+)`:
            `[A-Z]+` one or more uppercase letters (case sensitive).
        `:` matches the character ':'.
        `(?:&(.+))?` Non capturing group meaning its not part of any capture group:
            `&` matches the character '&'.
            Second capturing group `(.+)`:
                `.+` matches any single character one or unlimted times.
        `?` match Non capturing group zero or one time.
"""
RES_PTRN = re.compile(r'OK:([A-Z]+)(?:&(.+))?')
"""The pattern will match to a string if it has the following pattern:
        `(?:[^,]*(?:, )?)` Non capturing group meaning its not part of any capture group:
            `[^,]*` matches any character except ',' zero or unlimted times.
            `(?:, )` Non capturing group meaning its not part of any capture group:
                `,` matches the character ','.
                ` ` matches the character ' '.
            `?` match Non capturing group zero or one time.
        `{5}` match Non capturing group 5 times.
"""
FITH_PERIOD_PTRN = re.compile(r'(?:[^,]*(?:, )?){5}')

class console_colors:
    # This class is only used for aestetic reasons, and has no effect in the codes structure.
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[0m'
    GREEN = '\033[92m'

def create_request(choice) -> tuple:
    data = ''

    if choice in CHOICE_ALBM_INPUT:
        msg = 'Please enter album name (case sensitive): '
    elif choice in CHOICE_SONG_INPUT:
        msg = 'Please enter song name (case sensitive): '
    elif choice in CHOICE_KEYWORD_INPUT:
        msg = 'Please enter your desired keyword to search by (case insensitive): '
    else:
        msg = None # Flag to indicate that we do not want user input and skip the while loop
    
    while msg != None:
        try:
            data = str(input(f'{console_colors.GREEN}{msg}{console_colors.WHITE}'))
            break
        except ValueError or TypeError as err:
            print(f'{console_colors.YELLOW}[WARNING]: {console_colors.WHITE}Invalid input, please try again.')
            continue # As an invalid input was catched try getting the input again.
    
    request = ASIB_COMMAND_FORMATS[choice - 1].format(data).encode()
    return (request, data)
    
def print_response(requested_data : str, res : str) -> None:
    re_response = RES_PTRN.search(res) 

    if re_response is not None: # If the servers response does not match an error command print normally.
        responce_data = re_response.group(2)
        if re_response.group(1) == 'SNGLYR':
            responce_data = res.split('SNGLYR')[-1][1:]
        else:
            responce_data = list(filter(None, FITH_PERIOD_PTRN.findall(re_response.group(2))))
            responce_data = [line[:-2] if line[-2:-1] == ', ' else line for line in responce_data]
            responce_data = '\n'.join(responce_data)
        responce_data = RESULT_PRINT_FORMAT[re_response.group(1)].format(Req = requested_data, Res = responce_data)
       
        print(f'{console_colors.GREEN}[SERVER]: {console_colors.WHITE}{responce_data}\n')
    
    elif ERROR_PTRN.search(res) is not None:
        re_response = ERROR_PTRN.search(res) # Check if the servers response is an error.
        print(f'{console_colors.RED}[ERROR {re_response.group(1)}]: {console_colors.YELLOW}{re_response.group(2)}: {console_colors.WHITE}{re_response.group(3)}')
    
    else:
        print(f'{console_colors.GREEN}[SERVER]: {console_colors.WHITE}{res}')

def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as server_sock:
        try:
            server_sock.connect(SERVER_ADDRESS)
            
            welcome = server_sock.recv(1024).decode()
            print(f'{console_colors.GREEN}[SERVER]: {console_colors.WHITE}{welcome}') # Print Welcome Message.

            while True:
                print(CHOICE_MENU)
                try:
                    choice = int(input('Please make your choice: '))
                    if choice < 1 or choice > 8:
                        raise ValueError('Invalid choice')
                except ValueError or TypeError as err:
                    print(f'{console_colors.YELLOW}[WARNING]: {console_colors.WHITE}Invalid input, please try again.')
                    continue # As an invalid input was catched try getting the input again.

                request = create_request(choice) # Step down the choice to fit a l`ists index.
                server_sock.sendall(request[0])

                response = server_sock.recv(1024).decode()
                print_response(request[1], response)

                if choice == EXIT_ACTION:
                    break # Exit the loop as the user requested to exit.
        except sock.error as dcn:
            print(f'{console_colors.RED}[PROCESS STOPPED]: {console_colors.WHITE}Communication with the server has failed/ended, goodbye.')
        except Exception as err:
            print(f'{console_colors.RED}[PROCESS STOPPED]: {console_colors.WHITE}{err}')

if __name__ == '__main__':
    main()