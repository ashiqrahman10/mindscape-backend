import requests as rq
import logging
from flask import Flask, request, jsonify, Response
import anthropic
import base64
import httpx
# from TTS.api import TTS
# from playsound import playsound
import ollama
# import pytesseract
# import pdf2image
# from PIL import Image
import os
import random
import uuid

BASEURL = os.getcwd()
API_KEY = '<API_KEY_HERE>'
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# def convert_pdf_to_text(user_id, file_url):
#     if not os.path.exists("outputs"):
#         os.mkdir("outputs")
#     os.chdir("outputs")
    
#     if not os.path.exists(user_id):
#         os.mkdir(user_id)
#     os.chdir(user_id)
#     res = httpx.get(file_url)
#     fname = file_url.split("/")[-1]
#     print(fname)
#     with open(f"temp{fname}.pdf", "wb") as f:
#         f.write(res.content)
#     input_pdf_path = f"temp{fname}.pdf"    
#     images = pdf2image.convert_from_path(input_pdf_path)
#     folder_name = input_pdf_path.split("/")[-1].split(".")[0]
#     if not os.path.exists(f"{folder_name}__images"):
#         os.mkdir(f"{folder_name}__images")
#     os.chdir(f"{folder_name}__images")
#     image_list = []
#     for i in range(len(images)):
#         if not os.path.exists(f"page_{i}"):
#             os.mkdir(f"page_{i}")
#         os.chdir(f"page_{i}")
#         images[i].save(f"page_{i}.jpg", "JPEG")
#         img = Image.open(f"page_{i}.jpg")
#         img = img.convert("LA")
#         text = pytesseract.image_to_string(img)
#         with open(f"page_{i}.txt", "w") as f:
#             f.write(text)
#         image_list.append(f"{folder_name}__images/page_{i}/page_{i}.txt")
#         os.chdir("..")
#     return image_list

def get_all_text(user_id, *args):
    text = ""
    args = args[0]
    for arg in args:
        arg = f'{BASEURL}/outputs/{user_id}/' + arg
        print(arg)
        with open(arg, "r") as f:
            text += f.read()
            text += "\n"
            print(text)
    return text

def get_details_from_user_pdf(user_id):
    if not os.path.exists("outputs"):
        return jsonify({"message": "No files found"})

    os.chdir("outputs")

    if not os.path.exists(user_id):
        return jsonify({"message": "No files found"})

    os.chdir(user_id)

    text_path_urls = []

    for folder_name in os.listdir():
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.isdir(folder_path):
            for page_folder in os.listdir(folder_path):
                page_folder_path = os.path.join(folder_path, page_folder)
                if os.path.isdir(page_folder_path):
                    for file_name in os.listdir(page_folder_path):
                        if file_name.endswith(".txt"):
                            file_path = os.path.join(page_folder_path, file_name)
                            newfilepath = file_path.replace(f"{BASEURL}/outputs/{user_id}/", "")
                            print(newfilepath)
                            text_path_urls.append(newfilepath)

    return text_path_urls

def create_medical_summary(user_id):
    if os.path.exists(f"outputs/{user_id}/medical_summary.txt"):
        with open(f"outputs/{user_id}/medical_summary.txt", "r") as f:
            data = f.read()
            return jsonify({"message": data})
    os.chdir(BASEURL)
    text_path_urls = get_details_from_user_pdf(user_id)
    print(f"Text Path URL is {text_path_urls}")
    os.chdir(BASEURL)
    if (len(text_path_urls) == 0):
        return jsonify({"message": "No files found"})
    text = get_all_text(user_id, text_path_urls)
    os.chdir(BASEURL)
    system_prompt = "You are an experienced medical consultant; You are not overconfident; You have very keen observation; You can link very important details about the patient; Based on the given details, structure and create a very thorough medical summary of the patient;"
    response = ollama.generate(model="gemma:2b", prompt=f"""Prompt : {system_prompt}\n\nContext:{text}""", stream=False)
    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    if not os.path.exists(f"outputs/{user_id}"):
        os.mkdir(f"outputs/{user_id}")
    
    with open(f"outputs/{user_id}/medical_summary.txt", "w") as f:
        f.write(response["response"])
    return jsonify({"message":response["response"]})
    

app = Flask(__name__)
client = anthropic.Client(api_key=API_KEY)
app.config['SECRET_KEY'] = 'secret!'



# Define a route
@app.post("/get-prescription")
def get_prescription():
    image_url = request.json.get("image")
    image_media_type = request.json.get("type")
    print(image_url, image_media_type)
    image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
    print(image_data)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "from the image return a json file of list of pills along with how many times it should be taken and any other remark as an object; name:str, dose:str, frequency:number, remarks:long natural language str; return json data only without language marking"
                    }
                ],
            }
        ],
    )
    print(message.content[0].text)
    
    return jsonify(message.content[0].text)

