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

#relay_server_host = 'nebula.media.mit.edu'  # as both code is running on same pc
relay_server_host = 'ec2-3-14-72-103.us-east-2.compute.amazonaws.com'
#relay_server_host = '127.0.0.1' 
relay_server_port = 5004  # socket server port number

client_id = 'HARVARD'
client_send_to = 'MIT'

#define transformations
transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.5,), (0.5,)),])

#download dataset
trainset = datasets.MNIST('/tmp/splitlearning_relayserver/datasets/train', download=True, train=True, transform=transform)
valset = datasets.MNIST('/tmp/splitlearning_relayserver/datasets/val', download=True, train=False, transform=transform)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
valloader = torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)

#define models
input_size = 784
hidden_sizes = [128, 64]

epochs = 15

def reset_model():
    model = nn.Sequential(nn.Linear(input_size, hidden_sizes[0]),
                            nn.ReLU(),
                            nn.Linear(hidden_sizes[0], hidden_sizes[1]))

    client.sendData(client_send_to, dataPkg.ResetModelPackage())
    package = client.receiveData()

    if (type(package) is dataPkg.NewModelReadyPackage):
        return model
    else:
        print('Could not reset model')

def train(client, model):
    optimizer = optim.SGD(model.parameters(), lr=0.003, momentum=0.9)
    for e in range(epochs):
        running_loss = 0
        img = 0
        for images, labels in trainloader:
            # Flatten MNIST images into a 784 long vector
            images = images.view(images.shape[0], -1)
            
            # Cleaning gradients
            optimizer.zero_grad()

            # evaluate
            output = model(images)

            if output.data.size() != (64,64): 
                continue

            # prepare data for MIT
            y2 = Variable(output.data, requires_grad=True)

            # send to MIT to contine the process. 
            client.sendData(client_send_to, dataPkg.ForwardPropPackage(y2,labels))  

            # wait for MIT to calculate
            bwd_package = client.receiveData()

             # backprop
            output.backward(bwd_package.grad)
            
            # optimize the weights
            optimizer.step()
            
            running_loss += bwd_package.loss

            img = img+1

            print("Epoch {} {} - Training loss: {}".format(e, img, running_loss/len(trainloader)))
        else:
            print("Epoch {} - Training loss: {}".format(e, running_loss/len(trainloader)))

    print("Training finished")

    return model

def test(client, model):
    correct_count, all_count = 0, 0
    for images,labels in valloader:
        for i in range(len(labels)):
            img = images[i].view(1, 784)
            
            with torch.no_grad():
                output = model(img)
                # Prepare data to send to MIT
                y2 = Variable(output.data, requires_grad=True)
                # Send to MIT to contine the process. 
                client.sendData(client_send_to, dataPkg.EvaluatePackage(y2))
                # Wait for MIT to calculate and return the logPs
                logps = client.receiveData().logps   

            ps = torch.exp(logps)
            probab = list(ps.detach().numpy()[0])
            
            pred_label = probab.index(max(probab))
            true_label = labels.numpy()[i]

            if (true_label == pred_label):
                correct_count += 1

            all_count += 1

    print("Number Of Images Tested =", all_count)
    print("\nModel Accuracy =", (correct_count/all_count))

def harvard_program():
    client.connect(relay_server_host, relay_server_port, client_id)

    model = reset_model()
    train(client, model)
    test(client, model)

    client.disconnect()

if __name__ == '__main__':
    harvard_program()