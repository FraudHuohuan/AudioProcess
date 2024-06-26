import streamlit as st
import soundfile as sf
import requests
from gradio_client import Client
from audio_recorder_streamlit import audio_recorder
import base64
import numpy as np


def save_audio(audio_bytes, output_path):
    try:
        if audio_bytes is not None:
            st.audio(audio_bytes, format="audio/wav")
            st.session_state.audio_data = audio_bytes
            with open(output_path, "wb") as f:
                f.write(st.session_state.audio_data)
    except Exception as e:
        print(f"Error in save_audio: {e}")

def recognize_speech(audio_file):
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": "Bearer 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"}

    try:
        with open(audio_file, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print(f"Error in recognize_speech: {e}")
        return None

def enhance_audio(audio_file):
    EA_URL = "https://api-inference.huggingface.co/models/speechbrain/sepformer-whamr-enhancement"
    headers = {"Authorization": "Bearer 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"}

    try:
        with open(audio_file, "rb") as f:
            data = f.read()
        response = requests.post(EA_URL, headers=headers, data=data)
        output = response.json()
        if output is not None:
            enhanced_audio_data = base64.b64decode(output[0]["blob"])
            temp_file_path = "enhanced_audio.wav"
            with open(temp_file_path, "wb") as f:
                f.write(enhanced_audio_data)
            return temp_file_path
        else:
            return None
    except Exception as e:
        print(f"Error in enhance_audio: {e}")
        return None

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
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        print(f"Error in send_message: {e}")
        return None

def text_to_speech(text="I don't know", lang="EN", role="科比"):
    try:
        if role == "科比":
            client = Client("https://xzjosh-kobe-bert-vits2-2-3.hf.space/--replicas/9fhp9/")
        elif role == "永雏塔菲":
            client = Client("https://xzjosh-taffy-bert-vits2-2-3.hf.space/--replicas/bbldx/")
        example_audio = "./audio/audio_sample.wav"
        result = client.predict(
            text,
            role,
            0.4,
            0.1,
            0.1,
            2,
            lang,
            example_audio,
            "Angry",
            "Text prompt",
            "",
            0,
            fn_index=0
        )
        audio_path = result[1]
        return audio_path
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None


st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

isAvailable = False

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

with st.sidebar:
    tts_enabled = st.sidebar.checkbox("启用 TTS", value=False)
    language = st.sidebar.selectbox("选择语言", ["EN", "ZH", "JP"]) 
    voice_actor = st.sidebar.selectbox("选择人物", ["科比", "永雏塔菲"])

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
   isAvailable =  True

elif confirmation_button:
   enhancement_result = enhance_audio("output.wav")
   recognition_result = recognize_speech(enhancement_result)
   speech = recognition_result["text"]
   st.session_state.messages.append({"role": "user", "content": speech})
   st.chat_message("user").write(speech)
   msg = send_message(speech)
   st.session_state["messages"].append({"role": "assistant", "content": msg})
   st.chat_message("assistant").write(msg)
   confirmation_button = False
   isAvailable =  True

if isAvailable and tts_enabled:
   audio_result = text_to_speech(msg, language, voice_actor)
   st.session_state["messages"].append({"role": "assistant", "content": audio_result})
   st.audio(st.session_state["messages"][-1]["content"], format="audio/wav")
   isAvailable =  False



    
    

