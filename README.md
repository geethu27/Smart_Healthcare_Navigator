# 🏥 SMART HEALTHCARE NAVIGATOR

### *Privacy-First AI Symptom Checker & Clinical Bridge*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![RAG](https://img.shields.io/badge/Architecture-RAG%20Grounded-00ff88.svg)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM%20Ready-black.svg?logo=ollama\&logoColor=white)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview

**Smart Healthcare Navigator** is a privacy-first AI healthcare web application designed to help users understand common symptoms, analyze selected laboratory reports, and prepare information for a healthcare professional.

The application uses a **Retrieval-Augmented Generation (RAG)** approach to ground AI responses in a controlled medical knowledge base rather than relying only on the model's internal knowledge.

The system is designed around an important principle:

> **AI should assist healthcare navigation, not replace qualified healthcare professionals.**

Instead of making unsupported medical guesses, the system retrieves relevant information from its configured medical knowledge base and provides safety-focused responses when sufficient information is unavailable.

---

## 🎯 Problem Statement

People commonly search their symptoms online and may receive:

* Unverified medical information
* Overly broad or alarming possibilities
* Conflicting recommendations
* Difficult medical terminology
* No clear guidance about the appropriate healthcare specialist

Generic AI systems can also generate information that sounds convincing but is not grounded in reliable sources.

**Smart Healthcare Navigator** addresses these challenges through:

* Grounded retrieval
* Controlled AI generation
* Medical terminology expansion
* Safety-oriented responses
* Specialist recommendations
* Appointment workflow
* Clinical handoff generation
* Laboratory report analysis

---

## 💡 Solution

The application combines **RAG, AI models, document processing, and healthcare workflows** into one platform.

### Core principle

```text
User Input
    ↓
Symptom / Document Processing
    ↓
Medical Knowledge Retrieval
    ↓
Relevant Context
    ↓
AI Reasoning / Response Generation
    ↓
Safety Validation
    ↓
User-Friendly Healthcare Guidance
```

If sufficient information cannot be retrieved from the configured knowledge base, the system can provide a safe fallback rather than inventing unsupported medical information.

---

# 🤖 Supported AI Models

The application supports a **hybrid multi-model architecture**.

| AI Model / Mode           | Execution | Key Highlights                                                      |
| ------------------------- | --------- | ------------------------------------------------------------------- |
| **Local Grounded Engine** | Local     | Offline operation, controlled knowledge retrieval                   |
| **Ollama Local LLMs**     | Local     | Local inference with models such as `llama3`, `mistral`, and `phi3` |
| **Google Gemini**         | Cloud     | Cloud-based AI reasoning                                            |
| **OpenAI**                | Cloud     | Cloud-based LLM generation                                          |

### 🔐 Privacy Modes

The application provides local AI options for users who want to keep healthcare-related information on their own machine.

For cloud-based models, users should understand that information is processed according to the selected provider's services, configuration, and applicable policies.

> **Important:** Cloud execution should not be described as completely private or HIPAA-compliant unless the specific deployment, provider agreement, configuration, and regulatory requirements have been independently verified.

---

# 🧠 RAG Architecture

The application's primary AI architecture is based on **Retrieval-Augmented Generation (RAG)**.

### RAG Pipeline

```text
                  ┌──────────────────┐
                  │   User Query     │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ Query Processing │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ Query Expansion  │
                  │ & Synonym Boost  │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ Medical Knowledge│
                  │     Retrieval    │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ Relevant Medical │
                  │     Context      │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │   AI Response    │
                  │    Generation    │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ Safety-Oriented  │
                  │     Response     │
                  └──────────────────┘
```

### Retrieval Method

The current implementation uses:

* **TF-IDF Vectorization**
* **Cosine Similarity**
* Medical synonym expansion
* Query expansion
* Knowledge-base filtering

These techniques help identify medical information that is semantically relevant to the user's query before generating a response.

---

# 🌟 Key Features

## 1. 🩺 Symptom Reasoner

The Symptom Reasoner accepts user-described symptoms and retrieves relevant medical information.

### Features

* Symptom matching
* Medical terminology expansion
* Retrieval of relevant medical information
* Plain-language explanations
* Self-care guidance where appropriate
* Safety-oriented responses
* Source/reference information

The system is designed to avoid presenting AI output as a confirmed medical diagnosis.

---

## 2. 🧑‍⚕️ Hospital Specialist Booking

The application includes a healthcare navigation workflow that connects users with appropriate medical specialists.

### Workflow

```text
Symptoms
   ↓
Possible Medical Category
   ↓
Recommended Specialist
   ↓
Hospital Registry
   ↓
Available Doctors
   ↓
Appointment Slot
   ↓
Booking Confirmation
```

The current implementation can work with a **mock hospital registry** for demonstration purposes.

---

## 3. 📋 Multi-Agent Clinical Handoff

