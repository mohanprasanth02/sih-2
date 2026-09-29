"""
Publication-Quality PDF User Operating Manual Generator
Non-Automatic Weighing Instruments (NAWI) Model Approval & Test Reporting System
As per OIML R 76-1:2006 & Legal Metrology Act, 2009
Department of Consumer Affairs (DoCA), Government of India
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "GOVERNMENT OF INDIA • DEPARTMENT OF CONSUMER AFFAIRS • LEGAL METROLOGY DIVISION")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 26, "OIML R 76 NAWI SYSTEM USER MANUAL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 36, 8.5 * inch - 36, 36)
        
        self.drawString(36, 24, "CONFIDENTIAL & STATUTORY • FOR OFFICIAL USE ONLY • OIML R 76-1:2006 (E)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 24, page_str)
        self.restoreState()


def build_manual_pdf(output_paths: list[str]):
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)

    primary_path = output_paths[0]
    doc = SimpleDocTemplate(
        primary_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        alignment=1, # Center
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=15
    )
    badge_style = ParagraphStyle(
        "GovBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F2942"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A")
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E3A8A")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A")
    )
    table_cell_pass = ParagraphStyle(
        "TableCellPass",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#047857")
    )
    table_cell_fail = ParagraphStyle(
        "TableCellFail",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#B91C1C")
    )

    story = []

    # =========================================================================
    # COVER / HEADER BANNER
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("GOVERNMENT OF INDIA • MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", badge_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS • LEGAL METROLOGY DIVISION", badge_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE & COMPLETE APPLICATION USER MANUAL", title_style))
    story.append(Paragraph(
        "<b>Comprehensive Guide with Exact Values, Form Fields, Regulatory Calculations & Operational Workflows for All System Scenarios</b><br/>"
        "Technical Authority: OIML R 76-1:2006 (E) & OIML R 76-2:2007 (E) | Legal Metrology (General) Rules, 2011",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F2942"), spaceAfter=12))

    # Document Metadata Callout Box
    meta_data = [
        [
            Paragraph("<b>Document Version:</b> 1.0.0 (Official)", table_cell),
            Paragraph("<b>Target Audience:</b> Inspectors, Supervisors, RRSL Officers, Manufacturers", table_cell),
        ],
        [
            Paragraph("<b>Effective Date:</b> 29 September 2026", table_cell),
            Paragraph("<b>Standard Implementation:</b> OIML R 76 Non-Automatic Weighing Instruments", table_cell),
        ],
        [
            Paragraph("<b>System URL:</b> http://localhost:3000 (Vite) / :8005 (FastAPI)", table_cell),
            Paragraph("<b>Database:</b> Relational Normalized Persistence (labelguard.db)", table_cell),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 1: SYSTEM ROLES & ACCESS CREDENTIALS
    # =========================================================================
    story.append(Paragraph("1. System Architecture & Role-Based Access Control (RBAC)", h1_style))
    story.append(Paragraph(
        "The system strictly regulates operational actions based on user roles enforced at the FastAPI backend layer. "
        "Each user must use their official authorized credentials. Below is the operational role matrix:",
        body_style
    ))

    roles_data = [
        [Paragraph("Role Name", table_cell_bold), Paragraph("Login Email", table_cell_bold), Paragraph("Password", table_cell_bold), Paragraph("Authorized Permissions & Operations", table_cell_bold)],
        [
            Paragraph("<b>Inspector / Test Engineer</b>", table_cell),
            Paragraph("inspector@legalmetrology.gov.in", table_cell),
            Paragraph("Inspector@123", table_cell),
            Paragraph("Create manufacturers, instruments, enter observations, upload photos, calculate compliance, submit draft evaluations for review.", table_cell)
        ],
        [
            Paragraph("<b>Supervisor / Reviewer</b>", table_cell),
            Paragraph("supervisor@legalmetrology.gov.in", table_cell),
            Paragraph("Supervisor@123", table_cell),
            Paragraph("Technical review of observations, request corrections with mandatory notes, approve compliant reports, apply digital sign, finalize certificates.", table_cell)
        ],
        [
            Paragraph("<b>Directorate Administrator</b>", table_cell),
            Paragraph("admin@legalmetrology.gov.in", table_cell),
            Paragraph("Admin@123", table_cell),
            Paragraph("Manage testing laboratories, equipment manufacturers, statutory rule versions, view immutable audit logs, system-wide overrides.", table_cell)
        ],
        [
            Paragraph("<b>Public / Field Viewer</b>", table_cell),
            Paragraph("viewer@legalmetrology.gov.in", table_cell),
            Paragraph("Viewer@123", table_cell),
            Paragraph("Read-only access. Search pattern approvals, inspect approved certificates, download official PDF/DOCX reports. Blocked from write actions (HTTP 403).", table_cell)
        ],
    ]
    t_roles = Table(roles_data, colWidths=[90, 130, 80, 240])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    for i in range(len(roles_data[0])):
        roles_data[0][i].style.textColor = colors.white
    story.append(t_roles)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 2: SCENARIO 1 - COMPLIANT NAWI BENCH SCALE
    # =========================================================================
    story.append(Paragraph("2. Scenario 1: End-to-End Compliant Evaluation (Class III Bench Scale - BPM-15)", h1_style))
    story.append(Paragraph(
        "<b>Objective:</b> Complete testing and certification for a Class III Non-Automatic Weighing Instrument with maximum capacity 15 kg "
        "and verification scale interval <i>e</i> = 5 g. All errors remain strictly within OIML R 76 Table 6 limits.",
        body_style
    ))

    story.append(Paragraph("Step 1.1: Instrument Technical Specifications & Laboratory Conditions", h2_style))
    spec_data = [
        [Paragraph("Field Name", table_cell_bold), Paragraph("Exact Value to Enter", table_cell_bold), Paragraph("Regulatory Clause / Metrological Rationale", table_cell_bold)],
        [Paragraph("Applicant Type", table_cell), Paragraph("Manufacturer", table_cell), Paragraph("Section 22, Legal Metrology Act, 2009", table_cell)],
        [Paragraph("Manufacturer Name", table_cell), Paragraph("Bharat Precision Metrology Ltd.", table_cell), Paragraph("Registered under Legal Metrology Central Rules", table_cell)],
        [Paragraph("Manufacturer Address", table_cell), Paragraph("Plot 42, Okhla Industrial Area Phase-III, New Delhi", table_cell), Paragraph("Physical manufacturing & assembly facility", table_cell)],
        [Paragraph("Model Designation", table_cell), Paragraph("BPM-15-DIGITAL", table_cell), Paragraph("Model / Pattern approval identification", table_cell)],
        [Paragraph("Instrument Type", table_cell), Paragraph("Non-Automatic Counter Scale", table_cell), Paragraph("OIML R 76-1 Clause 2.1 definition", table_cell)],
        [Paragraph("Accuracy Class", table_cell), Paragraph("Class III (Medium)", table_cell), Paragraph("OIML R 76 Table 3 classification", table_cell)],
        [Paragraph("Max Capacity (Max)", table_cell), Paragraph("15.000 kg", table_cell), Paragraph("Maximum weighing capacity without tare", table_cell)],
        [Paragraph("Min Capacity (Min)", table_cell), Paragraph("0.100 kg", table_cell), Paragraph("Min = 20 e = 20 × 0.005 kg = 0.100 kg (Clause 3.4.3)", table_cell)],
        [Paragraph("Verification Scale (e)", table_cell), Paragraph("0.005 kg (5 g)", table_cell), Paragraph("Scale interval used for type approval (Clause 3.2)", table_cell)],
        [Paragraph("Actual Scale Interval (d)", table_cell), Paragraph("0.005 kg (d = e)", table_cell), Paragraph("Clause 3.4.1 (d = e for standard digital indicators)", table_cell)],
        [Paragraph("Scale Intervals count (n)", table_cell), Paragraph("3,000", table_cell_pass), Paragraph("Calculated: n = Max / e = 15.0 / 0.005 = 3,000 (Complies with 100 <= n <= 10,000)", table_cell)],
        [Paragraph("Temperature Range", table_cell), Paragraph("-10°C to +40°C", table_cell), Paragraph("Standard temperature limit per Clause 3.9.2.1", table_cell)],
        [Paragraph("Testing Laboratory", table_cell), Paragraph("National Legal Metrology Type Evaluation Lab", table_cell), Paragraph("NABL ISO/IEC 17025 Accredited & OIML Issuing Authority", table_cell)],
        [Paragraph("Standard Weights Used", table_cell), Paragraph("Class M1 Working Standards (NPL Traceable)", table_cell), Paragraph("OIML R 111-1 certified reference standard masses", table_cell)],
    ]
    t_specs = Table(spec_data, colWidths=[130, 160, 250])
    t_specs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    for i in range(len(spec_data[0])):
        spec_data[0][i].style.textColor = colors.white
    story.append(t_specs)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Step 1.2: Clause A.4.4 Weighing Performance Test Data Entry", h2_style))
    story.append(Paragraph(
        "Perform weighing with increasing loads from Zero to Max, then decreasing back to Zero. For each point, determine the "
        "changeover turning point by adding small weights $\\Delta L = 0.1e$ until the indication steps up by $1d$.<br/>"
        "Formula: <b>$E = I + 0.5e - \\Delta L - L$</b>; Corrected error: <b>$E_c = E - E_0$</b>.",
        body_style
    ))

    weigh_data = [
        [Paragraph("Dir", table_cell_bold), Paragraph("Load (L)", table_cell_bold), Paragraph("Indication (I)", table_cell_bold), Paragraph("Add Load (ΔL)", table_cell_bold), Paragraph("Corr Error (Ec)", table_cell_bold), Paragraph("MPE Limit", table_cell_bold), Paragraph("Clause / Result", table_cell_bold)],
        [Paragraph("INCR", table_cell), Paragraph("0.000 kg", table_cell), Paragraph("0.000 kg", table_cell), Paragraph("0.0025 kg", table_cell), Paragraph("0.0000 kg", table_cell), Paragraph("±0.0025 kg (0.5e)", table_cell), Paragraph("Zero Reference / PASS", table_cell_pass)],
        [Paragraph("INCR", table_cell), Paragraph("0.500 kg (100e)", table_cell), Paragraph("0.500 kg", table_cell), Paragraph("0.0025 kg", table_cell), Paragraph("0.0000 kg", table_cell), Paragraph("±0.0025 kg (0.5e)", table_cell), Paragraph("Table 6 Step 1 / PASS", table_cell_pass)],
        [Paragraph("INCR", table_cell), Paragraph("2.500 kg (500e)", table_cell), Paragraph("2.500 kg", table_cell), Paragraph("0.0025 kg", table_cell), Paragraph("0.0000 kg", table_cell), Paragraph("±0.0025 kg (0.5e)", table_cell), Paragraph("500e Boundary / PASS", table_cell_pass)],
        [Paragraph("INCR", table_cell), Paragraph("5.000 kg (1000e)", table_cell), Paragraph("5.000 kg", table_cell), Paragraph("0.0020 kg", table_cell), Paragraph("+0.0005 kg", table_cell), Paragraph("±0.0050 kg (1.0e)", table_cell), Paragraph("Table 6 Step 2 / PASS", table_cell_pass)],
        [Paragraph("INCR", table_cell), Paragraph("10.000 kg (2000e)", table_cell), Paragraph("10.000 kg", table_cell), Paragraph("0.0015 kg", table_cell), Paragraph("+0.0010 kg", table_cell), Paragraph("±0.0050 kg (1.0e)", table_cell), Paragraph("2000e Boundary / PASS", table_cell_pass)],
        [Paragraph("INCR", table_cell), Paragraph("15.000 kg (3000e)", table_cell), Paragraph("15.000 kg", table_cell), Paragraph("0.0010 kg", table_cell), Paragraph("+0.0015 kg", table_cell), Paragraph("±0.0075 kg (1.5e)", table_cell), Paragraph("Max Capacity / PASS", table_cell_pass)],
        [Paragraph("DECR", table_cell), Paragraph("10.000 kg", table_cell), Paragraph("10.000 kg", table_cell), Paragraph("0.0018 kg", table_cell), Paragraph("+0.0007 kg", table_cell), Paragraph("±0.0050 kg (1.0e)", table_cell), Paragraph("Hysteresis = 0.3g / PASS", table_cell_pass)],
        [Paragraph("DECR", table_cell), Paragraph("5.000 kg", table_cell), Paragraph("5.000 kg", table_cell), Paragraph("0.0022 kg", table_cell), Paragraph("+0.0003 kg", table_cell), Paragraph("±0.0050 kg (1.0e)", table_cell), Paragraph("Hysteresis = 0.2g / PASS", table_cell_pass)],
        [Paragraph("DECR", table_cell), Paragraph("0.000 kg", table_cell), Paragraph("0.000 kg", table_cell), Paragraph("0.0025 kg", table_cell), Paragraph("0.0000 kg", table_cell), Paragraph("±0.0025 kg (0.5e)", table_cell), Paragraph("Zero Return / PASS", table_cell_pass)],
    ]
    t_weigh = Table(weigh_data, colWidths=[40, 95, 80, 80, 80, 85, 80])
    t_weigh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    for i in range(len(weigh_data[0])):
        weigh_data[0][i].style.textColor = colors.white
    story.append(t_weigh)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Step 1.3: Clause A.4.10 Repeatability & Clause A.4.7 Eccentricity Test Data", h2_style))
    rep_data = [
        [Paragraph("Test Battery", table_cell_bold), Paragraph("Applied Test Load", table_cell_bold), Paragraph("Recorded Indications / Runs", table_cell_bold), Paragraph("Spread / Max Difference", table_cell_bold), Paragraph("Permissible Limit & Status", table_cell_bold)],
        [
            Paragraph("<b>Clause A.4.10 Repeatability</b>", table_cell),
            Paragraph("15.000 kg (Max)", table_cell),
            Paragraph("Run 1: 15.000 kg<br/>Run 2: 15.005 kg<br/>Run 3: 15.000 kg<br/>Run 4: 15.000 kg<br/>Run 5: 15.005 kg", table_cell),
            Paragraph("Max Diff: <b>0.005 kg</b><br/>(15.005 - 15.000)", table_cell),
            Paragraph("Limit: |MPE| = 0.0075 kg<br/><b>COMPLIANT (PASS)</b>", table_cell_pass)
        ],
        [
            Paragraph("<b>Clause A.4.7 Eccentricity</b> (Corner Loading)", table_cell),
            Paragraph("5.000 kg (1/3 Max)", table_cell),
            Paragraph("Pos 1 (Center): 5.000 kg (E=0.0)<br/>Pos 2 (Front-Left): 5.000 kg (E=0.0)<br/>Pos 3 (Rear-Left): 5.005 kg (E=+0.5e)<br/>Pos 4 (Rear-Right): 5.000 kg (E=0.0)<br/>Pos 5 (Front-Right): 5.000 kg (E=0.0)", table_cell),
            Paragraph("Max Error: <b>+0.0025 kg</b> (+0.5e)", table_cell),
            Paragraph("Limit: |MPE| = 0.0050 kg (1.0e)<br/><b>COMPLIANT (PASS)</b>", table_cell_pass)
        ]
    ]
    t_rep = Table(rep_data, colWidths=[110, 80, 160, 90, 100])
    t_rep.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    for i in range(len(rep_data[0])):
        rep_data[0][i].style.textColor = colors.white
    story.append(t_rep)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: SCENARIO 2 - NON-COMPLIANCE & REJECTION WORKFLOW
    # =========================================================================
    story.append(Paragraph("3. Scenario 2: Non-Compliance & Pattern Approval Rejection (Defective Load Cell)", h1_style))
    story.append(Paragraph(
        "<b>Objective:</b> Demonstrate how the calculation engine detects and flags excessive error violating OIML R 76 Table 6, "
        "and how the supervisor executes a statutory rejection under the Legal Metrology Act.",
        body_style
    ))

    fail_data = [
        [Paragraph("Parameter", table_cell_bold), Paragraph("Defective Test Input Value", table_cell_bold), Paragraph("Engine Evaluation & Non-Compliance Finding", table_cell_bold)],
        [Paragraph("Instrument Model", table_cell), Paragraph("DEFECT-20-FAIL", table_cell), Paragraph("Class III Electronic Retail Scale (Max: 20 kg, e = 5 g)", table_cell)],
        [Paragraph("Test Load Applied", table_cell), Paragraph("10.000 kg (2,000 e)", table_cell), Paragraph("Boundary load between Step 2 and Step 3 MPE tier", table_cell)],
        [Paragraph("Indicated Reading (I)", table_cell), Paragraph("10.015 kg", table_cell_fail), Paragraph("Instrument displays 15 grams over nominal weight", table_cell)],
        [Paragraph("Add-Load Turning (ΔL)", table_cell), Paragraph("0.0025 kg (0.5 e)", table_cell), Paragraph("Flash point changeover measurement", table_cell)],
        [Paragraph("Calculated Error (Ec)", table_cell), Paragraph("+0.0125 kg (+2.5 e)", table_cell_fail), Paragraph("E = 10.015 + 0.0025 - 0.0025 - 10.000 = +0.0150 kg; Ec = +0.0125 kg", table_cell)],
        [Paragraph("OIML R 76 Table 6 MPE", table_cell), Paragraph("±0.0050 kg (±1.0 e)", table_cell), Paragraph("Maximum Permissible Error at 10.0 kg is 1.0 e (5 grams)", table_cell)],
        [Paragraph("Engine Compliance Status", table_cell), Paragraph("NON_COMPLIANT (FAIL)", table_cell_fail), Paragraph("Violation: Measured error (+12.5 g) exceeds permissible limit (5.0 g) by 250%", table_cell)],
        [Paragraph("Supervisor Action", table_cell), Paragraph("Click 'Reject' Button", table_cell_bold), Paragraph("Enter statutory rejection grounds in modal; system records immutable REJECT status", table_cell)],
    ]
    t_fail = Table(fail_data, colWidths=[120, 140, 280])
    t_fail.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7F1D1D")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FEF2F2")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    for i in range(len(fail_data[0])):
        fail_data[0][i].style.textColor = colors.white
    story.append(t_fail)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: SCENARIO 3 - SUPERVISORY REVIEW & CORRECTIONS WORKFLOW
    # =========================================================================
    story.append(Paragraph("4. Scenario 3: Supervisory Technical Review & Correction Request Cycle", h1_style))
    story.append(Paragraph(
        "The workflow strictly enforces the legal hierarchy between Test Engineers and Supervisors:",
        body_style
    ))

    flow_steps = [
        [Paragraph("Step #", table_cell_bold), Paragraph("Actor & Role", table_cell_bold), Paragraph("UI Action / Screen", table_cell_bold), Paragraph("State Transition & Backend Event", table_cell_bold)],
        [
            Paragraph("1", table_cell),
            Paragraph("Inspector (Rajesh Sharma)", table_cell),
            Paragraph("Repository Detail Drawer &bull; Click <b>'Submit for Review'</b>", table_cell),
            Paragraph("Status transitions <b>DRAFT &rarr; SUBMITTED</b>. System logs audit record.", table_cell)
        ],
        [
            Paragraph("2", table_cell),
            Paragraph("Supervisor (Priya V. Iyer)", table_cell),
            Paragraph("Top Header Switcher &bull; Switch to <b>Supervisor Role</b> &bull; Click <b>'Begin Review'</b>", table_cell),
            Paragraph("Status transitions <b>SUBMITTED &rarr; UNDER_REVIEW</b>. Technical review lock engaged.", table_cell)
        ],
        [
            Paragraph("3", table_cell),
            Paragraph("Supervisor (Priya V. Iyer)", table_cell),
            Paragraph("Click <b>'Request Correction'</b> &bull; Enter note: <i>'Re-verify corner 3 eccentric loading; attach calibration certificate for F2 masses.'</i>", table_cell),
            Paragraph("Status transitions <b>UNDER_REVIEW &rarr; CORRECTION_REQUIRED</b>. Report returned to Inspector queue.", table_cell)
        ],
        [
            Paragraph("4", table_cell),
            Paragraph("Inspector (Rajesh Sharma)", table_cell),
            Paragraph("Evidence Tab &bull; Upload calibration cert &bull; Click <b>'Submit for Review'</b>", table_cell),
            Paragraph("Status transitions <b>CORRECTION_REQUIRED &rarr; SUBMITTED</b>. Ready for final review.", table_cell)
        ],
        [
            Paragraph("5", table_cell),
            Paragraph("Supervisor (Priya V. Iyer)", table_cell),
            Paragraph("Begin Review &bull; Verify all 7 batteries PASS &bull; Click <b>'Approve Report'</b>", table_cell),
            Paragraph("Status transitions <b>UNDER_REVIEW &rarr; APPROVED_COMPLIANT</b>.", table_cell_pass)
        ],
    ]
    t_flow = Table(flow_steps, colWidths=[35, 110, 185, 210])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    for i in range(len(flow_steps[0])):
        flow_steps[0][i].style.textColor = colors.white
    story.append(t_flow)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: SCENARIO 4 - DIGITAL CERTIFICATION & ARTIFACT EXPORT
    # =========================================================================
    story.append(Paragraph("5. Scenario 4: Digital Signing, Versioning & Document Export (PDF / Word)", h1_style))
    story.append(Paragraph(
        "Upon reaching <b>APPROVED_COMPLIANT</b> status, the supervisor applies a cryptographic digital signature stamp "
        "under Section 22 of the Legal Metrology Act, 2009. The document is permanently sealed into an immutable archive.",
        body_style
    ))

    sign_data = [
        [Paragraph("Signing Step", table_cell_bold), Paragraph("Required Input / Parameter", table_cell_bold), Paragraph("Output & Verification Metric", table_cell_bold)],
        [
            Paragraph("1. Digital Sign Modal", table_cell),
            Paragraph("Signing Officer: <b>Dr. Priya V. Iyer</b><br/>Designation: <b>Assistant Controller (Metrology)</b><br/>Remarks: Officially certified under Sec 22", table_cell),
            Paragraph("Generates 128-bit Signature Token & Cryptographic Token: <b>VERIFIED_AUTHENTIC</b>", table_cell)
        ],
        [
            Paragraph("2. SHA-256 Checksum", table_cell),
            Paragraph("Calculated across Report #, Model, Max, e, Status, and Test Summaries", table_cell),
            Paragraph("Example: <b>9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08</b>", table_cell)
        ],
        [
            Paragraph("3. Finalize Certificate", table_cell),
            Paragraph("Click <b>'Finalize & Lock Certificate'</b> button in Repository Drawer", table_cell),
            Paragraph("Status transitions to <b>FINALIZED</b>. Report is locked. Creates record in <code>report_versions</code>.", table_cell)
        ],
        [
            Paragraph("4. PDF Export", table_cell),
            Paragraph("Click <b>'Download PDF'</b> in Quick Actions Bar", table_cell),
            Paragraph("Streams official printable PDF with Government Emblem, Ashoka Seal, and table batteries.", table_cell)
        ],
        [
            Paragraph("5. Word (.docx) Export", table_cell),
            Paragraph("Click <b>'Download Word (.docx)'</b> in Quick Actions Bar", table_cell),
            Paragraph("Streams fully editable MS Word report for departmental filing.", table_cell)
        ],
    ]
    t_sign = Table(sign_data, colWidths=[120, 200, 220])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    for i in range(len(sign_data[0])):
        sign_data[0][i].style.textColor = colors.white
    story.append(t_sign)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: SCENARIO 5 - EVIDENCE UPLOAD & IMMUTABLE AUDIT LOG
    # =========================================================================
    story.append(Paragraph("6. Scenario 5: Uploading Physical Evidence & Inspecting Audit Logs", h1_style))
    story.append(Paragraph(
        "Every official type approval must include photographic documentation of the instrument, its rating nameplate, "
        "and traceable calibration certificates.",
        body_style
    ))

    story.append(Paragraph("<b>Attachment Upload Rules:</b><br/>"
                           "• Allowed formats: PNG, JPG, JPEG, WEBP, PDF, DOCX.<br/>"
                           "• Maximum file size: 15 MB per file.<br/>"
                           "• Upload categories: <code>INSTRUMENT_PHOTO</code>, <code>MARKING_PLATE</code>, <code>TEST_SETUP</code>, <code>CALIBRATION_CERTIFICATE</code>.<br/>"
                           "• Access: Inspect through the <b>'Evidence'</b> tab in the Evaluation Drawer.", body_style))

    story.append(Paragraph("<b>Audit Trail Verification:</b><br/>"
                           "Click the <b>'Audit Trail'</b> tab in the Evaluation Drawer. The system displays chronological, tamper-evident logs "
                           "recording: User ID, Timestamp, Action (e.g. <code>STATUS_TRANSITION_SUBMIT</code>, <code>ATTACHMENT_UPLOADED</code>, <code>DIGITAL_SIGNATURE_APPLIED</code>), "
                           "and previous vs. updated values.", body_style))
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 7: SCENARIO 6 - DUAL-ENGINE PACKAGED COMMODITIES RULES 2011
    # =========================================================================
    story.append(Paragraph("7. Scenario 6: Packaged Commodities Rules 2011 Compliance Verification", h1_style))
    story.append(Paragraph(
        "In addition to OIML R 76 NAWI weighing instruments, the application includes the Legal Metrology (Packaged Commodities) Rules, 2011 module:",
        body_style
    ))
    story.append(Paragraph(
        "1. Click the <b>Module Switcher</b> in the top navigation bar and select <b>'Packaged Commodities (Rules 2011)'</b>.<br/>"
        "2. Navigate to <b>'Verify Product'</b> tab.<br/>"
        "3. Upload product packaging images (Front, Back, Side).<br/>"
        "4. The integrated AI OCR pipeline extracts statutory declarations: <b>MRP (inclusive of all taxes)</b>, <b>Net Quantity (standard SI units)</b>, <b>Unit Sale Price (USP)</b>, <b>Month & Year of Manufacture</b>, and <b>Consumer Care Details</b>.<br/>"
        "5. The rule engine validates each declaration deterministically against Rule 6 statutory mandates and generates a violation breakdown if prohibited units or missing declarations are detected.",
        body_style
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # STATUTORY SIGN-OFF FOOTER
    # =========================================================================
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))
    story.append(Paragraph(
        "<b>OFFICIAL NOTICE:</b> This manual has been verified against OIML Recommendation R 76-1:2006 (E), "
        "OIML R 76-2:2007 (E), and the Legal Metrology (General) Rules, 2011 (Seventh Schedule). All calculations "
        "and tolerance limits depicted herein are statutory and binding on all accredited Regional Reference Standard Laboratories "
        "(RRSL) and Type Evaluation Testing Centers under the Department of Consumer Affairs, Government of India.",
        callout_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)

    # Copy to all target paths
    for p in output_paths[1:]:
        import shutil
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy2(primary_path, p)

    print(f"Manual successfully generated at:\n - " + "\n - ".join(output_paths))


if __name__ == "__main__":
    targets = [
        "docs/NAWI_OIML_R76_Application_User_Manual.pdf",
        "reports/generated/NAWI_OIML_R76_Application_User_Manual.pdf",
        "uploads/NAWI_OIML_R76_Application_User_Manual.pdf"
    ]
    build_manual_pdf(targets)
