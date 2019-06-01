# Simple relay server, a communication server where two clients 
# connect to and can message each other by name
# 
# It accepts socket connections with a specific json protocol: 
#
# 1. Registration: {"client_id": client_id}
#   This informs the server the name of the current socket connection
#
# 2. Send message to: {"to": the_other_client_id, "data": any object}
#   Informs the server to send the data to another known client
# 
# If the client is not found, the server returns: 
#   Client not connected: {"error": [name of the requested client] ' not found'}
# 
# If the message arrives broken, the server asks the client to send again: 
#   Repeat last message: {"repeat":'broken message'}
# 
# The client can also ask the server to send the message again by: 
#   Repeat last message: {"from": client_id, "repeat": "last_one"}
#
# USAGE: 
#   python server.py

import socket # for connecting to the server
import _thread # to manage multiple clients
import json # to enconde and decode the data

host = '0.0.0.0' # host public IP address
port = 5004  # initiate port no above 1024
buffer_size = 35000

clients = {} # {id, socket} list of all clients connected to the server.  
lastFormattedMsg = {} # {id,message}

def server_program():
    print('Starting Splitlearning Relay Server at ' + host + ':' + str(port))  # show in terminal
    print('Waiting for clients...')

    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together
    server_socket.settimeout(30)

    # configure how many clients the server can listen simultaneously
    server_socket.listen(2)

    while True:
        conn, address = server_socket.accept()  # accept new connection
        _thread.start_new_thread(on_new_client,(conn, address)) #puts the communication of this socket into a thread. 

    server_socket.close()  # close the connection when done. 

def on_new_client(clientsocket, addr):
    # wait for the first message, the client's name. 
    msgRaw = clientsocket.recv(1024).decode()

    # unpack Json {"client_id": client_id}
    msgDict = json.loads(msgRaw)

    print("Connection from: " + str(addr) + " " + msgDict['client_id'])
    
    # Register the socket name at a list. 
    clients[msgDict['client_id']] = clientsocket

    # keeps waitinf for the messages. 
    wait_for_next_message(clientsocket, msgDict['client_id'])

def wait_for_next_message(clientsocket, client_id): 
    # wait for a message. 
    msgRaw = clientsocket.recv(buffer_size).decode()

    while msgRaw:      
        print("Message received from " + client_id + ": " + msgRaw)
        #print("Message received from " + client_id)

        try: 
            # unpack json format {"to": client_send_to, "data": data}
            msgDict = json.loads(msgRaw)

            if 'repeat' in msgDict:
                # send last message again.
                print('Repeating')
                clients[msgDict['from']].send(lastFormattedMsg[msgDict['from']])  # send data to the client
            elif msgDict['to'] in clients.keys():
                #reformat the message    
                formattedMsg = json.dumps({'from': client_id, 'data': msgDict['data']})
                # sending it to the next partner   
                clients[msgDict['to']].send(formattedMsg.encode())  # send data to the client
                lastFormattedMsg[msgDict['to']] = formattedMsg
            else:
                print(msgDict['to'] + ' is not connected')
                # could not find the other socket 
                # sending error message back.
                clientsocket.send(json.dumps({'error':msgDict['to']+ ' not found'}).encode())  # send data to the client
        except Exception as inst:
            print(inst)
            clientsocket.send(json.dumps({'repeat':'broken message'}).encode()) 

        #wait for next message
        msgRaw = clientsocket.recv(buffer_size).decode()

    clientsocket.close()

if __name__ == '__main__':
    server_program()