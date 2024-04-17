import streamlit as st
import soundfile as sf
import requests
from gradio_client import Client
from audio_recorder_streamlit import audio_recorder
import base64
import numpy as np


def save_audio( audio_bytes,  output_path ):
   if audio_bytes is not None:
       st.audio(audio_bytes, format="audio/wav")
       st.session_state.audio_data = audio_bytes
       with open(output_path, "wb") as f:
           f.write(st.session_state.audio_data)

def recognize_speech(audio_file):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": "Bearer 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"}

    def recognize(filename):
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()
    output = recognize(audio_file)
    return output

def enhance_audio(audio_file):
    EA_URL = "https://api-inference.huggingface.co/models/speechbrain/sepformer-whamr-enhancement"
    headers = {"Authorization": "Bearer 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"}

    def enhance(filename):
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(EA_URL, headers=headers, data=data)
        return response.json()

    output = enhance(audio_file)
    if output is not None:
        enhanced_audio_data = base64.b64decode(output[0]["blob"])
        temp_file_path = "enhanced_audio.wav"
        with open(temp_file_path, "wb") as f:
            f.write(enhanced_audio_data)
        return temp_file_path
        #utf8_encoded_data = base64.b64encode(enhanced_audio_data).decode('utf-8')
    else:
        return None;

def send_message(data):
    url = "https://cn2us02.opapi.win/v1/chat/completions"
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Authorization": "sk-NLbBJJB6ac9E536E4B0ET3BlBKFJ8896848b116047d1aEd2"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": data}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    return content

def text_to_speech(text, lang='en'):
    client = Client("https://xzjosh-kobe-bert-vits2-2-3.hf.space/--replicas/9fhp9/")
    example_audio = "./audio/audio_sample.wav"
    result = client.predict(
        text, 
        "科比", 
        0.4, 
        0.1,
        0.1,
        2, 
        "EN",
        example_audio, 
        "Angry", 
        "Text prompt",
        "", 
        0, 
        fn_index=0
    )
    audio_path = result[1]
    return audio_path


st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

with st.sidebar:
    tts_enabled = st.sidebar.checkbox("启用 TTS", value=False)

with st.sidebar:
    st.sidebar.title("录音功能")
    audio_bytes = audio_recorder()
    save_audio(audio_bytes, "output.wav" )
    confirmation_button = st.sidebar.button("提交")

if prompt := st.chat_input():
   st.session_state.messages.append({"role": "user", "content": prompt})
   st.chat_message("user").write(prompt)
   msg = send_message(prompt)
   st.session_state.messages.append({"role": "assistant", "content": msg})
   st.chat_message("assistant").write(msg)

elif confirmation_button:
   enhancement_result = enhance_audio("output.wav")
   recognition_result = recognize_speech(enhancement_result)
   if(recognition_result["text"] is not None):
       speech = recognition_result["text"]
   st.session_state.messages.append({"role": "user", "content": speech})
   st.chat_message("user").write(speech)
   msg = send_message(speech)
   st.session_state["messages"].append({"role": "assistant", "content": msg})
   st.chat_message("assistant").write(msg)
   confirmation_button = False

if msg is not None and tts_enabled:
   audio_result = text_to_speech(msg)
   st.session_state["messages"].append({"role": "assistant", "content": audio_result})
   st.audio(st.session_state["messages"][-1]["content"], format="audio/wav")
   msg = None



    
    

