# Protocol using JSON for a Relay Server 
#
# 1. Registration: {"register_client_id": [name of the requested client]}
#   This informs the server the name of the current socket connection
#
# 2. Send message to: {"to": the_other_client_id, "data": any object}
#   Informs the server to send the data to another known client
# 
# If the client is not found, the server returns: 
#   Client not connected: {"client_id_not_connected": [name of the requested client]}
# 
# If the message arrives broken, you can ask the client to send again: 
#   Repeat last message: {"repeat_last_from": client_id}

import json # to enconde and decode the data

# Registration object for new connections
class Registration:
    def __init__(self, client_id):
        self.client_id = client_id

# Client receives a message from another client. 
class ReceivedFrom:   
    def __init__(self, client_id, data):
        self.client_id = client_id 
        self.data = data

# Client sends a message to another client. 
class SendTo:   
    def __init__(self, client_id, data):
        self.client_id = client_id 
        self.data = data  

# Repeat call to ask servers and clients to repeat their last message
class Repeat:
    def __init__(self, client_id):
        self.client_id = client_id

# Tells the client that the partner is not connected
class PartnerNotConnected:
    def __init__(self, client_id):
        self.client_id = client_id

# Process any received messages in the objects above. 
def parse_data_msg(data):
    msg = json.loads(data)

    if 'repeat_last_from' in msg.keys():
        return Repeat(msg['repeat_last_from'])
    
    if 'client_id_not_connected' in msg.keys():
        return PartnerNotConnected(msg['client_id_not_connected']) 

    if 'from' in msg.keys():
        return ReceivedFrom(msg['from'], msg['data'])

    if 'to' in msg.keys():
        return SendTo(msg['to'], msg['data'])  

    if 'register_client_id' in msg.keys(): 
        return Registration(msg['register_client_id'])

    return

# Creates the send message to another client. 
def send(to, serialized_str):
    message = {"to": to, "data": serialized_str}
    return json.dumps(message)

# Server relays a SendTo package into a ReceivedFrom package and sends it to the receiving client. 
def relay_message(client_id, data):
    return json.dumps({'from': client_id, 'data': data})

# Creates the registration message for the client to send to the server. 
def register(client_id):
    return json.dumps({"register_client_id": client_id})

# Creates the repeat message to send to the server. 
def repeat(client_id):
    return json.dumps({"repeat_last_from": client_id})

# Tells the client that the partner he is asking to connect to in not available. 
def not_connected(to):
    return json.dumps({"client_id_not_connected": to})  
