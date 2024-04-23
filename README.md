# Gender Classification Mobile Application

## Installation

```
git clone <repo>

# Frontend setup
cd iot-frontend
npm install

# Backend setup

cd flask-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Put the CelebA dataset here.
mkdir datasets/
```

## Training the ResNet 101 Model

The model is a ResNet101 model that has a total of 101 layers. I attached the output to the Fully Connected layer with a Sigmoid function to determine if the person is female or male.
You can get the CelebA dataset from this [link](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)

The `resnet_pretrained.pt` file is with me, you can train your own by using the `initial_train.ipynb` file. I recommend training using `initial_train.ipynb` file instead of the UI as there are more controllable parameters. This model is quite large so training will require a decent GPU (min 6GB VRAM). I trained the weights using the SCSEGPU-TC Cluster which have Tesla V100, not sure how it will perform on other GPUs for training. Inference can be done on laptop.

## Usage:

### Frontend

Install expoGO on your smartphone
Change backend_server in the App.js file to your LOCAL IP address.

```
cd iot-frontend
npm start
```

Scan the QR Code that appears and the application will load on your phone.  
Please remember to allow permissions to access the camera

### Backend

```
cd flask-backend
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

You can also run the application without GUNICORN by running python server.py
