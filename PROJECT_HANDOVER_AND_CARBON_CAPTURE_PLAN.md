# DistillAI Handover + Carbon Capture Project Blueprint

Repository link: https://github.com/zaini802/Distillation_proj_2.git

Use this file when starting a new Codex/chat session. Give the new chat this repository link and tell it:

> Read `PROJECT_HANDOVER_AND_CARBON_CAPTURE_PLAN.md` first. Understand the quality, UI style, engineering depth, and feature level of the completed DistillAI project. For the next project, build the Carbon Capture Design System at the same professional level.

---

## 1. Current Completed Project: DistillAI

Project name:

**DistillAI - Binary Distillation Column Design System**

Project type:

**Streamlit-based professional chemical engineering design software**

Main repository:

`https://github.com/zaini802/Distillation_proj_2.git`

Main entry file:

`app.py`

Main technology stack:

- Python
- Streamlit
- NumPy
- SciPy
- Pandas
- Plotly
- Groq AI API
- Custom DOCX/PDF report generation logic
- Dark industrial UI theme

Main purpose:

DistillAI is an AI-assisted binary distillation column design platform. It takes user inputs for feed, composition, pressure, purity, column type, and process basis, then performs engineering calculations, thermodynamic analysis, shortcut design, McCabe-Thiele method, tray/packed column sizing, heat exchanger duties, pressure drop, mechanical checks, economics, visualization, and professional report generation.

The project is designed to feel like a real engineering software tool, not a basic calculator.

---

## 2. DistillAI Quality Standard

Any future project should match this level:

- Professional dashboard
- Clear phase-wise workflow
- Industrial engineering calculations
- Step-by-step equations
- Formula boxes
- Color-coded calculation blocks
- Graphs with visible axes, legends, and reference lines
- User-friendly controls
- Session-state based design flow
- AI assistant integration
- Report export in Word/PDF style
- Sidebar branding and developer profile
- Final downloadable project files
- GitHub-ready structure
- Streamlit Cloud deploy readiness

The UI should not look like a simple student form. It should feel like a serious engineering design system.

---

## 3. DistillAI Existing Major Sections

### Home Dashboard

Includes:

- Project title and workflow overview
- Design progress tracker
- Main KPI cards
- Phase-based roadmap
- References and standards
- Clear dark theme styling

### Feed Specification

Includes:

- Binary component selection
- Light/heavy component data
- Feed flow rate
- Feed composition
- Distillate and bottoms purity
- Operating pressure and temperature
- Material balance
- Step-by-step calculations
- Clear equation/value/result formatting

### Thermodynamics Database

Includes:

- Built-in component database
- Vapor-liquid equilibrium curve
- Bubble/dew point calculations
- Relative volatility analysis
- VLE model advisor
- Manual VLE model selection
- Raoult's Law
- Modified Raoult's Law
- Wilson model
- NRTL model
- Azeotrope detection
- T-x-y phase diagram
- VLE models comparison
- Groq AI model explanation

### Column Type Selection

Includes:

- Tray column option
- Packed column option
- Selection guidance
- Comparison logic
- Suitability notes

### Shortcut Design

Includes:

- Fenske equation
- Underwood equation
- Gilliland correlation
- Kirkbride feed location
- Minimum stages
- Minimum reflux ratio
- Actual stages
- Reflux ratio
- Feed tray estimate
- Clear step-by-step calculations

### McCabe-Thiele Method

Includes:

- Pre-graph calculations
- Relative volatility
- Reflux ratio
- q-line
- Rectifying line
- Stripping line
- Stage stepping
- Interactive diagram controls above graph
- Stage labels toggle
- Clear plot styling

### Tray Design

Includes:

- Tray spacing
- Column diameter
- Column height
- Flooding velocity
- Active area
- Downcomer area
- Weeping/entrainment related checks
- Hydraulic calculations
- Graphs and visual clarity

### Packed Column Design

Includes:

- Packing type selection
- HETP/HTU-NTU style calculations
- Column diameter
- Packed height
- Flooding and pressure drop guidance
- Packing performance visibility

### Detailed Design

Includes:

- Reboiler design
- Condenser design
- Pressure drop
- Mechanical design
- Column internals
- Instrumentation
- Energy and economics
- Rigorous design style checks

### Visualization

Includes:

- Process animation
- Column visualization
- Packed/tray-based representation
- Multimedia support for local videos/images
- Process flow understanding