The system can transform conversational patient information into structured clinical information.

### Output formats

#### SOAP Notes

```text
Subjective
Objective
Assessment
Plan
```

#### FHIR JSON

The system can generate structured healthcare information following concepts from the **FHIR (Fast Healthcare Interoperability Resources)** standard.

### Example workflow

```text
Patient Conversation
        ↓
Information Extraction
        ↓
Clinical Structuring
        ↓
SOAP Note
        ↓
FHIR JSON
        ↓
Doctor Review
```

The goal is to reduce repetitive information collection during clinical intake.

---

## 4. 🩸 Lab Report Analyzer

The Lab Report Analyzer processes supported laboratory PDF documents.

### Current capabilities

* PDF document processing
* CBC report extraction
* Blood biomarker identification
* Identification of selected abnormal values
* Low-iron detection logic
* Plain-language explanations
* Basic dietary guidance

### Processing workflow

```text
CBC PDF
   ↓
PDF Text Extraction
   ↓
Biomarker Detection
   ↓
Value Extraction
   ↓
Reference-Range Comparison
   ↓
Explanation
   ↓
User-Friendly Summary
```

The system uses simple analogies to make medical information easier to understand.

For example:

> Red blood cells can be explained like vehicles carrying oxygen around the body.

---

# 🛠️ Technologies Used

## Backend

* **Python 3.10+**
* **FastAPI**
* **Uvicorn**
* **Pydantic**

### Why?

**Python**
Used as the primary backend programming language.

**FastAPI**
Provides a modern framework for building asynchronous REST APIs.

**Uvicorn**
Runs the FastAPI application as an ASGI server.

**Pydantic**
Provides request validation and structured data models.

---

## Artificial Intelligence & RAG

* **Retrieval-Augmented Generation (RAG)**
* **Scikit-learn**
* **TF-IDF**
* **Cosine Similarity**
* **Query Expansion**
* **Medical Synonym Boosting**
* **Ollama**
* Local LLMs

### Why RAG?

RAG allows the system to retrieve relevant information from a controlled knowledge source before generating an answer.

This helps reduce unsupported responses and makes the application's responses more grounded.

---

## Frontend

* **HTML5**
* **CSS3**
* **JavaScript**
* **Tailwind CSS**
* **FontAwesome**

The frontend provides a responsive single-page healthcare interface with a dark clinical-style design.

---

## Document Processing

* **PyPDF**
* **ReportLab**

### PyPDF

Used for extracting text and information from PDF documents.

### ReportLab

Used for generating structured PDF reports when required.

---

## Healthcare Standards

### SOAP

Used to structure clinical information into:

* Subjective
* Objective
* Assessment
* Plan

### FHIR

FHIR-compatible JSON structures can be generated to represent healthcare information in a standardized format.

---

# 🏗️ System Architecture

```text
┌──────────────────────────────────────────┐
│              FRONTEND                    │
│      HTML + CSS + JavaScript             │
└────────────────────┬─────────────────────┘
                     │
                     │ REST API
                     ↓
┌──────────────────────────────────────────┐
│              FASTAPI                     │
│              BACKEND                     │
├──────────────────────────────────────────┤
│                                          │
│  Symptom Processing                      │
│  RAG Pipeline                            │
│  Specialist Matching                     │
│  Appointment Management                  │
│  Clinical Handoff                        │
│  Lab Report Processing                   │
│                                          │
└───────────────┬───────────────┬──────────┘
                │               │
                ↓               ↓
      ┌────────────────┐  ┌───────────────┐
      │ Medical        │  │ AI Models     │
      │ Knowledge Base │  │               │
      │                │  │ Ollama        │
      │ TF-IDF         │  │ Gemini        │
      │ Similarity     │  │ OpenAI        │
      └────────────────┘  └───────────────┘
                │
                ↓
      ┌────────────────────┐
      │ Document Processing│
      │                    │
      │ CBC PDF / Reports  │
      └────────────────────┘
```

---

# 📂 Suggested Project Structure

```text
SMART-HEALTHCARE-NAVIGATOR/
│
├── backend/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── rag/
│   ├── utils/
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── knowledge_base/
│   └── medical_documents/
│
├── uploads/
│
├── reports/
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

> The exact structure may vary depending on the implementation.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SMART-HEALTHCARE-NAVIGATOR.git
```

```bash
cd SMART-HEALTHCARE-NAVIGATOR
```

---

## 2. Create a Python virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root if cloud AI providers are enabled.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

Do **not** commit `.env` to GitHub.

