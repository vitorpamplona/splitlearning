# Split Learning with a Relay Server

Simple MNIST Machine Learning code in three ways: 
1. Normal: sequential code to train and test an MNIST model (no split, no sockets)
2. Split: Split learning code to train and test an MNIST model (no sockets)
3. Split w/ Sockets: Split learning code to train and test an MNIST model between machines at Harvard - first layers - and MIT - last layers - using a relay message server. 

# Running Locally

Open 5 terminal windows and run in this sequence. 

## Terminal 1: Regular MNist code
```
python3 src/no_split/mnist.py
```

Expected output: Model Accuracy = 0.9775

## Terminal 2: Split Learning (no sockets) code
```
python3 src/split_no_socket/mnist_split.py
```

Expected output: Model Accuracy = 0.9742

## Terminal 3,4,5: Split Learning with a Relay Server

### Terminal 3: Relay Server 
```
python3 src/split_with_socket/utils/server.py
```

### Terminal 4: Run MIT
```
python3 src/split_with_socket/mnistMIT.py
```

### Terminal 5: Run Harvard
```
python3 src/split_with_socket/mnistHarvard.py 
```
Expected output: Model Accuracy = 0.9719

# Installing a server: 

Basic OS update:
```
sudo apt update
sudo apt upgrade
sudo hostnamectl set-hostname mit-relay
sudo shutdown -r now
```

Setup GIT
```
git config --global user.email "<YOUR EMAIL>"
git config --global user.name "<YOUR USERNAME>"
git clone https://github.mit.edu/vitor-1/split_learning_relay_server.git
```

Install Python for the server
```
sudo apt install python3
sudo apt install python3-pip
```

Install the ML tools if you want to run everything on the server for testing purposes. 
```
pip3 install torch
pip3 install torchvision
pip3 install matplotlib
pip3 install numpy
```

Pytorch needs at least 1.5GB of RAM. If you need more memory, don't forget to add a swap file 
```
sudo dd if=/dev/zero of=/swapfile bs=1k count=2048k
sudo chown root:root /swapfile
sudo chmod 0600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

To remove the Swap file 
```
sudo swapoff /swapfile
sudo rm /swapfile
```
