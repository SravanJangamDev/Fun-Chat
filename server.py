import socket
import multiprocessing

HOST = ""
PORT = 12347
CONN_LIMIT = 10
clients: list = []


class Client:
    def __init__(self, conn, ip, port, username="", verified=False):
        self.conn = conn
        self.ip = ip
        self.port = port
        self.username = username
        self.verified = verified

    def __str__(self):
        return self.username


def not_authorised_user(username, password):
    return False


def send_to_all_clients(msg: str, client) -> None:
    for c in clients:
        print(c)
        if c.conn == client.conn or (c.verified is False):
            continue

        c.conn.sendall(msg.encode())


def recv_data(client):
    data = ""
    while True:
        data = client.conn.recv(1024).decode()
        if data:
            break

    return data


def handle_connection(client):
    global clients
    username = ""
    password = ""
    msg = ""
    try:
        username = recv_data(client)
        password = recv_data(client)
        if not_authorised_user(username, password):
            client.conn.sendall("Wrong username or password".encode())

        client.verified = True
        client.username = username
        send_to_all_clients(f"{username} connected..", client)

        while True:
            msg = recv_data(client)
            send_to_all_clients(f"{username}: {msg}", client)

    except Exception as e:
        print(f"Error {username}. {e}")

    finally:
        clients = [c for c in clients if c.ip != client.ip]
        client.conn.close()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print("socket binded to port", PORT)

    s.listen(CONN_LIMIT)
    print("socket is listening")

    try:
        while True:
            conn, addr = s.accept()
            client = Client(conn, addr[0], addr[1])
            clients.append(client)
            print("Client connected to :", addr[0], ":", addr[1])

            # Start a new thread and return its identifier
            p = multiprocessing.Process(
                target=handle_connection, args=(client,)
            )
            p.start()
    except Exception as e:
        print(f"Exception occured: {e}")

    finally:
        for c in clients:
            c.conn.close()
        s.close()


if __name__ == "__main__":
    main()