Add it to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
uploads/
```

---

# 🦙 Ollama Setup

To use local Ollama models:

1. Install Ollama.
2. Start the Ollama service.
3. Download a supported model.

Example:

```bash
ollama pull llama3
```

You can also configure other supported models such as:

```bash
ollama pull mistral
```

```bash
ollama pull phi3
```

The exact model availability depends on your local Ollama installation and hardware.

---

# ▶️ Running the Application

Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Open the frontend in your browser according to the project's configured frontend setup.

---

# 🔌 API Overview

Typical API functionality includes:

| Endpoint Category   | Purpose                               |
| ------------------- | ------------------------------------- |
| Health Check        | Verify backend availability           |
| Symptom Analysis    | Process user symptoms                 |
| RAG Retrieval       | Retrieve relevant medical information |
| Specialist Search   | Find suitable specialists             |
| Appointment Booking | Book available appointment slots      |
| Clinical Handoff    | Generate SOAP/FHIR information        |
| Lab Analysis        | Process supported laboratory reports  |

> Exact endpoint names depend on the current backend implementation.

---

# 🔄 Complete Application Workflow

```text
                    USER
                     │
                     ↓
            ┌─────────────────┐
            │ Healthcare UI   │
            └────────┬────────┘
                     ↓
            ┌─────────────────┐
            │ FastAPI Backend │
            └────────┬────────┘
                     ↓
              ┌──────────────┐
              │ User Request │
              └──────┬───────┘
                     ↓
        ┌──────────────────────────┐
        │ Request Classification   │
        └────────────┬─────────────┘
                     ↓
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
   Symptoms       Lab PDF      Clinical
   Analysis       Analysis      Handoff
       │             │             │
       ↓             ↓             ↓
      RAG        PDF Parser    Structured
    Retrieval       │          Information
       │             ↓             │
       ↓          Biomarkers       ↓
    Context      & Values      SOAP/FHIR
       │
       ↓
    AI Model
       │
       ↓
 Safety Layer
       │
       ↓
 User-Friendly
    Response
```

---

# 🛡️ Safety & Privacy

Healthcare applications require additional care because incorrect information can potentially cause harm.

Smart Healthcare Navigator follows a **safety-first design philosophy**.

### Safety principles

* AI output is not presented as a confirmed diagnosis.
* Responses are grounded in the configured knowledge base where applicable.
* The system should avoid unsupported medical claims.
* Users are encouraged to consult qualified healthcare professionals.
* Emergency symptoms should be directed toward immediate professional/emergency care.
* Sensitive healthcare information should be handled carefully.
* API keys and secrets must never be committed to source control.

### Important Disclaimer

> **Smart Healthcare Navigator is an educational and healthcare-navigation application. It is not a medical diagnostic system and does not replace a qualified doctor, emergency service, or other healthcare professional. Users should seek professional medical advice for diagnosis, treatment, medication decisions, or urgent medical concerns.**

---

# 📊 Benefits

### For Users

* Easier understanding of symptoms
* Plain-language medical information
* Healthcare specialist navigation
* Laboratory report explanations
* Privacy-focused local AI options

### For Healthcare Professionals

* Structured patient information
* SOAP note generation
* FHIR-style structured data
* Reduced repetitive clinical intake work

### For Developers

* Practical RAG implementation
* FastAPI backend development
* LLM integration
* Local AI inference
* Document processing
* Healthcare data standardization

---

# 🚀 Future Enhancements

Possible future improvements include:

* [ ] Medical vector database integration
* [ ] Advanced embedding-based retrieval
* [ ] More laboratory report formats
* [ ] Multi-language healthcare explanations
* [ ] Voice-based symptom input
* [ ] Real hospital API integration
* [ ] Real appointment-provider integration
* [ ] Authentication and role-based access
* [ ] Secure encrypted healthcare data storage
* [ ] Improved clinical evaluation and safety testing
* [ ] Advanced FHIR resource support
* [ ] Mobile application
* [ ] Medical knowledge-base versioning

---

# 🧪 Testing

The application should be tested across different categories of inputs.

### Normal Cases

* Common symptoms
* Valid CBC reports
* Available specialists
* Valid appointment requests

### Edge Cases

* Empty symptom descriptions
* Unknown medical terms
* Unsupported documents
* Missing biomarkers
* Invalid PDF files
* No available appointment slots

### Safety Cases

* Unsupported medical questions
* Requests for diagnosis
* Potentially serious symptoms
* Medication-related questions
* Emergency-related situations

The goal is to ensure that the system responds safely instead of generating unsupported medical claims.

---

# 📜 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

# 👩‍💻 Project Purpose

**Smart Healthcare Navigator** demonstrates how modern AI engineering techniques such as **RAG, local LLMs, document processing, structured healthcare data, and REST APIs** can be combined to build a privacy-conscious healthcare navigation application.

The project focuses on one core idea:

> **Use AI to make healthcare information easier to understand and navigate while keeping professional medical judgment at the center.**

---

## ⚠️ Medical Disclaimer

This project is intended for **educational, demonstration, and software-development purposes only**.

It should not be used as a substitute for professional medical diagnosis, treatment, emergency care, or clinical decision-making.
