import streamlit as st
import io
import time
import requests
import subprocess
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Ultra AI Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Ultra AI Story Video Creator (Smart Theme)")
st.write("ক্রিস্টাল ক্লিয়ার ছবি এবং গল্প অনুযায়ী অটোমেটিক ডার্ক/লাইট থিম এআই ভিডিও জেনারেটর!")

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

st.subheader("৩. দৃশ্যসমূহ লিখুন (প্রতি লাইনে ১টি বাক্য বা ডায়লগ — সর্বোচ্চ ৫০টি):")
story_input_multi = st.text_area(
    "গল্পের ডায়লগ (প্রতি লাইনে ১টি লিখুন):",
    "বাইরে তখন গুঁড়ি গুঁড়ি বৃষ্টি পড়ছিল, পুরো শহর জুড়ে আলো-আঁধারির খেলা।\n"
    "অনিন্দ্য জানালার পাশে দাঁড়িয়ে কফি খাচ্ছিল এবং দূর আকাশের দিকে তাকিয়ে ছিল।\n"
    "হঠাৎ দরজায় বেল বাজার শব্দে অনিন্দ্য চকিত হয়ে দরজার দিকে এগিয়ে গেল।",
    height=200
)

st.subheader("৪. ছবির বিবরণ (ঐচ্ছিক — ফাঁকা রাখলে গল্প অনুযায়ী এআই নিজেই অটো প্রম্পট ও থিম সেট করবে):")
prompt_input_multi = st.text_area(
    "Visual Prompts (যদি নিজে না লিখতে চান, তবে এটি ফাঁকা রাখুন):",
    "",
    height=150,
    placeholder="ফাঁকা রাখলে গল্প ও থিম (ডার্ক বা লাইট) অনুযায়ী এআই নিজে থেকেই নিখুঁত প্রম্পট তৈরি করে নেবে।"
)

# গল্প অনুযায়ী স্মার্ট থিম ও প্রম্পট জেনারেটর (ডার্ক বা লাইট অটো ডিটেক্ট করবে)
def generate_smart_prompt(text):
    system_prompt = (
        f"Analyze this scene text and create a crystal clear, high-detail 1-sentence English image prompt. "
        f"Automatically adapt the lighting and mood based on the text: use dark/gothic/moody themes if the scene is sad, tense or dark; "
        f"use bright/warm/vibrant lighting if it's normal, happy or light. Text: '{text}'"
    )
    url = f"https://text.pollinations.ai/{requests.utils.quote(system_prompt)}?model=openai"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and len(res.text) > 5:
            return res.text.strip()
    except Exception:
        pass
    return f"High quality cinematic scene illustrating: {text}"

if st.button("🚀 পুরো ভিডিও তৈরি করুন (Create Video)"):
    dialogues = [line.strip() for line in story_input_multi.strip().split('\n') if line.strip()]
    custom_prompts = [line.strip() for line in prompt_input_multi.strip().split('\n') if line.strip()]
    
    if len(dialogues) > 50:
        st.error("⚠️ আপনি সর্বোচ্চ ৫০টি দৃশ্য একসাথে দিতে পারবেন। দয়া করে লাইনের সংখ্যা কমিয়ে নিন।")
    elif len(dialogues) == 0:
        st.warning("দয়া করে অন্তত একটি দৃশ্য বা ডায়লগ ইনপুট দিন!")
    elif len(custom_prompts) > 0 and len(custom_prompts) != len(dialogues):
        st.error(f"⚠️ ডায়লগ লাইন ({len(dialogues)}টি) এবং প্রম্পট লাইন ({len(custom_prompts)}টি) সমান হতে হবে। অথবা ৪ নম্বর ঘরটি ফাঁকা রাখুন।")
    else:
        video_clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_scenes = len(dialogues)
        
        for i in range(total_scenes):
            status_text.text(f"⏳ ক্রিস্টাল ক্লিয়ার ছবি তৈরি হচ্ছে... দৃশ্য {i+1}/{total_scenes}")
            curr_dialogue = dialogues[i]
            
            if len(custom_prompts) == len(dialogues):
                curr_prompt = custom_prompts[i]
            else:
                curr_prompt = generate_smart_prompt(curr_dialogue)
            
            # ক্রিস্টাল ক্লিয়ার ও ডিটেইলড রেন্ডারিং প্যারামিটার
            full_prompt = f"{curr_prompt}, crystal clear details, sharp focus, highly detailed digital art, 8k resolution, masterpiece"
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1280&height=720&nologo=true&seed={i+3030}&enhance=true"
            
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
            clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            video_clips.append(clip)
            
            progress_bar.progress((i + 1) / total_scenes)
            
        status_text.text("🎬 সবগুলো ক্লিপ জোড়া দিয়ে ভিডিও রেন্ডার করা হচ্ছে...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_video_path = "final_story_video.mp4"
        final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
        
        st.success("🎉 আপনার ক্রিস্টাল ক্লিয়ার এইচডি ভিডিও প্রস্তুত!")
        st.video(output_video_path)
        
        with open(output_video_path, "rb") as file:
            st.download_button(
                label="📥 সম্পূর্ণ ভিডিওটি ডাউনলোড করুন (Download MP4)",
                data=file,
                file_name="full_story_video.mp4",
                mime="video/mp4"
            )
            
