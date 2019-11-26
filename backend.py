#!/usr/bin/env python

import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 22222))

sock.listen(1)


while True:
    conn, addr = sock.accept()
    print("This be from {}".format(addr))
    print(conn.recv(1024))
    conn.close()



