from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import torch
import pyaudio
from vosk import Model, KaldiRecognizer
from transformers import BertTokenizer, BertForSequenceClassification
import threading
import time

app = Flask(__name__)
CORS(app)

# Path to the extracted Vosk model
model_path = "/vosk/model"

if not os.path.exists(model_path):
    print("Model not found, please ensure the model is extracted to", model_path)
    exit(1)

# Load the Vosk model for speech recognition
vosk_model = Model(model_path)
rec = KaldiRecognizer(vosk_model, 16000)

# Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

def preprocess_text(text):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    return inputs

def predict_phishing(text):
    inputs = preprocess_text(text)
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=1)
    phishing_probability = probabilities[0][1].item() * 100  # Convert to percentage
    return phishing_probability

# Global variables to store the latest recognition results
latest_text = ""
latest_probability = 0
is_detecting = False
high_risk_reached = False

def audio_recognition_thread():
    global latest_text, latest_probability, is_detecting, high_risk_reached
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=16384)
    stream.start_stream()

    while is_detecting and not high_risk_reached:
        data = stream.read(4096, exception_on_overflow=False)
        
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result.get("text", "")
            
            if recognized_text:
                latest_text = recognized_text
                latest_probability = predict_phishing(recognized_text)
                
                if latest_probability >= 80:
                    high_risk_reached = True

        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    stream.stop_stream()
    stream.close()
    p.terminate()

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global is_detecting, high_risk_reached
    if not is_detecting:
        is_detecting = True
        high_risk_reached = False
        threading.Thread(target=audio_recognition_thread).start()
    return jsonify({"status": "started"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global is_detecting
    is_detecting = False
    return jsonify({"status": "stopped"})

@app.route('/get_latest', methods=['GET'])
def get_latest():
    global latest_text, latest_probability, high_risk_reached
    return jsonify({
        "text": latest_text,
        "probability": latest_probability,
        "high_risk_reached": high_risk_reached
    })    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 