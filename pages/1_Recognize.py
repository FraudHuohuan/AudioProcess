import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

#语音识别
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

# 保存音频函数
def save_audio(output_path):
   if st.session_state.audio_data is not None:
       with open(output_path, "wb") as f:
           f.write(st.session_state.audio_data)
       st.success("音频已保存到 {}".format(output_path))
   else:
       st.warning("没有录制的音频可供保存！")


# Streamlit App
st.title("🎙️ Speech Recognition")

# 选择录音方式
choice = st.radio("请选择录音方式", ("录音", "上传音频文件"))

# 如果选择录音
if choice == "录音":
       seconds_to_record = st.slider("录音时长（秒）", min_value=1, max_value=10, value=3)
       record_audio(seconds_to_record)

# 如果选择上传音频文件
elif choice == "上传音频文件":
    upload_audio()

if st.session_state.audio_data is not None:
   save_audio("output.wav")
   st.write("正在识别语音，请稍候...")
   recognition_result = recognize_speech("output.wav")
   st.write("识别结果：", recognition_result["text"])
