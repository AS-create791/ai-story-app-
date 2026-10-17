    import streamlit as st
import io
import time
import requests
import subprocess
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Ultra AI Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Ultra AI Story Video Creator (Modern Chinese Anime)")
st.write("ক্রিস্টাল ক্লিয়ার ভাইব্রেন্ট ছবি এবং স্টাইলিশ মডার্ন চাইনিজ এনিমে আর্ট ভিডিও জেনারেটর!")

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

st.subheader("২. দৃশ্যসমূহ লিখুন (প্রতি লাইনে ১টি বাক্য বা ডায়লগ — সর্বোচ্চ ৫০টি):")
story_input_multi = st.text_area(
    "গল্পের ডায়লগ (প্রতি লাইনে ১টি লিখুন):",
    "বাইরে তখন গুঁড়ি গুঁড়ি বৃষ্টি পড়ছিল, পুরো শহর জুড়ে আলো-আঁধারির খেলা।\n"
    "অনিন্দ্য জানালার পাশে দাঁড়িয়ে কফি খাচ্ছিল এবং দূর আকাশের দিকে তাকিয়ে ছিল।\n"
    "হঠাৎ দরজায় বেল বাজার শব্দে অনিন্দ্য চকিত হয়ে দরজার দিকে এগিয়ে গেল।",
    height=200
)

st.subheader("৩. ছবির বিবরণ (ঐচ্ছিক — ফাঁকা রাখলে এআই নিজে থেকেই ডায়লগ অনুযায়ী মডার্ন এনিমে প্রম্পট বানাবে):")
prompt_input_multi = st.text_area(
    "Visual Prompts (যদি নিজে না লিখতে চান, তবে এটি ফাঁকা রাখুন):",
    "",
    height=150,
    placeholder="ফাঁকা রাখলে ডায়লগ ও পোশাকের বিবরণ অনুযায়ী এআই অটোমেটিক মডার্ন চাইনিজ এনিমে প্রম্পট বানিয়ে নেবে।"
)

# মডার্ন চাইনিজ এনিমে প্রম্পট জেনারেটর
def generate_anime_prompt(text):
    system_prompt = (
        f"Convert this story scene into a vivid, colorful 1-sentence English image prompt for AI generation. "
        f"Include details of character, outfits (modern casual jeans/jackets if unspecified, or historical if text explicitly specifies historical era), "
        f"beautiful detailed background, bright vibrant lighting. Text: '{text}'"
    )
    url = f"https://text.pollinations.ai/{requests.utils.quote(system_prompt)}?model=openai"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and len(res.text) > 5:
            return res.text.strip()
    except Exception:
        pass
    return f"Vibrant atmospheric modern anime scene illustrating: {text}"

if st.button("🚀 পুরো ভিডিও তৈরি করুন (Create Video)"):
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
        
        # ফিক্সড মডার্ন চাইনিজ এনিমে স্টাইল ও শার্পনেস প্রম্পট
        fixed_anime_style = (
            "modern chinese anime style, donghua art style, extremely sharp focus, crisp crystal clear details, "
            "vibrant beautiful rich colors, bright dramatic lighting, highly aesthetic background, 8k resolution, masterpiece"
        )
        
        for i in range(total_scenes):
            status_text.text(f"⏳ ক্রিস্টাল ক্লিয়ার ছবি জেনারেট হচ্ছে... দৃশ্য {i+1}/{total_scenes}")
            curr_dialogue = dialogues[i]
            
            if len(custom_prompts) == len(dialogues):
                curr_prompt = custom_prompts[i]
            else:
                curr_prompt = generate_anime_prompt(curr_dialogue)
            
            full_prompt = f"{curr_prompt}, {fixed_anime_style}"
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1280&height=720&nologo=true&seed={i+5050}&enhance=true&model=flux"
            
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
            
        status_text.text("🎬 সবগুলো ক্লিপ জোড়া দিয়ে হাই-ডেফিনিশন ভিডিও রেন্ডার করা হচ্ছে...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_video_path = "final_story_video.mp4"
        final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
        
        st.success("🎉 আপনার ক্রিস্টাল ক্লিয়ার মডার্ন এনিমে ভিডিও প্রস্তুত!")
        st.video(output_video_path)
        
        with open(output_video_path, "rb") as file:
            st.download_button(
                label="📥 সম্পূর্ণ ভিডিওটি ডাউনলোড করুন (Download MP4)",
                data=file,
                file_name="full_story_video.mp4",
                mime="video/mp4"
            )
