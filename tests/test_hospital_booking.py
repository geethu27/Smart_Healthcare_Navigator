import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.hospital_api import MockHospitalAPI

api = MockHospitalAPI()

# 1. Search for Dermatologist
derms = api.find_specialists("Dermatologist")
print("=== LEVEL 2: DERMATOLOGIST SEARCH ===")
for d in derms:
    print(f"- {d['name']} | {d['specialty']} | {d['hospital']} | Slots: {d['available_slots']}")

# 2. Book appointment
booking_res = api.book_appointment(
    patient_name="Alex Morgan",
    doctor_id=derms[0]["id"],
    date="2026-09-28",
    time_slot="11:00 AM",
    symptoms_summary="Dry itchy rash on inner forearms for 5 days"
)

print("\n=== LEVEL 2: BOOKING CONFIRMATION ===")
print(json.dumps(booking_res, indent=2))
