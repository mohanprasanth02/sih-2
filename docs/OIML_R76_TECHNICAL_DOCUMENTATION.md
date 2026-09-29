# OIML R 76 NAWI Type Evaluation & Model Approval System
## Technical Architecture, Calculation Methodology & Deployment Framework

---

### Executive Overview

Non-Automatic Weighing Instruments (NAWIs)—such as electronic retail counter scales, platform scales, precision laboratory balances, and industrial weighbridges—are critical infrastructure for fair trade, commerce, health, agriculture, and consumer protection.

Under the **Legal Metrology Act, 2009** (Section 22) and the **Legal Metrology (General) Rules, 2011** (Seventh Schedule), every weighing or measuring instrument intended for use in transaction or protection must conform to prescribed standards, obtain **Model Approval (Type Approval)** from designated national laboratories, and undergo initial verification and stamping before deployment.

This software application automates:
1. **Instrument Specification & Technical Parameter Recording**: Captures manufacturer details, serial numbers, accuracy class, capacity, verification intervals, sensor/load cell specifications, and firmware checksums.
2. **Laboratory & Environmental Condition Logging**: Records ambient temperature, relative humidity, barometric pressure, local gravitational acceleration $g$, and certified reference mass standards.
3. **Prescribed OIML R 76 Metrological Test Execution**: Automated digital data recording for weighing performance (increasing/decreasing loads), repeatability, eccentricity (off-center loading), zero-setting, tare weighing, discrimination, static temperatures, and voltage variations.
4. **Deterministic Calculation & Compliance Verification**: Real-time evaluation of error before rounding ($E$), zero error ($E_0$), corrected error ($E_c = E - E_0$), Maximum Permissible Error ($MPE$), and hysteresis.
5. **Standardized Report Generation in Dual Formats**:
   - **Printable, tamper-evident PDF** formatted as per OIML R 76-2 (Pattern Evaluation Report).
   - **Editable Microsoft Word (.docx)** format for designated laboratories to append custom statutory addenda.
6. **Tamper-Evident Digital Signatures**: Cryptographic SHA-256 data hashing and officer credential verification.
7. **Searchable Digital Repository & Dashboard**: Instrument-wise test history, multi-axis filtering, and monitoring metrics.
8. **Extensibility & Standards Revision Engine**: Declarative standard specifications supporting future revisions to OIML recommendations.

---

## 1. System Architecture

