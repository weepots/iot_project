import torch
import torch.nn as nn
import torchvision
from collections import OrderedDict
from torch.utils.data import DataLoader, Subset
import torch.nn.functional as F
import torchvision.transforms as transforms
import PIL
from tqdm import tqdm
from dataset import CelebA


class gender_classifier:

    def __init__(self):
        self.USE_CUDA = torch.cuda.is_available()
        self.DEVICE = torch.device('cuda' if self.USE_CUDA else 'cpu')
        # model_ = torchvision.models.resnet101(
        #     weights=torchvision.models.ResNet101_Weights.DEFAULT)
        model_ = torchvision.models.resnet101()
        n_inputs = model_.fc.in_features
        classifier = nn.Sequential(OrderedDict([
            ('fc1', nn.Linear(n_inputs, 1))
        ]))
        model_.fc = classifier
        model_.load_state_dict(torch.load(
            'resnet_pretrain.pt', map_location=self.DEVICE), strict=False)
        self.model = model_.to(self.DEVICE)
        self.transforms = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    def train(self, dataloader, model, criterion, optimizer, device):
        model.train()
        total_loss = 0
        for idx, (img, target) in tqdm(enumerate(dataloader), total=len(dataloader)):
            optimizer.zero_grad()
            img, target = img.to(device), target.to(device)
            output = F.sigmoid(model(img))
            loss = criterion(output, target)
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
        return total_loss/len(dataloader)

    def train_model(self, epochs=100, learning_rate=0.001):
        train_data = CelebA()
        prev_len = len(train_data)

        train_data.add_user_dataset()
        print(f"User samples added: {len(train_data)-prev_len}")
        indexes = [x for x in range(200000, len(train_data))]
        print(f"Starting training for {len(indexes)} samples")
        train_data_subset = Subset(train_data, indices=indexes)
        train_loader = DataLoader(
            train_data_subset, batch_size=32, shuffle=True)
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            epoch_loss = self.train(
                train_loader, self.model, criterion, optimizer, self.DEVICE)
            print(f'Epoch {epoch+1}: Loss {epoch_loss}', flush=True)
            torch.save(self.model.state_dict(), 'resnet_pretrain_USER.pt')

    def classify_gender(self, image):
        self.model.eval()
        image = transforms.functional.rotate(img=image, angle=270)
        image = transforms.functional.center_crop(
            img=image, output_size=[448, 448])
        image = transforms.functional.resize(
            img=image, size=[224, 224]
        )
        to_return = image.copy()
        image = self.transforms(image).unsqueeze(0)
        output_ = self.model(image)
        print(output_)
        output = F.sigmoid(output_)
        return output, to_return
