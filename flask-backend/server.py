from flask import Flask, request, jsonify
import base64
import PIL.Image
from flask_cors import CORS
import io
import time
import json
from gender_classification import gender_classifier
import os
import pandas as pd
import asyncio

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Hello world!"


@app.route("/classify", methods=["POST"])
def classify():
    classifier_instance = gender_classifier()
    # classifier_instance.train_model()
    requestJson = request.json
    arr = requestJson.get("image").split(",")
    base64Image = arr[1]
    image = PIL.Image.open(io.BytesIO(
        base64.b64decode(base64Image))).convert("RGB")

    output, image = classifier_instance.classify_gender(image)
    if output >= 0.5:
        gender = "Male"
    else:
        gender = "Female"
    print(gender)
    image.save("output_cropped.jpg")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    response = {
        "image": img_str,
        "gender": gender
    }
    response_json = json.dumps(response)
    return response_json


@app.route("/add_user_image", methods=["GET"])
def add_user_data():
    image = PIL.Image.open("output_cropped.jpg")
    user_dataset_location = "user_dataset"
    user_dataset_csv = os.path.join(
        user_dataset_location, "user_dataset_data.csv")
    template = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1]
    gender = request.args.get('gender')
    if gender == "male":
        attr_ = 1
    else:
        attr_ = 0
    template[20] = attr_
    new_image_attr = tuple(template)
    df = pd.read_csv(user_dataset_csv, index_col=False)
    last_image_name = df.loc[len(df)-1]['image_name'].split("_")
    image_number = int(last_image_name[-1].split(".")[0])

    new_image_name = f"user_image_{image_number+1}.jpg"
    new_image_path = os.path.join(user_dataset_location, new_image_name)

    image.save(new_image_path)

    df.loc[len(df)] = [new_image_path, new_image_attr]
    df.to_csv("./user_dataset/user_dataset_data.csv", index=False)

    response = {"message": "Successfully added."}
    return json.dumps(response)


@app.route("/train_new_model", methods=["GET"])
def train_new_model():
    classifier_instance = gender_classifier()
    asyncio.create_task(classifier_instance.train_model())
    print("ITS RUNNING ASYNC")
    response = {"message": "Successfully started."}
    return jsonify(response), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
