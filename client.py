import socket as sock
import re

SERVER_ADDRESS = ('127.0.0.1', 7160)

# Base commands in ASIB without data as we just want to test if the server received them and identifies them appropriately.
ASIB_COMMAND_FORMATS = [
    '200:ABMLIST',
    '207:SNGINABM&{0}',
    '214:SNGDUR&{0}',
    '221:SNGLYR&{0}',
    '228:ABMFROMSNG&{0}',
    '235:SNGBYNAME&{0}',
    '242:SNGBYLYR&{0}',
    '249:EXIT'
]

ASIB_SPECIAL_PRINT_TYPE = ['SNGLYR']

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

# The data passed may be bigger then the defualt recv size so we use a bigger buffer.
RECV_LARGE = 2048

# Choice input msgs.
CHOICE_INPUT_MSG = {
    2: 'Please enter album name (case sensitive): ',
    3: 'Please enter song name (case sensitive): ',
    4: 'Please enter song name (case sensitive): ',
    5: 'Please enter song name (case sensitive): ',
    6: 'Please enter your desired keyword to search by (case insensitive): ',
    7: 'Please enter your desired keyword to search by (case insensitive): '
}
EXIT_ACTION = 8

# Regex patterns.
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
        `{4}` match Non capturing group 4 times.
"""
FORTH_COMMA_PTRN = re.compile(r'(?:[^,]*(?:, )?){4}')

# These constants are only used for aestetic reasons, and has no effect in the codes structure.
RED = '\033[91m'
YELLOW = '\033[93m'
WHITE = '\033[0m'
GREEN = '\033[92m'


def create_request(choice: int) -> tuple:
    """create_request creates the ASIB request baased on the users choice and data.
    
    Args:
        choice (int): the user's choice of action.
    
    Returns:
        tuple: (request - The finalized ASIB request, data - the data that the user inputted).
    """    
    data = ''

    # Check if the choice is part of the CHOICE_INPUT_MSG dict as we want to get input only for request that require it.
    if choice in CHOICE_INPUT_MSG.keys():
        while True:
            try:
                data = str(input(f'{GREEN}{CHOICE_INPUT_MSG[choice]}{WHITE}'))
                if data == '':
                    raise ValueError('Invalid input')
                # Exit the loop as no exception has occured meaning data was inputted correctly.
                break
            except ValueError or TypeError as err:
                print(f'{YELLOW}[WARNING]: {WHITE}Invalid input, please try again.')
                # As an invalid input was catched try getting the input again.
                continue

    # Create the request msg.
    # Step down the choice to fit the lists index.
    request = ASIB_COMMAND_FORMATS[choice - 1].format(data).encode()
    return (request, data)


def print_response(requested_data: str, res: str) -> None:
    """print_response creates a pretty print from the servers ASIB response.
    
    Made for astetic reasons!!!

    Args:
        requested_data (str): the users requested data.
        res (str): the server's ASIB response.
    """    
    re_response = RES_PTRN.search(res) # Match the response to the regex pattern.

    # If the servers response does not match an error command print normally.
    if re_response is not None:
        responce_data = re_response.group(2)

        if re_response.group(1) in ASIB_SPECIAL_PRINT_TYPE:
            # Filter out the response header and keep only data (by splitting at '&')
            responce_data = res.split('&')[-1]

        else:
            # Filter out empty data and seperate the responce based on the 5th comma.
            responce_data = list(filter(None, FORTH_COMMA_PTRN.findall(re_response.group(2))))
            # Create a list of lines with the last to characters removed if the last two characters are ', '.
            responce_data = [line[:-2] if line[-2:-1] == ', ' else line for line in responce_data]
            # Join each line with '\n'.
            responce_data = '\n'.join(responce_data)

        # Create the response message dependend on the response type.
        responce_data = RESULT_PRINT_FORMAT[re_response.group(1)].format(Req=requested_data, Res=responce_data)
        print(f'{GREEN}[SERVER]: {WHITE}{responce_data}\n')

    # Check if the servers response is an error.
    elif ERROR_PTRN.search(res) is not None:
        re_response = ERROR_PTRN.search(res) # Match the error.
        # Print the error message based on each header of the error response.
        print(f'{RED}[ERROR {re_response.group(1)}]: {YELLOW}{re_response.group(2)}: {WHITE}{re_response.group(3)}')

    # If somehow the server returns a msg not recognized in the ASIB protocol print it as is.
    else:
        print(f'{GREEN}[SERVER]: {WHITE}{res}')


def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as server_sock:
        try:
            server_sock.connect(SERVER_ADDRESS)
        
            welcome = server_sock.recv(1024).decode()
            # Print Welcome Message.
            print(f'{GREEN}[SERVER]: {WHITE}{welcome}')

            while True:
                print(CHOICE_MENU)
                try:
                    try:
                        choice = int(input('Please make your choice: '))
                        if choice < 1 or choice > EXIT_ACTION:
                            raise ValueError('Invalid choice')
                    except ValueError or TypeError:
                        print(f'{YELLOW}[WARNING]: {WHITE}Invalid input, please try again.')
                        # As an invalid input was catched try getting the input again.
                        continue

                    # Create the request.
                    request = create_request(choice)
                    # Send the request part of the tuple returned from create_request(choice).
                    server_sock.sendall(request[0])

                    response = server_sock.recv(RECV_LARGE).decode()
                    print_response(request[1], response)

                    if choice == EXIT_ACTION:
                        break  # Exit the loop as the user requested to exit.
                except KeyboardInterrupt:
                    print(f'{YELLOW}[WARNING]: {WHITE}Keyboard interrupted, please try again.')

        except sock.error:
            print(f'{RED}[PROCESS STOPPED]: {WHITE}Communication with the server has failed/ended, goodbye.')
        except Exception as err:
            print(f'{RED}[PROCESS STOPPED]: {WHITE}{err}')


if __name__ == '__main__':
    main()