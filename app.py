import os
from PIL import Image
import requests as rq
from io import BytesIO
import google.generativeai as genai
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS 
from pathlib import Path

load_dotenv()
GOOGLE_API_KEY = "AIzaSyC9M85CX3GiZnnBey3ozlNux4GQElknFgI" 
# print(GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS

print("\n\nServer started")

@app.post("/get-prescription")
def get_prescription():
    model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest")
    # Validate that an image is present
    if not (img := Path("image.jpg")).exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
    {
        "mime_type": "image/jpg",
        "data": Path("image.jpg").read_bytes()
    },
    ]

    prompt_parts = [
    "YOU CAN REPLY IN A DETAILED RESPONSE ONLY. DO NOT INCLUDE MARKDOWN OR ANYTHING IN THE RESPONSE. INCLUDE ONLY PLAIN TEXT IN THE RESPONSE. SEND ME A SHORT EXPLANATION OF THE LECTURE NOTE OF THE IMAGE I SEND YOU.\n\n",
    image_parts[0],
    "\n",
    ]

    response = model.generate_content(prompt_parts)
    print(response.text)




# model2 = genai.GenerativeModel('gemini-pro')
# @app.post("/chat")
# def chat():
#     print(request.json)
#     chat_message = request.json.get("message")
#     print(chat_message)
#     response = model2.generate_content("You are Bloom, a medical assistance chatbot that can give answer to any medical relaed question and not any other type of question;\n"+chat_message, stream=False)
#     return response.text

# def convert_audio_to_text():
#     # Check if the POST request contains a file with key 'audio'
#     if 'audio' not in request.files:
#         return jsonify({'error': 'No audio file provided'}), 400

#     audio_file = request.files['audio']

#     # Check if the file has a valid extension (e.g., WAV or MP3)
#     if audio_file and audio_file.filename.lower().endswith(('.wav', '.mp3')):
#         recognizer = sr.Recognizer()

#         # Read the audio file using SpeechRecognition
#         with sr.AudioFile(audio_file) as source:
#             audio_data = recognizer.record(source)

#         # Perform speech-to-text conversion
#         text_result = recognizer.recognize_google(audio_data)

#         return jsonify({'result': text_result})

#     else:
#         return jsonify({'error': 'Invalid audio file format'}), 400


if __name__ == '__main__':
    app.run(debug=True)