### Theory Concepts

Includes:

- Distillation theory handbook
- Basic concepts
- Key equations
- Industrial explanation
- Groq AI Q&A

### AI Assistant

Includes:

- Groq-powered engineering advisor
- Uses model `llama-3.1-8b-instant`
- Handles Groq client and REST fallback
- Gives process/design explanations
- Helps with troubleshooting

### Report Generator

Includes:

- Professional report structure
- Cover page
- Input tables
- Calculation summaries
- VLE graphs
- McCabe-Thiele graph
- Design output summary
- Developer page
- Downloadable report package
- Word/PDF style outputs

### Design Manager

Includes:

- Save/load design case concept
- Design health/summary support
- Useful for re-opening previous designs

---

## 4. DistillAI UI Design Notes

Overall look:

- Dark industrial theme
- High contrast
- Cyan accents
- Golden headings
- Red highlighted subheadings
- Green for valid/success states
- Clear bordered cards
- Professional sidebar

Approximate color language:

- Background: very dark navy/black
- Panel background: deep blue/gray
- Primary cyan: `#00b4d8`
- Golden heading: `#ffd166`
- Red/pink emphasis: `#ff4d6d`
- Green success: `#22c55e`
- White/off-white text for readability

Important UI rule:

Visibility is critical. Equations, values, results, and section headings should not blend into the background. Every important item should be easy to read on a laptop screen and in recorded demo videos.

---

## 5. Important Development Rules for Future Work

- Do not damage completed DistillAI sections unless explicitly requested.
- Keep Streamlit app modular.
- Use `st.session_state` for cross-section results.
- Use Plotly for engineering graphs.
- Keep all calculations visible and explainable.
- Use real chemical engineering equations where practical.
- When using simplified correlations, clearly label assumptions.
- Keep AI features optional so the app works without API key.
- Never hard-code private API keys.
- Use Streamlit secrets/environment variables for deployment.
- Keep report output professional because it is one of the most important deliverables.

---

## 6. Next Project Idea: Carbon Capture Design System

Suggested project name:

**CarbonCaptureAI - Industrial CO2 Capture Design & Optimization System**

Alternative names:

- Carbon Capture Process Design System
- AI-Powered CO2 Capture Plant Designer
- Industrial Carbon Capture & Sustainability Analyzer
- CarbonCapture Pro

Recommended final name:

**CarbonCaptureAI**

Main idea:

Build a Streamlit-based chemical engineering design system for carbon capture from industrial flue gas. The app should let users enter flue gas composition, flow rate, temperature, pressure, CO2 concentration, target capture efficiency, and selected technology. It should then calculate CO2 captured, solvent/adsorbent requirements, absorber/stripper design, energy demand, equipment sizing, economics, emissions reduction, and sustainability impact.

The app should feel like a complete industrial design platform, similar in quality and depth to DistillAI.

---

## 7. Carbon Capture Project Background

Many industrial plants emit CO2 through flue gas. Major sources include:

- Power plants
- Cement plants
- Steel plants
- Fertilizer plants
- Refineries
- Petrochemical units
- Boilers and furnaces

Carbon capture is used to separate CO2 from these gas streams before release to the atmosphere. The captured CO2 can be:

- Compressed and stored underground
- Used in enhanced oil recovery
- Used in chemicals, fuels, urea, dry ice, or carbonation
- Sold as industrial CO2 if purity is suitable

This project is related to:

- Sustainability
- Climate change mitigation
- Environmental engineering
- Process design
- Energy optimization
- Green chemical engineering
- Industrial decarbonization

It can be useful for higher studies and scholarship applications because it connects chemical engineering with sustainability and modern AI/software tools.

---

## 8. What The User Will Actually Design

The project should mainly design a post-combustion CO2 capture system.

Recommended core technology for first version:

**Amine absorption using MEA solvent**

Why MEA first:

- Most common academic/industrial reference solvent
- Easy to understand
- Good for flue gas CO2 capture
- Strong engineering basis
- Many design equations are available

Later, add comparison with:

- DEA
- MDEA
- PZ-promoted solvents
- Physical solvents
- Solid adsorption
- Membranes
- Cryogenic separation
- Calcium looping

But first version should focus on amine absorption so the design is practical and not too scattered.

---

## 9. Carbon Capture Main Workflow

Recommended workflow:

