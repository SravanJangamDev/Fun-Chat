# Import socket module
import socket
import multiprocessing

HOST = ""
PORT = 12347


def receive_from_server(conn) -> None:
    while True:
        msg = conn.recv(1024).decode()
        if msg:
            print(msg)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    username = input("Enter Username: ")
    s.sendall(username.encode())
    try:
        p = multiprocessing.Process(target=receive_from_server, args=(s,))
        p.start()

        while True:
            message = input()
            if message:
                s.sendall(message.encode())
                print(f"You: {message}")
    except Exception as e:
        print(f"Exception occured. {e}")
    finally:
        s.close()


if __name__ == "__main__":
    main()
