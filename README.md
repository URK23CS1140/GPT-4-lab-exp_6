# AI-Powered Medical Symptom Assistant using GPT-4

> **Academic Course / Lab:** 24CS2506 – Building Applications using GPT-4  
> **Experiment Number:** Experiment 6 (Medical Symptom Assistant)  
> **Registration Number Reference:** URK23CS1197 / Lab Record Reference

---

## 1. Project Title
**AI-Powered Medical Symptom Assistant using GPT-4**

## 2. Objective
To design and develop an educational, AI-powered medical symptom assistant using GPT-4 (with resilient fallback to local Ollama and a deterministic clinical rule engine). The application collects user-reported symptoms in natural conversational language along with clinical context (age, biological sex, duration, severity, medical history, medications, allergies, and observations), parses and analyzes the symptoms, identifies candidate conditions with clinical reasoning, generates targeted follow-up clarifying questions, performs a triage and emergency red-flag risk assessment, and presents structured findings with medical safety disclaimers.

---

## 3. Key Features
- **Conversational Free-Text Input:** Patients describe chief complaints freely without rigid checkboxes or dropdown forms.
- **Natural Language Symptom Extraction:** Discrete clinical signs (e.g., *Fever*, *Cough*, *Sore throat*, *Headache*, *Fatigue*) are extracted and standardized.
- **Context-Aware Acuity Analysis:** Categorizes onset timeline into *Acute*, *Subacute*, or *Chronic*, and monitors comorbidity risk factors (e.g., Asthma, Diabetes, Hypertension).
- **Multi-Tiered LLM Provider Architecture:**
  - **OpenAI GPT-4 / GPT-4o / GPT-4o-mini:** Utilized when an API key is provided in `.env`.
  - **Ollama Local LLM (Llama 3 / Mistral):** Automatic local inference fallback when Ollama is active.
  - **Clinical Diagnostic Rule Engine:** High-fidelity offline fallback ensuring 100% operational reliability without external dependencies or paid API keys.
- **Emergency Red-Flag Detection:** Proactively screens for life-threatening complaints (e.g., chest pain radiating to arm/jaw, acute respiratory distress, stroke signs, syncope) and triggers emergency triage alerts.
- **Safety Guardrails & Triage:** Categorizes cases into `LOW`, `MODERATE`, `HIGH`, or `EMERGENCY` with actionable medical attention advice.
- **Quick View Presets:** One-click sample loaders for *Respiratory (Lab Example)*, *Tension & Migraine*, and *Emergency Red Flag*.
- **Report Persistence:** Automatically saves each completed clinical analysis to disk in both timestamped `.json` and formatted `.txt` files in `/reports/`.
- **Export & Utility Tools:** One-click copy to clipboard, `.txt` download, `.json` export, and print formatting.

---

## 4. System Architecture

```
                       ┌───────────────────────────────┐
                       │          User Input           │
                       │ (Natural Language & Context)  │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │     Patient Profile Intake    │
                       │ (Age, Sex, Demographic Group) │
                       └──────────────┬────────────────┘
                                      │
                       ┌──────────────┴───────────────┐
                       ▼                              ▼
        ┌────────────────────────────┐  ┌────────────────────────────┐
        │     Symptom Extraction     │  │      Context Analysis      │
        │ (Discrete Clinical Signs)  │  │(Acuity, Comorbidities, Meds│
        └──────────────┬─────────────┘  └─────────────┬──────────────┘
                       └──────────────┬───────────────┘
                                      ▼
                       ┌───────────────────────────────┐
                       │  Prompt Generation & Safety   │
                       │  (Guardrails, Strict Schema)  │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │    LLM Inference Engine       │
                       │ ┌───────────────────────────┐ │
                       │ │ OpenAI GPT-4 / GPT-4o-mini│ │
                       │ ├───────────────────────────┤ │
                       │ │ Ollama Local LLM (Llama3) │ │
                       │ ├───────────────────────────┤ │
                       │ │ Clinical Diagnostic Engine│ │
                       │ └───────────────────────────┘ │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │  Clinical Reasoning & Triage  │
                       │ ┌───────────────────────────┐ │
                       │ │ Candidate Conditions      │ │
                       │ │ Follow-up Clarifications  │ │
                       │ │ Red Flag / Triage Level   │ │
                       │ └───────────────────────────┘ │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │ Structured Response & Report  │
                       │  • UI Dashboard Display       │
                       │  • Timestamped .txt & .json   │
                       └───────────────────────────────┘
```

