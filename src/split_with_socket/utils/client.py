# Simple client library for the relay server, a communication server where two clients 
# connect to and can message each other by name. 
# 
# It sends socket connections with the relay protocol and guarantees the delivery of 
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
import time
import utils.relay_protocol as protocol
import utils.atomic_socket as atomic_socket
import pickle # object serialization 
import base64 # Make sure the serialized object can be transformed into a string

buffer_size = 35000

# instantiate
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
client_name = ''

last_message = ''

def connect(relay_server_host, relay_server_port, client_id):
    global client_name
    client_name = client_id
    print('Starting Client ' + client_id)  # show in terminal
    
    # connect to the server
    client_socket.connect((relay_server_host, relay_server_port)) 

    # register this computer by name
    atomic_socket.send(client_socket, protocol.register(client_id))

    # Wait for 1 second otherwise socket concatenates the two sends
    time.sleep(1)

def sendData(to, data):
    global last_message
    print('Sending ' + data.__class__.__name__ + ' data to ' + to)
    last_message = protocol.send(to, serializeObjToStr(data))
    atomic_socket.send(client_socket, last_message)

def receiveData():
    while True: 
        try:
            msgRaw = atomic_socket.recv(client_socket)
            obj = protocol.parse_data_msg(msgRaw)

            if type(obj) is protocol.Repeat:
                print('Repeating: ' + last_message)
                atomic_socket.send(client_socket, last_message)
            elif type(obj) is protocol.PartnerNotConnected:
                print('Error: ' + obj.client_id + ' not connected')
            elif type(obj) is protocol.ReceivedFrom:
                object = deserializeStrToObj(obj.data)
                print('Received ' + object.__class__.__name__ + ' data from ' + obj.client_id)
                return object
        except Exception as inst:
            print(inst)
            atomic_socket.send(client_socket, protocol.repeat(client_name))

    return

def serializeObjToStr(data):
    picked_byte_representation = pickle.dumps(data)
    serialized_bytes = base64.b64encode(picked_byte_representation)
    return serialized_bytes.decode('utf-8')

def deserializeStrToObj(str): 
    encodedStr = str.encode('utf-8')
    picked_byte_representation = base64.b64decode(encodedStr)
    return pickle.loads(picked_byte_representation)    

def disconnect():
    client_socket.close()  # close the connection