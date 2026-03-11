# 🛡️ ProofSAR AI - Glass-Box AML Copilot

## 🏆 Barclays Hackathon 2024 - Enterprise-Grade SAR Generation Platform

**ProofSAR AI** is a production-ready, explainable Suspicious Activity Report (SAR) generation system that combines rule-based detection, machine learning, and AI narrative generation with full audit traceability.

---

## 🎯 What Makes This Different

Unlike typical "AI chatbots," ProofSAR AI is a **complete compliance platform** with:

✅ **Dual AI Engine** - Toggle between Gemini (Cloud) and Local LLM (Offline)
✅ **"Why Guilty" Reasoning** - Evidence-based guilt explanation, not just pattern detection
✅ **Cryptographic Audit Trail** - SHA256 hash chain for tamper-proof logging
✅ **Gmail Alert System** - Automated notifications for high-risk cases
✅ **Human-in-the-Loop** - Editable narratives with version control
✅ **RAG Grounding** - Template-based generation with regulatory citations
✅ **Regulatory Compliance** - PMLA, RBI KYC, FIU-IND aligned

---

## 🏗️ System Architecture

```
Transaction Data → Detection Engine → Reasoning Engine → AI Generator
                                    ↓                         ↓
                              Audit Logger           Alert Service
                                    ↓                         ↓
                           Hash Chain Ledger         Gmail Alerts
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone repository
cd ProofSAR-AI

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run frontend/app.py
```

The app will open at `http://localhost:8501`

---

## 📊 Features Demo Flow

### 1. **Dashboard Overview**
- View key metrics: Total cases, high-risk alerts, SARs filed
- Risk distribution charts
- Detection trend analysis
- Recent case summary

### 2. **Case Analysis**
- Upload transaction CSV or use demo data
- Run comprehensive detection analysis
- View detected patterns:
  - Structuring (CTR threshold avoidance)
  - Smurfing (coordinated deposits)
  - Layering (complex fund movement)
- Quantitative evidence with statistical analysis
- Red flag identification

### 3. **SAR Generation**
- Toggle AI model (Gemini ☁️ / Local LLM 💻)
- Generate complete SAR narrative with:
  - Executive summary
  - Customer information
  - Transaction analysis
  - Suspicious activity description
  - Legal basis and citations
  - Recommendation
- **"Why Guilty" Reasoning Engine**:
  - Behavioral red flags
  - Financial inconsistencies
  - Legal violations
  - Supporting evidence
- Edit and refine narrative
- Approve or reject with comments

### 4. **Audit Trail**
- View complete cryptographic log
- Verify chain integrity
- Track all actions:
  - Case creation
  - Analysis execution
  - SAR generation
  - Edits and approvals
  - AI model switches
- Hash verification for tamper-proofing

### 5. **Alert System**
- View sent alerts by type:
  - 🚨 High Risk
  - 📋 Pending Review
  - ✅ Approved
  - ❌ Rejected
- Alert statistics
- Email content preview

---

## 🎨 UI Highlights

- **Barclays-Style Design** - Professional gradient cards, clean layout
- **Interactive Charts** - Plotly visualizations for risk analysis
- **Real-time Updates** - Session state management
- **Responsive Layout** - Wide-screen optimized
- **Color-Coded Risk** - Critical (red), High (orange), Medium (yellow), Low (green)

---

## 🔧 Technical Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Visualization | Plotly |
| Detection | NumPy, Pandas |
| AI Generation | Simulated Gemini/LLM |
| Audit | SHA256 Hashing |
| Alerts | Gmail SMTP (simulated) |

---

## 📁 Project Structure

```
ProofSAR-AI/
├── backend/
│   ├── config.py                    # Configuration
│   ├── detection/
│   │   └── structuring.py          # Pattern detection
│   ├── reasoning/
│   │   └── guilt_engine.py         # "Why Guilty" logic
│   ├── ai_engine/
│   │   └── gemini_client.py        # AI generation
│   ├── audit/
│   │   └── hash_chain.py           # Audit trail
│   └── alerts/
│       └── gmail_service.py        # Email alerts
├── frontend/
│   └── app.py                      # Main Streamlit app
├── demo_data/
│   └── transactions.csv            # Sample data
├── requirements.txt
└── README.md
```

## 🔐 Security Features

1. **Cryptographic Audit Trail**
   - SHA256 hash chain
   - Tamper detection
   - Full action logging

2. **Version Control**
   - Track all narrative edits
   - Before/after comparison
   - Reason logging

3. **Role-Based Access** (Extendable)
   - Analyst, Supervisor, Compliance Head
   - JWT authentication ready

4. **Offline Mode**
   - Local LLM option
   - No data leaves premises

---

## 📋 Regulatory Alignment

- **PMLA 2002** - Prevention of Money Laundering Act
- **RBI KYC 2016** - Know Your Customer Directive
- **FIU-IND Guidelines** - Financial Intelligence Unit reporting
- **CTR Threshold** - ₹10 Lakhs (configurable)

---

## 🎯 Hackathon Winning Elements

1. **Enterprise Architecture** - Not a toy demo, real system design
2. **Explainability** - "Why Guilty" reasoning is unique
3. **Audit Trail** - Cryptographic verification rarely seen
4. **Dual AI** - Cloud/local toggle shows security thinking
5. **Complete Workflow** - End-to-end from detection to filing
6. **Professional UI** - Barclays-quality design
7. **Real Alerts** - Gmail integration (simulated but realistic)

---

## 🚀 Future Enhancements

- [ ] Real Gemini API integration
- [ ] PostgreSQL database
- [ ] RAG with ChromaDB
- [ ] Advanced ML models (XGBoost, LSTM)
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Real-time transaction streaming
- [ ] Network graph visualization

---


## 👥 Team

TEAM VEXTRIA

MEMBERS:
Aditya Shetty
Anvesh Chaurpagar
Meenal Shendre
Mustansir Dabhiya
Prasad Dalvi
---

---


---
## 📞 Support

For questions or demo requests:
- Email:anveshchaurpagar193@gmail.com
- GitHub: [https://github.com/Anvesh1211/hire.git)]


---

**🛡️ ProofSAR AI - Making AML Compliance Transparent, Traceable, and Trustworthy**
