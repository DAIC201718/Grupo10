'''
Created on 16 de oct. de 2015

@author: ialonso2
'''
import socket
import subprocess
import pickle

def server():
    #create an INET, STREAMing socket
    serversocket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    #bind the socket to a public host,
    # and a well-known port
    serversocket.bind(('localhost', 8088))
    #become a server socket
    serversocket.listen(5)
    while 1:
        #accept connections from outside
        (clientsocket, address) = serversocket.accept()
        #now do something with the clientsocket
        #in this case, we'll pretend this is a threaded server
        print(clientsocket)
        msg=pickle.loads(clientsocket.recv(1024))
        
        print(msg) 
        if msg =='quit':
            clientsocket.send('exito')
            break
        else:
            if msg=='1':
                rolf=subprocess.call(["ping","www.marca.com"],shell=True)
                print rolf
                clientsocket.send('exito')
            else:
                clientsocket.send("Recibido")

    serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()
    print("fin")
    
print("servidor")
server()



