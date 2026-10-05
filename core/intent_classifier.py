"""
Intent Classifier & Guardrail Router
Classifies incoming user queries into:
1. GREETING -> Friendly greeting & capability orientation
2. HEALTHCARE_SYMPTOM -> Medical RAG + Symptom Navigation
3. APPOINTMENT_NAVIGATION -> Mock Hospital API Booking
4. LAB_REPORT_ANALYSIS -> Lab Report Parser / Multimodal Analyzer
5. EMERGENCY_ALERT -> Immediate Emergency Protocol
6. UNRELATED -> Politely decline out-of-domain requests
"""

import re
from typing import Dict, Any

class IntentType:
    GREETING = "GREETING"
    HEALTHCARE_SYMPTOM = "HEALTHCARE_SYMPTOM"
    APPOINTMENT_NAVIGATION = "APPOINTMENT_NAVIGATION"
    LAB_REPORT_ANALYSIS = "LAB_REPORT_ANALYSIS"
    EMERGENCY_ALERT = "EMERGENCY_ALERT"
    UNRELATED = "UNRELATED"

GREETING_RESPONSE = (
    "Hello! I am your Smart Healthcare Navigator. I'm here to listen to your symptoms "
    "(such as fever, cough, sore throat, stomach pain, headaches, fatigue, or skin rashes), "
    "explain possible common ailments in plain language, and help you find qualified specialists "
    "or review blood test reports.\n\n"
    "How can I assist you with your health today? Please describe what you are experiencing."
)

UNRELATED_RESPONSE = (
    "I am the Smart Healthcare Navigator, an AI assistant dedicated exclusively to health inquiries, "
    "symptom guidance, and medical appointment booking. I cannot assist with general topics, "
    "coding, politics, or non-healthcare questions. How can I assist you with your health today?"
)

EMERGENCY_RESPONSE = (
    "[CRITICAL MEDICAL ALERT: IMMEDIATE ATTENTION REQUIRED]\n\n"
    "Your description indicates potential emergency red-flag symptoms (such as severe chest pain, "
    "breathing difficulty, sudden weakness, or uncontrolled bleeding).\n\n"
    "Please take the following actions immediately:\n"
    "1. Call your local emergency number right away (e.g., 911 in the US/Canada, 112 in Europe/India, or 999 in the UK).\n"
    "2. If you are alone, inform someone near you or unlock your door for first responders.\n"
    "3. Do not drive yourself to the emergency department; request an ambulance.\n\n"
    "*The Smart Healthcare Navigator does not provide emergency triage or emergency medical interventions.*"
)

