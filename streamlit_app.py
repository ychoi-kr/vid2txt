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
    return transcript

def summarize_transcript(transcript, max_tokens=150):
    response = client.completions.create(
        model="gpt-4-turbo-preview",
        prompt=f"요약: {transcript}",
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()

# Streamlit UI 구성
st.title("Video Subtitles and Summary Generator")

url = st.text_input("Enter Video URL:")
prompt = st.text_area("What's the video about? (Optional)", value="", help="Provide a brief description of the video or include specific terms like unique names and key topics to enhance accuracy. This can include spelling out hard-to-distinguish proper nouns.")
response_format = st.selectbox("Select Output Format:", ('text', 'srt', 'vtt'))

if st.button("Generate Subtitles"):
    if url:
        video_path = download_video(url)
        transcript = transcribe(video_path, response_format=response_format, prompt=prompt)
        st.text_area("Subtitles:", value=transcript, height=300)
        
        # 다운로드한 파일 삭제
        os.remove(video_path)
    else:
        st.error("Please enter a URL.")

