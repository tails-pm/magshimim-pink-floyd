import socket as sock
import re

LISTEN_PORT = 7160
"""The pattern will match to a string if it has the following pattern:
        First capturing group `(\d{3})`:
            \d{3}` three digit number.
        `:ERROR:` matches the characters ':ERROR:' (case sensitive)
        Second capturing group `([A-Z]+)`:
            `[A-Z]+` one or more uppercase letters (case sensitive).
        `:` matches the character ':'.
        `(?:&(\w+(?: \w+)*))?')` Non capturing group meaning its not part of any capture group:
        `&` matches the character '&'.
            Third capturing group `(\w+(?: \w+)*)`:
                `\w+` one or more word characters.
                `(?: \w+)` Non capturing group meaning it is part of the Fourth capture group:
                    ` ` space character.
                    `\w+` one or more word characters.
                `*` match Non capturing group zero or unlimted times.
        `?` match Non capturing group zero or one time.
"""
REQ_PTRN = re.compile(r'(\d{3}):([A-Z]+)(?:&(\w+(?: \w+)*))?')
DEFAULT_REPLY = 'Request type: %s received!\nRequest code: %3d'
EXIT_CODE = 249

def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as listening_sock:
        listening_sock.bind(('', LISTEN_PORT))
        listening_sock.listen(1)

        try:
            client_sock, client_addr = listening_sock.accept()
            with client_sock:
                client_sock.sendall('Welcome to PinkFloyd Debug Server!\n'.encode()) # Send Welcome message.
                
                while True:
                    req = client_sock.recv(1024).decode()
                    
                    re_req = REQ_PTRN.search(req) # Check if the message received fits the requests of ASIB protocol.
                    if re_req is None: # If the message received does not match.
                        client_sock.sendall('707:ERROR:UNKNOWN:INVALID COMMAND WAS RECIVED.\n'.encode())
                        continue # As an invalid message was received continue to the next iteration.
                    if int(re_req.group(1)) is EXIT_CODE:
                        client_sock.sendall('Thank you for your time!\n'.encode())
                        break # Exit the loop as the user requested to exit.

                    client_sock.sendall((DEFAULT_REPLY % (re_req.group(2), int(re_req.group(1)))).encode())
        except Exception as err:
            print(err)



if __name__ == "__main__":
    main()