import utils.client as client
import data_package as dataPkg

import os
import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
from time import time
from torchvision import datasets, transforms
from torch import nn, optim
from torch.autograd import Variable

relay_server_host = '127.0.0.1'  # as both code is running on same pc
relay_server_port = 5004  # socket server port number

client_id = 'MIT'
client_send_to = 'HARVARD'

#define transformations
transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.5,), (0.5,)),])

#download dataset
trainset = datasets.MNIST('/Users/vitorhome/Documents/workspace/splitlearning_relayserver/datasets/train', download=True, train=True, transform=transform)
valset = datasets.MNIST('/Users/vitorhome/Documents/workspace/splitlearning_relayserver/datasets/val', download=True, train=False, transform=transform)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
valloader = torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)

#define models
hidden_sizes = [128, 64]
output_size = 10

criterion = nn.NLLLoss()

model = None
optimizer = None

def reset_model():
    global model
    model = nn.Sequential(nn.ReLU(),
					nn.Linear(hidden_sizes[1], output_size),
					nn.LogSoftmax(dim=1))
    
    global optimizer
    optimizer = optim.SGD(model.parameters(), lr=0.003, momentum=0.9)

    return dataPkg.NewModelReadyPackage()

def train_loop(fwd_package):
    # cleaning gradients
    optimizer.zero_grad()

    # evaluate
    output = model(fwd_package.y)

    # calculate losses
    loss = criterion(output, fwd_package.labels)

    # backprop
    loss.backward()

    # update weights
    optimizer.step()

    #return backward Prop package to Harvard.
    return dataPkg.BackwardPropPackage(fwd_package.y.grad, loss.item())

def eval(eval_package):
    output = model(eval_package.y)
    return dataPkg.EvaluationPackage(output)

def mit_program():
    client.connect(relay_server_host, relay_server_port, client_id)
    
    reset_model()

    while True:
        package = client.receiveData()

        if type(package) is dataPkg.ResetModelPackage: 
            client.sendData(client_send_to, reset_model())
        if type(package) is dataPkg.ForwardPropPackage: 
            client.sendData(client_send_to, train_loop(package))
        if type(package) is dataPkg.EvaluatePackage: 
            client.sendData(client_send_to, eval(package))   

    client.disconnect()  # close the connection

if __name__ == '__main__':
    mit_program()