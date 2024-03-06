import streamlit as st
from pytube import YouTube
from openai import OpenAI
import os

# API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def download_video(url):
    video = YouTube(url).streams.filter(only_audio=True).first().download()
    return video

def transcribe(audio_filepath, response_format='text', prompt=None):
    with open(audio_filepath, "rb") as file:
        transcript = client.audio.transcriptions.create(
            file=file,
            model="whisper-1",
            response_format=response_format,
            prompt=prompt,
        )
    st.session_state.transcript = transcript

def summarize_transcript(transcript):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "Summarizes text."},
            {"role": "user", "content": transcript},
        ],
    )
    return response.choices[0].message.content

# Streamlit UI 구성
st.title("Video Subtitles and Summary Generator")

url = st.text_input("Enter Video URL:")
prompt = st.text_area("What's the video about? (Optional)", value="", help="Provide a brief description of the video or include specific terms like unique names and key topics to enhance accuracy. This can include spelling out hard-to-distinguish proper nouns.")
response_format = st.selectbox("Select Output Format:", ('text', 'srt', 'vtt'))

# 세션 상태 초기화
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""

if st.button("Generate Subtitles"):
    if url:
        video_path = download_video(url)
        transcribe(video_path, response_format=response_format, prompt=prompt)
        os.remove(video_path)  # 다운로드한 파일 삭제
    else:
        st.error("Please enter a URL.")

# 자막이 있을 경우, 자막 필드를 항상 표시
if st.session_state.transcript:
    st.text_area("Subtitles:", value=st.session_state.transcript, height=300)

# "Summarize" 버튼 로직
if st.button("Summarize"):
    if st.session_state.transcript:
        st.session_state.summary = summarize_transcript(st.session_state.transcript)

# 요약문이 있을 경우, 요약문 필드를 표시
if st.session_state.summary:
    st.text_area("Summary:", value=st.session_state.summary, height=150)

