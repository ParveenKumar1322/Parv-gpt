import streamlit as st
from transformers import pipeline
import torch
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="Parv GPT - Free AI", layout="centered")

st.title("🎙️ Parv GPT - Free AI Chat + Image + Voice")
st.markdown("Chat with open-source AI, generate images, and use voice input!")

# Chatbot (Mistral 7B)
@st.cache_resource
def load_chat_model():
    return pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1", device_map="auto")

chat_model = load_chat_model()

# Image Generator using Hugging Face API
def generate_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    payload = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=payload)
    image = Image.open(BytesIO(response.content))
    return image

# Voice Input
st.markdown("""
<script>
function startRecognition() {
  const recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.onresult = function(event) {
    const result = event.results[0][0].transcript;
    document.getElementById("input-box").value = result;
    document.getElementById("submit-button").click();
  }
  recognition.start();
}
</script>
""", unsafe_allow_html=True)

# UI
option = st.radio("Choose what to do:", ["💬 Chat", "🖼️ Image Generator"])

if option == "💬 Chat":
    st.markdown("### Type your message or use mic:")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("You:", key="input-box")
    with col2:
        st.button("🎤 Mic", on_click=None, args=(), kwargs={}, key="mic-btn")
        st.markdown('<button onclick="startRecognition()">🎙️ Speak</button>', unsafe_allow_html=True)

    if st.button("Submit", key="submit-button") and user_input:
        with st.spinner("Thinking..."):
            reply = chat_model(user_input, max_length=100, do_sample=True)[0]['generated_text']
        st.markdown("**Parv GPT:** " + reply)

if option == "🖼️ Image Generator":
    prompt = st.text_input("Enter image description:")
    if st.button("Generate"):
        with st.spinner("Creating image..."):
            image = generate_image(prompt)
        st.image(image, caption="Generated Image")
