# Split Learning with a Relay Server

Simple MNIST Machine Learning code in three ways: 
1. Normal: sequential code to train and test an MNIST model (no split, no sockets)
2. Split: Split learning code to train and test an MNIST model (no sockets)
3. Split w/ Sockets: Split learning code to train and test an MNIST model between machines at Harvard - first layers - and MIT - last layers - using a relay message server. 

# Running

Open 5 terminal windows and run in this sequence. 

## Terminal 1: Normal code
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