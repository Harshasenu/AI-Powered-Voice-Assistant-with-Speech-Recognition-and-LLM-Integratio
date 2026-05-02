import streamlit as st # used to built frontend page


# configure the frontend
st.set_page_config(
    page_title = "Voice Assistant",
    layout = "wide"
)

# import all req lib

import os
import time 
import pyttsx3
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Load the API key from Local Envirnoment 
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# checking if API keys is uploaded or not 

if not GROQ_API_KEY:
    st.error("Missing API KEY")
    st.stop()

# intialization of LLM Model
client = Groq(api_key = GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# Intialization of Speech Recognizer and Text to Speech Engine
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

recognizer = get_recognizer()

# Intialization of Text to Speech 
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f"Error initializing TTS engine: {e}")
        return None
    
def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration = 1)
            audio = recognizer.listen(source, phrase_time_limit=10)

            text = recognizer.recognize_google(audio)
            return text.lower()
    except sr.UnknownValueError:
        return "Sorry. I don't catch you"
    except sr.RequestError:
        return "Speech Service is not avilable"
    except Exception as e:
        return f"Error: {e}"
    
def speak(text, voice_gender = "Girl"):
    try:
        engine = get_tts_engine()
        if engine is None:
            return
        
        # Choose the voice from pyttsx3
        # engine supports many voices 
        voices = engine.getProperty('voices')

        if voices:
            if voice_gender == 'boy':
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty("voice", voice.id)
                        break
            else:
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty("voice", voice.id)
                        break

        engine.setProperty('rate', 150)   # speed of speed
        engine.setProperty('volume', 0.8)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error("TTS Error: {e}")
    
def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            temperature=0.7
        )
        result = response.choices[0].message.content
        return result.strip() if result else "Sorry, I couldn't generate the rsponse"
    except Exception as e:
        return f"Error: {e}"



def main():
    st.title("AI Voice Assistant")
    st.markdown("---")

    # Initalizing chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content" : "You are a helpful voice assistant. Reply in just one line."}
        ]

    # initialize the messages to print on screen 
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("CONTROLS")

        tts_enabled = st.checkbox("Enter Text to speech", value = True)

        # selecting Gender of voice assistant
        voice_gender = st.selectbox(
            "Voice Gender",
            options = ["Girl", "boy"],
            index = 0,
            help = "Choose the Gender of Voice Assistant"
        )

        if st.button("Start Voice input", use_container_width = True):
            with st.spinner("Listning..."):
                user_input = listen_to_speech()

                if user_input and user_input not in ["Sorry. I don't catch you", "Speech Service is not avilable"]:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    with st.spinner("Thinking..."):
                        ai_response = get_ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                    if tts_enabled:
                        speak(ai_response, voice_gender)

                    st.rerun()
                
        st.markdown("---")

        st.subheader("Test Input")
        user_test = st.text_input("Type your message", key = "text_input")
        if st.button("SEND", use_container_width = True) and user_test:
            st.session_state.messages.append({"role": "user", "content": user_test})
            st.session_state.chat_history.append({"role": "user", "content": user_test})

            with st.spinner("Thinking..."):
                ai_response = get_ai_response(st.session_state.chat_history)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

            if tts_enabled:
                speak(ai_response, voice_gender)
            
            st.rerun()

        if st.button("Clear the Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful voice assistant. Reply just one line"}
            ]
            st.success("Chat history cleared!")
            st.rerun()

    st.subheader("CONVERSATION")

    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Starting Welcome message
    if not st.session_state.messages:
        st.info("Welcome to CHAT Assistant")

    # Copyright
    st.markdown("---")
    st.markdown(
        """
            <div style = 'text-align: center; color: #666;'>
                <p> Copyright @ Harsha </p>
            </div>
        """,
        unsafe_allow_html= True
    )

if __name__ == "__main__":
    main()