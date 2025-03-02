import pyttsx3
import speech_recognition as sr
import datetime
import time
import urllib.request
import webbrowser
import os
import streamlit as st
import threading
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Streamlit UI
st.title("Voice Assistant")
st.image("jarvis.jpeg", caption="JARVIS")
st.write("Assistant says:")
st.subheader("Assistant Response")

# Initialize Spoken Text in Session State
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""

spoken_text = st.empty()

# Hugging Face Authentication
HF_key = 'give acess toke of huggin face'
login(HF_key)  # Authenticate once

# Load Model and Tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_key)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

def get_openai_response(query):
    """Generate a response from LLaMA 2"""
    device = "cpu"
    inputs = tokenizer(query, return_tensors="pt").to(device)
    model.to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def initialize_engine():
    """Initialize text-to-speech engine"""
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 175)
    return engine

def speak(text):
    """Convert text to speech and update UI"""
    st.session_state.spoken_text = text  # Update UI
    engine = initialize_engine()
    engine.say(text)
    engine.runAndWait()

def command():
    """Capture voice command"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            print("Could not understand audio")
            return "None"
        except sr.RequestError:
            print("Could not request results")
            return "None"

def open_application(app_path, app_name):
    """Open applications"""
    try:
        speak(f"Opening {app_name}, boss.")
        os.startfile(app_path)
    except Exception:
        speak(f"I couldn't find {app_name}, boss.")

def cal_day():
    """Return the current day"""
    day_dict = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    return day_dict[datetime.datetime.today().weekday()]

def wishMe():
    """Greet the user"""
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = cal_day()
    if 0 <= hour < 12:
        speak(f"Good morning Boss, it's {day} and the time is {t}")
    elif 12 <= hour < 16:
        speak(f"Good afternoon Boss, it's {day} and the time is {t}")
    else:
        speak(f"Good evening Boss, it's {day} and the time is {t}")

def main():
    """Main assistant loop"""
    while True:
        query = command()
        if query == "None":
            continue  

        elif query == "how are you":
            speak('i am good how are you boss...')

        elif query == "what i have to do today":
            speak('Do code boss')

        elif "open google" in query:
            speak("Opening Google, boss")
            webbrowser.open_new_tab("https://www.google.com")

        elif "open vs code" in query:
            open_application("C:\\Users\\Aryan Thapa\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe", 'VS Code')

        elif "open python" in query:
            open_application("C:\\Users\\Aryan Thapa\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\JetBrains Toolbox\\PyCharm Community.lnk", 'PyCharm')
        elif "open whatsapp" in query:
            open_application('','whatsapp')
        elif "exit" in query:
            speak("Goodbye, boss")
            break
        else:
            response = get_openai_response(query)
            speak(response)
            print(response)

def run_assistant():
    """Start the voice assistant"""
    wishMe()
    main()

# Start assistant in a separate thread
assistant_thread = threading.Thread(target=run_assistant, daemon=True)
assistant_thread.start()

