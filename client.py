import socket as sock
SERVER_PORT = 7160
SERVER_IP = '127.0.0.1'
SKELETON_COMMAND_LIST = ['200:ABMLIST',
                         '207:SNGINABM',
                         '214:SNGDUR',
                         '221:SNGLYR',
                         '228:ABMFROMSNG',
                         '235:SNGBYNAME',
                         '242:SNGBYLYR',
                         '249:EXIT']

CHOICE_MENU = """Please choose one of the following actions:
1. List albums.
2. List songs in album
3. Get song duration.
4. Get song lyrics.
5. Get album from song.
6. Get song by name.
7. Get song by lyrics.
8. Exit.
"""

def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as server_sock:
        server_address = (SERVER_IP, SERVER_PORT)

        try:
            server_sock.connect(server_address)
            # TODO: continue where i left off with the skeleton
            print(server_sock.recv(1024).decode()) # Print Welcome Message
            while True:
                print(CHOICE_MENU)
                choice = int(input('Please make your choice: '))
                if choice > 0 and choice < 9:
                    choice -= 1 # Step down the choice to fit a lists index
                    msg = SKELETON_COMMAND_LIST[choice].encode()
                    server_sock.sendall(msg)
                    print(server_sock.recv(1024).decode())
                    print() #New line
                    if choice == 7:
                        break
        except Exception as err:
            print(err)

if __name__ == "__main__":
    main()