import socket as sock
import re
import data

LISTEN_PORT = 7160
REQ_PTRN = re.compile(r'(\d{3}):([A-Z]+)(?:&(\w+(?: \w+)*))?')
RECEIVE_CHECK = 'Request type: %s received!\nRequest code: %3d'
EXIT_CODE = 249

def main():
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as listening_sock:
        listening_sock.bind(('', LISTEN_PORT))
        listening_sock.listen(1)


        try:
            client_sock, client_addr = listening_sock.accept()
            with client_sock:
                # TODO: continue where i left off with the skeleton
                client_sock.sendall('Welcome to PinkFloyd Debug Server!\n'.encode())
                while True:
                    req = client_sock.recv(1024).decode()
                    re_req = REQ_PTRN.search(req)
                    if re_req is None:
                        client_sock.sendall('707:ERROR:UNKNOWN:INVALID COMMAND WAS RECIVED.\n'.encode())
                    if int(re_req.group(1)) is EXIT_CODE:
                        client_sock.sendall('Thank you for your time!\n'.encode())
                        break

                    client_sock.sendall(RECEIVE_CHECK % (re_req.group(2), int(re_req.group(1))))
        except Exception as err:
            print(err)



if __name__ == "__main__":
    main()