class IntentClassifier:
    def __init__(self):
        # Emergency Red Flags
        self.emergency_patterns = [
            r"\b(crushing|severe)\s+(chest\s+pain|chest\s+pressure)\b",
            r"\b(can'?t|cannot|unable\s+to)\s+breathe\b",
            r"\b(shortness\s+of\s+breath)\b",
            r"\b(coughing\s+up|vomiting)\s+blood\b",
            r"\b(loss\s+of\s+consciousness|passed\s+out|fainted)\b",
            r"\b(stroke|facial\s+droop|slurred\s+speech|sudden\s+paralysis)\b",
            r"\b(suicid(e|al)|kill\s+myself|overdose)\b",
            r"\b(thunderclap|worst\s+headache\s+of\s+life)\b"
        ]

        # Greeting patterns
        self.greeting_patterns = [
            r"^(hi|hello|hey|heya|hola|greetings|good\s+(morning|afternoon|evening|day)|howdy)[\s\.,!]*$",
            r"^(who\s+are\s+you|what\s+can\s+you\s+do|help|how\s+does\s+this\s+work)[\s\?]*$"
        ]

        # Appointment / Hospital Navigation
        self.appointment_patterns = [
            r"\b(book|schedule|reschedule|cancel)\s+.*?(appointment|slot|visit)\b",
            r"\b(find|need|want|see|consult|book|schedule)\s+.*?\b(doctor|specialist|physician|dermatologist|cardiologist|neurologist|gastroenterologist|pulmonologist|hematologist|ent)\b",
            r"\b(nearest|available)\s+(clinic|hospital|doctor|specialist|slot)\b",
            r"\bappointment\s+(tomorrow|today|this\s+week|slot|timing)\b",
            r"\b(clinic|hospital)\s+(near|address|location|hours)\b"
        ]

        # Lab Report / Blood Test
        self.lab_patterns = [
            r"\b(blood\s+test|cbc\s+panel|lab\s+report|blood\s+work|ferritin|hemoglobin|wbc|platelet|lipid\s+panel)\b",
            r"\b(upload|uploaded|analyze|explain|interpret)\s+.*?\b(report|blood\s+test|results|panel)\b"
        ]

        # Explicit non-healthcare
        self.unrelated_patterns = [
            r"\b(prime\s+minister|president|capital\s+of|weather\s+in|who\s+won|stock\s+price)\b",
            r"\b(python|javascript|write\s+a\s+code|programming|algorithm|debug\s+code|html|css|sql|react)\b",
            r"\b(recipe|how\s+to\s+cook|bake|movie|song|lyrics|sports|football|cricket|nba)\b",
            r"\b(bitcoin|crypto|investment|quantum\s+computer|matrix\s+multiplication)\b"
        ]

        # Core Healthcare / Symptom terms
        self.healthcare_terms = [
            "symptom", "pain", "fever", "cough", "cold", "throat", "headache", "migraine",
            "rash", "skin", "itch", "stomach", "cramp", "nausea", "vomit", "diarrhea",
            "fatigue", "tired", "exhausted", "dizzy", "dizziness", "swelling", "infection",
            "disease", "illness", "ache", "chills", "sneez", "congestion", "allergy", "allergic",
            "medicine", "doctor", "health", "hospital", "body", "breathing", "temperature",
            "iron", "deficiency", "anemia", "blood", "pressure", "hypertension", "diabetes",
            "heartburn", "acid reflux", "gerd", "gastritis", "eczema", "hives", "wheezing",
            "sick", "hurt", "hurts", "sore", "weak", "weakness"
        ]

    def classify(self, text: str) -> Dict[str, Any]:
        """Classifies the user input text and determines the routing action."""
        clean_text = text.strip()
        lower_text = clean_text.lower()

        # 1. Emergency Check
        for pattern in self.emergency_patterns:
            if re.search(pattern, lower_text):
                return {
                    "intent": IntentType.EMERGENCY_ALERT,
                    "reason": "Emergency red-flag symptoms detected",
                    "routed_to": "EMERGENCY_SYSTEM",
                    "direct_response": EMERGENCY_RESPONSE
                }

        # 2. Greeting Check
        for pattern in self.greeting_patterns:
            if re.search(pattern, lower_text):
                return {
                    "intent": IntentType.GREETING,
                    "reason": "Friendly conversational greeting or help request",
                    "routed_to": "DIRECT_GREETING",
                    "direct_response": GREETING_RESPONSE
                }

        # 3. Explicit Unrelated Check
        for pattern in self.unrelated_patterns:
            if re.search(pattern, lower_text):
                return {
                    "intent": IntentType.UNRELATED,
                    "reason": "Explicit non-healthcare domain query",
                    "routed_to": "REJECT",
                    "direct_response": UNRELATED_RESPONSE
                }

        # 4. Appointment Navigation Check
        for pattern in self.appointment_patterns:
            if re.search(pattern, lower_text):
                specialty = "General Physician"
                if "dermatolog" in lower_text:
                    specialty = "Dermatologist"
                elif "cardio" in lower_text:
                    specialty = "Cardiologist"
                elif "neuro" in lower_text:
                    specialty = "Neurologist"
                elif "gastro" in lower_text or "stomach" in lower_text:
                    specialty = "Gastroenterologist"
                elif "pulmon" in lower_text or "lung" in lower_text:
                    specialty = "Pulmonologist"
                elif "ent" in lower_text or "ear" in lower_text or "throat" in lower_text:
                    specialty = "ENT Specialist"
                elif "hematolog" in lower_text or "blood" in lower_text:
                    specialty = "Hematologist"

                return {
                    "intent": IntentType.APPOINTMENT_NAVIGATION,
                    "reason": "User requested appointment or provider search",
                    "specialty": specialty,
                    "routed_to": "HOSPITAL_API",
                    "direct_response": None
                }

        # 5. Lab Report Check
        for pattern in self.lab_patterns:
            if re.search(pattern, lower_text):
                return {
                    "intent": IntentType.LAB_REPORT_ANALYSIS,
                    "reason": "User referenced lab report or blood biomarker results",
                    "routed_to": "LAB_ANALYZER",
                    "direct_response": None
                }

        # 6. Healthcare Keyword Coverage Check
        has_health_term = any(term in lower_text for term in self.healthcare_terms)
        is_medical_question = bool(re.search(r"\b(symptom|cause|treatment|cure|mean|prevent|condition|feel|hurt)\b", lower_text))

        if has_health_term or is_medical_question:
            return {
                "intent": IntentType.HEALTHCARE_SYMPTOM,
                "reason": "Healthcare symptom or medical question detected",
                "routed_to": "MEDICAL_RAG",
                "direct_response": None
            }

        # Default fallback for out-of-domain queries
        word_count = len(clean_text.split())
        if word_count > 2:
            return {
                "intent": IntentType.UNRELATED,
                "reason": "No relevant healthcare or symptom terminology identified",
                "routed_to": "REJECT",
                "direct_response": UNRELATED_RESPONSE
            }

        # Short general greeting fallback
        return {
            "intent": IntentType.GREETING,
            "reason": "Short conversational greeting",
            "routed_to": "DIRECT_GREETING",
            "direct_response": GREETING_RESPONSE
        }
