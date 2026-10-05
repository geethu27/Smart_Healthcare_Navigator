"""
Mock Hospital & Provider API (Level 2 Tool Integration)
Provides:
- Directory of verified medical specialists across clinical departments
- Real-time availability lookup
- Booking execution with confirmation codes and structured appointments
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

MOCK_SPECIALISTS = [
    {
        "id": "doc_derm_01",
        "name": "Dr. Aisha Patel, MD",
        "specialty": "Dermatologist",
        "department": "Dermatology & Cutaneous Surgery",
        "hospital": "Metro Health Specialist Clinic",
        "address": "452 Wellness Blvd, Suite 300",
        "rating": 4.9,
        "experience_years": 14,
        "available_days": ["Monday", "Tuesday", "Thursday", "Friday"],
        "available_slots": ["09:30 AM", "11:00 AM", "02:15 PM", "04:00 PM"]
    },
    {
        "id": "doc_gen_01",
        "name": "Dr. Robert Chen, MD",
        "specialty": "General Physician",
        "department": "Internal Medicine & Primary Care",
        "hospital": "Downtown Comprehensive Health Center",
        "address": "120 Central Ave, Pavilion B",
        "rating": 4.8,
        "experience_years": 18,
        "available_days": ["Monday", "Wednesday", "Thursday", "Saturday"],
        "available_slots": ["08:45 AM", "10:30 AM", "01:00 PM", "03:30 PM"]
    },
    {
        "id": "doc_gastro_01",
        "name": "Dr. Sarah Jenkins, MD, FACG",
        "specialty": "Gastroenterologist",
        "department": "Digestive Health & Endoscopy",
        "hospital": "St. Jude Medical Pavilion",
        "address": "780 River Parkway, Tower 2",
        "rating": 4.9,
        "experience_years": 16,
        "available_days": ["Tuesday", "Wednesday", "Friday"],
        "available_slots": ["10:00 AM", "11:30 AM", "02:30 PM", "04:30 PM"]
    },
    {
        "id": "doc_pulm_01",
        "name": "Dr. Marcus Vance, MD, FCCP",
        "specialty": "Pulmonologist",
        "department": "Pulmonology & Respiratory Medicine",
        "hospital": "City Center Health Institute",
        "address": "900 Medical Heights Dr",
        "rating": 4.7,
        "experience_years": 12,
        "available_days": ["Monday", "Wednesday", "Friday"],
        "available_slots": ["09:00 AM", "11:15 AM", "01:45 PM", "03:15 PM"]
    },
    {
        "id": "doc_neuro_01",
        "name": "Dr. Elena Rostova, MD, PhD",
        "specialty": "Neurologist",
        "department": "Neurology & Headache Center",
        "hospital": "Northside Specialty Hospital",
        "address": "310 University Avenue",
        "rating": 4.9,
        "experience_years": 15,
        "available_days": ["Tuesday", "Thursday", "Saturday"],
        "available_slots": ["10:15 AM", "01:30 PM", "03:45 PM"]
    },
    {
        "id": "doc_ent_01",
        "name": "Dr. Tariq Al-Mansoor, MD",
        "specialty": "ENT Specialist",
        "department": "Otolaryngology & Sinus Center",
        "hospital": "Eastside Ear, Nose & Throat Clinic",
        "address": "520 Highland Park",
        "rating": 4.8,
        "experience_years": 11,
        "available_days": ["Monday", "Tuesday", "Thursday"],
        "available_slots": ["09:15 AM", "11:45 AM", "02:00 PM"]
    },
    {
        "id": "doc_hem_01",
        "name": "Dr. Miriam Gold, MD",
        "specialty": "Hematologist",
        "department": "Hematology & Blood Disorders",
        "hospital": "Metro Academic Health System",
        "address": "880 Oak Street",
        "rating": 4.9,
        "experience_years": 20,
        "available_days": ["Wednesday", "Thursday", "Friday"],
        "available_slots": ["10:00 AM", "01:15 PM", "03:00 PM"]
    }
]

class MockHospitalAPI:
    def __init__(self):
        self.specialists = MOCK_SPECIALISTS
        # In-memory booked appointments storage
        self.bookings: List[Dict[str, Any]] = []

    def get_all_specialists(self) -> List[Dict[str, Any]]:
        return self.specialists

    def find_specialists(self, query_specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Finds specialists matching specialty or symptom keywords."""
        if not query_specialty or query_specialty.strip() == "":
            return self.specialists

        target = query_specialty.strip().lower()
        matched = []
        for doc in self.specialists:
            if (target in doc["specialty"].lower() or 
                target in doc["department"].lower() or
                doc["specialty"].lower() in target):
                matched.append(doc)

        # Fallback to General Physician if no direct specialty match
        if not matched:
            for doc in self.specialists:
                if "general" in doc["specialty"].lower():
                    matched.append(doc)

        return matched

    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        for doc in self.specialists:
            if doc["id"] == doctor_id:
                return doc
        return None

    def book_appointment(self, 
                         patient_name: str, 
                         doctor_id: str, 
                         date: str, 
                         time_slot: str, 
                         symptoms_summary: str, 
                         patient_contact: str = "") -> Dict[str, Any]:
        """
        Executes appointment booking and returns machine-usable confirmation.
        """
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return {
                "success": False,
                "error": f"Doctor ID {doctor_id} not found."
            }

        confirmation_code = f"APT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        booking_record = {
            "confirmation_code": confirmation_code,
            "patient_name": patient_name or "Anonymous Patient",
            "patient_contact": patient_contact or "Not provided",
            "doctor_id": doctor["id"],
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "hospital": doctor["hospital"],
            "address": doctor["address"],
            "appointment_date": date,
            "appointment_time": time_slot,
            "symptoms_summary": symptoms_summary,
            "status": "CONFIRMED",
            "booked_at": datetime.now().isoformat(),
            "preparation_guidelines": [
                "Please arrive 15 minutes before your scheduled appointment time.",
                "Bring a valid photo ID, insurance card, and any relevant prior lab reports or medications.",
                "If your symptoms worsen or you develop severe chest pain/breathing distress, proceed to emergency care immediately."
            ]
        }

        self.bookings.append(booking_record)
        return {
            "success": True,
            "booking": booking_record
        }

    def list_patient_bookings(self) -> List[Dict[str, Any]]:
        return self.bookings
