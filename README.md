# GrowthGuru AI

> **Empowering small businesses with AI-driven marketing intelligence and automated sales analytics.**

---

## 🚀 Project Overview

Small and medium-sized businesses often struggle to convert raw sales records into high-converting marketing campaigns due to limited analytics resources and domain expertise. Without a dedicated data team, identifying growth opportunities, detecting inventory risks, and planning targeted social campaigns can be complex and time-consuming.

**GrowthGuru AI** acts as an AI-powered business growth assistant, combining data-driven business analytics with LLM-powered strategic recommendations. It executes a rigorous analytical pipeline—CSV upload, hybrid validation, data integrity checking, KPI computation, and insights generation—before applying AI reasoning. Powered by a FastAPI analytics backend and Groq LLMs, it ingests raw transaction data, extracts actionable business metrics, generates an AI Growth Plan, simulates strategic outcomes with GrowthLens, and creates ready-to-publish social media campaigns. This architecture helps reduce AI hallucinations by ensuring the language model consumes validated business metrics instead of recalculating them.

---

## 🚀 Highlights

- AI-powered business growth assistant for SMEs
- Hybrid CSV validation and Business Integrity Checker
- Python-based KPI computation with SSOT architecture
- AI-generated growth strategies using validated business metrics
- Business impact simulation with GrowthLens
- AI-generated social media captions and hashtags

---

## 🤔 Why GrowthGuru AI?

- **Reliable Business Metrics**: Core business KPIs are computed in Python before AI analysis.
- **Prevents AI from recalculating business metrics**: The AI never recalculates revenue, profit, margins, rankings, or inventory metrics.
- **Strategic Focus**: AI focuses exclusively on strategic reasoning based on hard data.
- **Single Source of Truth**: The Dashboard, GrowthEngine, and GrowthLens all use the very same backend metrics.
- **Explainable & Consistent**: Outputs are explainable and highly consistent across every component of the application.

---

## ⭐ Key Features

### 🧩 Business Intelligence Engine

- **KPI Engine** — Calculates revenue, profit, margins, contribution, inventory coverage, and product performance metrics in Python.
- **Business Integrity Checker** — Detects common business data integrity issues such as:
  - Negative revenue
  - Invalid customer ratings
  - Negative inventory
  - Revenue with zero sales
  - Missing required values
  - Inconsistent business records
- **Executive Insights Engine** — Generates prioritized dashboard insights using backend-calculated metrics.
- **Single Source of Truth (SSOT)** — Dashboard, GrowthEngine, and GrowthLens consume the same backend metrics to ensure consistency.

### 🤖 Core AI Modules

- 🧠 **GrowthEngine** — AI-powered business growth recommendations generated directly from validated backend KPIs.
- 📊 **GrowthLens** — Business impact simulation, opportunity analysis, confidence scoring, and implementation prioritization based on backend KPIs and generated strategy.
- 📱 **Social Studio** — AI-generated product captions and hashtags for product promotion.

### 📈 Business Dashboard

- 📊 **KPI Analytics**
- 🛍️ **Product Performance Analysis**
- 🚨 **Business Integrity Alerts**
- 💡 **Executive Business Insights**
- 📦 **Inventory Risk Monitoring**
- 📈 **AI Growth Plan Visualization**

### ⚙️ AI Infrastructure

- 🧩 **Business Integrity Middleware** — Backend layer that validates business logic before KPI computation and AI reasoning.
- 🔄 **Smart Model Router** — Automatic Groq model routing and intelligent fallback (LLaMA 3.3 70B → LLaMA 3.1 8B).
- 🛡️ **JSON Guard** — Structured JSON validation and automatic repair logic.
- 🔍 **AI Diagnostics Logger** — Server-side token estimation & request diagnostics logging.
- ⚡ **Rate Limit Recovery** — Intelligent HTTP 429 handling and error recovery.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite |
| **UI** | TailwindCSS, Lucide React |
| **Visualization** | Recharts |
| **Backend** | FastAPI, Pandas, Pydantic |
| **AI** | Groq SDK |
| **Architecture** | SSOT, Hybrid Validation Pipeline |

