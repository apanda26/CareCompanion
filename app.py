import streamlit as st
import google.generativeai as genai
import datetime
import json
from typing import Optional, List, Dict

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="💙 Care Companion",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# GOOGLE GEMINI SETUP
# -------------------------------
API_KEY = "AIzaSyBuLV_jzkqr-CXRiGY__utepQ_3I_dbIk8"  # 🔑 Replace with your Gemini key

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

# -------------------------------
# MEDICATION MANAGEMENT
# -------------------------------
def load_medications():
    try:
        with open("medications.json", "r") as f:
            return json.load(f)
    except:
        return [
            {"name": "Blood Pressure Medication", "times": ["08:00", "20:00"], "dosage": "1 tablet", "with_food": True},
            {"name": "Vitamin D", "times": ["09:00"], "dosage": "1 capsule", "with_food": False},
        ]

def get_medications_text(medications):
    text = "Current medications:\n"
    for med in medications:
        times_str = ", ".join(med['times'])
        food_note = " (take with food)" if med.get('with_food') else ""
        text += f"- {med['name']}: {med['dosage']} at {times_str}{food_note}\n"
    return text

# -------------------------------
# SAFETY CHECKS
# -------------------------------
def detect_concern(message: str) -> Optional[str]:
    emergency_keywords = ['chest pain', "can't breathe", 'heart attack', 'stroke', 'bleeding heavily', 'unconscious']
    urgent_keywords = ['fell', 'fall', 'hurt', 'pain', 'dizzy', 'confused', 'vomit', 'stuck', 'help me']
    
    lower = message.lower()
    if any(k in lower for k in emergency_keywords):
        return "EMERGENCY"
    if any(k in lower for k in urgent_keywords):
        return "URGENT"
    return None

# -------------------------------
# AI RESPONSE HANDLER
# -------------------------------
def generate_ai_response(user_message, history, meds_text):
    system_context = f"""
You are Care Companion, a warm and caring AI assistant for elderly users.

PERSONALITY:
- Warm, patient, and empathetic
- Speak simply and clearly
- Be kind, supportive, and concise

ROLE:
- Provide emotional support
- Help with medication reminders
- Monitor for safety concerns
- Engage in pleasant conversation

MEDICATIONS:
{meds_text}

SAFETY RULES:
If user mentions pain, falling, breathing trouble, or confusion:
- Show concern
- Recommend calling caregiver or 911 calmly
"""
    chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in history[-6:]])
    prompt = f"{system_context}\n\nConversation:\n{chat_context}\nUser: {user_message}\nCare Companion:"
    
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else "I'm here with you."

# -------------------------------
# UI START
# -------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#3b82f6;'>💙 Care Companion</h1>",
    unsafe_allow_html=True
)
st.markdown("<p style='text-align:center; color:gray;'>Your caring AI companion for safety, medication, and conversation.</p>", unsafe_allow_html=True)

# Session state setup
if "history" not in st.session_state:
    st.session_state.history = []
if "medications" not in st.session_state:
    st.session_state.medications = load_medications()

# Sidebar (Profile & Meds)
with st.sidebar:
    st.header("👤 Profile & Settings")
    name = st.text_input("Your name", st.session_state.get("name", ""))
    st.session_state.name = name

    st.divider()
    st.subheader("💊 Medications")
    for med in st.session_state.medications:
        st.write(f"**{med['name']}** — {med['dosage']} at {', '.join(med['times'])}")

    if st.button("➕ Add Medication"):
        with st.form("add_med"):
            name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage")
            times = st.text_input("Times (comma separated, e.g., 08:00, 20:00)")
            with_food = st.checkbox("Take with food?")
            submitted = st.form_submit_button("Save")
            if submitted and name and dosage and times:
                new_med = {
                    "name": name,
                    "dosage": dosage,
                    "times": [t.strip() for t in times.split(",")],
                    "with_food": with_food
                }
                st.session_state.medications.append(new_med)
                with open("medications.json", "w") as f:
                    json.dump(st.session_state.medications, f, indent=2)
                st.success("Medication added!")

st.divider()

# Chat UI
for msg in st.session_state.history:
    role = "🧠" if msg["role"] == "assistant" else "👤"
    bubble_color = "#3b82f6" if msg["role"] == "user" else "#f1f5f9"
    text_color = "white" if msg["role"] == "user" else "black"
    st.markdown(
        f"<div style='background:{bubble_color}; color:{text_color}; padding:12px; border-radius:12px; margin:8px 0;'>{role} {msg['content']}</div>",
        unsafe_allow_html=True
    )

# Input box
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    concern = detect_concern(user_input)
    if concern == "EMERGENCY":
        ai_reply = "🚨 This sounds serious! Please call 911 immediately or contact your caregiver."
    elif concern == "URGENT":
        ai_reply = "⚠️ I'm very concerned. Please reach your caregiver as soon as possible."
    else:
        meds_text = get_medications_text(st.session_state.medications)
        ai_reply = generate_ai_response(user_input, st.session_state.history, meds_text)
    st.session_state.history.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<br><p style='text-align:center; color:gray;'>💙 Powered by Google Gemini</p>", unsafe_allow_html=True)
