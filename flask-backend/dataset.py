
import os
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from PIL import Image
import pandas as pd
from ast import literal_eval


class CelebA(Dataset):
    def __init__(self, root="./datasets/CelebA"):
        self.root = root
        self.annotation = os.path.join(root, "Anno", "list_attr_celeba.txt")
        self.images = os.path.join(root, "Img", "img_align_celeba")

        self.data, self.attr_map = self.read_attr_file(self.annotation)

        self.transforms = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    def read_attr_file(self, attr_file):
        attr = []
        data = []
        with open(attr_file, "r") as f:
            line_count = 0
            for line in f:
                line_count += 1
                if line_count == 1:
                    continue
                if line_count == 2:
                    attr = line.split()
                    continue
                line_split = line.split()
                img_name = os.path.join(self.images, line_split[0])
                img_attr = tuple([max(int(x), 0) for x in line_split[1:]])
                data.append((img_name, img_attr))
        return data, attr

    def __len__(self):
        return len(self.data)

    def idx_to_attr(self, idx):
        return self.attr_map[idx]

    def add_user_dataset(self):
        user_dataset_location = "user_dataset"
        user_dataset_csv = os.path.join(
            user_dataset_location, "user_dataset_data.csv")
        df = pd.read_csv(user_dataset_csv)
        for row in range(len(df)):
            img_name = df.iloc[row]['image_name']
            if img_name == "user_image_00.jpg":
                continue
            img_attr = literal_eval(df.iloc[row]['new_image_attr'])
            self.data.append((img_name, img_attr))

    def __getitem__(self, idx):
        img, attr = self.data[idx]
        img = Image.open(img)
        img = self.transforms(img)
        return img, torch.Tensor([attr[20]])
