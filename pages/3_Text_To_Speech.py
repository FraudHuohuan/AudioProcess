import streamlit as st
import requests
from gradio_client import Client
from audio_recorder_streamlit import audio_recorder
import base64

# TTS
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

# Streamlit App
st.title("📜 Text to Speech")

text_input = st.text_input("请输入要转换成语音的文本")
# 确认按钮
submit_button = st.button("确认提交")
    
if submit_button and text_input:
   st.write("正在生成语音，请稍候...")
   # 调用text_to_speech函数生成语音
   audio_path = text_to_speech(text_input)
   # 播放生成的语音
   st.audio(audio_path, format='audio/wav')
