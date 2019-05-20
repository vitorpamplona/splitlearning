# Simple client library for the relay server, a communication server where two clients 
# connect to and can message each other by name. 
# 
# It sends socket connections with a specific json protocol and guarantees the delivery of 
#   the messages to the server and back to the client. 
#
# 1. Registration: {"client_id": client_id}
#   This informs the server the name of the current socket connection
#
# 2. Send message to: {"to": the_other_client_id, "data": any object}
#   Informs the server to send the data to another known client
# 
# USAGE: 
#   1. connect(SERVER_IP, PORT, CLIENT_ID) connects to the server and registers as a CLIENT_ID
#   2. sendData(CLIENT_ID, DATA) sends any python object to the desired client
#   3. receiveData() locks the current thread until it receives an object back. 
#   4. disconnect() closes the socket. 

import socket # for connecting to the server
import json # to enconde and decode the data
import time
import pickle
import base64

buffer_size = 35000

# instantiate
client_socket = socket.socket()  
client_name = ''

last_message = ''.encode()

def connect(relay_server_host, relay_server_port, client_id):
    global client_name
    client_name = client_id
    print('Starting Client ' + client_id)  # show in terminal
    
    # connect to the server
    client_socket.connect((relay_server_host, relay_server_port)) 

    # register this computer by name
    client_socket.send(format_client_id_msg(client_id))  

    # Wait for 1 second otherwise socket concatenates the two sends
    time.sleep(1)

def sendData(to, data):
    serialized_bytes = base64.b64encode(pickle.dumps(data))
    serialized_str = serialized_bytes.decode('utf-8')
    print('Sending ' + data.__class__.__name__ + ' data to ' + to + ' with '+str(len(serialized_str))+' bytes')
    global last_message
    last_message = format_data_msg(to, serialized_str)
    client_socket.send(last_message)

def receiveData():
    while True: 
        try:
            msg = parse_data_msg(client_socket.recv(buffer_size))

            if 'repeat' in msg.keys():
                print(last_message)
                client_socket.send(last_message)
            elif 'error' not in msg.keys():
                #print('Received data ' + msg['data'] + ' from ' + msg['from'])
                
                serialized_data = base64.b64decode(msg['data'].encode('utf-8'))
                object = pickle.loads(serialized_data)
                print('Received  ' + object.__class__.__name__ + ' data from ' + msg['from'])
                return object
            else:
                print('Error, other client wasn\'t connected')
        except Exception as inst:
            print(inst)
            client_socket.send(format_repeat(client_name))

    return

def disconnect():
    client_socket.close()  # close the connection

def format_data_msg(to, data):
    message = {"to": to, "data": data}
    return json.dumps(message).encode()

def format_client_id_msg(client_id):
    return json.dumps({"client_id": client_id}).encode()

def format_repeat(client_id):
    return json.dumps({"from": client_id, "repeat": "last_one"}).encode()

def parse_data_msg(data):
    return json.loads(data.decode()) 