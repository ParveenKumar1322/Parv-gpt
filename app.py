import os
from io import BytesIO

import streamlit as st
import speech_recognition as sr
from PIL import Image
import requests

# ---------- BASIC SETTINGS ----------
st.set_page_config(page_title="Parv GPT", page_icon="🤖", layout="centered")
st.title("🎙️ Parv GPT – Aapka AI Dost")
st.write("Namaste! Yahan aap **voice**, **text**, aur **image prompt** se AI se baat kar sakte ho.")

# ---------- OPENAI CLIENT ----------
# Get API key from Streamlit secrets OR env var
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip()
client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.warning("OpenAI library import issue: " + str(e))
else:
    st.info("⚠️ OPENAI_API_KEY set nahi hai. GPT reply disabled (sirf image feature chalega).")

# ---------- VOICE INPUT ----------
st.subheader("🎤 Voice Input (optional)")
st.caption("NOTE: Server-side mic hamesha available nahi hota. Agar mic fail ho, neeche 'Audio Upload' ka use karein.")

voice_text = ""

col1, col2 = st.columns(2)
with col1:
    if st.button("🎙️ Try Live Mic"):
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("🔴 Bolna start karo...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            with st.spinner("🔍 Sun raha tha..."):
                voice_text = r.recognize_google(audio, language="hi-IN")
            st.success(f"🗣️ Aapne bola: {voice_text}")
        except Exception as e:
            st.error("Mic se record nahi ho paya. Neeche audio upload try karo.")
            st.caption(str(e))

with col2:
    audio_file = st.file_uploader("📁 Audio Upload (wav/mp3)", type=["wav", "mp3", "m4a", "ogg"])
    if audio_file is not None:
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)
            with st.spinner("🧠 Speech se text nikal raha hoon..."):
                voice_text = r.recognize_google(audio, language="hi-IN")
            st.success(f"🗣️ Upload se mila: {voice_text}")
        except Exception as e:
            st.error("Audio samajh nahi aaya.")
            st.caption(str(e))

# ---------- USER TEXT QUERY ----------
st.subheader("💬 Text / Voice se Sawal Pucho")
query_default = voice_text if voice_text else ""
query = st.text_input("Yahan apna sawal likho (ya upar se voice lo):", value=query_default)

if st.button("🤖 Ask Parv GPT"):
    if not query.strip():
        st.warning("Pehle sawal likho ya bolo.")
    else:
        if not client:
            st.warning("OPENAI_API_KEY missing hai, isliye GPT reply nahi milega.")
        else:
            try:
                with st.spinner("Parv GPT soch raha hai..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # fast + sasta; change to gpt-4o if chaho
                        messages=[
                            {"role": "system", "content": "Tum Parv GPT ho. Hindi + Hinglish me friendly jawab do."},
                            {"role": "user", "content": query},
                        ],
                        max_tokens=500,
                    )
                answer = response.choices[0].message.content
                st.success("🧠 Parv GPT ka jawab:")
                st.write(answer)
            except Exception as e:
                st.error("GPT call fail ho gayi.")
                st.caption(str(e))

# ---------- IMAGE GENERATOR ----------
st.subheader("🖼️ Image Generator")
img_prompt = st.text_input("Image banane ke liye prompt likho (Hindi / English):")

col_a, col_b = st.columns(2)
with col_a:
    make_img = st.button("📷 Unsplash Se Image Lao")
with col_b:
    make_ai_img = st.button("🎨 (Optional) OpenAI Image Gen")

if make_img:
    if not img_prompt.strip():
        st.warning("Image prompt likho.")
    else:
        st.write("🔄 Image fetch kar raha hoon...")
        url = f"https://source.unsplash.com/800x600/?{img_prompt.replace(' ', '+')}"
        try:
            resp = requests.get(url, timeout=20)
            img = Image.open(BytesIO(resp.content))
            st.image(img, caption=f"Prompt: {img_prompt}", use_column_width=True)
            st.download_button("📥 Download Image", resp.content, file_name="parvgpt_image.jpg")
        except Exception as e:
            st.error("Unsplash image nahi mili.")
            st.caption(str(e))

if make_ai_img:
    if not client:
        st.warning("OPENAI_API_KEY required for AI image.")
    elif not img_prompt.strip():
        st.warning("Image prompt likho.")
    else:
        try:
            with st.spinner("AI se image bana raha hoon..."):
                # DALL·E style via OpenAI
                image_resp = client.images.generate(
                    model="gpt-image-1",  # updated OpenAI image model
                    prompt=img_prompt,
                    size="1024x1024"
                )
            img_url = image_resp.data[0].url
            st.image(img_url, caption=f"AI Image: {img_prompt}", use_column_width=True)
            # Download: fetch and give file
            img_data = requests.get(img_url, timeout=20).content
            st.download_button("📥 Download AI Image", img_data, file_name="parvgpt_ai_image.png")
        except Exception as e:
            st.error("AI image generate nahi ho payi.")
            st.caption(str(e))

# ---------- FOOTER ----------
st.markdown("---")
st.caption("🚀 Parv GPT • Built with Streamlit • @ParveenKumar1322")
