import streamlit as st
import io
import requests
import subprocess
import tempfile
from PIL import Image, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip

st.set_page_config(page_title="AI Story Video Engine", page_icon="🎬", layout="centered")

st.title("🎬 AI Story Video Engine")
st.write("আপনার পছন্দের ভাষা ও ক্যারেক্টার বেছে নিয়ে গল্প থেকে ভিডিও তৈরি করুন!")

lang_option = st.selectbox(
    "১. ভয়েসের ভাষা নির্বাচন করুন:",
    ["বাংলা (Bengali)", "হিন্দি (Hindi)", "ইংরেজি (English)"]
)

voice_mapping = {
    "বাংলা (Bengali)": "bn-BD-NabanitaNeural",
    "হিন্দি (Hindi)": "hi-IN-SwaraNeural",
    "ইংরেজি (English)": "en-US-AriaNeural"
}
selected_voice = voice_mapping[lang_option]

char_style = st.selectbox(
    "২. ক্যারেক্টার স্টাইল নির্বাচন করুন:",
    ["বাঙালি ক্যারেক্টার (Bengali / South Asian)", "চাইনিজ আধুনিক এনিমে (Modern Chinese Anime)"]
)

story_input = st.text_area("৩. আপনার গল্পের স্ক্রিপ্ট বা ডায়লগ লিখুন:", "ফিরোজ সাহেব আজ অনেকদিন পর বাড়ি ফিরছেন। বাইরে বৃষ্টি পড়ছে, আর জানালার পাশে দাঁড়িয়ে তাঁর অপেক্ষায় প্রহর গুনছে পুরো পরিবার।")
prompt_input = st.text_area("৪. ছবির বিবরণ (English Visual Prompt):", "a beautiful girl looking through a rainy window, emotional expression, dhaka rainy background")

is_sensitive = st.checkbox("⚠️ ১৮+ / সেনসিটিভ কন্টেন্ট (Auto Privacy Blur)")

if st.button("🚀 ভিডিও তৈরি করুন (Create Video)"):
    if not story_input or not prompt_input:
        st.warning("দয়া করে গল্প এবং ছবির প্রম্পট উভয়ই লিখুন!")
    else:
        with st.spinner("⏳ এআই কাজ করছে... ছবি, সুমিষ্ট ভয়েস ও ভিডিও তৈরি হচ্ছে..."):
            
            if "বাঙালি" in char_style:
                style_prompt = "south asian bengali ethnic features, wearing traditional bengali dress, realistic digital art"
            else:
                style_prompt = "modern stylish chinese anime style, trendy outfits, vivid colorful digital art"
                
            vivid_prompt = f"{prompt_input}, {style_prompt}, highly detailed, vivid vibrant colors, cinematic lighting, 8k"
            
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(vivid_prompt)}?width=1280&height=720&nologo=true"
            response = requests.get(image_url)
            img = Image.open(io.BytesIO(response.content))
            
            if 'kissing' in prompt_input.lower() or 'sex' in prompt_input.lower() or is_sensitive:
                img = img.filter(ImageFilter.GaussianBlur(radius=30))
                
            img_path = "temp_image.png"
            img.save(img_path)
            
            audio_path = "temp_voice.mp3"
            cmd = ["edge-tts", "--voice", selected_voice, "--text", story_input, "--write-media", audio_path]
            subprocess.run(cmd, check=True)
            
            audio_clip = AudioFileClip(audio_path)
            video_clip = ImageClip(img_path).set_duration(audio_clip.duration)
            video_clip = video_clip.set_audio(audio_clip)
            
            output_video_path = "story_video.mp4"
            video_clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
            
            st.success("🎉 আপনার ভিডিও সফলভাবে তৈরি হয়েছে!")
            st.video(output_video_path)
            
            with open(output_video_path, "rb") as file:
                st.download_button(
                    label="📥 ভিডিও ডাউনলোড করুন (Download MP4)",
                    data=file,
                    file_name="ai_story_video.mp4",
                    mime="video/mp4"
                )
                
