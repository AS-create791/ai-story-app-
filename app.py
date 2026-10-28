import streamlit as st
import io
import time
import subprocess
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import numpy as np
import os

st.set_page_config(page_title="Cinematic Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Cinematic Story Video Creator")
st.write("নিজের ছবি এবং গল্প আপলোড করে পছন্দের ভাষায় ভয়েস নিন এবং সিনেমাটিক জুম ইফেক্টযুক্ত ভিডিও তৈরি করুন!")

voice_lang_option = st.selectbox(
    "১. ভয়েস বা কথনের ভাষা নির্বাচন করুন:",
    ["বাংলা (Bengali)", "হিন্দি (Hindi)", "ইংরেজি (English)"]
)

voice_mapping = {
    "বাংলা (Bengali)": "bn-BD-NabanitaNeural",
    "হিন্দি (Hindi)": "hi-IN-SwaraNeural",
    "ইংরেজি (English)": "en-US-AriaNeural"
}
selected_voice = voice_mapping[voice_lang_option]

st.subheader("২. দৃশ্যসমূহ লিখুন:")
story_input_multi = st.text_area(
    "গল্প বা ডায়লগ (প্রতি লাইনে ১টি লিখুন):",
    "বাইরে তখন গুঁড়ি গুঁড়ি বৃষ্টি পড়ছিল, পুরো শহর জুড়ে আলো-আঁধারির খেলা.\n"
    "অনিন্দ্য জানালার পাশে দাঁড়িয়ে কফি খাচ্ছিল এবং দূর আকাশের দিকে তাকিয়ে ছিল.\n"
    "হঠাৎ দরজায় বেল বাজার শব্দে অনিন্দ্য চকিত হয়ে দরজার দিকে এগিয়ে গেল.",
    height=200
)

st.subheader("৩. ছবিগুলো আপলোড করুন (সিরিয়াল অনুযায়ী):")
uploaded_files = st.file_uploader("ছবি নির্বাচন করুন (PNG বা JPG):", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

def cinematic_zoom(get_frame, t):
    img = Image.fromarray(get_frame(t))
    w, h = img.size
    zoom_factor = 1.0 + (0.15 * (t / 5.0)) 
    new_w = int(w * zoom_factor)
    new_h = int(h * zoom_factor)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    right = left + w
    bottom = top + h
    img_cropped = img_resized.resize((w, h), box=(left, top, right, bottom))
    return np.array(img_cropped)

if st.button("🚀 সিনেমাটিক ভিডিও তৈরি করুন (Create Cinematic Video)"):
    dialogues = [line.strip() for line in story_input_multi.strip().split('\n') if line.strip()]
    
    if not dialogues:
        st.warning("দয়া করে অন্তত একটি দৃশ্য বা ডায়লগ ইনপুট দিন!")
    elif not uploaded_files:
        st.warning("দয়া করে ছবি আপলোড করুন!")
    elif len(uploaded_files) != len(dialogues):
        st.error(f"⚠️ ডায়লগ লাইন ({len(dialogues)}টি) এবং আপলোড করা ছবির সংখ্যা ({len(uploaded_files)}টি) সমান হতে হবে। প্রতিটি ডায়লগের জন্য ১টি করে ছবি আপলোড করুন।")
    else:
        video_clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_scenes = len(dialogues)
        sorted_files = sorted(uploaded_files, key=lambda x: x.name)

        for i in range(total_scenes):
            status_text.text(f"⏳ সিনেমাটিক দৃশ্য {i+1}/{total_scenes} প্রসেস হচ্ছে...")
            curr_dialogue = dialogues[i]
            img_file = sorted_files[i]
            
            img_path = f"temp_img_{i}.png"
            img = Image.open(img_file)
            img.save(img_path)
                
            audio_path = f"temp_audio_{i}.mp3"
            cmd = ["edge-tts", "--voice", selected_voice, "--text", curr_dialogue, "--write-media", audio_path]
            subprocess.run(cmd, check=True)
            
            audio_clip = AudioFileClip(audio_path)
            
            clip = ImageClip(img_path).set_duration(audio_clip.duration)
            cinematic_clip = clip.fl(cinematic_zoom, keep_duration=True).set_audio(audio_clip)
            
            video_clips.append(cinematic_clip)
            progress_bar.progress((i + 1) / total_scenes)
            
        status_text.text("🎬 সিনেমাটিক ক্লিপগুলো জোড়া দিয়ে চূড়ান্ত ভিডিও রেন্ডার করা হচ্ছে...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_video_path = "final_story_video.mp4"
        final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
        
        st.success("🎉 আপনার সিনেমাটিক ভিডিও সফলভাবে তৈরি হয়ে গেছে!")
        st.video(output_video_path)
        
        with open(output_video_path, "rb") as file:
            st.download_button(
                label="📥 সম্পূর্ণ ভিডিওটি ডাউনলোড করুন (Download MP4)",
                data=file,
                file_name="full_story_video.mp4",
                mime="video/mp4"
            )
        
        audio_clip.close()
        final_video.close()
        for i in range(total_scenes):
            if os.path.exists(f"temp_img_{i}.png"):
                os.remove(f"temp_img_{i}.png")
            if os.path.exists(f"temp_audio_{i}.mp3"):
                os.remove(f"temp_audio_{i}.mp3")
                
