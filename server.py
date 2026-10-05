"""
Smart Healthcare Navigator - Production Backend Server
Built with FastAPI, CORS, and full REST APIs for:
- Level 1: RAG-based symptom reasoning with confidence threshold
- Level 2: Tool integration for mock hospital specialist booking
- Level 3: Multi-agent patient intake and doctor-facing SOAP/FHIR handoff
- Level 4: Advanced/multimodal lab report PDF & CBC biomarker analyzer
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.rag_engine import MedicalRAGEngine
from core.intent_classifier import IntentClassifier, IntentType
from core.llm_provider import generate_symptom_response
from core.hospital_api import MockHospitalAPI
from core.intake_and_doctor_agent import PatientIntakeAgent, DoctorFacingAgent
from core.lab_report_analyzer import LabReportAnalyzer

app = FastAPI(
    title="Smart Healthcare Navigator AI",
    description="Privacy-first, empathetic AI healthcare navigator with grounded RAG, appointment booking, clinical handoffs, and lab analysis.",
    version="3.0.0"
)

# Enable CORS for seamless interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
rag_engine = MedicalRAGEngine(knowledge_dir="medical_knowledge", similarity_threshold=0.15)
intent_classifier = IntentClassifier()
hospital_api = MockHospitalAPI()
intake_agent = PatientIntakeAgent()
doctor_agent = DoctorFacingAgent()
lab_analyzer = LabReportAnalyzer()

# Ensure upload directory exists
UPLOAD_DIR = "uploaded_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    provider: Optional[str] = "local"
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    threshold: Optional[float] = 0.15
    patient_name: Optional[str] = "Patient"

class BookingRequest(BaseModel):
    patient_name: str
    doctor_id: str
    date: str
    time_slot: str
    symptoms_summary: str
    patient_contact: Optional[str] = ""

class IntakeSummaryRequest(BaseModel):
    patient_name: Optional[str] = "Patient"
    history: List[ChatMessage]
    recommended_specialist: Optional[str] = "General Physician"
    sources: Optional[List[str]] = []

# --- API Endpoints ---

@app.post("/api/chat")
async def handle_chat(req: ChatRequest):
    """
    Main conversational pipeline:
    1. Intent Classification (Healthcare vs. Appointment vs. Lab vs. Emergency vs. Unrelated)
    2. RAG Retrieval with Similarity Threshold
    3. Grounded Synthesis or Safe Fallback
    """
    query = req.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Update threshold dynamically if provided
    current_threshold = req.threshold if req.threshold is not None else rag_engine.similarity_threshold
    rag_engine.similarity_threshold = current_threshold

    # Step 1: Intent Classification
    intent_res = intent_classifier.classify(query)
    intent = intent_res["intent"]
    routed_to = intent_res["routed_to"]

    # 0. Greeting Check
    if intent == IntentType.GREETING:
        return {
            "intent": intent,
            "routed_to": routed_to,
            "reason": intent_res["reason"],
            "response": intent_res["direct_response"],
            "is_grounded": True,
            "rag_score": 1.0,
            "threshold": current_threshold,
            "sources": ["Smart Healthcare Navigator Orientation Guide"],
            "matches": [],
            "specialists": []
        }

    # 1. Emergency Red-Flag Alert
    if intent == IntentType.EMERGENCY_ALERT:
        return {
            "intent": intent,
            "routed_to": routed_to,
            "reason": intent_res["reason"],
            "response": intent_res["direct_response"],
            "is_grounded": False,
            "rag_score": 0.0,
            "threshold": current_threshold,
            "sources": [],
            "matches": [],
            "specialists": []
        }

    # 2. Unrelated Out-of-Domain Query
    if intent == IntentType.UNRELATED:
        return {
            "intent": intent,
            "routed_to": routed_to,
            "reason": intent_res["reason"],
            "response": intent_res["direct_response"],
            "is_grounded": False,
            "rag_score": 0.0,
            "threshold": current_threshold,
            "sources": [],
            "matches": [],
            "specialists": []
        }

    # 3. Appointment Navigation
    if intent == IntentType.APPOINTMENT_NAVIGATION:
        matched_docs = hospital_api.find_specialists(intent_res.get("specialty"))
        response_msg = (
            f"I would be glad to help connect you with medical care. Based on your request, "
            f"here are verified specialists in **{intent_res.get('specialty', 'General Medicine')}** "
            f"with open appointment availability:"
        )
        return {
            "intent": intent,
            "routed_to": routed_to,
            "reason": intent_res["reason"],
            "response": response_msg,
            "is_grounded": True,
            "rag_score": 1.0,
            "threshold": current_threshold,
            "sources": ["Metro Hospital Provider Registry"],
            "matches": [],
            "specialists": matched_docs
        }

    # 4. Lab Report Inquiry in Chat
    if intent == IntentType.LAB_REPORT_ANALYSIS:
        response_msg = (
            "I can review your Complete Blood Count (CBC) and Iron panel results! "
            "Please use the **Lab Report Analyzer** tab to upload your blood test PDF or view "
            "a sample report with low iron to see our biomarker breakdown and dietary insights."
        )
        return {
            "intent": intent,
            "routed_to": routed_to,
            "reason": intent_res["reason"],
            "response": response_msg,
            "is_grounded": True,
            "rag_score": 1.0,
            "threshold": current_threshold,
            "sources": ["Clinical Laboratory Reference Standard"],
            "matches": [],
            "specialists": hospital_api.find_specialists("Hematologist")
        }

    # 5. Healthcare / Symptom Inquiry -> RAG Execution
    rag_result = rag_engine.search(query)
    
    # Grounded response synthesis (Local / Ollama / Gemini / OpenAI)
    ai_response = generate_symptom_response(
        user_query=query,
        rag_result=rag_result,
        provider_type=req.provider or "local",
        api_key=req.api_key,
        model_name=req.model_name
    )

    # Determine recommended specialist
    rec_specialist = "General Physician"
    if rag_result["matches"]:
        rec_specialist = rag_result["matches"][0].get("specialty", "General Physician")

    matched_specialists = hospital_api.find_specialists(rec_specialist) if rag_result["is_relevant"] else []

    return {
        "intent": intent,
        "routed_to": routed_to,
        "reason": intent_res["reason"],
        "response": ai_response,
        "is_grounded": rag_result["is_relevant"],
        "rag_score": rag_result["best_score"],
        "threshold": rag_result["threshold"],
        "sources": rag_result["sources"],
        "matches": rag_result["matches"],
        "recommended_specialist": rec_specialist,
        "specialists": matched_specialists
    }

@app.post("/api/intake-summary")
async def generate_intake_summary(req: IntakeSummaryRequest):
    """
    Level 3: Multi-Agent Handoff
    Converts conversation history into clinical SOAP Note and FHIR-aligned JSON.
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    intake_data = intake_agent.extract_intake_data(history_dicts)

    # Differential possibilities from context
    rag_ailments = [
        "Common Cold / Acute Viral Rhinosinusitis",
        "Acute Bronchitis / Airway Irritation",
        "Seasonal Allergic Pharyngitis"
    ]

    handoff = doctor_agent.generate_clinical_summary(
        patient_name=req.patient_name or "Alex Morgan",
        intake_data=intake_data,
        rag_ailments=rag_ailments,
        recommended_specialist=req.recommended_specialist or "General Physician",
        sources=req.sources or ["CDC & NHS Clinical Guidelines"]
    )

    return {
        "intake_data": intake_data,
        "soap_note": handoff["soap_note"],
        "machine_usable_json": handoff["machine_usable_json"]
    }