1. Home Dashboard
2. Flue Gas Input
3. Technology Selection
4. Solvent/Material Database
5. Capture Performance
6. Absorber Design
7. Regenerator/Stripper Design
8. Heat Exchanger and Utility Design
9. CO2 Compression and Drying
10. Emissions Reduction
11. Energy and Economics
12. Environmental Impact
13. Optimization
14. Visualization
15. AI Sustainability Advisor
16. Report Generator
17. Design Case Manager

---

## 10. CarbonCaptureAI Detailed Module Plan

### Module 1: Home Dashboard

Purpose:

Give user a complete overview of the carbon capture system.

Should include:

- Project title
- Short system description
- Workflow progress
- Main KPIs:
  - CO2 captured
  - Capture efficiency
  - Solvent circulation rate
  - Reboiler duty
  - CO2 avoided
  - Cost per ton CO2
- Phase cards
- References and standards
- Quick design health indicator

UI style:

- Same professional dark theme as DistillAI
- Green/cyan sustainability accents
- Golden headings
- Clear KPI cards

---

### Module 2: Flue Gas Input

Purpose:

Collect all process basis inputs.

Inputs:

- Industry type:
  - Coal power plant
  - Natural gas power plant
  - Cement plant
  - Steel plant
  - Refinery heater
  - Boiler
  - Custom
- Flue gas flow rate:
  - kmol/h
  - kg/h
  - Nm3/h
- Temperature
- Pressure
- CO2 mole percentage
- N2 mole percentage
- O2 mole percentage
- H2O/vapor percentage
- SOx ppm
- NOx ppm
- Particulates flag
- Operating hours per year
- Target capture efficiency
- Required CO2 product purity

Outputs:

- Total molar flow
- CO2 inlet flow
- CO2 mass flow
- CO2 annual emissions
- Dry/wet gas basis conversion
- Flue gas molecular weight
- Gas density
- Volumetric flow

Calculations:

- CO2 molar flow
- CO2 mass flow
- Annual CO2 emission
- Mixture molecular weight
- Ideal gas density
- Gas volumetric flow

Display:

- Input table
- Composition pie chart
- Flow summary cards
- Step-by-step material balance

---

### Module 3: Technology Selection

Purpose:

Help user select suitable carbon capture technology.

Technologies:

- Chemical absorption using MEA
- Chemical absorption using MDEA/PZ
- Physical absorption
- Membrane separation
- PSA/VSA adsorption
- Cryogenic separation
- Calcium looping
- Oxy-fuel combustion concept

Selection logic:

- Low CO2 concentration flue gas: amine absorption
- High pressure gas: physical solvent or membrane
- High CO2 concentration: membrane/cryogenic may be possible
- Very dilute stream: chemical absorption
- High purity requirement: absorption + compression/polishing

Outputs:

- Suggested technology
- Suitability score
- Advantages
- Limitations
- Recommended next design path

Add AI button:

**Ask AI - Why this technology?**

AI should explain:

- Why selected technology is suitable
- Main trade-offs
- Energy penalty
- Environmental concerns
- Industrial use cases

---

### Module 4: Solvent/Material Database

Purpose:

Store and compare capture solvents/materials.

Solvent database:

- MEA
- DEA
- MDEA
- Piperazine
- AMP
- Potassium carbonate
- Chilled ammonia

Properties:

- Molecular weight
- Typical concentration
- CO2 loading capacity
- Lean loading
- Rich loading
- Heat of absorption
- Specific heat
- Density
- Viscosity
- Corrosion risk
- Regeneration energy range
- Degradation risk

Outputs:

- Solvent comparison table
- Best solvent recommendation
- Solvent property cards

Graphs:

- Solvent capacity comparison
- Reboiler duty comparison
- Corrosion/degradation risk chart

---

### Module 5: Capture Performance

Purpose:

Calculate actual CO2 captured and outlet gas composition.

Inputs:

- Capture efficiency
- Solvent selected
- CO2 inlet flow
- Target outlet CO2

Outputs:

- CO2 captured
- CO2 remaining in treated gas
- Outlet gas composition
- CO2 removal efficiency
- Annual CO2 captured
- Annual CO2 emitted after capture
- CO2 avoided

Calculations:

- CO2 captured = inlet CO2 x capture efficiency
- CO2 outlet = inlet CO2 - captured CO2
- Annual captured mass = hourly captured mass x operating hours
- CO2 avoided accounts for energy penalty

