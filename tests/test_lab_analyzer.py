import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.lab_report_analyzer import LabReportAnalyzer

analyzer = LabReportAnalyzer()
pdf_path = "sample_reports/patient_cbc_iron_deficiency.pdf"
raw_text = analyzer.extract_text_from_pdf(pdf_path)

analysis = analyzer.analyze(raw_text, filename="patient_cbc_iron_deficiency.pdf")
print("=" * 70)
print(f"REPORT: {analysis['report_name']}")
print(f"Total Biomarkers: {analysis['total_biomarkers_extracted']}")
print(f"Has Low Iron: {analysis['has_low_iron']}")
print("-" * 70)
for b in analysis["biomarkers"]:
    print(f"  {b['name']:<30} | {b['value']} {b['unit']:<10} | [{b['status']}] (Ref: {b['reference_range']})")
print("-" * 70)
print("PLAIN LANGUAGE EXPLANATION:")
print(analysis["plain_explanation"])
print("-" * 70)
print("DIETARY RECOMMENDATIONS:")
for d in analysis["dietary_recommendations"]:
    print(f"- {d}")
print("=" * 70)
