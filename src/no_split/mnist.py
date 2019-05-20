import os
import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
from time import time
from torchvision import datasets, transforms
from torch import nn, optim
from torch.autograd import Variable

#define transformations
transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.5,), (0.5,)),])

#download dataset
trainset = datasets.MNIST('/Users/vitorhome/Documents/workspace/splitlearning_relayserver/datasets/train', download=True, train=True, transform=transform)
valset = datasets.MNIST('/Users/vitorhome/Documents/workspace/splitlearning_relayserver/datasets/val', download=True, train=False, transform=transform)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
valloader = torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)

#define models
input_size = 784
hidden_sizes = [128, 64]
output_size = 10

# Build a feed-forward network
model = nn.Sequential(nn.Linear(input_size, hidden_sizes[0]),
                      nn.ReLU(),
                      nn.Linear(hidden_sizes[0], hidden_sizes[1]),
                      nn.ReLU(),
                      nn.Linear(hidden_sizes[1], output_size),
                      nn.LogSoftmax(dim=1))

criterion = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr=0.003, momentum=0.9)

time0 = time()
epochs = 15
for e in range(epochs):
	running_loss = 0
	img = 0

	for images, labels in trainloader:
		# Flatten MNIST images into a 784 long vector
		images = images.view(images.shape[0], -1)
		
		# Clean the gradients
		optimizer.zero_grad()

		# evaluate full model in one pass. 
		output = model(images)

		# calculate loss
		loss = criterion(output, labels)

		#backprop the second model
		loss.backward()
		
		#optimize the weights
		optimizer.step()
		
		running_loss += loss.item()

		img = img+1

		print("Epoch {} {} - Training loss: {}".format(e, img, running_loss/len(trainloader)))
	else:
		print("Epoch {} - Training loss: {}".format(e, running_loss/len(trainloader)))

print("\nTraining Time (in minutes) =",(time()-time0)/60)


correct_count, all_count = 0, 0
for images,labels in valloader:
	for i in range(len(labels)):
		img = images[i].view(1, 784)
		with torch.no_grad():
			logps = model(img)

		ps = torch.exp(logps)
		probab = list(ps.numpy()[0])
		pred_label = probab.index(max(probab))
		true_label = labels.numpy()[i]
		if(true_label == pred_label):
			correct_count += 1
		all_count += 1

print("Number Of Images Tested =", all_count)
print("\nModel Accuracy =", (correct_count/all_count))