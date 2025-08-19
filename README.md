🌍 Travel Assistant

An interactive AI-powered trip planning assistant that remembers your preferences across a session.
Built with FastAPI (backend) and a lightweight HTML/JS frontend, it integrates an LLM for recommendations and external APIs for country information.

✨ Features

💬 Conversational Interface — Chat naturally about destinations, packing, or day plans.

🧠 Session Memory — Assistant remembers your context (e.g., travel dates, origin, budget, interests).

🌐 Geo Lookup — Extracts locations from chat and fetches real-world data (via REST Countries API).

🔄 Reset Anytime — Clear memory with a single click.

⚡ FastAPI Backend — Simple, async, and easy to extend.

🎨 Minimal Frontend — Clean chat UI with sticky headers and bubbles.

<img width="722" height="736" alt="Travel-Assitant" src="https://github.com/user-attachments/assets/bfbe24d5-1e75-48b8-83de-3711870a0fd0" />

⚙️ Setup
1. Clone the repo
git clone https://github.com/yourusername/travel-assistant.git
cd travel-assistant

2. Install dependencies
pip install -r requirements.txt

3. Run backend
uvicorn main:app --reload --port 8000

4. Open frontend

Simply open index.html in your browser.
By default it connects to http://localhost:8000/chat.

🔌 API Endpoints

POST /chat → Send a user message, get LLM reply.

POST /reset → Clear memory for current session.

GET /memory?session_id=... → Inspect memory state.
