# Smart Healthcare Navigator (Symptom Checker & AI Clinical Bridge)

> **A privacy-first, empathetic AI healthcare assistant with retrieval-grounded symptom reasoning, strict confidence thresholding, autonomous appointment booking, multi-agent clinical handoffs, and multimodal lab report analysis.**

---

## 🌟 Overview & Key Principles

A common issue in digital health chatbots is either being **too rigid** (yes/no menus) or **too dangerous** (hallucinating clinical diagnoses). When people feel sick and search their symptoms online, they often face worst-case-scenario panic. 

**Smart Healthcare Navigator** solves this problem by adhering to the core principle:
> **"RAG doesn't mean 'answer everything.' It means: Answer when reliable knowledge can be retrieved; otherwise, say that the knowledge base does not contain enough information."**

---

## 🧭 System Flowchart & Recommended Behavior

```
                        User Question
                             │
                     Intent Classifier
                             │
     ┌───────────────────────┼────────────────────────┐
     ▼                       ▼                        ▼
Healthcare Symptom     Appointment / Nav         Unrelated Topic
     │                       │                        │
Search Medical RAG     Mock Hospital API        Politely Decline
     │                       │                        │
Similarity Score             │                        │
     │                       │                        │
Is Score >= Threshold?       │                        │
     ├── YES ──┐             │                        │
     ▼         ▼             ▼                        ▼
 Grounded   Safe        Directory Lookup &      "I am an AI health
 Answer +   Fallback    Real-Time Slot Booking   assistant and cannot
 Sources    Message                              assist with non-health
 (No Guess) (Don't Guess)                        queries."
```

### The 7 Mandatory Code-Enforced Safety Rules
1. **Use only the provided retrieved medical context.**
2. **Do not invent medical facts or ailments.**
3. **Do not diagnose the user** (never say *"You have X"*; say *"Possible common ailments associated with these symptoms include..."*).
4. **Do not prescribe medication** (no prescription drugs, dosages, or regimens).
5. **If the context lacks sufficient information, clearly state that the information is unavailable.**
6. **Do not use general knowledge to fill in missing information.**
7. **Encourage professional medical consultation** and consistently attach standard safety disclaimers.

---

## 🏆 Project Challenge Difficulty Levels (All 4 Implemented)

| Level | Capability | Implementation in this Project |
| :--- | :--- | :--- |
| **Level 1: Basic Agency** | RAG over verified medical documents, suggests 3 possible ailments, advises seeing a doctor. | TF-IDF + Cosine similarity vector search over 6 verified clinical guides (CDC/WHO/NHS), retrieval threshold gating (`0.15`), and extractive synthesis. |
| **Level 2: Tool Integration** | Identifies specialist domain, queries mock hospital API, finds nearest available slot, and books appointment. | `MockHospitalAPI` featuring real-world specialty matching (Dermatologist, Pulmonologist, etc.), interactive calendar slot booking, and confirmed ticket generation (`APT-...`). |
| **Level 3: Multi-Agent Collaboration** | Patient Intake Agent chats with patient, passes structured summary to Doctor-Facing Agent to save 15 minutes of chart review. | `PatientIntakeAgent` extracts duration, severity scale (1-10), and complaints; `DoctorFacingAgent` outputs a formal clinical SOAP Note + FHIR-compliant machine-usable JSON. |
| **Level 4: Advanced / Multimodal** | Ingests PDF blood test (CBC panel), reads biomarkers via PDF parser, identifies low iron, explains in 8th-grade language, and suggests dietary adjustments. | `LabReportAnalyzer` extracts Hemoglobin, Ferritin, Serum Iron, RBC, MCV, WBC, Platelets; flags low iron; delivers plain-English *"oxygen delivery trucks"* analogy and evidence-based nutrition tips. |

---

## 📁 Repository Structure

```
Smart_healtcare_Navigator/
├── medical_knowledge/              # Verified medical reference markdown corpus
│   ├── fever_and_infections.md     # CDC/NHS fever & acute viral pathways
│   ├── respiratory_and_cough.md    # WHO/AAFP respiratory & cough guidelines
│   ├── gastrointestinal_and_stomach.md # NIDDK digestive & abdominal guidelines
│   ├── dermatology_and_rash.md     # AAD/BAD cutaneous & rash guidelines
│   ├── headaches_and_neurology.md  # IHS/NINDS headache & cranial protocols
│   └── fatigue_and_deficiencies.md # NIH/WHO fatigue, anemia, & biomarker reference
├── core/                           # Core intelligence and agent engines
│   ├── rag_engine.py               # Vector search & similarity threshold gating
│   ├── intent_classifier.py        # Intent classification & out-of-domain router
│   ├── llm_provider.py             # Grounded generator (Local offline + Gemini + OpenAI)
│   ├── hospital_api.py             # Mock Hospital API & booking service (Level 2)
│   ├── intake_and_doctor_agent.py  # Patient Intake & Doctor SOAP/FHIR agents (Level 3)
│   └── lab_report_analyzer.py      # CBC blood report parser & low iron explainer (Level 4)
├── static/                         # Modern responsive web frontend
│   ├── index.html                  # Multi-tab SPA (Chat, Inspector, Booking, SOAP, Lab)
│   ├── style.css                   # Glassmorphism, animations, and custom scrollbars
│   └── app.js                      # Client state, API interactions, and live RAG meter
├── sample_reports/                 # Sample clinical PDF blood reports for testing
│   ├── patient_cbc_iron_deficiency.pdf
│   └── patient_cbc_normal.pdf
├── scripts/                        # Utility scripts
│   └── generate_sample_reports.py  # Generates clinical CBC test PDFs
├── tests/                          # Automated integration test suite
│   ├── test_rag_threshold.py       # Validates confidence threshold gating
│   ├── test_intent_classifier.py   # Validates intent routing & out-of-domain rejection
│   ├── test_grounded_generation.py # Validates 3-ailment extraction & fallback
│   ├── test_hospital_booking.py    # Validates Level 2 specialist booking
│   ├── test_multiagent_handoff.py  # Validates Level 3 SOAP & FHIR handoff
│   ├── test_lab_analyzer.py        # Validates Level 4 PDF extraction & low iron detection
│   └── test_api_endpoints.py       # Full end-to-end FastAPI test suite
├── server.py                       # FastAPI application entrypoint
└── README.md                       # Comprehensive system documentation
```

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ (tested on Python 3.14)
- Packages already installed in this environment: `fastapi`, `uvicorn`, `scikit-learn`, `pypdf`, `reportlab`

