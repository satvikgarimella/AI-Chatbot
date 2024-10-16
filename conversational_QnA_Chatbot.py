from dotenv import load_dotenv
load_dotenv()  
import streamlit as st
import os
import google.generativeai as genai
import io
import speech_recognition as sr
import pyttsx3 as pt
import threading

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

tts_engine = pt.init()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'input' not in st.session_state:
    st.session_state['input'] = ""

st.set_page_config(page_title="Satvik's  Chatbot", page_icon="🤖")

background_image_url = '/mnt/data/ED9941CE-7E03-4818-9A2D-1F98C74FD743.jpeg'

st.markdown(f"""
    <style>
    body {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        font-family: 'Arial', sans-serif;
    }}
    
    .main {{
        background-color: rgba(13, 27, 42, 0.8); 
        padding: 20px;
        border-radius: 10px;
    }}
    
    h1 {{
        color: #FFFFFF;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 30px;
    }}
    
    .chat-box {{
        border-radius: 10px;
        padding: 15px;
        background-color: rgba(241, 245, 249, 0.9);
        margin-bottom: 10px;
        box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
    }}
    
    .user-message {{
        background-color: #00aaff;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    .bot-message {{
        background-color: #FFFFFF;
        color: #333333;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: right;
    }}
    
    input {{
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 100%;
        margin-bottom: 20px;
    }}
    
    .stButton>button {{
        background-color: #00aaff;
        color: white;
        font-size: 1.2rem;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        margin-top: 10px;
    }}
    .stButton>button:hover {{
        background-color: #007acc;
    }}
    
    .stInfo, .stSuccess, .stError {{
        color: white;
        background-color: #1d2f40;
        border: 1px solid #ccc;
    }}

    .stError {{
        background-color: #4a90e2;
        color: white;
    }}
    
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-thumb {{
        background-color: #00aaff;
        border-radius: 8px;
    }}
    </style>
""", unsafe_allow_html=True)

st.header("🤖 Satvik's Cool Chatbot")

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    full_response = ''.join([chunk.text for chunk in response])
    return full_response

def speak_text(text):
    def run_speech():
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=run_speech).start()

def speech_to_text():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("Listening to your input (Max silence of 3 seconds)", icon="🎤")
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"Recognized Speech: {text}", icon="✅")
            return text
        except sr.UnknownValueError:
            st.error("Unable to recognize your speech.", icon="❌")
        except sr.RequestError as e:
            st.error(f"Error occurred while requesting Google Speech Recognition: {e}")
        except Exception as ex:
            st.error(f"An error occurred: {str(ex)}")

col1, col2 = st.columns([3, 1])
with col1:
    input = st.text_input("Input:", key="input", value=st.session_state.input, placeholder="Ask me anything...")
with col2:
    if st.button("🎤 Listen"):
        text = speech_to_text()
        if text:
            st.session_state.input = text

submit = st.button("🚀 Request Response")

if input and submit:
    response = get_gemini_response(input)
    st.session_state['chat_history'].append(("You", input))
    st.session_state['chat_history'].append(("ChatBot", response))
    speak_text(response)

st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "You":
        st.markdown(f"<div class='chat-box user-message'><b>{role}:</b> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box bot-message'><b>{role}:</b> {text}</div>", unsafe_allow_html=True)

if st.button("🧹 Clear Chat"):
    st.session_state['chat_history'] = []

if st.session_state['chat_history']:
    chat_history_text = "\n".join([f"{role}: {text}" for role, text in st.session_state['chat_history']])
    download_button = st.download_button(
        label="💾 Download Chat History", 
        data=io.StringIO(chat_history_text).getvalue(), 
        file_name='chat_history.txt', 
        mime="text/plain"
    )