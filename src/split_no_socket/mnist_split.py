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

model_1 = nn.Sequential(nn.Linear(input_size, hidden_sizes[0]),
					nn.ReLU(),
					nn.Linear(hidden_sizes[0], hidden_sizes[1]))


model_2 = nn.Sequential(nn.ReLU(),
					nn.Linear(hidden_sizes[1], output_size),
					nn.LogSoftmax(dim=1))


criterion = nn.NLLLoss()

optimizer_1 = optim.SGD(model_1.parameters(), lr=0.003, momentum=0.9)
optimizer_2 = optim.SGD(model_2.parameters(), lr=0.003, momentum=0.9)

time0 = time()

epochs = 15

for e in range(epochs):
	running_loss = 0
	img = 0

	for images, labels in trainloader:
		# Flatten MNIST images into a 784 long vector
		images = images.view(images.shape[0], -1)
		
		# clean the gradients
		optimizer_1.zero_grad()
		optimizer_2.zero_grad()

		# evaluate the first model
		output_1 = model_1(images)

		# get the gradients 
		y2 = Variable(output_1.data, requires_grad=True)

		# evaluate the 2nd model with the gradients 
		output_2 = model_2(y2)

		# calculate the loss
		loss = criterion(output_2, labels)

		# backprop the second model
		loss.backward()

		# continue backproping through the first model with the gradients (that have been updated)
		output_1.backward(y2.grad)
		
		#optimize the weights for both models
		optimizer_1.step()
		optimizer_2.step()
		
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
			output1 = model_1(img)
			y2 = Variable(output1.data, requires_grad=True)
			logps = model_2(y2)

		ps = torch.exp(logps)
		probab = list(ps.numpy()[0])
		pred_label = probab.index(max(probab))
		true_label = labels.numpy()[i]
		if(true_label == pred_label):
			correct_count += 1
		all_count += 1

print("Number Of Images Tested =", all_count)
print("\nModel Accuracy =", (correct_count/all_count))