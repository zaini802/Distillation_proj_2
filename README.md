# ⚗️ DistillAI — Industrial Distillation Column Design System

AI-powered industrial distillation column design platform built with Python + Streamlit + Groq.

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Enter Groq API Key
- In the sidebar, expand **🔑 Groq API Key**
- Paste your key (get free key at https://console.groq.com)

---

## 📁 Project Structure

```
distillation-ai-system/
├── app.py                      ← Main entry point
├── requirements.txt
├── assets/
│   └── styles.css              ← Global styles
├── pages/                      ← All 20 UI sections
│   ├── home.py
│   ├── feed.py
│   ├── thermodynamics.py
│   ├── column_type.py
│   ├── tray_design.py
│   ├── packing_design.py
│   ├── shortcut.py
│   ├── mccabe_thiele.py
│   ├── rigorous.py
│   ├── diameter.py
│   ├── height.py
│   ├── reboiler.py
│   ├── condenser.py
│   ├── mechanical.py
│   ├── internals.py
│   ├── instrumentation.py
│   ├── energy_economics.py
│   ├── visualization.py
│   ├── ai_assistant.py
│   └── report.py
├── calculations/
│   └── distillation_calc.py    ← Engineering calculation engine
└── thermodynamics/
    └── thermo_engine.py        ← Thermodynamic property engine
```

## 🔧 Tech Stack
- **Frontend**: Streamlit + Custom CSS
- **Charts**: Plotly
- **Engineering Math**: NumPy, SciPy, Pandas
- **Thermodynamics**: `chemicals`, `thermo` libraries
- **AI**: Groq API (Llama 3.3 70B)

## 📐 Design Workflow (20 Sections)
1. 🏠 Home Dashboard
2. 📥 Feed Specifications
3. 🧪 Thermodynamics Database
4. 🏗️ Column Type Selection
5. ▦ Tray Design
6. ◎ Packing Design
7. ⚡ Shortcut Design (Fenske-Underwood-Gilliland)
8. 📈 McCabe-Thiele Graphical Method
9. 🔬 Rigorous Stage-by-Stage Design
10. 📐 Column Diameter (Fair Method)
11. 📏 Column Height
12. ♨️ Reboiler Design
13. ❄️ Condenser Design
14. ⚙️ Mechanical Design (ASME)
15. 🔧 Column Internals
16. 🎛️ Instrumentation & Control
17. 💰 Energy & Economics
18. 🖼️ Visualization (2D/3D)
19. 🤖 AI Assistant
20. 📋 Report Generator

## 📚 References
- McCabe, Smith & Harriott — Unit Operations
- Seader, Henley & Roper — Separation Process Principles
- Perry's Chemical Engineers' Handbook
- ASME & TEMA Standards
