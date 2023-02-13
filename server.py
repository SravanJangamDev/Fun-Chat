# import socket programming library
import socket

# import thread module
import threading

print_lock = threading.Lock()


# thread function
def threaded(c):
    while True:
        # data received from client
        data = c.recv(1024)
        if not data:
            print("Client Closed the connection")

            # lock released on exit
            # print_lock.release()
            break

        # send back reversed string to client
        print(data)
        # c.send(data)

    # connection closed
    c.close()


def Main():
    host = ""
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        c, addr = s.accept()

        # lock acquired by client
        # print_lock.acquire()
        print("Connected to :", addr[0], ":", addr[1])

        # Start a new thread and return its identifier
        threading.Thread(threaded, (c,)).start()
    s.close()


if __name__ == "__main__":
    Main()
