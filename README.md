💙 Care Companion

Care Companion is a Streamlit-based AI application designed to support elderly users with medication management, safety monitoring, and empathetic conversation, powered by Google Gemini.

🚀 Features

💬 Conversational AI Companion
Warm, empathetic chat experience designed for elderly users using Google Gemini.

💊 Medication Management

Add, view, and remove medications

Supports dosage, multiple daily times, and food requirements

Persistent storage using JSON files

🚨 Safety & Emergency Detection

Automatically detects emergency and urgent keywords (e.g., chest pain, falls, dizziness)

Provides immediate guidance to call emergency services or caregivers

📂 Multiple Chat Sessions

Save, load, switch, and delete conversation sessions

Persistent session history using local storage

📖 Interactive User Guide

Built-in guide explaining features and usage for non-technical users

🎯 Quick Action Buttons

One-click actions for common requests (medications, chatting, emergency help)

🧠 How It Works

Built with Streamlit for a clean, accessible UI

Uses Google Gemini (gemini-flash-latest) for natural language understanding and response generation

Stores medications and chat sessions locally using JSON files

Includes keyword-based safety detection for emergency escalation

🛠️ Tech Stack

Frontend / UI: Streamlit, HTML, CSS

AI / NLP: Google Generative AI (Gemini)

Backend Logic: Python

Data Storage: JSON (local persistence)

📁 Project Structure
care-companion/
├── app.py                  # Main Streamlit application
├── medications.json        # Medication data storage
├── chat_sessions.json      # Saved chat sessions
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies

⚙️ Setup & Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/care-companion.git
cd care-companion

2️⃣ Create a Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt




⚠️ Do not commit your API key to GitHub

▶️ Running the App
streamlit run app.py


Open your browser at:

http://localhost:8501

🔐 Safety & Disclaimer

Care Companion is not a medical device and does not replace professional medical care.
In emergencies, users should always contact 911 or a medical professional immediately.

📌 Future Improvements

SMS / push notification reminders

Caregiver dashboard

Cloud database (Firebase / PostgreSQL)

Voice input and text-to-speech support

HIPAA-compliant deployment

👨‍💻 Author

Asish Panda

LinkedIn: https://www.linkedin.com/in/asish-panda1/

GitHub: https://github.com/apanda26

⭐ Why This Project Matters

This project demonstrates:

Real-world full-stack development

AI integration with safety constraints

User-centered design for accessibility

Clean state management and persistence

Practical application of NLP in healthcare support