---

## ⚙️ System Architecture

```text
[ Raw CSV Upload ]
       │
       ▼
┌─────────────────────────────────────────┐
│ 1. Hybrid CSV Validation                │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 2. Business Integrity Checker           │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 3. KPI Engine                           │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 4. Executive Insights Generator         │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 5. AI Context Builder                   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 6. Smart Model Router                   │
└────────────────────┬────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌───────────────┐
│ GrowthEngine │ │GrowthLens│ │ Social Studio │
└──────┬───────┘ └────┬─────┘ └───────┬───────┘
       │              │               │
       └──────────────┼───────────────┘
                      ▼
┌─────────────────────────────────────────┐
│ 7. React Dashboard                      │
└─────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
.
├── backend/                  # FastAPI Backend Service
│   ├── validation/           # Hybrid CSV & Schema Validation Engine
│   │   ├── column_mapper.py  # Data Alignment & Mapping
│   │   └── integrity_checker.py # Business Integrity Checker
│   ├── config.py             # Global configurations & LLM settings
│   ├── groq_client.py        # Smart Model Router & JSON Guard
│   ├── groq_logger.py        # Token Diagnostics & Console Logger
│   ├── insights.py           # Executive Insights Generator
│   ├── main.py               # Core REST API Endpoints
│   ├── scenario_simulator.py # AI Scenario Simulation Engine
│   ├── schemas.py            # Pydantic Request/Response Schemas
│   └── storage.py            # Memory Storage Abstraction
├── frontend/                 # React 19 + Vite Web Application
│   ├── public/               # Static assets & sample datasets
│   ├── src/                  # React components, screens, and services
│   ├── package.json          # Frontend dependencies
│   ├── tailwind.config.js    # TailwindCSS configuration
│   └── vite.config.js        # Vite bundler configuration
├── docs/                     # Documentation & UI Screenshots
└── README.md                 # Project documentation
```

---

## 🎯 Workflow

1. Upload Business CSV
2. Validate Dataset Structure
3. Detect Business Integrity Issues
4. Compute KPIs
5. Generate Executive Insights
6. Generate AI Growth Strategy
7. Simulate Business Impact with GrowthLens
8. Create Social Media Content with Social Studio

---

## 🔌 API Endpoints

- **POST /upload**  
  Upload and validate the raw business CSV.

- **POST /validate-alignment**  
  Verify data structure and business type alignment.

- **POST /analyze**  
  Aggregate uploaded CSV data and extract KPIs.
  
- **POST /generate-growth-plan**  
  Generate AI-powered business growth strategy.
  
- **POST /simulate-impact**  
  Run GrowthLens business impact simulation.

---

## 💻 Installation & Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Groq API Key**: Available at [console.groq.com](https://console.groq.com)

---

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows PowerShell:
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Configure environment variables:
Create a `.env` file in the `backend/` directory:
```env
FRONTEND_URL=http://localhost:5173
GROQ_API_KEY=your_groq_api_key_here
```

Start the FastAPI development server:
```bash
uvicorn main:app --reload --port 8000
```
*Backend API will be running at `http://localhost:8000` (Swagger docs available at `/docs`).*

---

### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

Install Node.js dependencies:
```bash
npm install
```

Configure environment variables:
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the Vite development server:
```bash
npm run dev
```
*Frontend application will be accessible at `http://localhost:5173`.*

---

## 📸 Screenshots

| Dashboard Analytics | GrowthEngine Strategy |
|---|---|
| ![Dashboard Analytics](docs/images/dashboard_analytics.png) | ![GrowthEngine Strategy](docs/images/growth_engine.png) |

| Hybrid CSV Validation | GrowthLens Impact Simulator |
|---|---|
| ![CSV Validation](docs/images/csv_validation.png) | ![GrowthLens Impact Simulator](docs/images/growth_lens.png) |


## 🤝 Team

Developed with ❤️ by **Team PixelForge**.
