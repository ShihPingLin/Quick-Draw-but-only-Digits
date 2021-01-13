import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from dataset import MNIST
from model import Net

def test(model, device, test_image):
    transform=transforms.Compose([
        transforms.Resize((28,28)),
        transforms.ToTensor(),
        ])
    model.eval()
    with torch.no_grad():
        # data = Image.open(test_image).convert('L')
        data = Image.fromarray(test_image).convert('L')
        data = transform(data)
        data = torch.unsqueeze(data, 0)
        data = data.to(device)
        output = model(data)
        print(output)
        pred = output.max(1, keepdim=True)[1] # get the index of the max log-probability

    return pred

def main():
    # Testing settings
    parser = argparse.ArgumentParser(description='MNIST Testing')
    parser.add_argument('--test_image', type=str, help="Testing images file")
    parser.add_argument('--load', type=str, default='best_mnist.pth', help="Model checkpoint path")
    args = parser.parse_args()

    use_cuda = torch.cuda.is_available()

    device = torch.device("cuda" if use_cuda else "cpu")

    model = Net().to(device)

    state = torch.load(args.load)
    model.load_state_dict(state)
    pred = test(model, device, args.test_image)
    print(pred.item())

if __name__ == '__main__':
    main()