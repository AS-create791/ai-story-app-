import os
import time
import asyncio
import subprocess
import numpy as np
from PIL import Image
import streamlit as st
from moviepy.video.io.ImageClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

# Page Configuration
st.set_page_config(page_title="Cinematic Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Cinematic Story Video Creator")
st.write("আপনার পছন্দের গল্প বা স্ক্রিপ্ট লিখুন এবং খুব সহজেই সিনেমাটিক ভিডিও তৈরি করে ফেলুন!")

# Input fields
story_script = st.text_area("আপনার গল্পের স্ক্রিপ্ট বা টেক্সট এখানে লিখুন:", height=150, placeholder="Once upon a time...")

# Voice selection for edge-tts
voice_option = st.selectbox(
    "ভয়েস সিলেক্ট করুন (Voice):",
    ("en-US-AriaNeural", "en-US-GuyNeural", "bn-BD-PrabhatNeural", "bn-BD-NabanitaNeural")
)

# Generate Video Button
if st.button("🎥 ভিডিও তৈরি করুন (Generate Video)"):
    if not story_script.strip():
        st.warning("দয়া করে কিছু টেক্সট বা স্ক্রিপ্ট লিখুন।")
    else:
        with st.status("ভিডিও তৈরি করা হচ্ছে, দয়া করে অপেক্ষা করুন...", expanded=True) as status:
            try:
                # Step 1: Text to Speech using edge-tts
                st.write("🎙️ ভয়েস ওভার (Audio) তৈরি করা হচ্ছে...")
                audio_file = "story_audio.mp3"
                
                # Run edge-tts command
                tts_command = f'edge-tts --voice "{voice_option}" --text "{story_script}" --write-media "{audio_file}"'
                subprocess.run(tts_command, shell=True, check=True)
                
                # Step 2: Create a placeholder background image using Pillow
                st.write("🖼️ ব্যাকগ্রাউন্ড ইমেজ তৈরি করা হচ্ছে...")
                img_path = "background.png"
                img = Image.new('RGB', (1280, 720), color = (20, 20, 40))
                img.save(img_path)
                
                # Step 3: Create Video using MoviePy (Fixed imports)
                st.write("🎞️ ভিডিও রেন্ডারিং করা হচ্ছে...")
                audio_clip = AudioFileClip(audio_file)
                duration = audio_clip.duration
                
                # Create Image clip with same duration as audio
                image_clip = ImageClip(img_path).set_duration(duration)
                image_clip = image_clip.set_audio(audio_clip)
                
                # Output video file
                output_video = "cinematic_output.mp4"
                image_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
                
                status.update(label="✅ ভিডিও তৈরি সফল হয়েছে!", state="complete", expanded=False)
                
                # Show success and video player
                st.success("আপনার সিনেমাটিক ভিডিও প্রস্তুত!")
                st.video(output_video)
                
            except Exception as e:
                status.update(label="❌ ত্রুটি দেখা দিয়েছে!", state="error", expanded=True)
                st.error(f"একটি সমস্যা হয়েছে: {e}")
                