Display:

- Sankey diagram
- Before/after emission bar chart
- Treated gas composition table

---

### Module 6: Solvent Circulation Rate

Purpose:

Calculate required liquid solvent flow rate.

Inputs:

- CO2 captured
- Lean loading
- Rich loading
- Solvent concentration
- Solvent molecular weight/density

Key equation:

Solvent molar flow = CO2 captured / (rich loading - lean loading)

Outputs:

- Solvent circulation rate
- Lean solvent flow
- Rich solvent flow
- Water/amine fraction
- L/G ratio

Display:

- Step-by-step solvent balance
- Solvent rate KPI card
- Sensitivity chart vs lean/rich loading

---

### Module 7: Absorber Column Design

Purpose:

Size the CO2 absorber column.

Inputs:

- Gas flow rate
- Liquid solvent rate
- Operating temperature
- Operating pressure
- Packing type
- Target removal efficiency
- Allowable pressure drop
- Flooding fraction

Packing types:

- Raschig rings
- Pall rings
- Intalox saddles
- Structured packing
- Mellapak type packing

Calculations:

- Gas superficial velocity
- Flooding velocity estimate
- Column diameter
- Cross-sectional area
- Packing height
- HTU/NTU method
- Pressure drop
- Liquid distributor check

Outputs:

- Absorber diameter
- Packed height
- Total column height
- Pressure drop
- Flooding percentage
- L/G ratio
- Design status

Graphs:

- Operating point vs flooding limit
- Absorber height vs capture efficiency
- Pressure drop vs gas velocity

Visualization:

- Packed absorber diagram
- Gas rising / liquid falling animation
- CO2 absorption color gradient

---

### Module 8: Regenerator/Stripper Design

Purpose:

Design solvent regeneration section where CO2 is stripped from rich solvent.

Inputs:

- Rich solvent flow
- Lean loading target
- Reboiler temperature
- Stripper pressure
- Reflux ratio estimate
- Steam pressure

Calculations:

- CO2 stripped
- Reboiler duty
- Condenser duty
- Steam consumption
- Regenerator diameter
- Regenerator height
- Lean/rich heat exchanger duty

Outputs:

- Stripper diameter
- Stripper height
- Reboiler duty
- Condenser duty
- Steam rate
- Regenerated solvent flow
- CO2 overhead flow

Graphs:

- Reboiler duty vs lean loading
- Steam consumption vs capture efficiency
- Rich/lean loading profile

---

### Module 9: Heat Exchanger and Utility Design

Purpose:

Calculate heat duties and utility requirements.

Equipment:

- Lean/rich solvent heat exchanger
- Reboiler
- Condenser
- Solvent cooler
- CO2 cooler

Calculations:

- Heat exchanger duty
- LMTD
- Heat transfer area
- Cooling water requirement
- Steam requirement
- Utility cost

Outputs:

- Heat duty table
- Utility consumption table
- Annual energy use
- Energy penalty

Graphs:

- Utility breakdown
- Energy Sankey diagram
- Temperature profiles

---

### Module 10: CO2 Compression and Drying

Purpose:

Prepare captured CO2 for transport/storage/utilization.

Inputs:

- CO2 flow rate
- CO2 purity
- Initial pressure
- Final pressure
- Compressor stages
- Compressor efficiency
- Intercooling temperature

Calculations:

- Multistage compression power
- Outlet temperature
- Intercooler duty
- Dehydration requirement

Outputs:

- Compressor power
- Number of stages
- Cooling duty
- CO2 product conditions
- Specific energy per ton CO2

Graphs:

- Pressure vs stage
- Temperature vs stage
- Compression power vs final pressure

---

### Module 11: Emissions Reduction and Sustainability

Purpose:

Show environmental value of the design.

Calculations:

- Baseline annual CO2 emissions
- Captured CO2
- Residual emissions
- Energy penalty emissions
- Net CO2 avoided
- Capture efficiency
- Avoided emission percentage

Optional equivalence metrics:

- Cars removed equivalent
- Trees equivalent
- Annual emission reduction

Important:

Use careful wording. Equivalence values should be approximate and clearly marked as estimates.

Graphs:

- Before/after emissions
- Net avoided CO2
- Annual reduction trend
- Carbon intensity reduction

---

### Module 12: Energy and Economics

Purpose:

Estimate project cost and operating cost.

Inputs:

