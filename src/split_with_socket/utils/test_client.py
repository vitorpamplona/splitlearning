import utils.client as client

#relay_server_host = 'nebula.media.mit.edu'  # as both code is running on same pc
#relay_server_host = 'ec2-3-14-72-103.us-east-2.compute.amazonaws.com'
relay_server_host = '127.0.0.1' 
relay_server_port = 5004  # socket server port number

client_id = 'ME'
client_send_to = 'ME'
test_data = 'Hello'

class DataPackage():
    def __init__(self, s):
        self.s = s


client.connect(relay_server_host, relay_server_port, client_id)

print('Testing sending the word ' + test_data)

client.sendData(client_send_to, DataPackage(test_data))

print('Received back the word: ' + client.receiveData().s)

client.disconnect()  # close the connection

