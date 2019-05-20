# This file contains the objects that encompass the basic Split Learning protocol. 
# They can be changed to anything you want. The Client API will serialize this objects
#  and send them to the desired client. 

# Asks the other side to reset the current model if any. Receives confirmation back
class ResetModelPackage():
    pass

class NewModelReadyPackage():
    pass

# Asks the other side to train with the following data and labels. It should return a backward prop object. 
class ForwardPropPackage():
    def __init__(self, y, labels):
        self.y = y
        self.labels = labels

class BackwardPropPackage():
    def __init__(self, grad, loss):
        self.grad = grad
        self.loss = loss

# Packages to evaluate the model
class EvaluatePackage():
    def __init__(self, y):
        self.y = y

class EvaluationPackage():
    def __init__(self, logps):
        self.logps = logps