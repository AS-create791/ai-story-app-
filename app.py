import streamlit as st
import io
import requests
import subprocess
from PIL import Image, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Ultra AI Story Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 Ultra AI Story Video Creator")
st.write("আপনার গল্প ও প্রম্পট থেকে সরাসরি মাল্টি-সিন হাই-কোয়ালিটি এআই ভিডিও তৈরি করুন!")

# ১. ভয়েস অপশন
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

# ২. আর্ট ও ক্যারেক্টার স্টাইল
char_style = st.selectbox(
    "২. ক্যারেক্টার ও ছবির আর্ট স্টাইল নির্বাচন করুন:",
    [
        "ডার্ক ফ্যান্টাসি ওয়েবটুন (Dark Fantasy Webtoon / Manhwa)",
        "আধুনিক বাঙালি (Modern Bangladeshi / South Asian)",
        "চাইনিজ আধুনিক এনিমে (Modern Chinese Anime)"
    ]
)

# ৩. ডায়লগ / স্ক্রিপ্ট ইনপুট
st.subheader("৩. দৃশ্যসমূহ লিখুন (প্রতি লাইনে ১টি বাক্য বা ডায়লগ):")
story_input_multi = st.text_area(
    "গল্পের ডায়লগ (প্রতি লাইনে ১টি লিখুন):",
    "বাইরে তখন গুঁড়ি গুঁড়ি বৃষ্টি পড়ছিল, পুরো শহর জুড়ে আলো-আঁধারির খেলা।\n"
    "অনিন্দ্য জানালার পাশে দাঁড়িয়ে কফি খাচ্ছিল এবং দূর আকাশের দিকে তাকিয়ে ছিল।\n"
    "হঠাৎ দরজায় বেল বাজার শব্দে অনিন্দ্য চকিত হয়ে দরজার দিকে এগিয়ে গেল।",
    height=150
)

# ৪. ভিজ্যুয়াল প্রম্পট ইনপুট
st.subheader("৪. ছবির বিবরণ (প্রতি লাইনে ডায়লগের সাথে মিলিয়ে English Prompt লিখুন):")
prompt_input_multi = st.text_area(
    "Visual Prompts (প্রতি লাইনে ১টি ভিজ্যুয়াল প্রম্পট):",
    "A guy with messy dark hair sitting at a dark gothic table holding a cup, dark fantasy webtoon style, high detail, 8k\n"
    "A dark detailed room, looking out a rainy window, gothic architecture, dramatic lighting, masterpiece\n"
    "A sleek door inside a dark gothic room, subtle warm light, cinematic composition, detailed 8k",
    height=150
)

is_sensitive = st.checkbox("⚠️ ১৮+ / সেনসিটিভ কন্টেন্ট (Auto Privacy Blur)")

# ভিডিও তৈরি করার বাটন
if st.button("🚀 পুরো ভিডিও তৈরি করুন (Create Video)"):
    dialogues = [line.strip() for line in story_input_multi.strip().split('\n') if line.strip()]
    prompts = [line.strip() for line in prompt_input_multi.strip().split('\n') if line.strip()]
    
    if len(dialogues) != len(prompts):
        st.error(f"⚠️ ডায়লগ আছে {len(dialogues)}টি, কিন্তু প্রম্পট আছে {len(prompts)}টি। দুটো ঘরের লাইন সংখ্যা অবশ্যই সমান হতে হবে!")
    elif len(dialogues) == 0:
        st.warning("দয়া করে অন্তত একটি দৃশ্য ও প্রম্পট ইনপুট দিন!")
    else:
        video_clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_scenes = len(dialogues)
        
        for i in range(total_scenes):
            status_text.text(f"⏳ প্রসেস চলছে... দৃশ্য {i+1}/{total_scenes} তৈরি হচ্ছে...")
            curr_dialogue = dialogues[i]
            curr_prompt = prompts[i]
            
            # স্টাইল ফিল্টারিং
            if "ডার্ক ফ্যান্টাসি" in char_style:
                style_prompt = "dark fantasy webtoon style, shadow slave manhwa art, highly detailed gothic art, sharp lineart, dramatic moody backlighting, masterpiece quality, 8k resolution"
            elif "আধুনিক বাঙালি" in char_style:
                style_prompt = "handsome modern Bangladeshi South Asian aesthetic, trendy attractive modern clothes, realistic digital photography, cinematic 8k"
            else:
                style_prompt = "modern stylish anime style, vibrant aesthetic digital art, trendy outfit, 8k"
                
            full_prompt = f"{curr_prompt}, {style_prompt}"
            
            # হাই-কোয়ালিটি এআই ইমেজ ইঞ্জিন ফেচিং (ফ্রি ও রিয়েলিস্টিক এআই মডেল)
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1280&height=720&nologo=true&seed={i+100}&enhance=true"
            
            try:
                response = requests.get(image_url, timeout=40)
                if response.status_code == 200 and len(response.content) > 1000:
                    img = Image.open(io.BytesIO(response.content))
                    
                    if 'kissing' in curr_prompt.lower() or 'sex' in curr_prompt.lower() or is_sensitive:
                        img = img.filter(ImageFilter.GaussianBlur(radius=30))
                        
                    img_path = f"temp_img_{i}.png"
                    img.save(img_path)
                else:
                    st.error(f"দৃশ্য {i+1}-এর ছবি সার্ভার থেকে তৈরি করা যায়নি। আবার চেষ্টা করুন।")
                    st.stop()
            except Exception as e:
                st.error(f"ইমেজ ফেচিং এ সমস্যা হয়েছে: {str(e)}")
                st.stop()
                
            # ভয়েস টেক্সট টু স্পিচ ফেচিং
            audio_path = f"temp_audio_{i}.mp3"
            cmd = ["edge-tts", "--voice", selected_voice, "--text", curr_dialogue, "--write-media", audio_path]
            subprocess.run(cmd, check=True)
            
            # অডিও ও ছবি দিয়ে সিঙ্গেল ক্লিপ তৈরি
            audio_clip = AudioFileClip(audio_path)
            clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            video_clips.append(clip)
            
            progress_bar.progress((i + 1) / total_scenes)
            
        status_text.text("🎬 সবগুলো ক্লিপ জোড়া দিয়ে একটি ফুল ভিডিও রেন্ডার করা হচ্ছে...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_video_path = "final_story_video.mp4"
        final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
        
        st.success("🎉 আপনার পূর্ণাঙ্গ এইচডি ভিডিও প্রস্তুত!")
        st.video(output_video_path)
        
        with open(output_video_path, "rb") as file:
            st.download_button(
                label="📥 সম্পূর্ণ ভিডিওটি ডাউনলোড করুন (Download MP4)",
                data=file,
                file_name="full_story_video.mp4",
                mime="video/mp4"
            )
            
            
