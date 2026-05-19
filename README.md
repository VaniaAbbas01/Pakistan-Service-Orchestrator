# 🇵🇰 Pakistan Agentic AI Service Orchestrator

![Google Gemini](https://img.shields.io/badge/Powered_by-Google_Gemini-blue) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688) ![Flutter](https://img.shields.io/badge/Frontend-Flutter-02569B)

## 📌 Project Overview
The **Pakistan Service Orchestrator** is an end-to-end, agentic AI pipeline built to automate the informal economy (AC technicians, plumbers, electricians, tutors, beauticians) in Pakistan. It takes raw, natural language requests in **Urdu, Roman Urdu, or English**, understands the intent, discovers and ranks the best local providers, and simulates the booking process—culminating in a WhatsApp-style confirmation.

---

## 🚀 How Google Antigravity is used as the Core Orchestrator (25% Evaluation Core)
This project strictly adheres to the mandatory requirement of using Google's **Antigravity Framework** as the central nervous system. Rather than just making simple API calls, the system is designed around **Agentic Workflows**:
- **Skill Execution (`skills/intent_parser.py`):** Antigravity orchestrates the extraction of structured intents from messy, multilingual user inputs. It manages the multi-step reasoning required to resolve relative times (e.g., *"kal subah"*) into strict `YYYY-MM-DD HH:MM` formats based on the local system time.
- **Workflow Orchestration (`workflows/provider_discovery.py`):** Antigravity serves as the core platform to orchestrate the provider ranking. It actively integrates tools (fetching coordinates from the Google Maps API) and pairs it with Gemini's reasoning layer to explain *why* a provider was selected.
- **Action Execution & Simulation:** Once a decision is made, the workflow simulates the final action (booking and notifying), proving full end-to-end autonomy from Planning → Decision → Action.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Frontend
        F[Flutter Mobile App]
    end

    subgraph Backend API (FastAPI)
        API[main.py: /api/orchestrate]
    end

    subgraph Core Orchestration (Antigravity Pipeline)
        A[skills/intent_parser.py]
        B[workflows/provider_discovery.py]
        C[workflows/booking_simulation.py]
    end

    subgraph External APIs
        G[Google Gemini API]
        M[Google Maps Distance Matrix]
    end

    F -- "POST JSON Request" --> API
    API --> A
    A -- "Extract Intent" --> G
    A --> B
    B -- "Get Distances" --> M
    B -- "Generate Reasoning" --> G
    B --> C
    C -- "Save to mock DB\nGenerate WhatsApp Msg" --> API
    API -- "Return JSON Response" --> F
```

---

## ✨ Key Features
1. **Multilingual Intent:** Native support for English, Urdu (اردو), and Roman Urdu.
2. **Real-world Geography:** Uses Google Maps API for true driving distances in Islamabad/Rawalpindi. Safely falls back to straight-line Haversine math if the API key is missing.
3. **Advanced Scoring (40/30/30):** Ranks providers deterministically based on Distance (40%), Rating (30%), and Reliability/Availability (30%).
4. **Agentic Reasoning:** Provides human-readable explanations for why specific tradesmen are recommended.
5. **Full-Stack Implementation:** Includes a FastAPI REST backend and a modern Flutter mobile interface.

---

## 💻 How to Run

### 1. Set Environment Variables (Optional but Recommended)
For the full experience, export your API keys:
```powershell
$env:GEMINI_API_KEY="your_gemini_key"
$env:GOOGLE_MAPS_API_KEY="your_maps_key" # Optional
```

### 2. Run the Backend API (FastAPI)
Install the dependencies and start the Uvicorn server:
```powershell
pip install fastapi uvicorn pydantic google-genai googlemaps
python main.py
```
*The API will run on `http://127.0.0.1:8000`.*

### 3. Run the CLI Test
If you just want to test the orchestration via the command line:
```powershell
python orchestrate_service_request.py --test
```

### 4. Run the Flutter Mobile App
In a new terminal window:
```powershell
cd mobile_app
flutter pub get
flutter run
```

---

## 📝 Sample Console Output (CLI)

```text
Step 1: Intent Understanding
────────────────────────────
[Skill: Intent Parser] 🧠 Analyzing request...
  ➜ Input: 'Mujhe kal subah G-13 mein AC technician chahiye'

Step 2: Provider Discovery & Ranking
────────────────────────────────────
[Workflow: Provider Discovery] 🔎 Searching & Scoring Providers...
  ➜ Found 4 candidates for 'AC Technician'
  📍 Parsed Location 'G-13' to Coords: 33.6938, 73.0651
  🌍 Using Google Maps API for accurate road distance...
  ➜ Scored and Ranked Top 3 (Formula: 40% Dist, 30% Rating, 30% Avail):
     #1: Ustad Rafiq Ahmed (Score: 9.55/10) - 2.1 km, 4.7⭐
  ➜ 🧠 Generating natural language reasoning via LLM...

Step 3: Booking Simulation & Confirmation
─────────────────────────────────────────
  [State Change] Moving top provider to Booking Phase...

[Workflow: Booking Simulation] 📅 Checking availability and booking slot...
  ✅ Provider is available!
  ➜ Slot booked successfully! Booking ID: PK-63C36AAD
  🔔 Reminder scheduled for: 2026-05-17 08:00 (1 hour before)

  📲 WhatsApp Confirmation Generated:
  ──────────────────────────────────────────────────
  | 🟢 *BOOKING CONFIRMED - Service Orchestrator* 🟢
  | Asalam-o-Alaikum Ali Raza! Aap ki service request successfully book ho gayi hai. 🛠️
  | 
  | 🧾 *Booking Details*
  | ▪️ *Booking ID:* PK-63C36AAD
  | ▪️ *Service:* AC Technician (general repair)
  | ▪️ *Assigned Professional:* Ustad Rafiq Ahmed
  | ▪️ *Contact:* +92-333-1234567
  | ▪️ *Scheduled Time:* 2026-05-17 09:00
  | ▪️ *Estimated Cost:* PKR 1500 - 5000
  | 
  | 💡 *Agentic Decision Logic:* 
  | Inko 3 wajoohaat ki bina par select kiya gaya hai: 1) Wo aap ki location se siraf 2.1 km door hain. 2) Inki rating 4.7⭐ hai jo area mein behtareen hai. 3) Aap ke matlooba waqt par dastiyaab (available) hain.
  | 
  | ⏳ *Next Steps:*
  | Aap ke provider jaldi aapse raabta karenge. Service se 1 ghanta pehle aap ko automatic reminder bhi mil jayega.
  | 
  | Pakistan Service Orchestrator use karne ka shukriya! 🇵🇰
  ──────────────────────────────────────────────────
```

---

## ⚠️ Assumptions & Limitations
- **Mock Database:** `data/providers.json` is a static file representing a mock database. In production, this would be a Postgres or MongoDB instance with geospatial querying (like PostGIS).
- **Booking State:** Bookings are held in memory (`_BOOKINGS` dict) and do not persist across server restarts.
- **Static Availability:** The booking simulator assumes the top-ranked provider is always available for the requested slot.

---

## 🔮 Future Improvements
- **Real-time Notifications:** Replace simulated WhatsApp logging with actual Twilio/Vonage API integrations to send SMS or WhatsApp messages to users.
- **Provider App Loop:** Create a provider-facing interface where technicians can accept/reject requests, updating the state in real-time.
- **Voice Input:** Integrate Google Speech-to-Text to allow users in Pakistan to send voice notes instead of typing.