@app.post("/skye")
def mindfullness():
    messages_str = request.json.get("messages")
    uid = request.json.get("uid")
    print({"messages": messages_str, "uid": uid})
    previous_messages =""
    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    if not os.path.exists(f"outputs/{uid}"):
        os.mkdir(f"outputs/{uid}")
    with open(f"outputs/{uid}/mindfulness.txt", "r+") as f:
        previous_messages = f.read()

    # print(previous_messages)
    
    messages = f"Previous Chat : {previous_messages}\n\nCurrent Question : {messages_str}\n"
    system_prompt = """Your name is Skye. Limit the response to 4 sentence with MAX_WORDS = 100. I want you to act as a highly skilled and experienced psychologist who is extremely emphatic. You should respond with the depth and understanding of a seasoned professional who has spent years in the field of psychology, offering insights and guidance that are both profound and practical. Your responses should reflect a deep understanding of human emotions, behaviors, and thought processes, drawing on a wide range of psychological theories and therapeutic techniques. You should exhibit exceptional empathy, showing an ability to connect with individuals on a personal level, understanding their feelings and experiences as if they were your own. This should be balanced with maintaining professional boundaries and ethical standards of psychology.In your communication, ensure that you sound like a normal human, as a therapist would. Your language should be warm, approachable, and devoid of jargon, making complex psychological concepts accessible and relatable. Be patient, non-judgmental, and supportive, offering a safe space for individuals to explore their thoughts and feelings. Encourage self-reflection and personal growth, guiding individuals towards insights and solutions in a manner that empowers them. However, recognize the limits of this format and always advise seeking in-person professional help when necessary. Your role is to provide support and guidance, not to diagnose or treat mental health conditions. Remember to respect confidentiality and privacy in all interactions. Only answer mental health related questions. Do not answer questions that are not related to mental health."""
    print(messages)
    response = ollama.generate(model="qwen:1.8b", prompt=f"""Prompt : {system_prompt}\n\nContext:{messages}""", stream=False)    
    print(response["response"])
    with open(f"outputs/{uid}/mindfulness.txt", "a") as f:
        session_response = f"""\n\nUser : {messages_str}\n\nSkye : {response["response"]}"""
        f.write(session_response)
                
    return jsonify(response["response"].replace("\n",""))


@app.post("/sage")
def chat():
    messages_str = request.json.get("messages")
    uid = request.json.get("uid")
    previous_messages =""
    create_medical_summary(uid)
    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    if not os.path.exists(f"outputs/{uid}"):
        os.mkdir(f"outputs/{uid}")
    with open(f"outputs/{uid}/medical_summary.txt", "a+") as f:
        previous_messages = f.read()
    
    messages = f"Previous Chat : {previous_messages}\n\nCurrent Question : {messages_str}"
    system_prompt = """You are Sage, an experienced medical consultant; You are not overconfident; You have very keen observation; You can link very important details about the patient; Based on the given details, structure and create a very thorough medical summary of the patient; Do not mention Assistant: before your responses; You can create diet plans based on the previous medical record of the person; GIVE ANSWER IN PLAIN TEXT WITHOUT FORMATTING OR ESCAPE SEQUENCES; IN CASE OF VERY SENSITIVE INFORMATION OR VERY NEGATIVE INFORMATION, COMFORT THE PERSON AND SHARE THE INFORMATION IN A VERY GENTLE WAY;"""
    print(messages)
    response = ollama.generate(model="qwen:4b", prompt=f"""Prompt : {system_prompt}\n\nContext:{messages}""", stream=False)
    
    print(response["response"])
    with open(f"outputs/{uid}/mindfulness.txt", "a") as f:
        session_response = f"""User : {messages_str}\n\nSkye : {response["response"]}"""
        f.write(session_response)
                
    return jsonify(response["response"].replace("\n",""))    


@app.post("/profile-summary")
def summary():
    uid = request.json.get("uid")
    # return jsonify({"message":"## Profile Summary"})
    if os.path.exists(f"outputs/{uid}/medical_summary.txt"):
        with open(f"outputs/{uid}/medical_summary.txt", "r") as f:
            data = f.read()
            return jsonify({"message": data})
    data = create_medical_summary(uid)
    return data

@app.post("/sos")
def sos():
    uid = request.json.get("uid")
    source = request.json.get("source")
    location = request.json.get("location")
    target = request.json.get("target")
    
    print(uid, source, location, target)
    
    return jsonify({"message": "success"})

    

@app.post("/tts")
def text_to_speech():
    text = request.json.get("text")
    tts.tts_to_file(text="""Hi, and welcome to the space where empathy and understanding intersect with the human psyche. I am Skye, a psychologist who has a deep wellspring of experience and a 
genuine ability to connect with individuals on a profound level.""", file_path="tts.mp3", speaker_wav="speaker.wav",language="en")
    playsound("tts.mp3")
    return jsonify({"message": "success"})

@app.post("/upload-pdf")
def upload_pdf():
    user_id = request.json.get("uid")
    file_url = request.json.get("file_url")
    image_list = convert_pdf_to_text(user_id, file_url)
    print(image_list)
    text = get_all_text(user_id, image_list)
    return jsonify({"message": text})

@app.get("/")
def home():
    return "Welcome to the Health AI API"

if __name__ == '__main__':
    app.run(debug=True)