- Electricity cost
- Steam cost
- Cooling water cost
- Solvent cost
- Plant operating hours
- CEPCI factor
- Installation factor
- Carbon credit price
- CO2 selling price

CAPEX:

- Absorber cost
- Stripper cost
- Heat exchangers
- Reboiler
- Condenser
- Pumps
- Compressor
- Solvent inventory
- Installation factor

OPEX:

- Steam cost
- Electricity cost
- Cooling water cost
- Solvent makeup
- Maintenance
- Labor estimate

Outputs:

- Total installed cost
- Annual operating cost
- Cost per ton CO2 captured
- Cost per ton CO2 avoided
- Payback period
- NPV estimate
- Carbon credit benefit

Graphs:

- CAPEX breakdown
- OPEX breakdown
- Cost per ton sensitivity
- Payback chart

---

### Module 13: Optimization

Purpose:

Let user improve design using parameter sweeps.

Optimization variables:

- Capture efficiency
- Solvent circulation rate
- Lean loading
- Rich loading
- Absorber pressure drop
- Packing height
- Reboiler duty
- Compressor pressure

Objective options:

- Minimize cost per ton CO2
- Minimize energy consumption
- Maximize capture efficiency
- Minimize column size
- Balanced design

Outputs:

- Best operating point
- Trade-off table
- Sensitivity plots
- Recommendation cards

Graphs:

- Capture efficiency vs reboiler duty
- Cost vs capture efficiency
- Solvent flow vs column diameter
- Pareto-style plot

---

### Module 14: Visualization

Purpose:

Show the full carbon capture process visually.

Visuals:

- Complete process flow diagram
- Flue gas to absorber
- Lean solvent entering top
- Rich solvent leaving bottom
- Regenerator/stripper
- Reboiler/condenser
- CO2 compression
- CO2 storage/utilization

Animations:

- Gas rising through absorber
- Solvent falling through packing
- CO2 transfer from gas to liquid
- Solvent regeneration
- CO2 product stream leaving system

Images:

- Absorber column
- Structured packing
- Random packing
- Amine plant flow diagram
- CO2 compressor
- CO2 storage concept

Interactive controls:

- Capture efficiency slider
- Solvent rate slider
- Reboiler duty slider
- Compression pressure slider
- Show/hide stream labels

---

### Module 15: AI Sustainability Advisor

Purpose:

Use Groq AI as an engineering and sustainability advisor.

Features:

- Explain selected capture technology
- Explain why energy penalty is high
- Suggest how to reduce reboiler duty
- Explain absorber flooding or pressure drop
- Compare MEA vs MDEA
- Explain cost per ton CO2
- Suggest optimization direction
- Help interpret final report

API model:

- `llama-3.1-8b-instant`

Important:

- App must work without API key
- If key is missing, show friendly message
- Do not crash
- Do not expose key

---

### Module 16: Report Generator

Purpose:

Generate a professional engineering report.

Report sections:

- Cover page
- Executive summary
- Project overview
- Input data
- Flue gas basis
- Technology selection
- Solvent selection
- CO2 capture calculations
- Absorber design
- Regenerator design
- Heat exchanger/utility summary
- Compression section
- Energy and economics
- Environmental impact
- Optimization results
- Graphs and visualizations
- Final design summary
- Conclusion
- About developer

Output formats:

- DOCX
- PDF
- ZIP package with graphs and data

Report should feel like:

- Professional engineering design report
- Internship/project submission quality
- Industrial software output

---

### Module 17: Design Case Manager

Purpose:

Let user save and reload design cases.

Features:

- Save current case as JSON
- Load previous design
- Compare two cases
- Export case summary
- Track design status

Useful case examples:

- Cement plant capture
- Coal power plant capture
- Natural gas flue gas capture
- Refinery heater capture

---

## 11. CarbonCaptureAI Suggested File Structure

Recommended structure:

```text
carbon-capture-ai/
  app.py
  requirements.txt
  README.md
  assets/
    styles.css
    images/
    media/
  sections/
    home.py
    flue_gas.py
    technology_selection.py
    solvent_database.py
    capture_performance.py
    absorber_design.py
    stripper_design.py
    heat_exchangers.py
    compression.py
    emissions.py
    economics.py
    optimization.py
    visualization.py
    ai_advisor.py
    report.py
    design_manager.py
  calculations/
    gas_properties.py
    capture_balance.py
    absorber.py
    stripper.py
    utilities.py
    compression.py
    economics.py
    emissions.py
  data/
    solvents.json
    packing_data.json
    standards.json
    sample_cases.json
  saved_cases/
```

