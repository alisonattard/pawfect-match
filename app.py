from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
import torch
import clip  # OpenAI's CLIP library
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, MarianMTModel, MarianTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import login
import numpy as np
import requests

# Initialize Flask app
app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("FIREBASE_KEY")  # Replace with the actual file name if different
firebase_admin.initialize_app(cred)
db = firestore.client()

# CLIP model setup
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)

# Login to HuggingFace
login("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")

# FLAN-T5 model setup
FLAN_MODEL_PATH = "Alexandra26/SE_t5"
flan_tokenizer = AutoTokenizer.from_pretrained(FLAN_MODEL_PATH)
flan_model = AutoModelForSeq2SeqLM.from_pretrained(FLAN_MODEL_PATH).to(device)

# MarianMT model setup
MODEL_2_PATH = "Alexandra26/SE_project"
marian_tokenizer = MarianTokenizer.from_pretrained(MODEL_2_PATH)
marian_model = MarianMTModel.from_pretrained(MODEL_2_PATH)

# Predefined lists of animals and general keywords
animals = ["cat", "dog"]
keywords_list = ["small", "fluffy", "sleek", "spotted", "striped", "soft", "shiny", "bright-eyed", "whiskered", "short-haired", "long-haired"]

# Routes
@app.route('/test_firebase')
def test_firebase():
    try:
        doc_ref = db.collection('testCollection').document('testDoc')
        doc_ref.set({'message': 'Hello, Firebase!'})
        return "Firebase connection successful!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

@app.route('/predict_image_keywords', methods=['POST'])
def predict_image_keywords():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    
    try:
        image = Image.open(image_file.stream)
        image_input = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
        image_features = image_features.cpu().numpy()

        all_keywords = animals + keywords_list
        text_inputs = clip.tokenize(all_keywords).to(device)
        with torch.no_grad():
            text_features = clip_model.encode_text(text_inputs)
        text_features = text_features.cpu().numpy()

        similarities = cosine_similarity(image_features, text_features)
        animal_similarities = similarities[0, :len(animals)]
        keyword_similarities = similarities[0, len(animals):]

        best_animal_index = np.argmax(animal_similarities)
        best_animal = animals[best_animal_index]

        top_keyword_indices = np.argsort(keyword_similarities)[-3:][::-1]
        top_keywords = [keywords_list[i] for i in top_keyword_indices]

        final_keywords = [best_animal] + top_keywords
        description = generate_description(final_keywords)

        result = {"message": "Prediction successful", "description": description}
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_description', methods=['POST'])
def generate_description_route():
    if not request.json or 'prompt' not in request.json:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        prompt = request.json['prompt']
        inputs = flan_tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
        outputs = flan_model.generate(**inputs, max_length=130, num_beams=5, early_stopping=True, 
                                      repetition_penalty=1.8, temperature=1.2, length_penalty=1.2, 
                                      do_sample=True, top_k=30, top_p=0.9)
        description = flan_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return jsonify({"description": description})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400

    try:
        text = request.json['text']
        inputs = marian_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated = marian_model.generate(**inputs)
        translation = marian_tokenizer.decode(translated[0], skip_special_tokens=True)
        return jsonify({"translation": translation})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function
def generate_description(keywords):
    prompt = "Generate an engaging and lively pet adoption description. Highlight the pet's best traits and personality while making it irresistible for adoption. Use the following characteristics: " + " ".join(keywords)
    inputs = flan_tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    outputs = flan_model.generate(**inputs, max_length=130, num_beams=5, early_stopping=True, 
                                  repetition_penalty=1.8, temperature=1.2, length_penalty=1.2, 
                                  do_sample=True, top_k=10, top_p=0.8)
    description = flan_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return description

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)