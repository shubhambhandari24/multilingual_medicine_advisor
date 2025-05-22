import speech_recognition as sr
import streamlit as st

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.success(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Could not understand your voice.")
        except sr.RequestError:
            st.error("Speech recognition service is down.")
    return ""
