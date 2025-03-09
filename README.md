# AI Digital Twin 🤖

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)

An intelligent meeting assistant that transforms calendar events into actionable insights using AI.

![Demo](https://via.placeholder.com/800x400.png?text=AI+Digital+Twin+Interface+Preview)

## 🌟 Key Features

- 📅 **Google Calendar Integration** - Automatically fetch upcoming meetings
- 🤖 **AI-Powered Summaries** - GPT-4 generated meeting briefs with key points
- 🔊 **Natural Voice Synthesis** - ElevenLabs text-to-speech conversion
- 🌐 **Timezone Aware** - Automatic IST conversion with fallback
- 🔒 **Secure Auth** - OAuth2 for Google, encrypted API keys
- 📊 **Interactive UI** - Streamlit dashboard with real-time updates

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/vrushabh-09/AI-Digital-Twin.git
cd AI-Digital-Twin

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
⚙️ Configuration
Create .env file in project root:

ini
Copy
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_11labs_key_here
GOOGLE_CREDENTIALS=credentials.json
TIMEZONE=Asia/Kolkata
Google API Setup:

Enable Calendar API

Create OAuth 2.0 credentials

Download credentials.json to project root

🚀 Usage
bash
Copy
streamlit run app.py
Access the interface at:
🌐 Local: http://localhost:8501
🌍 Network: http://<your-ip>:8501

📂 Project Structure
Copy
AI-Digital-Twin/
├── app.py                  # Main application logic
├── requirements.txt        # Dependency list
├── .env.template           # Environment configuration
├── services/
│   ├── google_calendar.py  # Calendar integration
│   └── ai_services.py      # AI processing core
└── assets/                 # Static resources
    └── demo.gif            # Usage demonstration
🤝 Contributing
🍴 Fork the repository

🌿 Create feature branch:
git checkout -b feature/amazing-feature

💾 Commit changes:
git commit -m 'Add amazing feature'

🚀 Push to branch:
git push origin feature/amazing-feature

🔀 Open a Pull Request

📜 License
Distributed under MIT License. See LICENSE for more information.

📬 Contact
Vrushabh Patil
📧 vrushabhpatil97711@gmail.com
🔗https://www.linkedin.com/in/patilvrushabh/
❤️Acknowledgments
Streamlit for UI components

OpenAI for GPT-4 integration

ElevenLabs for voice synthesis

⚠️ Important Note: This project is for educational purposes only. Never commit sensitive credentials to version control.
