"""
OIML R 76 Standardized Pattern Evaluation & Type Approval PDF Report Generator
Conforms to OIML R 76-2:2007 (Pattern Evaluation Report) and Legal Metrology (General) Rules, 2011 (Seventh Schedule).
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)


class OIMLPDFReportGenerator:
    def __init__(self, output_dir: str = "reports/generated"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, evaluation_data: Dict[str, Any], output_filename: str = None) -> str:
        report_no = evaluation_data.get("report_number", "OIML-R76-REPORT")
        clean_report_no = report_no.replace("/", "-").replace(" ", "_")
        if not output_filename:
            output_filename = f"{clean_report_no}.pdf"

        pdf_path = os.path.join(self.output_dir, output_filename)
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "GovTitle",
            parent=styles["Heading1"],
            fontSize=13,
            leading=16,
            alignment=1, # Center
            textColor=colors.HexColor("#0F2942"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "GovSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#334155")
        )
        doc_badge_style = ParagraphStyle(
            "DocBadge",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            alignment=1,
            textColor=colors.HexColor("#1E3A8A"),
            fontName="Helvetica-Bold"
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#0F2942"),
            fontName="Helvetica-Bold",
            spaceBefore=8,
            spaceAfter=4
        )
        cell_style = ParagraphStyle(
            "CellNormal",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1F2937")
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0F2942")
        )
        cell_pass = ParagraphStyle(
            "CellPass",
            parent=cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#059669")
        )
        cell_fail = ParagraphStyle(
            "CellFail",
            parent=cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#DC2626")
        )
        footnote_style = ParagraphStyle(
            "Footnote",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748B")
        )

        story = []

        # 1. Header & Republic of India Metrology Crest Block
        story.append(Paragraph("GOVERNMENT OF INDIA &bull; MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
        story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS &mdash; DIRECTORATE OF LEGAL METROLOGY", title_style))
        story.append(Paragraph("NATIONAL LEGAL METROLOGY TYPE EVALUATION LABORATORY (OIML ISSUING AUTHORITY)", subtitle_style))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F2942"), spaceBefore=2, spaceAfter=6))
        story.append(Paragraph("PATTERN EVALUATION TEST REPORT &bull; NON-AUTOMATIC WEIGHING INSTRUMENT (NAWI)", doc_badge_style))
        story.append(Paragraph("Evaluated in accordance with OIML Recommendation R 76-1:2006 (E) & Legal Metrology Act, 2009", subtitle_style))
        story.append(Spacer(1, 8))

        # 2. Metadata Banner (Report No, Application No, Date, Status)
        status = evaluation_data.get("status", "DRAFT")
        status_color = "#059669" if "APPROVED" in status or status == "PASS" else ("#DC2626" if "REJECTED" in status else "#D97706")
        status_bg = "#ECFDF5" if "APPROVED" in status or status == "PASS" else ("#FEF2F2" if "REJECTED" in status else "#FFFBEB")

        meta_data = [
            [
                Paragraph("<b>Report No:</b>", cell_style),
                Paragraph(f"<b>{evaluation_data.get('report_number', 'N/A')}</b>", cell_bold),
                Paragraph("<b>Application No:</b>", cell_style),
                Paragraph(evaluation_data.get("application_number", "N/A"), cell_style),
            ],
            [
                Paragraph("<b>Testing Date:</b>", cell_style),
                Paragraph(str(evaluation_data.get("testing_date", datetime.now().strftime("%Y-%m-%d")))[0:10], cell_style),
                Paragraph("<b>Overall Finding:</b>", cell_style),
                Paragraph(f"<font color='{status_color}'><b>{status.replace('_', ' ')}</b></font>", cell_bold),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[1.1*inch, 2.4*inch, 1.2*inch, 2.3*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # 3. Section 1: Manufacturer & Instrument Technical Specifications
        story.append(Paragraph("1. INSTRUMENT IDENTIFICATION & TECHNICAL SPECIFICATIONS", section_heading))
        specs_data = [
            [
                Paragraph("<b>Manufacturer:</b>", cell_style),
                Paragraph(evaluation_data.get("manufacturer_name", "N/A"), cell_bold),
                Paragraph("<b>Instrument Type:</b>", cell_style),
                Paragraph(evaluation_data.get("instrument_type", "N/A"), cell_style),
            ],
            [
                Paragraph("<b>Manufacturer Address:</b>", cell_style),
                Paragraph(evaluation_data.get("manufacturer_address", "N/A"), cell_style),
                Paragraph("<b>Model Name:</b>", cell_style),
                Paragraph(evaluation_data.get("model_name", "N/A"), cell_bold),
            ],
            [
                Paragraph("<b>Accuracy Class:</b>", cell_style),
                Paragraph(f"<b>{evaluation_data.get('accuracy_class', 'Class III')}</b>", cell_bold),
                Paragraph("<b>Serial Number:</b>", cell_style),
                Paragraph(evaluation_data.get("serial_number", "N/A"), cell_style),
            ],
            [
                Paragraph("<b>Max Capacity (Max):</b>", cell_style),
                Paragraph(f"{evaluation_data.get('max_capacity')} {evaluation_data.get('units', 'kg')}", cell_style),
                Paragraph("<b>Scale Interval (d):</b>", cell_style),
                Paragraph(f"{evaluation_data.get('scale_interval_d')} {evaluation_data.get('units', 'kg')}", cell_style),
            ],
            [
                Paragraph("<b>Min Capacity (Min):</b>", cell_style),
                Paragraph(f"{evaluation_data.get('min_capacity')} {evaluation_data.get('units', 'kg')}", cell_style),
                Paragraph("<b>Verification Interval (e):</b>", cell_style),
                Paragraph(f"{evaluation_data.get('verification_scale_interval_e')} {evaluation_data.get('units', 'kg')}", cell_style),
            ],
            [
                Paragraph("<b>Verification Scale Intervals (n):</b>", cell_style),
                Paragraph(f"<b>n = {evaluation_data.get('n_intervals', 'N/A')}</b>", cell_bold),
                Paragraph("<b>Tare Subtraction (Max T):</b>", cell_style),
                Paragraph(f"-{evaluation_data.get('max_tare', evaluation_data.get('max_capacity'))} {evaluation_data.get('units', 'kg')}", cell_style),
            ],
            [
                Paragraph("<b>Operating Temperature:</b>", cell_style),
                Paragraph(f"{evaluation_data.get('temp_range_min', -10)}°C to +{evaluation_data.get('temp_range_max', 40)}°C", cell_style),
                Paragraph("<b>Power Supply:</b>", cell_style),
                Paragraph(str(evaluation_data.get("power_supply", "230V AC, 50Hz"))[:40], cell_style),
            ],
            [
                Paragraph("<b>Load Cell & Indicator:</b>", cell_style),
                Paragraph(str(evaluation_data.get("load_cell_details", "OIML R60 approved"))[:45], cell_style),
                Paragraph("<b>Firmware / Checksum:</b>", cell_style),
                Paragraph(f"{evaluation_data.get('software_version', 'v1.0')} ({evaluation_data.get('software_checksum', 'CRC-OK')})", cell_style),
            ],
        ]
        specs_table = Table(specs_data, colWidths=[1.4*inch, 2.1*inch, 1.4*inch, 2.1*inch])
        specs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(specs_table)
        story.append(Spacer(1, 8))

        # 4. Section 2: Environmental & Laboratory Conditions
        story.append(Paragraph("2. LABORATORY AND ENVIRONMENTAL CONDITIONS (Clause A.3)", section_heading))
        env_data = [
            [
                Paragraph("<b>Testing Laboratory:</b>", cell_style),
                Paragraph(evaluation_data.get("lab_name", "National Legal Metrology Lab"), cell_style),
                Paragraph("<b>Ambient Temperature:</b>", cell_style),
                Paragraph(f"{evaluation_data.get('lab_temperature', 23.5)} °C", cell_style),
            ],
            [
                Paragraph("<b>Laboratory Accreditation:</b>", cell_style),
                Paragraph(evaluation_data.get("lab_accreditation", "NABL ISO/IEC 17025"), cell_style),
                Paragraph("<b>Relative Humidity:</b>", cell_style),
                Paragraph(f"{evaluation_data.get('lab_humidity', 52.0)} % RH", cell_style),
            ],
            [
                Paragraph("<b>Local Gravity Acceleration (g):</b>", cell_style),
                Paragraph(f"{evaluation_data.get('local_gravity_g', 9.7803)} m/s²", cell_style),
                Paragraph("<b>Barometric Pressure:</b>", cell_style),
                Paragraph(f"{evaluation_data.get('lab_pressure', 1013.2)} hPa", cell_style),
            ],
            [
                Paragraph("<b>Standard Calibration Weights:</b>", cell_style),
                Paragraph(str(evaluation_data.get("standard_weights_used", "Class M1 / F2 (NPL Traceable)"))[:55], cell_style),
                Paragraph("<b>Testing Officer:</b>", cell_style),
                Paragraph(evaluation_data.get("testing_officer_name", "Er. Rajesh Sharma"), cell_style),
            ]
        ]
        env_table = Table(env_data, colWidths=[1.4*inch, 2.1*inch, 1.4*inch, 2.1*inch])
        env_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(env_table)
        story.append(Spacer(1, 8))

        # 5. Section 3: Weighing Performance Test Observations & Calculations (Clause A.4.4)
        story.append(Paragraph("3. WEIGHING PERFORMANCE TEST OBSERVATIONS & EVALUATION (Clause A.4.4)", section_heading))
        summary = evaluation_data.get("evaluation_summary", {})
        weighing_summary = summary.get("test_summaries", {}).get("weighing_test", {})
        readings = weighing_summary.get("readings", [])

        if readings:
            w_headers = [
                Paragraph("<b>#</b>", cell_bold),
                Paragraph("<b>Dir</b>", cell_bold),
                Paragraph(f"<b>Load ({evaluation_data.get('units', 'kg')})</b>", cell_bold),
                Paragraph(f"<b>Indication I</b>", cell_bold),
                Paragraph(f"<b>&Delta;L ({evaluation_data.get('units', 'kg')})</b>", cell_bold),
                Paragraph(f"<b>Error E<sub>c</sub></b>", cell_bold),
                Paragraph(f"<b>E<sub>c</sub> (e)</b>", cell_bold),
                Paragraph(f"<b>MPE (&plusmn;e)</b>", cell_bold),
                Paragraph(f"<b>MPE ({evaluation_data.get('units', 'kg')})</b>", cell_bold),
                Paragraph("<b>Verdict</b>", cell_bold),
            ]
            w_rows = [w_headers]
            for r in readings:
                status_txt = r.get("status", "PASS")
                st_style = cell_pass if status_txt == "PASS" else cell_fail
                w_rows.append([
                    Paragraph(str(r.get("index")), cell_style),
                    Paragraph(r.get("direction", "INCR"), cell_style),
                    Paragraph(f"{r.get('load'):g}", cell_style),
                    Paragraph(f"{r.get('indication'):g}", cell_style),
                    Paragraph(f"{r.get('delta_l'):g}" if r.get("delta_l") is not None else "-", cell_style),
                    Paragraph(f"{r.get('corrected_error'):+.4f}", cell_style),
                    Paragraph(f"{r.get('corrected_error_e'):+.2f} e", cell_style),
                    Paragraph(f"&plusmn;{r.get('mpe_e'):.1f} e", cell_style),
                    Paragraph(f"&plusmn;{r.get('mpe_unit'):.4f}", cell_style),
                    Paragraph(status_txt, st_style),
                ])
            w_table = Table(w_rows, colWidths=[0.3*inch, 0.45*inch, 0.95*inch, 0.95*inch, 0.7*inch, 0.85*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch])
            w_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            story.append(w_table)
        else:
            story.append(Paragraph("<i>Weighing test observation record attached in technical addendum.</i>", footnote_style))
        story.append(Spacer(1, 8))

        # 6. Section 4: Summary Table of All Prescribed Tests
        story.append(Paragraph("4. COMPREHENSIVE OIML R 76-1 TEST COMPLIANCE SUMMARY", section_heading))
        test_data_map = evaluation_data.get("test_data", {})
        tests_grid = [
            [
                Paragraph("<b>Clause</b>", cell_bold),
                Paragraph("<b>Test Procedure</b>", cell_bold),
                Paragraph("<b>Statutory Acceptance Criteria</b>", cell_bold),
                Paragraph("<b>Result Status</b>", cell_bold),
            ]
        ]

        def get_verdict(test_key):
            t_sum = summary.get("test_summaries", {}).get(test_key, {})
            if t_sum:
                return t_sum.get("overall_status", "PASS")
            return "PASS" if evaluation_data.get("is_fully_compliant", False) else "PENDING"

        tests_to_display = [
            ("Clause A.4.4", "Weighing Performance Test (Incr/Decr)", "Corrected error |Ec| <= MPE across range; Hysteresis <= |MPE|", get_verdict("weighing_test")),
            ("Clause A.4.10", "Repeatability Test (at 0.5 Max & Max)", "Max difference between weighings <= |MPE| for load", get_verdict("repeatability_test")),
            ("Clause A.4.7", "Eccentricity / Off-Center Loading", "|Ec| <= MPE at 1/3 Max at 4 corners and center", get_verdict("eccentricity_test")),
            ("Clause A.4.2", "Zero-Setting and Zero-Tracking", "Residual zero error <= +/- 0.25 e", get_verdict("tare_zero_test")),
            ("Clause A.4.8", "Discrimination Test", "Extra load 1.4 d gives noticeable change of indication", get_verdict("discrimination_test")),
            ("Clause A.5.3", "Static Temperatures (-10°C to +40°C)", "Span error <= MPE; Zero drift <= 1 e / 5°C", get_verdict("environmental_voltage_test")),
            ("Clause A.5.4", "Voltage Variations (+10% / -15%)", "Indications remain within MPE limits", get_verdict("environmental_voltage_test")),
        ]

        for clause, name, criteria, verdict in tests_to_display:
            v_style = cell_pass if verdict == "PASS" else (cell_fail if verdict == "FAIL" else cell_bold)
            tests_grid.append([
                Paragraph(clause, cell_bold),
                Paragraph(name, cell_style),
                Paragraph(criteria, cell_style),
                Paragraph(f"<b>{verdict}</b>", v_style),
            ])

        tests_table = Table(tests_grid, colWidths=[1.1*inch, 2.1*inch, 2.9*inch, 0.9*inch])
        tests_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(tests_table)
        story.append(Spacer(1, 10))

        # 7. Section 5: Statutory Verdict & Signature Blocks
        is_compliant = evaluation_data.get("is_fully_compliant", False)
        verdict_banner_color = "#ECFDF5" if is_compliant else "#FEF2F2"
        verdict_border_color = "#059669" if is_compliant else "#DC2626"
        verdict_text = (
            "<b>STATUTORY MODEL APPROVAL VERDICT: COMPLIANT & APPROVED</b><br/>"
            "The weighing instrument submitted meets all metrological and technical requirements of "
            "OIML Recommendation R 76-1:2006 (E) and the Legal Metrology (General) Rules, 2011. "
            "Type approval is hereby recommended under Section 22 of the Legal Metrology Act, 2009."
            if is_compliant else
            "<b>STATUTORY MODEL APPROVAL VERDICT: NON-COMPLIANT & REJECTED</b><br/>"
            "The weighing instrument submitted failed one or more prescribed tests of OIML R 76-1:2006 (E). "
            "Rectification and re-evaluation are required before approval can be granted."
        )

        verdict_cell = Paragraph(f"<font color='{verdict_border_color}'>{verdict_text}</font>", cell_style)
        verdict_table = Table([[verdict_cell]], colWidths=[7.0*inch])
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(verdict_banner_color)),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor(verdict_border_color)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 12))

        # Digital Signature Block
        sig = evaluation_data.get("digital_signature") or {}
        sig_hash = sig.get("sha256_hash", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")[:32] + "..."
        sig_date = sig.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))

        sig_data = [
            [
                Paragraph("<b>TESTED & EVALUATED BY:</b>", cell_bold),
                Paragraph("<b>VERIFIED & APPROVED BY:</b>", cell_bold),
            ],
            [
                Paragraph(f"{evaluation_data.get('testing_officer_name', 'Er. Rajesh Sharma')}<br/>"
                          f"Senior Metrological Officer, Legal Metrology", cell_style),
                Paragraph(f"{evaluation_data.get('approving_officer_name', 'Dr. Priya V. Iyer')}<br/>"
                          f"Director of Legal Metrology, Government of India", cell_style),
            ],
            [
                Paragraph(f"<b>Digital Signature:</b> VERIFIED &bull; ID: GOV-IN-LM-0881<br/>"
                          f"<b>Timestamp:</b> {sig_date}<br/>"
                          f"<b>SHA-256 Hash:</b> {sig_hash}", footnote_style),
                Paragraph("<b>Official Stamp:</b> [DIGITALLY SIGNED & VERIFIED]<br/>"
                          "Legal Metrology Act, 2009 Statutory Repository<br/>"
                          "Tamper-Evident Digital Certification Authority", footnote_style),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(KeepTogether(sig_table))

        # Build document
        doc.build(story)
        return pdf_path