### 2. Run the Server
Launch the server from the project directory:
```bash
python server.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Testing the 5 Key Project Demonstration Scenarios

### Scenario 1: Information Exists in Verified Corpus (In-Corpus Grounding)
- **User Input**: `"What are common symptoms associated with fever?"`
- **System Behavior**:
  - Intent Classifier: `HEALTHCARE_SYMPTOM` -> Routes to `MEDICAL_RAG`
  - Cosine Similarity Score: **~0.21** (Exceeds threshold `0.15`)
  - Grounded Output: Explains fever physiology, highlights **3 possible common ailments** (*Acute Viral Upper Respiratory Infection, Influenza, Gastroenteritis*), cites verified sources (*CDC & NHS Guidelines*), and includes non-diagnostic disclaimer.

### Scenario 2: Information Does NOT Exist (Strict Retrieval Fallback)
- **User Input**: `"What are the symptoms of a rare neurological disorder?"`
- **System Behavior**:
  - Intent Classifier: `HEALTHCARE_SYMPTOM` -> Routes to `MEDICAL_RAG`
  - Cosine Similarity Score: **~0.11** (Fails threshold `0.15`)
  - Grounded Output: **DOES NOT ASK THE LLM TO GUESS FROM MEMORY**.
  - Safe Fallback Response:
    > *"I don't have enough verified information in my medical knowledge base to answer that question reliably. I don't want to guess or provide potentially unsafe medical information. Please consult a qualified healthcare professional or use a verified medical source."*

### Scenario 3: Completely Unrelated Query (Out-of-Domain Filter)
- **User Input**: `"Who is the Prime Minister of India?"` or `"Write a Python program"`
- **System Behavior**:
  - Intent Classifier: `UNRELATED` -> Routes to `REJECT`
  - **Does not search medical vector database**.
  - Polite Decline:
    > *"I am the Smart Healthcare Navigator, an AI assistant dedicated exclusively to health inquiries, symptom guidance, and medical appointment booking. I cannot assist with general topics, coding, politics, or non-healthcare questions."*

### Scenario 4: Autonomous Hospital Appointment Booking (Level 2)
- **User Input**: `"Find me a dermatologist for a dry skin rash"`
- **System Behavior**:
  - Intent Classifier: `APPOINTMENT_NAVIGATION` -> Specialty: `Dermatologist`
  - Hospital API queries available providers and shows doctor cards with slots (*Dr. Aisha Patel, MD*).
  - Clicking **"Book Visit"** opens the modal and generates a confirmed ticket with code `APT-20260926-XXXXXX`.

### Scenario 5: Multimodal Blood Test Analysis & Low Iron (Level 4)
- **Action**: Open the **Lab Report Analyzer** tab and click **"Load Sample Low-Iron CBC"** (or upload `sample_reports/patient_cbc_iron_deficiency.pdf`).
- **System Behavior**:
  - Parses 8 biomarkers: Hemoglobin (9.8 g/dL), Serum Iron (36 mcg/dL), Ferritin (12 ng/mL), Hematocrit (31.2%), RBC, MCV, WBC, Platelets.
  - Flags low iron and translates into plain 8th-grade language using the *"oxygen delivery trucks"* analogy.
  - Suggests evidence-based nutrition tips (spinach, lentils, vitamin C absorption pairing) and links to a Hematologist.

---

## 📊 Running Automated Tests

Run the complete test suite at any time:
```bash
python tests/test_api_endpoints.py
```
Expected output:
```
============================================================
RUNNING END-TO-END TEST SUITE FOR SMART HEALTHCARE NAVIGATOR
============================================================
[PASS] Test 1: Chat Symptom In-Corpus passed
[PASS] Test 2: Out-of-Corpus Fallback passed
[PASS] Test 3: Unrelated Rejection passed
[PASS] Test 4: Appointment Navigation passed
[PASS] Test 5: Specialist Directory & Booking passed
[PASS] Test 6: Multi-Agent Clinical Handoff passed
[PASS] Test 7: Sample Lab Report Analyzer passed
============================================================
ALL 7 END-TO-END TESTS PASSED SUCCESSFULLY!
============================================================
```

---

## 🔒 Privacy & Safety Compliance

- **Zero-Storage Privacy**: Patient messages and uploaded PDF files are processed in ephemeral memory.
- **Configurable LLM Backend**: Default operates 100% offline via `LocalGroundedGenerator` with zero telemetry and zero external API calls. Gemini and OpenAI backends can be activated optionally in the Settings tab.
- **Non-Diagnostic Stance**: Every response includes an explicit medical disclaimer stating that the system provides educational information grounded in reference protocols, not clinical diagnoses or prescriptions.
#   S m a r t _ H e a l t h c a r e _ N a v i g a t o r  
 