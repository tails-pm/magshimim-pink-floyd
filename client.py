import socket as sock
import re

SERVER_ADDRESS = ('127.0.0.1', 7160)

# Base commands in ASIB without data as we just want to test if the server received them and identifies them appropriately.
ASIB_COMMAND_LIST = ['200:ABMLIST',
                         '207:SNGINABM',
                         '214:SNGDUR',
                         '221:SNGLYR',
                         '228:ABMFROMSNG',
                         '235:SNGBYNAME',
                         '242:SNGBYLYR',
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

EXIT_ACTION = 8

"""The pattern will match to a string if it has the following pattern:
        First capturing group `(\d{3})`:
            \d{3}` three digit number.
        `:ERROR:` matches the characters ':ERROR:' (case sensitive)
        Second capturing group `([A-Z]+)`:
            `[A-Z]+` one or more uppercase letters (case sensitive).
        `:` matches the character ':'.
        Third capturing group `(\w+(?: \w+)*)`:
            `\w+` one or more word characters.
            `(?: \w+)` Non capturing group meaning it is part of the Third capture group:
                ` ` space character.
                `\w+` one or more word characters.
            `*` match Non capturing group zero or unlimted times.
"""
ERROR_PTRN = re.compile(r'(\d{3}):ERROR:([A-Z]+):(\w+(?: \w+)*)')

class console_colors:
    # This class is only used for aestetic reasons, and has no effect in the codes structure.
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[0m'
    GREEN = '\033[92m'

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
                    print(f'{console_colors.YELLOW}[WARNING]: {console_colors.WHITE}{err}{err.args}, please try again.')
                    continue # As an invalid input was catched try getting the input again.

                request = ASIB_COMMAND_LIST[choice - 1].encode() # Step down the choice to fit a lists index.
                server_sock.sendall(request)

                reply = server_sock.recv(1024).decode()

                re_reply = ERROR_PTRN.search(reply) # Check if the servers reply is an error.
                if re_reply is not None: # If the servers reply does not match an error command print normally.
                    print(f'{console_colors.GREEN}[SERVER]: {console_colors.WHITE}{reply}\n')
                else:
                    print(f'{console_colors.RED}[ERROR {re_reply.group(1)}]: {console_colors.YELLOW}{re_reply.group(2)}, {console_colors.WHITE}{re_reply.group(3)}')
                
                if choice == EXIT_ACTION:
                    break # Exit the loop as the user requested to exit.
        except Exception as err:
            print(f'{console_colors.RED}[PROCESS STOPPED]: {console_colors.WHITE}{err}')

if __name__ == '__main__':
    main()