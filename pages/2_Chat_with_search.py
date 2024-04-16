import streamlit as st
import requests
from gradio_client import Client
import numpy as np
import soundfile as sf
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings, WebRtcMode
from pydub import AudioSegment
import base64

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

# 录音并返回音频数据
def record_audio(seconds_to_record):
    # 使用容器创建录音部分
    with st.container():
        # 创建 WebRTC 流以录制音频
        webrtc_ctx = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"audio": True, "video": False},
        )

        # 开始旋转加载动画
        spinner_text = st.empty()
        spinner = st.spinner(text="recording...")

        # 等待开始录音
        while not st.session_state.get('recording_started'):
            pass

        # 检查是否有音频接收器
        if webrtc_ctx.audio_receiver:
            print("receiver")
            try:
                recording_time = 0
                # 开始计时录音时间
                while recording_time < seconds_to_record:
                    print(recording_time)
                    # 获取音频帧
                    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=3)
                    if not audio_frames:
                        st.write("no audio received...")
                        break
                    sound_chunk = AudioSegment.empty()
                    try:
                        # 遍历音频帧并添加到音频块中
                        for audio_frame in audio_frames:
                            sound = AudioSegment(
                                data=audio_frame.to_ndarray().tobytes(),
                                sample_width=audio_frame.format.bytes,
                                frame_rate=audio_frame.sample_rate,
                                channels=len(audio_frame.layout.channels),
                            )
                            sound_chunk += sound
                        # 如果音频块不为空，则将其保存到会话状态的音频数据中
                        if len(sound_chunk) > 0:
                            st.session_state.audio_data = sound_chunk
                            recording_time += len(sound_chunk) / sound_chunk.frame_rate
                            spinner.text("recording... ({}s)".format(round(recording_time, 2)))
                    except Exception as e:
                        st.write("Error:", e)
                        break
            except Exception as e:
                st.write("Error:", e)
        else:
            st.write("no audio receiver...")


       

# 保存音频数据到文件
def save_audio(filename="output.wav"):
    # 检查会话状态中是否存在音频数据
    sample = st.session_state.audio_data
    # 检查音频数据是否为空
    audio_available = sample is not None

    # 如果音频可用，则保存音频到文件
    if audio_available:
        if st.button("保存音频"):
            sample.export(filename, format="wav")

def display_audio():
    # 检查会话状态中是否存在音频数据
    sample = st.session_state.audio_data
    # 检查音频数据是否为空
    audio_available = sample is not None

    # 如果音频可用，则显示音频播放器
    if audio_available:
        st.audio(
            sample.export(format="wav", codec="pcm_s16le", bitrate="128k").read()
        )


# 音频上传函数
def upload_audio():
    # 显示上传文件的区域
    uploaded_file = st.file_uploader("上传音频文件（覆盖旧的录音）", type=["wav", "mp3"])

    # 如果用户上传了文件
    if uploaded_file is not None:
        
        # 读取上传的文件内容
        audio_data = uploaded_file.read()
        # 将文件内容转换为音频对象
        sample = AudioSegment.from_file(uploaded_file)
        # 将音频对象保存到会话状态中
        st.session_state.audio_data = sample




# Streamlit App
st.title("🎙️ Voice Assistant")

# 选择录音方式
choice = st.radio("请选择录音方式", ("录音", "上传音频文件"))

# 如果选择录音
if choice == "录音":
       seconds_to_record = st.slider("录音时长（秒）", min_value=1, max_value=10, value=3)
       record_audio(seconds_to_record)

# 如果选择上传音频文件
elif choice == "上传音频文件":
    upload_audio()

# 如果音频数据不为空，则显示保存音频按钮和音频播放器
if st.session_state.audio_data is not None:
    print("!")
    save_audio( "output.wav")
    st.audio("output.wav", format="audio/wav")

    