from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np
import os

app = Flask(__name__)

model_name = os.getenv('MODEL_NAME')
model_folder = "models"
model_local_path = f'{model_folder}/{model_name}'
try:
    model = SentenceTransformer(model_local_path)
except:
    model = SentenceTransformer(model_name)
    model.save(model_local_path)
@app.route("/encode", methods=["POST"])
def encode():
    data = request.json
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        # Encode the text
        embedding = model.encode(text, normalize_embeddings=True)
        return [float(item) for item in embedding]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
