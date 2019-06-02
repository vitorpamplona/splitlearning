# Socket wrapper that sends the amount of data before each message. 

buffer_size = 4096    

def send(socket, data): 
    bytes = len(data.encode())
    socket.sendall(str(format(bytes, '10d')).encode())
    socket.sendall(data.encode())

def recv(socket):
    # Look for the response
    data = socket.recv(10)
    if (len(data) == 0):
        return

    amount_received = 0
    amount_expected = int(data)

    complete_str = ""

    while amount_received < amount_expected:
        data = socket.recv(buffer_size)
        amount_received += len(data)
        complete_str += data.decode()

    return complete_str