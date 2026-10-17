import streamlit as st
import io
import time
import requests
import subprocess
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import numpy as np

st.set_page_config(page_title="Cinematic AI Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Cinematic AI Story Video Creator")
st.write("যেকোনো ভাষায় লিখে পছন্দের ভাষায় ভয়েস নিন এবং সিনেমাটিক জুম ইফেক্টযুক্ত ভিডিও তৈরি করুন!")

# ১. ভয়েসের ভাষা নির্বাচন (যাতে যেকোনো ভাষায় ভয়েস জেনারেট করা যায়)
voice_lang_option = st.selectbox(
    "১. ভয়েস বা কথনের ভাষা নির্বাচন করুন (আপনি যে ভাষায় শুনতে চান):",
    ["বাংলা (Bengali)", "হিন্দি (Hindi)", "ইংরেজি (English)"]
)

voice_mapping = {
    "বাংলা (Bengali)": "bn-BD-NabanitaNeural",
    "হিন্দি (Hindi)": "hi-IN-SwaraNeural",
    "ইংরেজি (English)": "en-US-AriaNeural"
}
selected_voice = voice_mapping[voice_lang_option]

st.subheader("২. দৃশ্যসমূহ লিখুন (বাংলা, ইংরেজি বা হিন্দি যেকোনো ভাষায় — সর্বোচ্চ ৫০টি):")
story_input_multi = st.text_area(
    "গল্প বা ডায়লগ (প্রতি লাইনে ১টি লিখুন, ভাষা যেকোনো হতে পারে):",
    "বাইরে তখন গুঁড়ি গুঁড়ি বৃষ্টি পড়ছিল, পুরো শহর জুড়ে আলো-আঁধারির খেলা।\n"
    "অনিন্দ্য জানালার পাশে দাঁড়িয়ে কফি খাচ্ছিল এবং দূর আকাশের দিকে তাকিয়ে ছিল।\n"
    "হঠাৎ দরজায় বেল বাজার শব্দে অনিন্দ্য চকিত হয়ে দরজার দিকে এগিয়ে গেল।",
    height=200
)

st.subheader("৩. ছবির বিবরণ (ঐচ্ছিক — ফাঁকা রাখলে এআই নিজে থেকেই নিখুঁত প্রম্পট বানিয়ে নেবে):")
prompt_input_multi = st.text_area(
    "Visual Prompts (যদি নিজে না লিখতে চান, তবে এটি ফাঁকা রাখুন):",
    "",
    height=150,
    placeholder="ফাঁকা রাখলে আপনার লেখা ডায়লগ বুঝে এআই নিজে থেকেই ক্রিস্টাল ক্লিয়ার এনিমে প্রম্পট তৈরি করে নেবে।"
)

# এআই প্রম্পট জেনারেটর (যেকোনো ভাষার ইনপুটকে ইংরেজিতে নিখুঁত ভিজ্যুয়াল প্রম্পটে রূপান্তর করবে)
def generate_anime_prompt(text):
    system_prompt = (
        f"Convert this story scene into an ultra-detailed, crystal-clear 1-sentence English image prompt for AI generation. "
        f"Include sharp character features, modern casual outfits (jeans/jackets), beautiful detailed background, vibrant colors. Text: '{text}'"
    )
    url = f"https://text.pollinations.ai/{requests.utils.quote(system_prompt)}?model=openai"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and len(res.text) > 5:
            return res.text.strip()
    except Exception:
        pass
    return f"Vibrant modern anime cinematic scene illustrating: {text}"

# সিনেমাটিক জুম ইফেক্ট (Ken Burns Effect) ফাংশন
def cinematic_zoom(get_frame, t):
    img = Image.fromarray(get_frame(t))
    w, h = img.size
    # জুম ইন হওয়ার স্কেল হিসাব
    zoom_factor = 1.0 + (0.15 * (t / 5.0)) # ধীরে ধীরে ১৫% জুম হবে
    new_w = int(w * zoom_factor)
    new_h = int(h * zoom_factor)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # সেন্টারে ক্রপ করে আগের সাইজে ফিরিয়ে আনা
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    right = left + w
    bottom = top + h
    img_cropped = img_resized.crop((left, top, right, bottom))
    return np.array(img_cropped)

if st.button("🚀 সিনেমাটিক ভিডিও তৈরি করুন (Create Cinematic Video)"):
    dialogues = [line.strip() for line in story_input_multi.strip().split('\n') if line.strip()]
    custom_prompts = [line.strip() for line in prompt_input_multi.strip().split('\n') if line.strip()]
    
    if len(dialogues) > 50:
        st.error("⚠️ আপনি সর্বোচ্চ ৫০টি দৃশ্য একসাথে দিতে পারবেন। দয়া করে লাইনের সংখ্যা কমিয়ে নিন।")
    elif len(dialogues) == 0:
        st.warning("দয়া করে অন্তত একটি দৃশ্য বা ডায়লগ ইনপুট দিন!")
    elif len(custom_prompts) > 0 and len(custom_prompts) != len(dialogues):
        st.error(f"⚠️ ডায়লগ লাইন ({len(dialogues)}টি) এবং প্রম্পট লাইন ({len(custom_prompts)}টি) সমান হতে হবে। অথবা ৩ নম্বর ঘরটি ফাঁকা রাখুন।")
    else:
        video_clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_scenes = len(dialogues)
        
        ultra_clear_style = (
            "modern chinese anime donghua style, hyper-realistic lighting, ultra-sharp focus, crisp crystal clear details, "
            "vibrant rich colors, flawless facial features, high-end digital art masterpiece, 8k resolution"
        )
        
        for i in range(total_scenes):
            status_text.text(f"⏳ সিনেমাটিক দৃশ্য {i+1}/{total_scenes} প্রসেস হচ্ছে...")
            curr_dialogue = dialogues[i]
            
            if len(custom_prompts) == len(dialogues):
                curr_prompt = custom_prompts[i]
            else:
                curr_prompt = generate_anime_prompt(curr_dialogue)
            
            full_prompt = f"{curr_prompt}, {ultra_clear_style}"
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1280&height=720&nologo=true&private=true&seed={i+8888}&model=flux"
            
            success = False
            img = None
            for attempt in range(5):
                try:
                    response = requests.get(image_url, timeout=60)
                    if response.status_code == 200 and len(response.content) > 1000:
                        img = Image.open(io.BytesIO(response.content))
                        success = True
                        break
                except Exception:
                    pass
                time.sleep(3)
                
            if not success or img is None:
                st.error(f"⚠️ দৃশ্য {i+1}-এর ছবি সার্ভার থেকে লোড হতে পারেনি। আবার চেষ্টা করুন।")
                st.stop()
                
            img_path = f"temp_img_{i}.png"
            img.save(img_path)
                
            audio_path = f"temp_audio_{i}.mp3"
            cmd = ["edge-tts", "--voice", selected_voice, "--text", curr_dialogue, "--write-media", audio_path]
            subprocess.run(cmd, check=True)
            
            audio_clip = AudioFileClip(audio_path)
            
            # ক্লিপ তৈরি এবং তার ওপর সিনেমাটিক জুম ইফেক্ট প্রয়োগ
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
