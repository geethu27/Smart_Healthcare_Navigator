import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_chat_symptom_in_corpus():
    response = client.post("/api/chat", json={
        "message": "What are common symptoms associated with fever?",
        "provider": "local",
        "threshold": 0.15
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "HEALTHCARE_SYMPTOM"
    assert data["is_grounded"] is True
    assert data["rag_score"] >= 0.15
    assert len(data["sources"]) > 0
    print("[PASS] Test 1: Chat Symptom In-Corpus passed")

def test_chat_out_of_corpus_fallback():
    response = client.post("/api/chat", json={
        "message": "What are the symptoms of a rare neurological disorder?",
        "provider": "local",
        "threshold": 0.15
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "HEALTHCARE_SYMPTOM"
    assert data["is_grounded"] is False
    assert "I don't have enough verified information" in data["response"]
    print("[PASS] Test 2: Out-of-Corpus Fallback passed")

def test_chat_unrelated_rejection():
    response = client.post("/api/chat", json={
        "message": "Who is the Prime Minister of India?",
        "provider": "local",
        "threshold": 0.15
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "UNRELATED"
    assert data["is_grounded"] is False
    assert "dedicated exclusively to health inquiries" in data["response"]
    print("[PASS] Test 3: Unrelated Rejection passed")

def test_chat_appointment_navigation():
    response = client.post("/api/chat", json={
        "message": "Find me a dermatologist for skin rash",
        "provider": "local",
        "threshold": 0.15
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "APPOINTMENT_NAVIGATION"
    assert len(data["specialists"]) > 0
    assert any("Dermatologist" in s["specialty"] for s in data["specialists"])
    print("[PASS] Test 4: Appointment Navigation passed")

def test_specialists_and_booking():
    # 1. Query specialists
    res_spec = client.get("/api/specialists?specialty=Dermatologist")
    assert res_spec.status_code == 200
    specs = res_spec.json()
    assert len(specs) > 0
    doc_id = specs[0]["id"]

    # 2. Book appointment
    res_book = client.post("/api/book-appointment", json={
        "patient_name": "Alex Morgan",
        "doctor_id": doc_id,
        "date": "2026-09-28",
        "time_slot": "11:00 AM",
        "symptoms_summary": "Dry itchy patch on arms"
    })
    assert res_book.status_code == 200
    book_data = res_book.json()
    assert book_data["success"] is True
    assert "APT-" in book_data["booking"]["confirmation_code"]
    print("[PASS] Test 5: Specialist Directory & Booking passed")

def test_intake_handoff():
    response = client.post("/api/intake-summary", json={
        "patient_name": "Alex Morgan",
        "history": [
            {"role": "user", "content": "I have had a severe cough and sore throat for 4 days."},
            {"role": "assistant", "content": "Are there other symptoms?"},
            {"role": "user", "content": "Pain is 7 out of 10 and I feel chills."}
        ],
        "recommended_specialist": "Pulmonologist"
    })
    assert response.status_code == 200
    data = response.json()
    assert "SOAP" in data["soap_note"]
    assert data["machine_usable_json"]["resourceType"] == "ClinicalIntakeSummary"
    print("[PASS] Test 6: Multi-Agent Clinical Handoff passed")

def test_sample_lab_report():
    response = client.get("/api/sample-lab-report/low_iron")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["analysis"]["has_low_iron"] is True
    assert data["analysis"]["total_biomarkers_extracted"] >= 6
    print("[PASS] Test 7: Sample Lab Report Analyzer passed")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING END-TO-END TEST SUITE FOR SMART HEALTHCARE NAVIGATOR")
    print("=" * 60)
    test_chat_symptom_in_corpus()
    test_chat_out_of_corpus_fallback()
    test_chat_unrelated_rejection()
    test_chat_appointment_navigation()
    test_specialists_and_booking()
    test_intake_handoff()
    test_sample_lab_report()
    print("=" * 60)
    print("ALL 7 END-TO-END TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