The application is structured into a modular, decoupled architecture:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               Presentation Layer (Web Console)                         │
│  - React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts                          │
│  - NAWI Dashboard, Digital Test Wizard, Report Repository, OIML Standards Explorer     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP / JSON API & REST
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                FastAPI Gateway & API Layer                             │
│  - Endpoint Routing (/api/v1/oiml/*)                                                   │
│  - Pydantic v2 Input Validation & Serialization                                        │
│  - Authentication & Role-Based Access Control (Inspector, Supervisor, Admin)           │
└───────────────────────┬───────────────────┬───────────────────┬────────────────────────┘
                        │                   │                   │
┌───────────────────────▼───────┐   ┌───────▼───────┐   ┌───────▼────────────────────────┐
│   OIML Metrological Engine    │   │  Persistence  │   │  Standardized Report Engines   │
│ - Accuracy Class & n Checks   │   │ - SQLAlchemy  │   │ - ReportLab PDF Engine         │
│ - OIML R 76 Table 6 MPE Steps │   │ - SQLite /    │   │ - Python-Docx MS Word Engine   │
│ - Flash Point Error (Ec)      │   │   PostgreSQL  │   │ - Cryptographic SHA-256 Signer │
│ - Prescribed Test Evaluators  │   │ - Repository  │   │ - Official Statutory Templates │
└───────────────────────────────┘   └───────────────┘   └────────────────────────────────┘
```

### Component Roles:
- **`rules/oiml_r76/__init__.py`**: Deterministic metrological computation engine adhering strictly to OIML R 76-1:2006. No floating approximations; rigorous changeover point and rounding logic.
- **`rules/oiml_r76/standards.py`**: OIML recommendations version registry, allowing seamless configuration of revisions or national deviations.
- **`services/api/routers/oiml_r76.py`**: REST controllers exposing CRUD, on-the-fly metrological calculation (`/calculate`), digital signing (`/sign`), and file export streams.
- **`services/api/models.py` & `schemas_oiml.py`**: Relational data schema representing instruments, environmental conditions, observation datasets, and audit trails.
- **`reports/oiml_pdf_generator.py`**: Formal PDF pattern evaluation report generator with official Government of India header, tables, MPE columns, pass/fail highlights, and signature block.
- **`reports/oiml_docx_generator.py`**: Word generator creating fully editable `.docx` files formatted with identical statutory data tables.
- **`apps/web/src/components/oiml/`**: Rich web application frontend featuring test observation entry wizards, live calculation feedback, and search repository.

---

## 2. Metrological Calculation Methodology

### 2.1 Verification Scale Interval & Number of Scale Intervals
The number of verification scale intervals ($n$) is calculated as:
$$n = \frac{\text{Max}}{e}$$
Where:
- $\text{Max}$ is the maximum capacity of the instrument.
- $e$ is the verification scale interval.
- $d$ is the actual scale interval ($d \le e$).

### 2.2 Accuracy Class Validation (OIML R 76-1 Table 3)
The calculated $n$ and $e$ are validated against the permissible limits:

| Accuracy Class | Verification Scale Interval ($e$) | Minimum $n$ ($n_{\min}$) | Maximum $n$ ($n_{\max}$) | Minimum Capacity ($\text{Min}$) |
| :--- | :--- | :--- | :--- | :--- |
| **Class I** (Special) | $e \ge 0.001\text{ g}$ | $50\,000$ | No Limit | $100\,e$ |
| **Class II** (High) | $0.001\text{ g} \le e \le 0.05\text{ g}$<br/>$e \ge 0.1\text{ g}$ | $100$<br/>$5\,000$ | $100\,000$<br/>$100\,000$ | $20\,e$<br/>$50\,e$ |
| **Class III** (Medium) | $0.1\text{ g} \le e \le 2\text{ g}$<br/>$e \ge 5\text{ g}$ | $100$<br/>$500$ | $10\,000$<br/>$10\,000$ | $20\,e$<br/>$20\,e$ |
| **Class IIII** (Ordinary) | $e \ge 5\text{ g}$ | $100$ | $1\,000$ | $10\,e$ |

### 2.3 Maximum Permissible Error (MPE) (OIML R 76-1 Table 6)
On initial pattern evaluation and verification, the maximum permissible error is calculated per load $m$ expressed in verification scale intervals $e$:

#### For Class I:
- $0 \le m \le 50\,000\,e \implies \text{MPE} = \pm 0.5\,e$
- $50\,000\,e < m \le 200\,000\,e \implies \text{MPE} = \pm 1.0\,e$
- $m > 200\,000\,e \implies \text{MPE} = \pm 1.5\,e$

#### For Class II:
- $0 \le m \le 5\,000\,e \implies \text{MPE} = \pm 0.5\,e$
- $5\,000\,e < m \le 20\,000\,e \implies \text{MPE} = \pm 1.0\,e$
- $20\,000\,e < m \le 100\,000\,e \implies \text{MPE} = \pm 1.5\,e$

#### For Class III:
- $0 \le m \le 500\,e \implies \text{MPE} = \pm 0.5\,e$
- $500\,e < m \le 2\,000\,e \implies \text{MPE} = \pm 1.0\,e$
- $2\,000\,e < m \le 10\,000\,e \implies \text{MPE} = \pm 1.5\,e$

#### For Class IIII:
- $0 \le m \le 50\,e \implies \text{MPE} = \pm 0.5\,e$
- $50\,e < m \le 200\,e \implies \text{MPE} = \pm 1.0\,e$
- $200\,e < m \le 1\,000\,e \implies \text{MPE} = \pm 1.5\,e$

*Note: For subsequent in-service verification, MPE tolerances are doubled ($2 \times \text{MPE}$).*

### 2.4 Error Calculation (Changeover / Flash Point Method - Clause A.4.4.3)
When an instrument has digital indication with $d = e$, rounding error must be eliminated using the small additional weights (flash point) method:
$$E = I + \frac{1}{2}e - \Delta L - L$$
Where:
- $I$ = Indication on the instrument display.
- $e$ = Verification scale interval.
- $\Delta L$ = Additional small weights placed on the receptor until the indication unambiguously flashes to the next interval ($I + d$).
- $L$ = Load on the receptor.

The **corrected error** ($E_c$) takes into account the error at zero load ($E_0$):
$$E_c = E - E_0$$

Compliance criterion:
$$|E_c| \le \text{MPE}(L)$$

### 2.5 Prescribed OIML R 76 Test Procedures

1. **Weighing Performance Test (Clause A.4.4)**:
   - At least 5 increasing load points ($\text{Min}, 500e, 2000e, 0.5\text{Max}, \text{Max}$) and decreasing load points.
   - Hysteresis: Difference in corrected error between increasing and decreasing loads at the same load point:
     $$\text{Hysteresis} = |E_{c,\text{decr}} - E_{c,\text{incr}}| \le |\text{MPE}(L)|$$

2. **Repeatability Test (Clause A.4.10)**:
   - Series of 10 weighings (or 3 for large instruments $>1\text{ t}$) at $\approx 0.5\text{Max}$ and $\approx \text{Max}$.
   - Maximum range difference:
     $$\Delta_{\max} = I_{\max} - I_{\min} \le |\text{MPE}(L)|$$

3. **Eccentricity / Off-Center Loading Test (Clause A.4.7)**:
   - Load applied at Center and 4 corner quadrants (Front-Left, Rear-Left, Rear-Right, Front-Right) using $L = \frac{1}{3}\text{Max}$ (or $\frac{1}{N-1}\text{Max}$ for $N$ supports).
   - Compliance: $|E_c| \le \text{MPE}(L)$ at every position.

4. **Zero-Setting & Tare Test (Clauses A.4.2 & A.4.6)**:
   - Residual zero-setting error $|E_0| \le 0.25\,e$.
   - Net load tare weighing complying with MPE for that net load.

5. **Discrimination Test (Clause A.4.8)**:
   - At $\text{Min}$, $0.5\text{Max}$, and $\text{Max}$, smoothly applying an extra load of $1.4\,d$ must increment the indication by at least $1\,d$.

6. **Static Temperature Test (Clause A.5.3)**:
   - Evaluated across prescribed range (standard: $-10^\circ\text{C}$ to $+40^\circ\text{C}$).
   - Span error must remain within MPE.
   - Zero drift with temperature shall not exceed $1\,e$ per $5^\circ\text{C}$.

7. **Voltage Variations Test (Clause A.5.4)**:
   - Tested at nominal mains voltage ($230\text{V}$), $+10\%$ ($253\text{V}$), and $-15\%$ ($187\text{V}$). Indications must remain within MPE.

---

## 3. Cryptographic Verification & Audit Trail

To prevent post-test manipulation, every completed model evaluation is hashed using SHA-256 across all metrological fields:
$$\text{Hash} = \text{SHA256}(\text{ReportNo} \parallel \text{Manufacturer} \parallel \text{Model} \parallel \text{Max} \parallel e \parallel \text{Status} \parallel \text{Summary})$$
When an authorized officer signs the report:
- The hash is sealed into the record with the officer's ID, timestamp, and a unique cryptographic certificate token (`GOV-IN-LM-CERT-*`).
- If any test observation is altered thereafter, the hash verification fails automatically.

---

## 4. REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/oiml/standards` | List active OIML recommendations, accuracy classes, and MPE rules. |
| `POST` | `/api/v1/oiml/calculate` | Instant calculation API for digital forms (computes $E, E_c, \text{MPE}$, hysteresis, pass/fail). |
| `GET` | `/api/v1/oiml/dashboard-stats`| Retrieve high-level KPIs, pass rate, class breakdown, and recent records. |
| `GET` | `/api/v1/oiml/evaluations` | List evaluations with multi-parameter search, status, and class filtering. |
| `POST` | `/api/v1/oiml/evaluations` | Create a new NAWI type evaluation submission and evaluate compliance. |
| `GET` | `/api/v1/oiml/evaluations/{id}` | Retrieve comprehensive evaluation details and test observations. |
| `PUT` | `/api/v1/oiml/evaluations/{id}` | Update evaluation observations and recompute metrological compliance. |
| `POST`| `/api/v1/oiml/evaluations/{id}/upload-photo` | Attach instrument photos, nameplate, load cell mount, and sealing evidence. |
| `POST`| `/api/v1/oiml/evaluations/{id}/sign` | Apply tamper-evident digital signature and seal approval verdict. |
| `GET` | `/api/v1/oiml/evaluations/{id}/export/pdf` | Generate and download standardized OIML R 76-2 printable PDF report. |
| `GET` | `/api/v1/oiml/evaluations/{id}/export/docx`| Generate and download standardized editable Microsoft Word (.docx) report. |
| `POST`| `/api/v1/oiml/seed-demo` | Seed realistic multi-class NAWI evaluation records for demonstration. |

---

## 5. Deployment Framework

### 5.1 Local Execution
```bash
# 1. Activate Python virtual environment
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate # Linux/macOS

# 2. Run Database Migrations / Ensure Tables
python -c "from services.api.database import engine, Base; Base.metadata.create_all(bind=engine)"

# 3. Start Backend API Server
uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --reload

# 4. Start Web Application Frontend
cd apps/web
npm run dev
```

### 5.2 Production Container Deployment (Docker Compose)
The application can be deployed using Docker and Docker Compose with Nginx reverse proxy:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: infrastructure/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./labelguard.db
      - SECRET_KEY=PROD_SECRET_KEY_METROLOGY_2026
    volumes:
      - ./uploads:/app/uploads
      - ./reports/generated:/app/reports/generated

  frontend:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
```

---

## 6. Verification and Testing

All calculation routines, MPE tolerance curves, and API endpoints are covered by comprehensive unit tests:
```bash
pytest tests/test_oiml_r76.py -v
```
Verified dimensions:
- Accuracy class normalization and verification scale intervals calculation ($n$).
- Step-by-step MPE bounds checking across Class I, II, III, and IIII.
- Changeover flash point error determination ($E = I + 0.5e - \Delta L - L$).
- Weighing performance test evaluation and hysteresis detection.
- Repeatability range tolerance ($\Delta_{\max} \le |\text{MPE}|$).
- Eccentricity off-center quadrant evaluation.
- PDF generation and Word (.docx) generation with tables, headers, and signatures.
- API REST integration and digital signature cryptographic hash verification.
