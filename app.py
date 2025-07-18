import streamlit as st
import speech_recognition as sr
from PIL import Image
import openai

st.set_page_config(page_title="Parv GPT", layout="centered")

st.title("🧠 Parv GPT")
st.write("Talk to AI using voice or image!")

# Voice input
if st.button("🎤 Start Voice Input"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.success(f"You said: {text}")
        except:
            st.error("Voice not clear")

# Image input
uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Text input and OpenAI response
query = st.text_input("💬 Ask something")
if st.button("🔍 Submit"):
    if query:
        openai.api_key = "your-openai-api-key"
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": query}]
            )
        st.success(response['choices'][0]['message']['content'])
    else:
        st.warning("Please enter some text.")
