# NADRA Service Center Simulation System
**Discrete-Event Simulation (DES) — Simulation & Modeling Project**

Built with **Python** & **Streamlit** following the classical discrete simulation table format (*Discrete-Event System Simulation*, Jerry Banks).

---

## 📁 Project Structure (3 Files Only)

```
d:/SM Project/
├── config.py           # Baseline probability distributions & default counter settings
├── simulation.py       # Core discrete-event simulation engine & textbook formulas
├── app.py              # Modern Streamlit UI displaying textbook tables & summaries
└── requirements.txt    # Dependencies (streamlit, pandas)
```

---

## 🚀 How to Run

1. Open PowerShell or Command Prompt in this folder (`d:\SM Project`):
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. The interactive dashboard will automatically open in your web browser at `http://localhost:8501`.

---

## 📋 Features & Tables

1. **Top KPI Summary Cards**:
   - Total Citizens Served
   - Average Waiting Time (mins)
   - Total & Average Service Time (mins)
   - Average Time in System (mins)
   - Probability of Waiting (%)
   - Overtime Minutes

2. **Tab 1: Simulation Ledger Table (Table 2.21 Format)**:
   - Row-by-row simulation log with 2-digit random numbers (`01-99`, `00`).
   - Columns: `Citizen #`, `RN Arrival`, `Inter-Arrival (min)`, `Arrival Time`, `RN Service Type`, `Service Type`, `RN Duration`, `Service Time (min)`, `Assigned Counter`, `Service Begins`, `Wait Time (min)`, `Service Ends`, `Time in System (min)`.
   - Filter by Service Type and Day.
   - Column totals ($\sum \text{Service Time}$, $\sum \text{Wait Time}$, $\sum \text{Time in System}$).
   - **Download as CSV** button for Excel verification.

3. **Tab 2: Service & Counter Analysis Tables (Manual Analysis)**:
   - **Service Demand Table**: Shows which service comes most, total service time, and average waiting time per service category.
   - **Counter Performance Table**: Shows citizens served, busy time, and percentage utilization per counter.

4. **Tab 3: Random-Digit Probability Tables (Table 2.19 & 2.20 Format)**:
   - Theoretical cumulative probability ranges mapped to classroom intervals (`01-15`, `16-40`, ..., `91-00`).

---

## 🎯 How to Test Different Scenarios

- In the left sidebar, change the number of counters assigned to any service (e.g. increase New CNIC counters from 2 to 3).
- Click **"🚀 Run Simulation"**.
- Instantly compare the new average waiting time, total service time, and counter utilizations.
