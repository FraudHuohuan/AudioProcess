import streamlit as st
import requests
from gradio_client import Client
import numpy as np
import soundfile as sf
from audio_recorder_streamlit import audio_recorder
import base64

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None


# 录音函数
def record_audio(seconds):
    st.write("请点击下面的按钮开始录音：")
    audio_bytes = audio_recorder(energy_threshold=(-1.0, 1.0), pause_threshold=seconds, sample_rate=41_000)
    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")
        st.session_state.audio_data = audio_bytes

def upload_audio():
   st.write("请上传您的音频文件：")
   uploaded_file = st.file_uploader("选择音频文件", type=["wav"])
   if uploaded_file is not None:
        audio_bytes = uploaded_file.read()        
        st.audio(audio_bytes, format="audio/wav")        
        st.session_state.audio_data = audio_bytes

def save_audio(output_path):
   if st.session_state.audio_data is not None:
       with open(output_path, "wb") as f:
           f.write(st.session_state.audio_data)
       st.success("音频已保存到 {}".format(output_path))
   else:
       st.warning("没有录制的音频可供保存！")


def clone(text="Hello", style = "default", audio = None):
    try:
        client = Client("https://myshell-ai-openvoice.hf.space/--replicas/88xs1/")
        result = client.predict(
		text,	# str  in 'Text Prompt' Textbox component
		style,  #default, sad, whispering, cheerful, terrified, angry,friendly 
		audio,  # str (filepath on your audio file)
		True,	# bool  in 'Agree' Checkbox component
		fn_index=1
        )
        print(result)
        audio_path = result[1]
        return audio_path
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None



# Streamlit App
st.title("🎤 Speech Cloning")

text_input = st.text_input("请输入要转换成语音的文本")
submit_button = st.button("确认提交")

# 选择录音方式
choice = st.radio("请选择录音方式", ("录音", "上传音频文件"))

# 如果选择录音
if choice == "录音":
       seconds_to_record = st.slider("录音时长（秒）", min_value=1, max_value=30, value=15)
       record_audio(seconds_to_record)

# 如果选择上传音频文件
elif choice == "上传音频文件":
    upload_audio()

if submit_button and st.session_state.audio_data is not None:
   save_audio("output.wav")
   st.write("正在进行语音克隆，请稍候...")
   print(text_input+"\n")
   clone_result = clone(text_input+"\n", "default", "output.wav")
   st.audio(clone_result, format='audio/wav')
   submit_button = False


    