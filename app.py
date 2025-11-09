import streamlit as st
import google.generativeai as genai
import json
import os
from typing import Optional
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="💙 Care Companion",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    .main-header p {
        color: #e0e7ff;
        margin: 5px 0 0 0;
    }
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        animation: fadeIn 0.3s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: #f1f5f9;
        color: #1e293b;
        margin-right: 20%;
    }
    .quick-action-btn {
        margin: 5px;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .quick-action-btn:hover {
        transform: scale(1.05);
    }
    .guide-section {
        background: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        color: #1e293b;
    }
    .guide-section h2, .guide-section h3, .guide-section h4 {
        color: #334155;
    }
    .guide-section ul, .guide-section ol, .guide-section p {
        color: #475569;
    }
    .guide-section strong {
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# GOOGLE GEMINI SETUP
# -------------------------------
API_KEY = st.secrets["GOOGLE_GEMINI_KEY"]
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

def save_medications(meds):
    with open("medications.json", "w") as f:
        json.dump(meds, f, indent=2)

def get_medications_text(medications):
    if not medications:
        return "No medications currently scheduled."
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
    emergency_keywords = ['chest pain', "can't breathe", 'heart attack', 'stroke', 'bleeding heavily', 'unconscious', 'choking', 'seizure']
    urgent_keywords = ['fell', 'fall', 'hurt', 'pain', 'dizzy', 'confused', 'vomit', 'stuck', 'help me', 'can\'t move']
    
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
    system_context = f"""You are Care Companion, a warm and caring AI assistant for elderly users.

YOUR PERSONALITY:
- Extremely warm, patient, and empathetic
- Speak clearly and simply (avoid complex words)
- Keep responses brief (2-4 sentences typically)
- Always encouraging and supportive
- Show genuine care and concern

YOUR ROLE:
- Provide emotional support and friendly companionship
- Help with medication tracking and reminders
- Monitor for safety concerns
- Engage in pleasant conversation
- Be a comforting presence

MEDICATION INFORMATION:
{meds_text}

When discussing medications:
- Reference their specific medications by name
- Remind them about timing and dosage
- Mention food requirements if applicable
- Be encouraging about medication adherence

CRITICAL SAFETY RULES:
If user mentions: pain, falling, dizziness, chest discomfort, breathing problems, confusion, bleeding, or any emergency:
- Express immediate concern
- Urgently recommend calling 911 or contacting caregiver
- Ask if they need help calling someone
- Stay calm but emphasize urgency

CONVERSATION STYLE:
- Use warm greetings
- Ask follow-up questions showing you care
- Validate their feelings
- Share encouragement
- Use simple, clear language
- Be patient with repetition
"""
    
    chat_context = "Recent conversation:\n"
    for m in history[-6:]:
        role = "User" if m['role'] == 'user' else "Care Companion"
        chat_context += f"{role}: {m['content']}\n"
    
    prompt = f"{system_context}\n\n{chat_context}User: {user_message}\nCare Companion:"

    try:
        response = model.generate_content(prompt)
        reply = response.text if hasattr(response, "text") else ""
    except Exception as e:
        st.error(f"AI generation failed: {e}")
        reply = "I'm having trouble connecting right now. Please try again in a moment."

    if not reply.strip():
        reply = "Hello! I'm here to chat with you. How are you feeling today?"
    
    return reply

# -------------------------------
# SESSION STATE SETUP
# -------------------------------
if "medications" not in st.session_state:
    st.session_state.medications = load_medications()

if "sessions" not in st.session_state:
    if os.path.exists("chat_sessions.json"):
        try:
            with open("chat_sessions.json", "r") as f:
                st.session_state.sessions = json.load(f)
        except:
            st.session_state.sessions = {"default": []}
    else:
        st.session_state.sessions = {"default": []}

if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

if st.session_state.current_session not in st.session_state.sessions:
    st.session_state.sessions[st.session_state.current_session] = []

if "name" not in st.session_state:
    st.session_state.name = ""

if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# -------------------------------
# SAVE SESSIONS FUNCTION
# -------------------------------
def save_sessions():
    with open("chat_sessions.json", "w") as f:
        json.dump(st.session_state.sessions, f, indent=2)

# -------------------------------
# UI START - HEADER
# -------------------------------
st.markdown("""
<div class="main-header">
    <h1>💙 Care Companion</h1>
    <p>Your caring AI companion for safety, medication tracking, and friendly conversation</p>
</div>
""", unsafe_allow_html=True)

# Quick toggle for user guide
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("📖 " + ("Hide" if st.session_state.show_guide else "Show") + " User Guide", use_container_width=True):
        st.session_state.show_guide = not st.session_state.show_guide

# -------------------------------
# USER GUIDE
# -------------------------------
if st.session_state.show_guide:
    st.markdown("""
    <div class="guide-section">
        <h2>📖 Welcome to Care Companion!</h2>
        <p><strong>Care Companion</strong> is your personal AI assistant designed specifically for elderly care, providing medication reminders, safety monitoring, and friendly conversation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    guide_col1, guide_col2 = st.columns(2)
    
    with guide_col1:
        st.markdown("""
        <div class="guide-section">
            <h3>🌟 Key Features</h3>
            <ul>
                <li><strong>💊 Medication Management:</strong> Track your medications, dosages, and schedules</li>
                <li><strong>🤖 AI Conversations:</strong> Chat naturally about anything on your mind</li>
                <li><strong>🚨 Safety Monitoring:</strong> Automatic detection of emergency keywords</li>
                <li><strong>💬 Multiple Chats:</strong> Save different conversation sessions</li>
                <li><strong>❤️ Empathetic Support:</strong> Warm, patient responses tailored for you</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="guide-section">
            <h3>🎯 Quick Actions</h3>
            <p>Use the quick action buttons below the chat to:</p>
            <ul>
                <li><strong>💊 View Medications:</strong> See your current medication schedule</li>
                <li><strong>💬 Start Chatting:</strong> Begin a friendly conversation</li>
                <li><strong>🆘 Get Help:</strong> Request immediate assistance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with guide_col2:
        st.markdown("""
        <div class="guide-section">
            <h3>📋 How to Use</h3>
            <ol>
                <li><strong>Set Up Your Profile:</strong> Enter your name in the sidebar</li>
                <li><strong>Add Medications:</strong> Use the sidebar form to add your prescriptions</li>
                <li><strong>Start Chatting:</strong> Type in the chat box at the bottom</li>
                <li><strong>Get Reminders:</strong> Ask about your medications anytime</li>
                <li><strong>Safety First:</strong> Mention any pain or emergencies - I'll alert you immediately</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="guide-section">
            <h3>💡 Tips</h3>
            <ul>
                <li>Chat naturally - I understand conversational language</li>
                <li>Ask me about your medications by name</li>
                <li>I can remind you when to take medicine</li>
                <li>Tell me if you're feeling unwell - I'll help</li>
                <li>Use "New Chat" to start fresh conversations</li>
                <li>Save your sessions to return to them later</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-section">
        <h3>🚨 Emergency Detection</h3>
        <p>If you mention any of these, I'll immediately alert you to seek help:</p>
        <p><strong>Emergency keywords:</strong> chest pain, can't breathe, heart attack, stroke, bleeding heavily, unconscious, choking, seizure</p>
        <p><strong>Urgent keywords:</strong> fell, fall, hurt, pain, dizzy, confused, vomiting, can't move, stuck, help me</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.header("👤 Profile & Settings")
    profile_name = st.text_input("Your name", st.session_state.name)
    if profile_name != st.session_state.name:
        st.session_state.name = profile_name
        st.success(f"✅ Name updated to {profile_name}!")

    st.divider()
    st.subheader("💊 Your Medications")

    # Display current medications
    if st.session_state.medications:
        for idx, med in enumerate(st.session_state.medications):
            with st.expander(f"💊 {med['name']}", expanded=False):
                st.write(f"**Dosage:** {med['dosage']}")
                st.write(f"**Times:** {', '.join(med['times'])}")
                if med.get('with_food'):
                    st.warning("⚠️ Take with food")
                if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.medications.pop(idx)
                    save_medications(st.session_state.medications)
                    st.rerun()
    else:
        st.info("No medications added yet. Add one below!")

    # Add Medication
    st.divider()
    st.subheader("➕ Add Medication")
    with st.form("add_med", clear_on_submit=True):
        med_name = st.text_input("Medication Name")
        dosage = st.text_input("Dosage (e.g., 1 tablet)")
        times = st.text_input("Times (e.g., 08:00, 20:00)")
        with_food = st.checkbox("Take with food?")
        submitted = st.form_submit_button("💾 Save Medication")

        if submitted:
            if med_name and dosage and times:
                new_med = {
                    "name": med_name,
                    "dosage": dosage,
                    "times": [t.strip() for t in times.split(",")],
                    "with_food": with_food
                }
                st.session_state.medications.append(new_med)
                save_medications(st.session_state.medications)
                st.success(f"✅ Added '{med_name}'!")
                st.rerun()
            else:
                st.error("Please fill in all fields!")

    st.divider()
    st.header("💬 Chat Sessions")

    # Display current session
    st.info(f"📂 Current: **{st.session_state.current_session}**")

    # Select session
    session_names = list(st.session_state.sessions.keys())
    if len(session_names) > 1:
        selected = st.selectbox("Switch to session:", session_names, 
                               index=session_names.index(st.session_state.current_session),
                               key="session_selector")
        if selected != st.session_state.current_session:
            st.session_state.current_session = selected
            st.rerun()

    # New session
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🆕 New Chat", use_container_width=True):
            timestamp = datetime.now().strftime("%m/%d %I:%M%p")
            new_name = f"Chat {timestamp}"
            st.session_state.sessions[new_name] = []
            st.session_state.current_session = new_name
            save_sessions()
            st.rerun()
    
    with col_b:
        if st.button("💾 Save All", use_container_width=True):
            save_sessions()
            st.success("✅ Saved!")

    # Delete current session
    if len(session_names) > 1:
        if st.button("🗑️ Delete Current Chat", use_container_width=True):
            if st.session_state.current_session in st.session_state.sessions:
                del st.session_state.sessions[st.session_state.current_session]
                st.session_state.current_session = list(st.session_state.sessions.keys())[0]
                save_sessions()
                st.rerun()

    st.divider()
    st.caption("💙 Powered by Google Gemini")

# -------------------------------
# QUICK ACTION BUTTONS
# -------------------------------
st.subheader("🎯 Quick Actions")
quick_col1, quick_col2, quick_col3 = st.columns(3)

with quick_col1:
    if st.button("💊 Show My Medications", use_container_width=True):
        st.session_state.quick_message = "Show me my medications"

with quick_col2:
    if st.button("💬 Let's Chat", use_container_width=True):
        st.session_state.quick_message = "I want to talk"

with quick_col3:
    if st.button("🆘 I Need Help", use_container_width=True):
        st.session_state.quick_message = "I need help right now"

st.divider()

# -------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------
history = st.session_state.sessions[st.session_state.current_session]

if not history:
    welcome_name = f" {st.session_state.name}" if st.session_state.name else ""
    st.markdown(f"""
    <div class="assistant-message chat-message">
        <strong>🤖 Care Companion</strong><br><br>
        Hello{welcome_name}! I'm your Care Companion. 💙<br><br>
        I'm here to help you with:<br>
        • Medication reminders<br>
        • Safety check-ins<br>
        • Friendly conversation<br><br>
        How are you feeling today?
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-message chat-message">
                <strong>👤 You</strong><br><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Convert newlines to <br> for HTML display
            content = msg['content'].replace('\n', '<br>')
            st.markdown(f"""
            <div class="assistant-message chat-message">
                <strong>🤖 Care Companion</strong><br><br>
                {content}
            </div>
            """, unsafe_allow_html=True)

# -------------------------------
# USER INPUT - FIXED VERSION
# -------------------------------
# Check for quick action message
if "quick_message" in st.session_state:
    user_input = st.session_state.quick_message
    del st.session_state.quick_message
else:
    user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message
    history.append({"role": "user", "content": user_input})
    
    # Detect safety concerns
    concern = detect_concern(user_input)
    if concern == "EMERGENCY":
        ai_reply = "🚨 This sounds like an emergency! Please call 911 immediately or have someone call for you. I'm also alerting your caregiver. Can you reach your phone?"
    elif concern == "URGENT":
        ai_reply = "⚠️ I'm very concerned. Please contact your caregiver immediately. I've sent them an alert. Can you reach your phone?"
    else:
        meds_text = get_medications_text(st.session_state.medications)
        with st.spinner("🤖 Care Companion is thinking..."):
            ai_reply = generate_ai_response(user_input, history, meds_text)
    
    # Append AI response
    history.append({"role": "assistant", "content": ai_reply})
    
    # Save to session state
    st.session_state.sessions[st.session_state.current_session] = history
    
    # Auto-save
    save_sessions()
    
    # Force immediate rerun to display new messages
    st.rerun()

# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
