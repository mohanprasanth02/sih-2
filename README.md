# LabelGuard AI

**Scan. Verify. Detect. Report.**

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH%202026-Problem%20SIH26034-blue)](https://sih.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20Python-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Tailwind-61DAFB)](https://react.dev)
[![Flutter](https://img.shields.io/badge/Mobile-Flutter%20%7C%20Dart-02569B)](https://flutter.dev)
[![OpenCV](https://img.shields.io/badge/Computer%20Vision-OpenCV%20headless-5C3EE8)](https://opencv.org)

> **Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.**

---

## 1. Executive Summary & Problem Solved

The Department of Consumer Affairs, Government of India enforces the **Legal Metrology (Packaged Commodities) Rules, 2011** across millions of retail packaging units. Manual inspection of packaged goods in the field is labor-intensive, error-prone, and slow to document.

**LabelGuard AI** provides an end-to-end AI-assisted Legal Metrology inspection platform connecting:
- **Field Inspectors**: Live multi-surface mobile scanning, intelligent blur and illumination guidance, offline queueing, and GPS metadata.
- **AI/Vision Orchestrator**: OpenCV-based quality metrics, text region localization, OCR token extraction, structured declaration normalization, and cross-image conflict detection.
- **Deterministic Rule Engine**: Codified Legal Metrology Rules 2011 (Rule 6(1)(a) through Rule 18) evaluating extracted declarations without hallucination.
- **Enforcement Web Console**: Evidence-first bounding-box visualizer, human-in-the-loop audit trails, supervisor approval workflows, and tamper-evident official PDF report generation.

---

## 2. Core Architectural Principles

1. **Strict Separation of Concerns**:
   - **AI Extraction**: Determines *"What text appears on the package?"*
   - **Compliance Rule Engine**: Determines *"Does the declaration satisfy the configured statutory rule?"*
   - **Human Verification**: Authorized officers determine *"Should this finding be certified as an official inspection finding?"*
2. **Never Guess or Hallucinate**:
   - If confidence is below 70%, image is blurred, or required evidence is ambiguous, the system flags **`MANUAL REVIEW REQUIRED`**.
3. **Multi-Surface Cross-Checking**:
   - Compares declarations found on Front vs Back vs Sides. Detects discrepancies (e.g. 500g front vs 450g back) as potential deceptive packaging under Rule 10.
4. **Immutable Audit Trail**:
   - Human corrections do not overwrite original AI extraction; they record original value, corrected value, officer ID, reason, and timestamp.

---

## 3. Technology Stack

- **Backend API Gateway**: Python 3.12, FastAPI, SQLAlchemy ORM, Alembic, Pydantic v2, Python-JOSE (JWT), Bcrypt, WebSockets.
- **AI & Computer Vision**: OpenCV Headless (Laplacian blur variance, luminance, contrast), RapidOCR/PaddleOCR/CV Text Engine adapters, regex/heuristic field normalizers, Pillow.
- **Web Application**: React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts, Vite.
- **Mobile Application**: Flutter, Dart, Camera, SQLite (`sqflite`), Dio, WebSocketChannel, Secure Storage.
- **Official Reporting**: ReportLab PDF Engine with statutory disclaimers and visual evidence crops.
- **Database**: PostgreSQL / SQLite hybrid with relational schema and indexes.

---

## 4. Codified Legal Metrology Rules (2011)

| Rule Code | Statutory Reference | Title | Severity |
| :--- | :--- | :--- | :--- |
| **LM-RULE-001** | Rule 6(1)(a) | Common or Generic Commodity Name | CRITICAL |
| **LM-RULE-002** | Rule 6(1)(b) | Name & Address of Manufacturer / Packer / Importer | CRITICAL |
| **LM-RULE-003** | Rule 6(1)(c) | Country of Origin Declaration (Imported Goods) | CRITICAL |
| **LM-RULE-004** | Rule 6(1)(d) & Rule 11 | Net Quantity in Standard Metric SI Units (g, kg, ml, l) | CRITICAL |
| **LM-RULE-005** | Rule 6(1)(e) | Maximum Retail Price (MRP) with Mandatory Tax Clause | CRITICAL |
| **LM-RULE-006** | Rule 6(1)(n) | Unit Sale Price (USP) Declaration (2021 Amendment) | MAJOR |
| **LM-RULE-007** | Rule 6(1)(f) | Month & Year of Manufacture / Packing / Import | CRITICAL |
| **LM-RULE-008** | Rule 6(2) | Consumer Care Cell / Grievance Redressal Details | MAJOR |
| **LM-RULE-009** | Rule 9 | Minimum Font Size / Height Proportionality (Advisory) | MINOR |
| **LM-RULE-010** | Rule 10 | Cross-Surface Package Declaration Consistency | CRITICAL |

---

## 5. Repository Monorepo Structure

```text
labelguard-ai/
├── apps/
│   ├── web/                    # React 18, TypeScript, Tailwind CSS, Recharts
│   └── mobile/                 # Flutter mobile application (Camera, SQLite, Dio)
├── services/
│   ├── api/                    # FastAPI core service & routers
│   ├── ai/                     # AI Orchestrator, OpenCV Quality, OCR & Extraction
│   └── worker/                 # Background inspection worker
├── packages/
│   ├── shared-types/           # Shared TypeScript & schema definitions
│   └── validation/             # Deterministic Legal Metrology validators
├── database/
│   ├── migrations/             # Alembic database migrations
│   └── seeds/                  # Seed script (Users, official rules, demo records)
├── rules/
│   └── legal_metrology/        # Codified Legal Metrology Rules 2011 & engine
├── reports/                    # ReportLab PDF report generators
├── tests/                      # Pytest backend and rule verification tests
├── infrastructure/             # Docker compose, Dockerfile, Nginx config
└── README.md
```

---

## 6. Quick Start & Local Execution

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Flutter SDK

### 1. Start Backend Service
```bash
# Setup Python environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install fastapi "uvicorn[standard]" pydantic sqlalchemy alembic python-multipart \
    "python-jose[cryptography]" bcrypt websockets reportlab pillow \
    opencv-python-headless numpy pytest httpx

# Seed Database with official rules and users
python database/seeds/seed_data.py

# Launch FastAPI server on port 8000
python -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
```

### 2. Start Web Application
```bash
cd apps/web
npm install
npm run dev
```
Open **`http://127.0.0.1:3000`** in your browser.

### 3. Run Backend Test Suite
```bash
python -m pytest tests/test_backend.py -v
```

---

## 7. Default Demo Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Inspector** | `inspector@legalmetrology.gov.in` | `Inspector@123` |
| **Supervisor** | `supervisor@legalmetrology.gov.in` | `Supervisor@123` |
| **Administrator** | `admin@legalmetrology.gov.in` | `Admin@123` |

---

## 8. SIH Demonstration Workflow

1. **Open Dashboard**: View real-time aggregated metrics from database records.
2. **Verify Product**:
   - Click **Verify Product** in the sidebar.
   - Click **"Load Standard Commodity Sample"** or upload your own package photos.
   - Click **"RUN COMPLIANCE VERIFICATION"**.
   - Watch the live 8-stage WebSocket pipeline stream real-time events.
3. **Examine Evidence Visualizer**:
   - Inspect the interactive package viewer with bounding boxes.
   - Click any declaration (e.g. `MRP`, `Net Quantity`) to focus the bounding box.
   - Click the pencil icon to simulate human-in-the-loop correction.
   - Click **"OFFICIAL PDF REPORT"** to generate and download the tamper-evident certificate.
4. **Test Rules in Playground**:
   - Navigate to **"Rules & Playground"**.
   - Enter arbitrary values (e.g. Net Qty: `500 gms`) and click **"TEST RULES DETERMINISTICALLY"** to see instant rule failure with statutory citation.
5. **Field Scanner Simulator**:
   - Navigate to **"Mobile Scanner Demo"** to experience the mobile camera guidance overlay.

---

## 9. Statutory Legal Notice

*LabelGuard AI provides AI-assisted screening, vision extraction, and decision support in accordance with the Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011. Findings requiring enforcement action must be reviewed and confirmed by an authorized Legal Metrology Inspector or Officer.*
