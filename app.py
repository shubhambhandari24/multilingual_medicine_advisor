import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import requests
from fuzzywuzzy import process
import socket

# Detect cloud environment (disable microphone)
is_cloud = "streamlit" in socket.gethostname().lower()

translator = Translator()

def translate_to_user_lang(text, lang_code):
    try:
        return translator.translate(text, dest=lang_code).text
    except:
        return text

# Voice input (with PyAudio-safe fallback)
def listen(language='en'):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source)
            try:
                query = r.recognize_google(audio, language=language)
                st.success(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                st.error("❌ Could not understand audio.")
            except sr.RequestError:
                st.error("❌ Speech service error.")
    except:
        st.warning("🎙️ Voice input not supported in this environment.")
    return ""

# Medicine info
def get_medicine_info(med_name, api_key):
    mapped_name = custom_name_map.get(med_name.lower(), med_name)
    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{mapped_name}&limit=1&api_key={api_key}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and 'results' in res.json():
            result = res.json()['results'][0]
            return {
                "name": mapped_name,
                "usage": result.get("indications_and_usage", ["Not available"])[0],
                "dosage": result.get("dosage_and_administration", ["Not available"])[0],
                "warnings": result.get("warnings", ["Not available"])[0],
                "effects": result.get("adverse_reactions", ["Not available"])[0]
            }
    except:
        return None

# Format into bullet points
def format_bullets(text, lang):
    lines = [s.strip() for s in text.replace("\n", ". ").split(".") if len(s.strip()) > 5]
    return "\n".join([f"- {translate_to_user_lang(s, lang)}" for s in lines[:5]])

# Fuzzy symptom detection
def detect_symptom(user_input):
    all_symptoms = []
    for symptom, synonyms in known_symptoms.items():
        all_symptoms.extend(synonyms)
    match, score = process.extractOne(user_input, all_symptoms)
    if score > 80:
        for symptom, synonyms in known_symptoms.items():
            if match in synonyms:
                return symptom
    return None

# Data mappings
symptom_medicine_map = {
    "fever": ["paracetamol", "ibuprofen"],
    "cold": ["cetirizine", "diphenhydramine"],
    "cough": ["guaifenesin", "dextromethorphan"],
    "vomiting": ["ondansetron"],
    "stomach ache": ["pantoprazole", "omeprazole"],
    "headache": ["acetaminophen", "ibuprofen"],
    "body pain": ["ibuprofen", "paracetamol"],
    "diarrhea": ["loperamide"],
}

custom_name_map = {
    "paracetamol": "acetaminophen", "dolo": "acetaminophen", "crocin": "acetaminophen",
    "calpol": "acetaminophen", "tylenol": "acetaminophen", "panadol": "acetaminophen",
    "combiflam": "ibuprofen + paracetamol", "nurofen": "ibuprofen", "advil": "ibuprofen",
    "motrin": "ibuprofen", "aspirin": "acetylsalicylic acid", "augmentin": "amoxicillin + clavulanate",
    "amoxil": "amoxicillin", "azithral": "azithromycin", "zithromax": "azithromycin",
    "cipro": "ciprofloxacin", "cefixime": "cefixime", "levoflox": "levofloxacin",
    "doxy": "doxycycline", "flagyl": "metronidazole", "benadryl": "diphenhydramine",
    "mucinex": "guaifenesin", "vicks": "dextromethorphan", "chlorpheniramine": "chlorpheniramine",
    "zyrtec": "cetirizine", "claritin": "loratadine", "allegra": "fexofenadine",
    "zofran": "ondansetron", "emetrol": "phosphorated carbohydrate", "digene": "magnesium hydroxide + simethicone",
    "pantoprazole": "pantoprazole", "omeprazole": "omeprazole", "ranitidine": "ranitidine",
    "pepto": "bismuth subsalicylate", "metformin": "metformin", "glucophage": "metformin",
    "januvia": "sitagliptin", "glimepiride": "glimepiride", "atenolol": "atenolol",
    "amlodipine": "amlodipine", "losartan": "losartan", "telmisartan": "telmisartan",
    "olmesartan": "olmesartan", "viagra": "sildenafil", "calcium sandoz": "calcium carbonate",
    "neurobion": "vitamin B complex"
}

known_symptoms = {
    "fever": ["fever", "high temperature", "pyrexia", "बुखार", "calor"],
    "cold": ["cold", "runny nose", "sneezing", "जुकाम", "resfriado"],
    "headache": ["headache", "migraine", "सिरदर्द", "dolor de cabeza"],
    "cough": ["cough", "dry cough", "productive cough", "खांसी", "tos"],
    "vomiting": ["vomiting", "nausea", "उल्टी", "vómito"]
}

# --- Streamlit UI ---
st.set_page_config(page_title="Multilingual Medicine Advisor", layout="centered")
st.title("💊 Multilingual Symptom-Based Medicine Advisor")

lang_map = {"English": "en", "Hindi": "hi", "Spanish": "es", "Tamil": "ta", "Telugu": "te", "Bengali": "bn", "Gujarati": "gu", "Kannada": "kn", "Marathi": "mr", "Punjabi": "pa"}
selected_lang = st.selectbox("🌐 Choose your language", list(lang_map.keys()))
lang_code = lang_map[selected_lang]

# Input type
if not is_cloud:
    input_mode = st.radio("Select Input Mode", ["🎙️ Voice", "⌨️ Text"])
else:
    st.info("🎙️ Voice input disabled on cloud")
    input_mode = "⌨️ Text"

api_key = st.text_input("🔑 OpenFDA API Key")

# Get symptom input
symptom_input = ""
if input_mode == "🎙️ Voice":
    if st.button("🎤 Describe Your Symptoms"):
        symptom_input = listen(language=lang_code)
else:
    symptom_input = st.text_input("💬 Describe your symptoms")

if symptom_input and api_key:
    translated = translator.translate(symptom_input, src=lang_code, dest='en').text.lower()
    st.markdown(f"🧠 {translate_to_user_lang('Interpreted Symptoms:', lang_code)} **{translated}**")

    detected = detect_symptom(translated)
    if detected:
        st.markdown(f"🤔 {translate_to_user_lang(f'You seem to have {detected}', lang_code)}")
        duration = st.text_input(translate_to_user_lang("📆 How many days have you had this symptom?", lang_code))

        if duration:
            st.markdown(f"✅ {translate_to_user_lang(f'Duration noted: {duration} days', lang_code)}")
            st.markdown(f"### 💊 {translate_to_user_lang('Suggested Medicines', lang_code)}")
            for med in symptom_medicine_map[detected]:
                info = get_medicine_info(med, api_key)
                if info:
                    st.markdown(f"""
#### {translate_to_user_lang(info['name'].title(), lang_code)}
**{translate_to_user_lang('Usage', lang_code)}**  
{format_bullets(info['usage'], lang_code)}

**{translate_to_user_lang('Dosage', lang_code)}**  
{format_bullets(info['dosage'], lang_code)}

**{translate_to_user_lang('Warnings', lang_code)}**  
{format_bullets(info['warnings'], lang_code)}

**{translate_to_user_lang('Side Effects', lang_code)}**  
{format_bullets(info['effects'], lang_code)}
                    """)
                else:
                    st.warning(translate_to_user_lang(f"No info found for {med}", lang_code))
            st.info(translate_to_user_lang("This is not medical advice. Always consult a doctor.", lang_code))
        else:
            st.warning(translate_to_user_lang("Please enter how long you've had the symptom.", lang_code))
    else:
        st.warning(translate_to_user_lang("Symptom not recognized. Please try again.", lang_code))
