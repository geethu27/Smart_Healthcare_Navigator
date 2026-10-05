"""
Lab Report & Blood Biomarker Analyzer (Level 4 Advanced / Multimodal)
Extracts CBC and Iron panel values from PDFs/text,
identifies abnormalities (e.g. low iron/hemoglobin),
translates clinical jargon into 8th-grade reading level explanations,
and provides evidence-based dietary recommendations.
"""

import re
import os
from typing import Dict, Any, List, Optional
import PyPDF2

REFERENCE_RANGES = {
    "hemoglobin": {"min": 12.0, "max": 16.5, "unit": "g/dL", "name": "Hemoglobin (Hb)", "role": "Oxygen-carrying protein in red blood cells"},
    "iron": {"min": 60.0, "max": 170.0, "unit": "mcg/dL", "name": "Serum Iron", "role": "Mineral circulating in blood used to produce energy"},
    "ferritin": {"min": 30.0, "max": 300.0, "unit": "ng/mL", "name": "Ferritin", "role": "Your body's deep storage bank of iron"},
    "hematocrit": {"min": 36.0, "max": 48.0, "unit": "%", "name": "Hematocrit (Hct)", "role": "Percentage of total blood made up of red blood cells"},
    "rbc": {"min": 4.2, "max": 5.8, "unit": "x10^6/mcL", "name": "Red Blood Cells (RBC)", "role": "Microscopic cells that circulate oxygen throughout organs"},
    "mcv": {"min": 80.0, "max": 100.0, "unit": "fL", "name": "Mean Corpuscular Volume (MCV)", "role": "Average size of individual red blood cells"},
    "wbc": {"min": 4.5, "max": 11.0, "unit": "x10^3/mcL", "name": "White Blood Cells (WBC)", "role": "Immune defense cells that fight off infections"},
    "platelets": {"min": 150.0, "max": 450.0, "unit": "x10^3/mcL", "name": "Platelets", "role": "Cell fragments that help blood clot to stop cuts from bleeding"}
}

class LabReportAnalyzer:
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text content from a PDF document."""
        extracted_text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except Exception as e:
            print(f"[LabReportAnalyzer] PDF extraction error: {e}")
        return extracted_text

    def parse_biomarkers(self, text: str) -> List[Dict[str, Any]]:
        """Parses numerical values for key blood markers using multiline flexible matching."""
        biomarkers = []
        lower = text.lower()

        patterns = {
            "hemoglobin": [
                r"hemoglobin(?:\s*\([^\)]*\))?[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\bhb\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "iron": [
                r"serum\s*iron[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\biron\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "ferritin": [
                r"ferritin[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "hematocrit": [
                r"hematocrit(?:\s*\([^\)]*\))?[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\bhct\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "rbc": [
                r"red\s*blood\s*(?:cells?|count)?(?:\s*\([^\)]*\))?[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\brbc\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "mcv": [
                r"mean\s*corpuscular\s*volume(?:\s*\([^\)]*\))?[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\bmcv\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "wbc": [
                r"white\s*blood\s*(?:cells?|count)?(?:\s*\([^\)]*\))?[\s:=\n\-]+([0-9]+\.?[0-9]*)",
                r"\bwbc\b[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ],
            "platelets": [
                r"platelets?[\s:=\n\-]+([0-9]+\.?[0-9]*)"
            ]
        }

        for key, regexes in patterns.items():
            for rgx in regexes:
                match = re.search(rgx, lower, re.MULTILINE)
                if match:
                    try:
                        val = float(match.group(1))
                        ref = REFERENCE_RANGES[key]
                        
                        # Unit check normalization (e.g. 6500 WBC -> 6.5)
                        if key == "wbc" and val > 1000:
                            val = round(val / 1000.0, 2)
                        elif key == "platelets" and val > 1000:
                            val = round(val / 1000.0, 1)

                        status = "NORMAL"
                        if val < ref["min"]:
                            status = "LOW"
                        elif val > ref["max"]:
                            status = "HIGH"

                        biomarkers.append({
                            "key": key,
                            "name": ref["name"],
                            "value": val,
                            "unit": ref["unit"],
                            "reference_range": f"{ref['min']} - {ref['max']} {ref['unit']}",
                            "status": status,
                            "role": ref["role"]
                        })
                        break
                    except ValueError:
                        continue

        return biomarkers

    def analyze(self, raw_text: str, filename: str = "blood_test_report.pdf") -> Dict[str, Any]:
        """
        Executes complete lab report interpretation:
        - Extracts values
        - Flags anomalies
        - Generates 8th-grade plain-language translation
        - Recommends dietary and specialist adjustments
        """
        biomarkers = self.parse_biomarkers(raw_text)

        low_markers = [b for b in biomarkers if b["status"] == "LOW"]
        high_markers = [b for b in biomarkers if b["status"] == "HIGH"]
        
        has_low_iron_or_hb = any(b["key"] in ["iron", "ferritin", "hemoglobin"] and b["status"] == "LOW" for b in biomarkers)

        # Plain Language Jargon Translation (8th-grade level)
        explanation_paragraphs = []
        explanation_paragraphs.append(
            f"We carefully examined your {filename}. Out of {len(biomarkers)} detected biomarkers, "
            f"{len(low_markers)} are lower than average and {len(high_markers)} are higher than average."
        )

        if has_low_iron_or_hb:
            explanation_paragraphs.append(
                "### Clinical Interpretation in Plain English:\n"
                "Your test shows that your **Iron or Hemoglobin levels are lower than normal**.\n\n"
                "- **Think of Hemoglobin like tiny delivery trucks** inside your bloodstream. Their job is to carry fresh oxygen from your lungs to your muscles, brain, and heart.\n"
                "- **Iron is the essential metal used to build those delivery trucks.**\n"
                "- When iron is low, fewer trucks are available. This explains why you might be experiencing **fatigue, sluggishness, cold hands or feet, mild dizziness, or feeling short of breath** during everyday walking."
            )
        else:
            explanation_paragraphs.append(
                "### Clinical Interpretation in Plain English:\n"
                "Your tested blood parameters are predominantly within standard reference boundaries, indicating stable cellular counts."
            )

        # Dietary Suggestions
        dietary_recommendations = []
        if has_low_iron_or_hb:
            dietary_recommendations = [
                "**Eat Iron-Dense Foods**: Incorporate foods like cooked lentils, chickpeas, dark leafy greens (spinach, kale), pumpkin seeds, and lean chicken or turkey into your meals.",
                "**Supercharge with Vitamin C**: Pair your iron foods with Vitamin C (such as a squeeze of lemon juice, orange slices, or bell peppers). Vitamin C acts like a magnet, helping your body absorb up to 3 times more plant-based iron!",
                "**Avoid Iron Blockers During Meals**: Try to avoid drinking black tea, coffee, or milk right when eating your main iron-rich meals, as the tannins and calcium can block your body from taking in the iron."
            ]

        summary = {
            "report_name": filename,
            "total_biomarkers_extracted": len(biomarkers),
            "abnormalities_count": len(low_markers) + len(high_markers),
            "biomarkers": biomarkers,
            "has_low_iron": has_low_iron_or_hb,
            "plain_explanation": "\n\n".join(explanation_paragraphs),
            "dietary_recommendations": dietary_recommendations,
            "recommended_specialist": "Hematologist or General Physician",
            "disclaimer": (
                "Lab analysis provided for informational and educational interpretation only. "
                "Do not start high-dose iron pills without clinical blood confirmation and advice from a doctor."
            )
        }

        return summary
