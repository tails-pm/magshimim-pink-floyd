import socket as sock

LISTEN_PORT = 7160
RECEIVE_CHECK = 'Request type: %s received!\nRequest code: %3d'
EXIT_CODE = 249

def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as listening_sock:
        listening_sock.bind(('', LISTEN_PORT))
        listening_sock.listen(1)


        try:
            client_sock, client_addr = listening_sock.accept()
            msg_code = 0
            with client_sock:
                pass
                # TODO: continue where i left off with the skeleton
                # while msg_code is not EXIT_CODE:
                #     client_sock.sendall('Welcome to PinkFloyd Debug Server!'.encode())
        except Exception as e:
            pass



if __name__ == "__main__":
    main()