---

## 5. Module Architecture & Responsibilities

| Module | Location | Responsibility |
| :--- | :--- | :--- |
| **Input Module** | `modules/input_module.py` | Collects unstructured free-text symptom descriptions and form fields from web interface; sanitizes and normalizes values. |
| **Profile Module** | `modules/profile_module.py` | Validates age constraints ($0 \le \text{age} \le 125$), validates biological sex, and categorizes demographic group (*Pediatric*, *Adult*, *Geriatric*). |
| **Symptom Module** | `modules/symptom_module.py` | Parses natural language to isolate discrete medical symptoms and signs using clinical keyword dictionaries and heuristic grammar parsing. |
| **Context Module** | `modules/context_module.py` | Evaluates duration acuity (*Acute*, *Subacute*, *Chronic*), severity scale, chronic comorbidities (e.g. Asthma, Diabetes), medications, and known allergies. |
| **Prompt Module** | `modules/prompt_module.py` | Formulates clinical system and user prompts embedding strict safety instructions, medical uncertainty phrasing, and rigid JSON schema specifications. |
| **Analysis Module** | `modules/analysis_module.py` | Dispatches prompts to OpenAI GPT-4 or local Ollama; provides automatic fallback to the deterministic Clinical Diagnostic Rule Engine if external APIs are unavailable; cleans and validates JSON response. |
| **Question Module** | `modules/question_module.py` | Generates targeted clinical follow-up clarifying questions to collect missing diagnostic parameters based on affected symptom domains. |
| **Safety Module** | `modules/safety_module.py` | Scans for emergency red flags (e.g. chest pain with radiation, stroke indicators, acute dyspnea), assigns triage severity, and enforces mandatory safety disclaimers. |
| **Save Module** | `modules/save_module.py` | Persists formatted clinical analysis records to disk in `/reports/` as timestamped `.txt` and `.json` documents. |
| **Main Module** | `app.py` | Coordinates Flask web server startup, registers REST API endpoints (`/`, `/analyze`, `/api/status`, `/save-report`, `/reports/<filename>`), and serves the UI. |

---

## 6. Technologies Used
- **Python:** 3.11+ (Tested on Python 3.11, 3.12, 3.14)
- **Flask:** Web framework and REST API routing
- **Requests:** HTTP client for cloud and local LLM endpoints
- **Pandas:** Data structures and tabular reporting support
- **HTML5 / CSS3 / JavaScript (Vanilla ES6):** Modern, responsive, high-fidelity clinical dashboard UI with no heavy third-party CSS bloat
- **Ollama / Local LLM:** Local privacy-first model support (e.g. `llama3`, `mistral`)
- **OpenAI API:** GPT-4 / GPT-4o-mini compatibility

---

## 7. Installation & Setup Instructions

### Step 1: Clone or Open the Project
Open a terminal in the project directory:
```bash
cd "AI-Powered-Medical-Symptom-Assistant"
```

### Step 2: Create a Python Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
- **On macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **On Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 8. Configuration (`.env`)

The application includes an `.env.example` file. Copy it to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your preferred engine:

```ini
# LLM Provider Preference: 'openai', 'ollama', 'auto', or 'fallback'
LLM_PROVIDER=auto

# Option A: OpenAI GPT-4 (Optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Option B: Ollama Local LLM (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Server Settings
PORT=5000
HOST=127.0.0.1
FLASK_DEBUG=True
SECRET_KEY=medical_symptom_assistant_lab6_secret
```

