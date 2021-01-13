import os
import flask
from flask import render_template, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from PIL import Image
import torch
from digits_recognition.test import test
from digits_recognition.model import Net

# comment out this section
# path = os.path.abspath('./back_end/cccs-73770-firebase-adminsdk-843vx-620d8dbb71.json')
# cred = credentials.Certificate(path)
# firebase_admin.initialize_app(cred)
# firestore_db = firestore.client()

template_dir = os.path.abspath('./front_end/')
static_dir = os.path.abspath('./front_end/')
app = flask.Flask(__name__, template_folder=template_dir, static_folder=static_dir)

CORS(app)

model_path = os.path.abspath('./digits_recognition/best_mnist.pth')

use_cuda = torch.cuda.is_available()

device = torch.device("cuda" if use_cuda else "cpu")

model = Net().to(device)

state = torch.load(model_path)
model.load_state_dict(state)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    req = request.json
    # make some prediction
    # transmitted format is in H, W, C
    # RGBA
    features = np.uint8(req['features']).reshape((224, 224, -1))
    pred = test(model, device, features)
    response = {
        'prediction': pred.squeeze().cpu().numpy().tolist()
    }
    return jsonify(response)

@app.route('/supervise', methods=['POST'])
def supvervise():
    req = request.json
    features = np.uint8(req['features']).reshape((224, 224, -1))
    img = np.asarray(Image.fromarray(features).resize((28, 28), resample=Image.BILINEAR))
    sample = {
        u'features': img.reshape(-1).tolist(),
        u'label': req['gt'],
        u'timestamp': firestore.SERVER_TIMESTAMP
    }
    firestore_db.collection(u'mnist').add(sample)
    return {'message': 'model saved'}