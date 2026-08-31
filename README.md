# Automatic Fan Speed Control using Fuzzy Logic (Mamdani FIS)

An interactive Streamlit application and Python implementation of a Mamdani Fuzzy Inference System for controlling fan speed based on ambient temperature and humidity.

## Project Structure
- `app.py` - Streamlit application entry point (UI layout and pipeline orchestration)
- `fuzzy_engine.py` - Core fuzzy inference system logic (membership functions, rules, fuzzification, aggregation, defuzzification)
- `charts.py` - Matplotlib visualization generator for each step of fuzzy inference
- `theme.py` - Design tokens, color palettes, and custom styling
- `practice/main.py` - CLI script and standalone implementation
- `requirements.txt` - Dependencies

## Setup & Running

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Streamlit App**:
   ```bash
   streamlit run app.py
   ```
