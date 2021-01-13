import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.backends import cudnn
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import Dataset, DataLoader
from dataset import MNIST
from model import Net

def train_one_epoch(args, model, device, train_loader, optimizer, epoch):
    criterion = nn.CrossEntropyLoss()
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))

def validate(model, device, val_loader):
    criterion = nn.CrossEntropyLoss(reduction='sum')
    model.eval()
    val_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            val_loss += criterion(output, target).item()  # sum up batch loss
            pred = output.max(1, keepdim=True)[1] # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    val_loss /= len(val_loader.dataset)

    print('\nVal set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        val_loss, correct, len(val_loader.dataset),
        100. * correct / len(val_loader.dataset)))

    return val_loss, 100. * correct / len(val_loader.dataset)

def main():
    # Training settings
    parser = argparse.ArgumentParser(description='MNIST Training')
    parser.add_argument('--batch_size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--val_batch_size', type=int, default=1000, metavar='N',
                        help='input batch size for val (default: 1000)')
    parser.add_argument('--epochs', type=int, default=15, metavar='N',
                        help='number of epochs to train (default: 14)')
    parser.add_argument('--lr', type=float, default=1e-3, metavar='LR',
                        help='learning rate (default: 1e-3)')
    parser.add_argument('--momentum', type=float, default=0.9,
                        help='momentum (default: 0.9)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--log-interval', type=int, default=100, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--ckpt_path', default='best_mnist.pth', type=str, 
                        help='Checkpoint path')
    args = parser.parse_args()

    use_cuda = torch.cuda.is_available()

    device = torch.device("cuda" if use_cuda else "cpu")

    cudnn.deterministic = True
    cudnn.benchmark = True
    
    train_transform = transforms.Compose([
        transforms.RandomRotation(30),
        transforms.RandomResizedCrop(28, scale=(0.75, 1.0)),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.5,],[0.5,])
        ])

    test_transform = transforms.Compose([
        transforms.Resize(28),
        transforms.ToTensor(),
        transforms.Normalize([0.5,],[0.5])
        ])
        
    trainset = MNIST(root='mnist_png/training',
        transform=train_transform)

    # load the testset
    testset = MNIST(root='mnist_png/testing',
        transform=test_transform)

    train_loader = DataLoader(trainset, batch_size=args.batch_size, shuffle=True, num_workers=1)
    test_loader = DataLoader(testset, batch_size=args.val_batch_size, shuffle=False, num_workers=1)

    model = Net().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    best_acc = -np.inf
    scheduler = StepLR(optimizer, step_size=5, gamma=args.gamma)
    for epoch in range(1, args.epochs + 1):
        train_one_epoch(args, model, device, train_loader, optimizer, epoch)
        val_loss, val_acc = validate(model, device, test_loader)
        scheduler.step()

        if val_acc >= best_acc:
            torch.save(model.state_dict(), args.ckpt_path)
            print('model saved to %s' % args.ckpt_path)

if __name__ == '__main__':
    main()