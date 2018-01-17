'''
Created on 16 de oct. de 2015

@author: ialonso2
'''

import socket
def client(string):
    print type(string)
    HOST, PORT = 'localhost', 8088
    # SOCK_STREAM == a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.setblocking(0)  # optional non-blocking
    sock.connect((HOST, PORT))
    sock.send(string)
    reply = sock.recv(1024)  # limit reply to 16K
    print(reply)
    sock.close()
    return reply

print "cliente"
client('1')
#client('MENSAJE =)')