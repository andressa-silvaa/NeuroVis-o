# engine.py
import time
import torch
import numpy as np


def train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq):
    model.train()
    for images, targets in data_loader:
        images = list(image.to(device) for image in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

        if print_freq > 0 and (i + 1) % print_freq == 0:
            print(f'Epoch: [{epoch}] Loss: {losses.item()}')


def evaluate(model, data_loader, device):
    model.eval()
    cpu_device = torch.device("cpu")
    detections = []
    for images, targets in data_loader:
        images = list(image.to(device) for image in images)
        with torch.no_grad():
            prediction = model(images)
        detections.extend(prediction)
    return detections
