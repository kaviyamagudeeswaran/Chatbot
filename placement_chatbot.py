import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import io

# ==== Configure Gemini API ====
genai.configure(api_key="AIzaSyCkvtK9JuJNTkkqwCn1XccxdtJmPlKqIwQ")
text_model = genai.GenerativeModel("models/gemini-1.5-flash")
vision_model = genai.GenerativeModel("models/gemini-1.5-pro-vision")

st.set_page_config(page_title="🎓 Placement Chatbot", layout="wide")
st.title("🎓 Placement Chatbot")

# ==== Session State ====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==== Column Layout: ChatGPT Style ====
col1, col2, col3 = st.columns([1, 2, 1])

# ==== LEFT: Chat History + User Photos ====
with col1:
    st.subheader("📜 History")
    for i, (q, a, img) in enumerate(st.session_state.chat_history):
        st.markdown(f"**{i+1}. You:** {q[:30]}...")
        if img:
            st.image(img, caption=f"📷 Img {i+1}", use_column_width=True)

# ==== RIGHT: Voice Input ====
with col3:
    st.subheader("🎙️ Voice Input")
    def transcribe_voice():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Speak now...")
            audio = r.listen(source, phrase_time_limit=8)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return "❌ Couldn't understand your voice."
        except sr.RequestError:
            return "❌ Voice service error."

    if st.button("🎤 Use Voice"):
        voice_result = transcribe_voice()
        st.session_state.voice_input = voice_result
        st.success(f"🗣️ Voice: {voice_result}")
    else:
        voice_result = st.session_state.get("voice_input", "")

# ==== CENTER: Main Chat Input ====
with col2:
    st.subheader("💬 Ask your question")

    uploaded_image = st.file_uploader("📷 Upload an image (optional)", type=["png", "jpg", "jpeg"])
    text_input = st.text_input("💬 Type your question")

    combined_input = (voice_result + " " + text_input).strip()

    if st.button("📨 Send"):
        with st.spinner("🤖 Generating..."):
            try:
                if uploaded_image:
                    image = Image.open(uploaded_image)
                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format="PNG")
                    image_bytes.seek(0)
                    response = vision_model.generate_content([
                        combined_input,
                        genai.types.content.Part.from_data(data=image_bytes.read(), mime_type="image/png")
                    ])
                else:
                    response = text_model.generate_content(combined_input)
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"❌ Error: {str(e)}"

            st.session_state.chat_history.append((combined_input, bot_reply, uploaded_image))

# ==== Full Chat Below ====
st.markdown("---")
st.subheader("🧠 Conversation")
for q, a, img in reversed(st.session_state.chat_history):
    st.markdown(
        f"""
        <div style="border:1px solid #ccc; padding:15px; border-radius:12px; margin:10px 0; background-color:#f9f9f9;">
            <b>👤 You:</b> {q}<br><br>
            {'<img src="data:image/png;base64,' + st.image(img, use_column_width=False)._repr_png_().decode('utf-8') + '" width="100">' if img else ''}
            <b>🤖 Bot:</b> {a}
        </div>
        """,
        unsafe_allow_html=True
    )
