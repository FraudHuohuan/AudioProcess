import streamlit as st
import requests
import numpy as np
import soundfile as sf
import os

proxy_address = "127.0.0.1:7890"
os.environ["http_proxy"] = proxy_address
os.environ["https_proxy"] = proxy_address

# 全局变量存储语音数据
audio_data = None

# 语音识别
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

# 录音函数
def record_audio(sample_rate=16000):
    st.write("请开始说话，录音将持续直到您点击停止...")
    audio_data = sf.audio_recorder(sampling_rate=sample_rate, duration=record_seconds, codec='wav')
    st.write("录音进行中...")
    return audio_data

# 保存录音数据到WAV文件
def save_audio(filename):
    global audio_data
    # 保存录音数据到WAV文件
    sf.write(filename, audio_data, 44100, subtype='PCM_16')

# 显示录音数据
def display_audio(filename):
    audio_data_saved = np.array(sf.read(filename)[0])
    st.audio(audio_data_saved, format='audio/wav', sample_rate=44100)

# 音频上传函数
def upload_audio():
    global audio_data

    uploaded_file = st.file_uploader("上传音频文件（覆盖旧的录音）", type=["wav", "mp3"])
    if uploaded_file is not None:
        # 保存上传的音频文件
        with open("uploaded_audio.wav", "wb") as f:
            f.write(uploaded_file.getvalue())

        # 读取上传的音频文件并保存到audio_data
        audio_data, _ = sf.read("uploaded_audio.wav")

# Streamlit App
st.title("🎙️ Speech Recognition")


# 选择录音或上传音频文件
choice = st.radio("请选择录音方式", ("录音", "上传音频文件"))
# 如果选择录音
if choice == "录音":
   seconds_to_record = st.slider("录音时长（秒）", min_value=1, max_value=10, value=3)
   if st.button("开始录音"):
       # 执行录音操作
       record_audio(seconds_to_record)       
# 如果选择上传音频文件
elif choice == "上传音频文件":
   upload_audio()

if audio_data is not None:
  save_audio("output.wav")
  display_audio("output.wav")
  st.write("正在识别语音，请稍候...")
  recognition_result = recognize_speech("output.wav")
  st.write("识别结果：", recognition_result["text"])