---

## 12. CarbonCaptureAI Important Calculations

### Flue Gas Molecular Weight

Mixture molecular weight:

`MW_mix = sum(y_i * MW_i)`

### CO2 Inlet Flow

`n_CO2,in = y_CO2 * n_total`

### CO2 Captured

`n_CO2,captured = eta_capture * n_CO2,in`

### CO2 Outlet

`n_CO2,out = n_CO2,in - n_CO2,captured`

### Annual Captured CO2

`m_CO2,annual = m_CO2,captured_hourly * operating_hours`

### Solvent Circulation Rate

`L_solvent = n_CO2,captured / (alpha_rich - alpha_lean)`

Where:

- `alpha_rich` = rich CO2 loading
- `alpha_lean` = lean CO2 loading

### Absorber Diameter

Estimate from allowable superficial gas velocity:

`A = Q_gas / u_allowable`

`D = sqrt(4A/pi)`

### Packed Height

Using HTU/NTU concept:

`Z = HTU * NTU`

### Reboiler Duty

Simplified:

`Q_reb = m_CO2,captured * specific_regeneration_energy`

Typical MEA range:

`3.0 - 4.5 GJ/ton CO2`

### Compression Power

Use multistage compressor approximation:

`W = n * R * T * k/(k-1) * [(P2/P1)^((k-1)/k) - 1] / efficiency`

### Cost Per Ton CO2

`Cost_per_ton = Annualized_total_cost / Annual_CO2_captured`

### Net CO2 Avoided

`CO2_avoided = CO2_captured - CO2_emitted_due_to_energy_penalty`

---

## 13. International Standards and References

Useful standards/references for CarbonCaptureAI:

- IPCC Carbon Capture and Storage reports
- IEA carbon capture reports
- NETL Carbon Capture Program references
- DOE/NETL cost estimation methodology
- ISO 27914 - Carbon dioxide capture, transportation and geological storage
- ISO 14040 / ISO 14044 - Life cycle assessment
- ISO 14064 - Greenhouse gas accounting and verification
- API 521 / API 520 for pressure relief concepts
- ASME BPVC Section VIII for pressure vessels
- TEMA for heat exchangers
- GPSA Engineering Data Book for gas processing
- Perry's Chemical Engineers' Handbook
- Coulson & Richardson Chemical Engineering Design
- Seader, Henley & Roper separation process principles
- Kohl & Nielsen gas purification

Use these references for credibility, but do not claim strict certified design unless the app actually implements the full standard.

---

## 14. CarbonCaptureAI Recommended Sample Cases

### Case 1: Natural Gas Power Plant

- CO2 concentration: 3-5 mol%
- Large gas flow
- Low CO2 concentration
- MEA absorption recommended

### Case 2: Coal Power Plant

- CO2 concentration: 12-15 mol%
- High gas flow
- MEA or advanced amine recommended

### Case 3: Cement Plant

- CO2 concentration: 20-30 mol%
- Strong sustainability relevance
- Good for LinkedIn/project demo

### Case 4: Refinery Heater

- CO2 concentration: 8-12 mol%
- Industrial process relevance

Recommended demo case:

**Cement plant CO2 capture**, because it is highly related to industrial decarbonization and sustainability.

---

## 15. CarbonCaptureAI UI/UX Requirements

The app should:

- Be modular like DistillAI
- Use sidebar phase navigation
- Use dark professional theme
- Use clear colored KPI cards
- Use golden headings
- Use red for important input headings/warnings
- Use green for sustainability/success metrics
- Use cyan for main accents
- Show equations clearly
- Use tables for inputs and results
- Use graphs in every technical section where useful
- Avoid crowded screens
- Avoid low-contrast text
- Keep charts readable in screen recordings

Recommended sidebar phases:

- Phase 1 - Process Basis
- Phase 2 - Capture Technology
- Phase 3 - Equipment Design
- Phase 4 - Energy & Economics
- Phase 5 - Output & AI

---

## 16. CarbonCaptureAI Graphs To Include

Important graphs:

