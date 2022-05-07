import socket as sock
import re
from data import data

LISTEN_PORT = 7160

DB = data() # Create the db object so we can create the list of commands.
REQ_COMMANDS = {
    200: DB.get_albms,
    207: DB.get_albm_songs,
    214: DB.get_sng_dur,
    221: DB.get_song_lyr,
    228: DB.find_songs_albm,
    235: DB.songs_by_name,
    242: DB.songs_by_lyr
}

WELCOME_MSG = 'Welcome to PinkFloyd Archive Server!\n'
GOODBYE_MSG = 'Thank you for your time!\n'
RES_FORMAT = 'OK:{0}&{1}\n'

ERR_DB_FORMAT = "707:ERROR:UNKNOWN:\"{0}\" wasn't found.\n"
ERR_SYNTAX = '700:ERROR:BADREQ:Invalid command was received.\n'

EXIT_CODE = 249

# Regex patterns.
"""The pattern will match to a string if it has the following pattern:
        First capturing group `(\d{3})`:
            \d{3}` three digit number.
        `:` matches the character ':'.
        Second capturing group `([A-Z]+)`:
            `[A-Z]+` one or more uppercase letters (case sensitive).
        `:` matches the character ':'.
        `(?:&(\w+(?: \w+)*))?')` Non capturing group meaning its not part of any capture group:
            `&` matches the character '&'.
            Third capturing group `(\w+(?: \w+)*)`:
                `\w+` one or more word characters.
                `(?: \w+)` Non capturing group meaning it is part of the Third capture group:
                    ` ` matches the character ' '.
                    `\w+` one or more word characters.
                `*` match Non capturing group zero or unlimted times.
        `?` match Non capturing group zero or one time.
"""
REQ_PTRN = re.compile(r'(\d{3}):([A-Z]+)(?:&(\w+(?: \w+)*))?')

# These constants are only used for aestetic reasons, and has no effect in the codes structure.
RED = '\033[91m'
YELLOW = '\033[93m'
WHITE = '\033[0m'
GREEN = '\033[92m'


def create_response(re_req : re.Pattern[str]) -> bytes:
    """create_response creates the ASIB response for the client.
    
    Args:
        re_req (re.Pattern[str]): the regex match of the clients ASIB request.
    
    Returns:
        bytes: encoded ASIB response.
    """    
    # Run the command of the clients ASIB request type and request data.
    db_data = REQ_COMMANDS.get(int(re_req.group(1)))(re_req.group(3))

    if db_data is not None: # If the db_data was received properly set the response accordingly.
        response = RES_FORMAT.format(re_req.group(2), db_data) 
    else: # Otherwise set the response as an error response.
        response = ERR_DB_FORMAT.format(re_req.group(3))

    return response.encode()


def main():
    while True:
        with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as listening_sock:
            listening_sock.bind(('', LISTEN_PORT))
            listening_sock.listen(1)
            try:
                client_sock, client_addr = listening_sock.accept()
                print(f'{GREEN}[NOTICE]: {WHITE}User has connected to the server.')

                with client_sock:
                    client_sock.sendall(WELCOME_MSG.encode()) # Send Welcome message.
                    
                    while True:
                        req = client_sock.recv(1024).decode()
                        
                        re_req = REQ_PTRN.search(req) # Check if the message received fits the requests of ASIB protocol.
                       
                        if re_req is None: # If the message received does not match.
                            client_sock.sendall(ERR_SYNTAX.encode())
                            continue # As an invalid message was received continue to the next iteration.
                        
                        if int(re_req.group(1)) is EXIT_CODE:
                            client_sock.sendall(GOODBYE_MSG.encode())
                            break # Exit the loop as the user requested to exit.
                        
                        client_sock.sendall(create_response(re_req)) # If all is well, send the client its requested data.
            except Exception as err:
                print(f'{RED}[ERROR]: {WHITE}{err}')
            finally:
                print(f'{YELLOW}[NOTICE]: {WHITE}User has disconnected from the server.')



if __name__ == "__main__":
    main()