> **Note on Zero-Configuration Fallback:** If you do not have an OpenAI API key or Ollama running, the application **automatically uses the built-in Clinical Diagnostic Rule Engine**. You can run and evaluate the application immediately without signing up for any API keys.

---

## 9. Setting Up Ollama (Optional Local LLM)
If you wish to use a free local LLM on your machine:
1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Pull the desired model:
   ```bash
   ollama pull llama3
   ```
3. Verify that the Ollama service is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
4. Set `LLM_PROVIDER=ollama` in your `.env`.

---

## 10. Running the Application

With your virtual environment activated, run:
```bash
python3 app.py
```

You will see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 11. Running Automated Tests

Run the comprehensive unit test suite:
```bash
python3 -m unittest tests/test_modules.py
```

All 11 unit tests covering validation, extraction, triage, JSON schema, file persistence, and REST endpoints will run and verify module behavior.

---

## 12. How to Use the Application

1. **Header Status:** The live status pill in the top right confirms whether the app is connected to GPT-4, Ollama, or the active Clinical Diagnostic Rule Engine.
2. **Quick View Presets:** Click one of the top preset buttons to instantly populate the form:
   - `📋 Respiratory (Lab Example)`: The standard benchmark case (Age 22, fever, cough, sore throat, 2 days).
   - `⚡ Tension & Migraine`: Neurological headache case with light sensitivity.
   - `🚨 Emergency Red Flag`: Cardiac chest pain emergency demonstration.
   - `🗑️ Clear`: Reset all fields.
3. **Analyze:** Click `✨ Analyze Symptoms with GPT-4`.
4. **Review Results:** The right-hand panel renders:
   - **Triage Level Alert:** `LOW` (Green), `MODERATE` (Yellow), `HIGH` (Orange), or `EMERGENCY` (Red).
   - **Reported Symptoms:** Discrete list of extracted clinical entities.
   - **Possible Conditions:** Ranked differential possibilities with clinical rationales.
   - **Why These Were Considered:** Explanatory clinical synthesis.
   - **Additional Information Needed:** Diagnostic tests and measurements recommended.
   - **Follow-up Questions:** Clarifying questions for patient history.
   - **Medical Attention Advice:** Actionable guidance on when/where to seek professional care.
   - **Safety Disclaimer:** Prominent informational disclaimer.
5. **Report Export:**
   - Click `📋 Copy` to copy the formatted clinical summary.
   - Click `📄 TXT` or `💾 JSON` to download the persistent report from `/reports/`.
   - Click `🖨️ Print` to trigger a clean printable clinical summary.

---

## 13. Reports Storage
All reports generated during sessions are automatically archived in:
```
reports/
  ├── medical_report_YYYY-MM-DD_HH-MM-SS_<id>.json
  └── medical_report_YYYY-MM-DD_HH-MM-SS_<id>.txt
```

---

## 14. Medical Safety & Disclaimer
> [!IMPORTANT]
> **Educational Laboratory Project Only:**
> This application is strictly an educational university laboratory project (Experiment 6 / 24CS2506) created to explore AI workflow design and prompt engineering using LLMs.
> 
> - **NOT A MEDICAL DEVICE:** This system is NOT certified, evaluated, or approved as a medical device or diagnostic tool.
> - **NO MEDICAL DIAGNOSIS:** This application does not diagnose illness, prescribe medication, or formulate treatment plans.
> - **EMERGENCIES:** In any acute, life-threatening, or severe medical situation, users must immediately contact emergency services (e.g., 911 / 112) or seek in-person evaluation from licensed physicians.

---

## 15. Troubleshooting

- **Port 5000 Already in Use:**  
  Change `PORT=5001` in `.env` or run:
  ```bash
  PORT=5001 python3 app.py
  ```
- **OpenAI Key Not Recognized:**  
  Ensure there are no extra spaces or quotation marks in `OPENAI_API_KEY=` within `.env`. If invalid, the system automatically falls back to the clinical rule engine without crashing.
- **Ollama Connection Refused:**  
  Make sure Ollama is launched (`ollama serve`). If Ollama is not active, the system falls back seamlessly to the clinical rule engine.