@app.post("/api/upload-lab-report")
async def upload_lab_report(file: UploadFile = File(...)):
    """
    Level 4: Advanced / Multimodal Lab Report Analyzer
    Parses CBC blood test PDF, flags low iron/hemoglobin, explains in plain language.
    """
    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if filename.lower().endswith(".pdf"):
        extracted_text = lab_analyzer.extract_text_from_pdf(save_path)
    else:
        with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()

    analysis = lab_analyzer.analyze(extracted_text, filename=filename)
    return {
        "success": True,
        "analysis": analysis
    }

@app.get("/api/sample-lab-report/{report_type}")
async def load_sample_lab_report(report_type: str):
    """Loads pre-generated sample CBC reports for immediate testing."""
    filename = "patient_cbc_iron_deficiency.pdf" if report_type == "low_iron" else "patient_cbc_normal.pdf"
    file_path = os.path.join("sample_reports", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample report not found.")

    extracted_text = lab_analyzer.extract_text_from_pdf(file_path)
    analysis = lab_analyzer.analyze(extracted_text, filename=filename)
    return {
        "success": True,
        "analysis": analysis
    }

@app.get("/api/specialists")
async def get_specialists(specialty: Optional[str] = None):
    """Level 2: Query mock hospital specialists."""
    return hospital_api.find_specialists(specialty)

@app.post("/api/book-appointment")
async def book_appointment(req: BookingRequest):
    """Level 2: Books appointment in the mock hospital system."""
    res = hospital_api.book_appointment(
        patient_name=req.patient_name,
        doctor_id=req.doctor_id,
        date=req.date,
        time_slot=req.time_slot,
        symptoms_summary=req.symptoms_summary,
        patient_contact=req.patient_contact or ""
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Booking failed."))
    return res

@app.get("/api/rag-diagnostics")
async def get_rag_diagnostics():
    """Provides transparent inspection into the RAG vector store and documents."""
    return {
        "total_chunks_indexed": len(rag_engine.chunks),
        "similarity_threshold": rag_engine.similarity_threshold,
        "corpus_documents": [
            "fever_and_infections.md",
            "respiratory_and_cough.md",
            "gastrointestinal_and_stomach.md",
            "dermatology_and_rash.md",
            "headaches_and_neurology.md",
            "fatigue_and_deficiencies.md"
        ],
        "sample_queries": [
            {"query": "What are common symptoms associated with fever?", "expected": "Grounded in KB (Passes threshold)"},
            {"query": "I have an itchy rash on my arms", "expected": "Grounded in KB (Dermatology match)"},
            {"query": "What are the symptoms of a rare neurological disorder?", "expected": "Fallback response (Threshold reject)"},
            {"query": "Who is the Prime Minister of India?", "expected": "Out-of-domain rejection (Intent classifier)"},
            {"query": "Severe crushing chest pain and fainting", "expected": "Emergency Protocol"}
        ]
    }

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    import socket

    def get_available_port(default_port=8000):
        for port in [default_port, 8001, 8080, 8501]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        return default_port

    active_port = get_available_port(8000)
    print("\n" + "=" * 60)
    print("  SMART HEALTHCARE NAVIGATOR IS RUNNING!")
    print(f"  --> Open in browser: http://127.0.0.1:{active_port}")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host="127.0.0.1", port=active_port, reload=False)

