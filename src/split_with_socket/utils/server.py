# Simple relay server: a communication server where two clients 
# connect to and can message each other by name
# 
# It accepts socket connections with the relay protocol
#
# USAGE: 
#   python server.py

import socket # for connecting to the server
import atomic_socket
import _thread # to manage multiple clients
import relay_protocol as protocol

host = '0.0.0.0' # host public IP address
port = 5004  # initiate port no above 1024

clients = {} # {id, socket} list of all clients connected to the server.  
lastFormattedMsg = {} # {id,message}

def server_program():
    print('Starting Relay Server at ' + host + ':' + str(port))  # show in terminal
    print('Waiting for clients...')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many clients the server can listen simultaneously
    server_socket.listen(2)

    while True:
        conn, address = server_socket.accept()  # accept new connection
        _thread.start_new_thread(on_new_client,(conn, address)) #puts the communication of this socket into a thread. 

    server_socket.close()  # close the connection when done. 

def on_new_client(clientsocket, addr):
    # wait for the first message, the client's name. 
    msgRaw = atomic_socket.recv(clientsocket)

    # First object is a registration object. 
    # Register the name of the client into the list. 
    obj = protocol.parse_data_msg(msgRaw)

    print("Connection from: " + str(addr) + " " + obj.client_id)
    
    # Register the socket name at a list. 
    clients[obj.client_id] = clientsocket

    # keeps waitinf for the messages. 
    wait_for_next_message(obj.client_id)

def wait_for_next_message(client_id): 
    clientsocket = clients[client_id]

    # keeps waitinf for the messages. 
    # msgRaw = clientsocket.recv(buffer_size)
    msgRaw = atomic_socket.recv(clientsocket)

    while msgRaw:      
        print("Message received from " + client_id + ": " + msgRaw)
    
        try: 
            obj = protocol.parse_data_msg(msgRaw)
            print("Object decoded " + obj.__class__.__name__)

            if type(obj) is protocol.Repeat:
                print('Repeating the message ' + lastFormattedMsg[obj.client_id])
                atomic_socket.send(clientsocket, lastFormattedMsg[obj.client_id])
            elif type(obj) is protocol.SendTo: 
                if obj.client_id in clients.keys():
                    #reformat the message and store it if we need to repeat it.    
                    lastFormattedMsg[obj.client_id] = protocol.relay_message(client_id,  obj.data)
                    print('Sending message to ' + obj.client_id + ' with data ' + lastFormattedMsg[obj.client_id])
                    # sending it to the next partner   
                    atomic_socket.send(clients[obj.client_id], lastFormattedMsg[obj.client_id])
                else:
                    print(obj.client_id + ' is not connected. Sending error message back.')
                    atomic_socket.send(clientsocket, protocol.not_connected(obj.client_id))
            else: 
                print('Unexpected object ' + obj.__class__.__name__ + ' as a reply to server')
        
        except Exception as inst:
            print('Exception')
            print(inst)
            atomic_socket.send(clientsocket, protocol.repeat(client_id))

        #wait for next message
        msgRaw = atomic_socket.recv(clientsocket)

    clientsocket.close()

if __name__ == '__main__':
    server_program()