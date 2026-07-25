# GrowthGuru AI

*AI-powered Social Media Marketing Assistant for small businesses.*

---

## 🚀 Project Overview

Small businesses often struggle with creating effective, data-driven social media marketing campaigns due to a lack of dedicated resources and expertise. Without a specialized analytics team, translating raw sales data into actionable business strategies can feel overwhelming.

**GrowthGuru AI** solves this by democratizing access to expert-level marketing intelligence. By leveraging advanced AI models (via Groq), it automates data analysis, detects hidden business insights, and generates tailored growth plans—empowering businesses to make confident, data-driven decisions seamlessly.

---

## ⭐ Key Features

| Feature | Description |
|---|---|
| 🚀 **AI Growth Engine** | Generates data-driven business growth strategies from uploaded sales data, prioritizing recommendations based on real business metrics. |
| 🧠 **AI Hybrid CSV Validation** | Combines rule-based and AI-powered validation to detect data quality issues and verify smart alignment with business goals. |
| 📊 **Growth Lens** | Analyzes sales performance to identify trends, pinpoint revenue opportunities, detect inventory risks, and suggest cross-selling strategies. |
| 🎯 **AI Scenario Simulator** | Simulates possible business outcomes and estimates the potential impact of implementing the recommended AI strategies. |
| 📱 **AI Social Media Generator** | Creates product promotion captions, platform-ready marketing copy, and relevant hashtags for engagement-focused campaigns. |
| 🔄 **Intelligent Model Router** | Automatically switches between primary and fallback Groq models upon quota/rate-limit events, ensuring high availability. |
| 🛡️ **Production-Grade Engine** | Features a token-efficient AI pipeline, automatic JSON validation/repair, and a secure backend architecture. |

---

## 🛠️ Technology Stack

- **Frontend:** React 19, Vite, TailwindCSS, Recharts, Lucide React
- **Backend:** Python, FastAPI, Pandas, Uvicorn
- **AI Models:** Groq SDK (LLaMA 3.3 70b versatile / llama 3.1 8b model fallback support)
- **Architecture:** Client-Server API Workflow

---

## ⚙️ System Architecture

The complete end-to-end data processing workflow:

1. **CSV Upload**: Securely upload raw sales data.
2. **↓ Validation Engine**: Hybrid verification guarantees data integrity.
3. **↓ Business Summary**: Pandas extracts KPIs and core business metrics.
4. **↓ Growth Engine**: AI analyzes metrics to formulate an initial growth strategy.
5. **↓ Growth Lens**: Actionable insights (inventory alerts, cross-sell/up-sell targets) are highlighted.
6. **↓ Scenario Simulation**: Forecasts the revenue impact of adopting the generated strategy.
7. **↓ Social Media Generator**: Outputs platform-ready captions and hashtags based on the winning products.
8. **↓ Final Dashboard**: Renders insights interactively in the React frontend.

---

## 🧠 AI Workflow

When business data is uploaded, it is first cleaned and normalized natively. The Pandas engine computes critical KPIs like Total Revenue, Best Sellers, and Inventory Risks. This robust context is securely formatted and passed to the **Groq API** with an optimized system prompt. 

The AI model evaluates the data, generates actionable insights via the Growth Engine, and drafts engaging social media captions. Our **Intelligent Model Router** guarantees zero downtime by automatically falling back to secondary models if API rate limits are hit, while a built-in JSON repair agent instantly fixes any malformed model responses.

---

## 📂 Folder Structure

```text
Growth GuruAI/growthguru-ai/
├── backend/                  # FastAPI Backend Service
│   ├── validation/           # Hybrid CSV and Business Validation Engine
│   ├── config.py             # Global configurations & LLM settings
│   ├── groq_client.py        # Intelligent Model Router & JSON Repair
│   ├── insights.py           # Growth Lens & Data Analytics logic
│   ├── main.py               # Core API routes
│   ├── scenario_simulator.py # AI Scenario Simulation engine
│   └── schemas.py            # Pydantic request/response models
├── frontend/                 # React + Vite Frontend Application
│   ├── public/               # Static assets
│   ├── src/                  # React components, pages, and hooks
│   ├── package.json          # Frontend dependencies
│   ├── tailwind.config.js    # TailwindCSS styling configurations
│   └── vite.config.js        # Vite bundler configurations
├── .gitignore                # Secure ignore rules
└── README.md                 # Project documentation
```

---

## 💻 Installation & Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd "Growth GuruAI/growthguru-ai/backend"
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd "Growth GuruAI/growthguru-ai/frontend"
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```

### Environment Variables
**Backend (`Growth GuruAI/growthguru-ai/backend/.env`)**
Create the `.env` file from the example:
```env
FRONTEND_URL=http://localhost:5173
GROQ_API_KEY=your_groq_api_key_here
```

**Frontend (`Growth GuruAI/growthguru-ai/frontend/.env`)**
Create the `.env` file from the example:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Run Commands
**Start the Backend Server:**
```bash
cd "Growth GuruAI/growthguru-ai/backend"
uvicorn main:app --reload --port 8000
```

**Start the Frontend App:**
```bash
cd "Growth GuruAI/growthguru-ai/frontend"
npm run dev
```
*Access the application interface at `http://localhost:5173`.*

---

## 💡 Why GrowthGuru AI?

Unlike simple analytics dashboards that only visualize past performance, **GrowthGuru AI** acts as a proactive Chief Marketing Officer (CMO). 

- **AI-Driven Decision Support:** It doesn't just show you numbers; it tells you exactly *what to do* next.
- **Actionable Recommendations:** Delivers prioritized, confidence-scored recommendations tailored to your unique sales data.
- **Business Intelligence Meets Marketing:** Bridges the gap between raw data and marketing execution by instantly generating ready-to-post social media content.

---

## 🛣️ Future Roadmap

- **CRM & POS Integrations:** Direct synchronization with platforms like Shopify, WooCommerce, and Salesforce.
- **Predictive Analytics:** Advanced time-series forecasting for seasonal inventory trends.
- **Live Sales Integration:** Real-time dashboard updates via secure WebSockets.
- **Multi-Language Support:** Localized insights for global small businesses.

---

## 🤝 Contributors

- **Team PixelForge**