- Flue gas composition pie chart
- CO2 captured vs emitted bar chart
- Capture efficiency vs solvent flow
- Solvent comparison chart
- Absorber flooding plot
- Pressure drop vs gas velocity
- Absorber height vs capture efficiency
- Rich/lean loading profile
- Reboiler duty vs lean loading
- Energy Sankey diagram
- Compression pressure profile
- CAPEX breakdown
- OPEX breakdown
- Cost per ton sensitivity
- CO2 avoided over years
- Optimization trade-off plot

---

## 17. CarbonCaptureAI Visualizations

Should include:

- 2D process flow diagram
- Animated absorber column
- CO2 absorption gradient
- Regenerator animation
- Solvent loop visualization
- CO2 compression train
- Stream labels with flow rates
- Optional local image/video support

Potential visual concept:

Flue gas enters absorber from bottom. Lean solvent enters from top. CO2 is transferred from gas to liquid. Clean gas exits top. Rich solvent goes to regenerator. Heat strips CO2. Lean solvent recycles back. CO2 product goes to compression/storage.

---

## 18. CarbonCaptureAI AI Prompts

AI advisor should be specialized as:

**AI Carbon Capture Engineering Advisor**

It should answer:

- Why is MEA selected?
- Why is reboiler duty high?
- How can energy consumption be reduced?
- What happens if capture efficiency is increased?
- What is the meaning of lean/rich loading?
- How does absorber flooding affect design?
- Is this design economical?
- What are the environmental benefits?
- How does cement plant capture differ from power plant capture?

AI responses should be:

- Engineering-focused
- Short enough to read
- Practical
- Based on current user inputs when possible
- Clearly marked as advisory, not certified design

---

## 19. CarbonCaptureAI Final Report Structure

Report title:

**Carbon Capture Process Design Report**

Required sections:

1. Cover Page
2. Executive Summary
3. Introduction
4. Process Basis
5. Flue Gas Characterization
6. Technology Selection
7. Solvent/Material Selection
8. CO2 Capture Material Balance
9. Absorber Design
10. Regenerator Design
11. Heat Exchanger and Utilities
12. CO2 Compression
13. Energy Analysis
14. Economic Evaluation
15. Environmental Impact
16. Optimization Results
17. Final Design Summary
18. Conclusion
19. About Developer

Developer info:

- Zunair Shahzad
- Chemical Engineering - UET Lahore New Campus
- AI-assisted Chemical Engineering Projects

---

## 20. CarbonCaptureAI Deployment Notes

Recommended deployment:

- GitHub repository
- Streamlit Community Cloud
- `app.py` at root
- `requirements.txt` complete
- Secrets stored in Streamlit secrets

Secrets:

```toml
GROQ_API_KEY = "your_key_here"
GROQ_MODEL = "llama-3.1-8b-instant"
```

Do not commit API keys.

---

## 21. First Build Milestone For CarbonCaptureAI

Start with a clean MVP:

1. Home dashboard
2. Flue gas input
3. CO2 material balance
4. MEA solvent circulation
5. Absorber sizing
6. Regenerator duty
7. Emissions reduction
8. Basic economics
9. Visualization
10. Report generator

After MVP:

1. Add solvent comparison
2. Add technology advisor
3. Add optimization
4. Add AI assistant
5. Add case manager
6. Add advanced graphics and animations

---

## 22. Suggested New Chat Starting Prompt

Use this prompt in a new Codex/chat session:

```text
I have completed a Streamlit project called DistillAI. Repository:
https://github.com/zaini802/Distillation_proj_2.git

Please read PROJECT_HANDOVER_AND_CARBON_CAPTURE_PLAN.md in that repository first.

Now I want to build a new project called CarbonCaptureAI at the same quality level:
- professional Streamlit UI
- dark industrial theme
- chemical engineering calculations
- graphs and visualizations
- AI advisor
- report generator
- design case manager
- GitHub/Streamlit deployment ready

Start by creating the full project structure and MVP for post-combustion CO2 capture using MEA absorption.
Do not make it a simple calculator. Make it a complete engineering design system.
```

---

## 23. Final Direction

DistillAI is the quality benchmark.

CarbonCaptureAI should become the next portfolio-level project, focused on sustainability, environment, and industrial decarbonization. It should demonstrate that the developer can combine:

- Chemical engineering fundamentals
- Process design
- Sustainability analysis
- Engineering economics
- AI assistance
- Software development
- Professional reporting

This makes it valuable for LinkedIn, GitHub, higher studies, scholarships, and technical interviews.

