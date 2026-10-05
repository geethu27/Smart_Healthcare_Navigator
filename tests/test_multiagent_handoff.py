import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.intake_and_doctor_agent import PatientIntakeAgent, DoctorFacingAgent

intake_agent = PatientIntakeAgent()
doctor_agent = DoctorFacingAgent()

conversation_history = [
    {"role": "user", "content": "Hello, I have had a bad cough and sore throat for 4 days."},
    {"role": "assistant", "content": "I am here to help. Could you tell me how severe the pain is and if you have other symptoms?"},
    {"role": "user", "content": "The pain is about 6 out of 10, especially when swallowing, and I feel a bit of mild fever."}
]

# 1. Intake Agent processes conversation
intake_data = intake_agent.extract_intake_data(conversation_history)
print("=== LEVEL 3: INTAKE AGENT EXTRACTED DATA ===")
print(json.dumps(intake_data, indent=2))

# 2. Doctor Agent generates SOAP Note and Machine-Usable JSON
handoff = doctor_agent.generate_clinical_summary(
    patient_name="Alex Morgan",
    intake_data=intake_data,
    rag_ailments=[
        "Common Cold (Viral Rhinosinusitis)",
        "Acute Bronchitis (Chest Cold)",
        "Allergic Rhinitis / Pharyngitis"
    ],
    recommended_specialist="Ear, Nose, Throat (ENT) Specialist / General Physician",
    sources=["WHO & AAFP Guidelines (Respiratory Symptoms)"]
)

print("\n=== LEVEL 3: DOCTOR-FACING SOAP NOTE ===")
print(handoff["soap_note"])

print("\n=== LEVEL 3: MACHINE-USABLE JSON SUMMARY ===")
print(json.dumps(handoff["machine_usable_json"], indent=2))
