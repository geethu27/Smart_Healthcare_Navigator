import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf_report(filename, title, patient_name, age, sex, test_date, biomarkers_data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A')
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#4B5563')
    )
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14
    )

    story.append(Paragraph("METRO DIAGNOSTICS & CLINICAL LABORATORY", title_style))
    story.append(Paragraph("100 Medical Center Way | CAP & CLIA Certified Clinical Facility", subtitle_style))
    story.append(Spacer(1, 15))

    # Patient Details Box
    patient_info = [
        [Paragraph(f"<b>Patient Name:</b> {patient_name}", meta_style), Paragraph(f"<b>MRN:</b> MDX-{abs(hash(patient_name)) % 90000 + 10000}", meta_style)],
        [Paragraph(f"<b>Age / Sex:</b> {age} / {sex}", meta_style), Paragraph(f"<b>Collection Date:</b> {test_date}", meta_style)],
        [Paragraph(f"<b>Referring Physician:</b> Dr. Robert Chen, MD", meta_style), Paragraph(f"<b>Test Panel:</b> {title}", meta_style)]
    ]
    t_patient = Table(patient_info, colWidths=[270, 270])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 20))

    # Table of Biomarkers
    headers = [
        Paragraph("<b>Biomarker / Test Name</b>", meta_style),
        Paragraph("<b>Result</b>", meta_style),
        Paragraph("<b>Flag</b>", meta_style),
        Paragraph("<b>Reference Range</b>", meta_style),
        Paragraph("<b>Units</b>", meta_style)
    ]
    table_rows = [headers]

    for item in biomarkers_data:
        flag_color = '#DC2626' if item['flag'] in ['LOW', 'HIGH'] else '#16A34A'
        flag_p = Paragraph(f"<font color='{flag_color}'><b>{item['flag']}</b></font>", meta_style)
        row = [
            Paragraph(item['name'], meta_style),
            Paragraph(f"<b>{item['value']}</b>", meta_style),
            flag_p,
            Paragraph(item['range'], meta_style),
            Paragraph(item['unit'], meta_style)
        ]
        table_rows.append(row)

    t_bio = Table(table_rows, colWidths=[180, 80, 70, 130, 80])
    t_bio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E7FF')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_bio)
    story.append(Spacer(1, 20))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.HexColor('#6B7280')
    )
    story.append(Paragraph("DISCLAIMER: Laboratory findings should be correlated with clinical history and physical examination by the treating physician.", footer_style))

    doc.build(story)
    print(f"Generated PDF: {filename}")

if __name__ == "__main__":
    # 1. Low Iron CBC Panel
    low_iron_data = [
        {"name": "Hemoglobin (Hb)", "value": "9.8", "flag": "LOW", "range": "12.0 - 16.5", "unit": "g/dL"},
        {"name": "Serum Iron", "value": "36.0", "flag": "LOW", "range": "60.0 - 170.0", "unit": "mcg/dL"},
        {"name": "Ferritin", "value": "12.0", "flag": "LOW", "range": "30.0 - 300.0", "unit": "ng/mL"},
        {"name": "Hematocrit (Hct)", "value": "31.2", "flag": "LOW", "range": "36.0 - 48.0", "unit": "%"},
        {"name": "Red Blood Cells (RBC)", "value": "3.85", "flag": "LOW", "range": "4.20 - 5.80", "unit": "x10^6/mcL"},
        {"name": "Mean Corpuscular Volume (MCV)", "value": "73.5", "flag": "LOW", "range": "80.0 - 100.0", "unit": "fL"},
        {"name": "White Blood Cells (WBC)", "value": "6.8", "flag": "NORMAL", "range": "4.5 - 11.0", "unit": "x10^3/mcL"},
        {"name": "Platelets", "value": "245.0", "flag": "NORMAL", "range": "150.0 - 450.0", "unit": "x10^3/mcL"}
    ]
    create_pdf_report(
        "sample_reports/patient_cbc_iron_deficiency.pdf",
        "Complete Blood Count (CBC) with Iron Panel",
        "Jane Doe", "34", "Female", "2026-09-20",
        low_iron_data
    )

    # 2. Normal CBC Panel
    normal_data = [
        {"name": "Hemoglobin (Hb)", "value": "14.2", "flag": "NORMAL", "range": "12.0 - 16.5", "unit": "g/dL"},
        {"name": "Serum Iron", "value": "98.0", "flag": "NORMAL", "range": "60.0 - 170.0", "unit": "mcg/dL"},
        {"name": "Ferritin", "value": "115.0", "flag": "NORMAL", "range": "30.0 - 300.0", "unit": "ng/mL"},
        {"name": "Hematocrit (Hct)", "value": "42.5", "flag": "NORMAL", "range": "36.0 - 48.0", "unit": "%"},
        {"name": "Red Blood Cells (RBC)", "value": "4.75", "flag": "NORMAL", "range": "4.20 - 5.80", "unit": "x10^6/mcL"},
        {"name": "Mean Corpuscular Volume (MCV)", "value": "88.0", "flag": "NORMAL", "range": "80.0 - 100.0", "unit": "fL"},
        {"name": "White Blood Cells (WBC)", "value": "7.2", "flag": "NORMAL", "range": "4.5 - 11.0", "unit": "x10^3/mcL"},
        {"name": "Platelets", "value": "270.0", "flag": "NORMAL", "range": "150.0 - 450.0", "unit": "x10^3/mcL"}
    ]
    create_pdf_report(
        "sample_reports/patient_cbc_normal.pdf",
        "Comprehensive Complete Blood Count (CBC)",
        "John Smith", "45", "Male", "2026-09-22",
        normal_data
    )
