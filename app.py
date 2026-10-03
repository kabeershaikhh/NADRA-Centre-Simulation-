"""
NADRA Service Center Simulation System
Streamlit Application — High-Contrast Professional UI
- Deep Blue Sidebar with crisp white text
- Royal Blue table headers (#1E40AF) with guaranteed visibility
- All 7 theoretical probability tables displayed on initial load
- Manual execution only (runs on button click)
"""

import streamlit as st
import pandas as pd
from config import (
    DEFAULT_WORKING_HOURS,
    DEFAULT_DAYS,
    DEFAULT_COUNTERS,
    INTER_ARRIVAL_DIST,
    SERVICE_TYPE_DIST,
    SERVICE_TIME_DISTS
)
from simulation import run_simulation, build_rn_table, build_split_ledger

# Page Configuration
st.set_page_config(
    page_title="NADRA Simulation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Deep Blue Sidebar + Crisp White Main View + Blue Table Accents
st.markdown("""
<style>
    /* Main App Background */
    html, body, [class*="css"], .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* DEEP BLUE SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #1E3A8A !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #3B82F6 !important;
        opacity: 0.3 !important;
        margin: 16px 0 !important;
    }
    /* Number input boxes inside sidebar */
    section[data-testid="stSidebar"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
    }

    /* Primary Run Simulation Button in Sidebar */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: 1px solid #60A5FA !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
        margin-top: 10px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Main Area Form Controls */
    label, .stSelectbox label {
        color: #0F172A !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        background-color: transparent !important;
        border: none !important;
        padding: 10px 18px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1E40AF !important;
        border-bottom: 3px solid #1E40AF !important;
    }
    div[data-baseweb="tab-list"] {
        border-bottom: 2px solid #E2E8F0 !important;
        gap: 8px !important;
    }

    /* Download Button */
    div.stDownloadButton > button {
        background-color: #1E40AF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
    }

    /* Metric KPI Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #1E40AF;
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 6px;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #64748B;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Ledger Column Totals Box */
    .totals-box {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 4px solid #1E40AF;
        border-radius: 8px;
        padding: 12px 18px;
        margin-top: 15px;
    }

    /* Hide column header menu button in dataframes */
    [data-testid="stDataFrame"] [data-testid="glideDataEditor"] th button,
    [data-testid="stDataFrame"] header button,
    .dvn-scroller th button,
    [data-testid="column-header-menu-button"] {
        display: none !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)


def render_html_table(df, title=None):
    """
    Renders a DataFrame as an HTML table with solid Royal Blue headers (#1E40AF),
    white text, and clean borders for 100% guaranteed high contrast.
    """
    html = ""
    if title:
        html += f"<div style='font-weight: 700; color: #1E3A8A; font-size: 14px; margin-bottom: 6px;'>{title}</div>"
    
    html += """
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; border: 1px solid #CBD5E1; border-radius: 6px; overflow: hidden; font-size: 13px;">
        <thead>
            <tr style="background-color: #1E40AF; color: #FFFFFF; text-align: left;">
    """
    for col in df.columns:
        html += f"<th style='padding: 9px 12px; font-weight: 600; font-size: 12px; letter-spacing: 0.3px; border-right: 1px solid rgba(255,255,255,0.15); position: sticky; top: 0; background-color: #1E40AF; z-index: 1;'>{col}</th>"
    
    html += "</tr></thead><tbody>"
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#F8FAFC" if i % 2 == 1 else "#FFFFFF"
        html += f"<tr style='background-color: {bg}; border-bottom: 1px solid #E2E8F0; color: #0F172A;'>"
        for col in df.columns:
            val = row[col]
            html += f"<td style='padding: 7px 12px; border-right: 1px solid #E2E8F0;'>{val}</td>"
        html += "</tr>"
    
    html += "</tbody></table>"
    return html


# Main Header
st.markdown("""
<div style="padding-bottom: 12px; margin-bottom: 20px; border-bottom: 2px solid #E2E8F0;">
    <h2 style="margin: 0; font-size: 26px; font-weight: 800; color: #0F172A;">NADRA Service Center Simulation</h2>
    <p style="margin: 4px 0 0 0; font-size: 14px; color: #475569; font-weight: 500;">
        Discrete-Event Queueing Model
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR (DEEP BLUE THEME) -----------------
st.sidebar.markdown("### Simulation Settings")

sim_days = st.sidebar.number_input("Duration (Days)", min_value=1, max_value=30, value=DEFAULT_DAYS, step=1)
working_hours = st.sidebar.number_input("Working Hours / Day", min_value=1, max_value=24, value=DEFAULT_WORKING_HOURS, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### Counter Allocation")
counters = {}
counters["New CNIC"] = st.sidebar.number_input("New CNIC Counters", min_value=1, max_value=10, value=DEFAULT_COUNTERS["New CNIC"])
counters["CNIC Renewal"] = st.sidebar.number_input("CNIC Renewal Counters", min_value=1, max_value=10, value=DEFAULT_COUNTERS["CNIC Renewal"])
counters["B-Form / CRC"] = st.sidebar.number_input("B-Form / CRC Counters", min_value=1, max_value=10, value=DEFAULT_COUNTERS["B-Form / CRC"])
counters["Modification"] = st.sidebar.number_input("Modification Counters", min_value=1, max_value=10, value=DEFAULT_COUNTERS["Modification"])
counters["Lost CNIC"] = st.sidebar.number_input("Lost CNIC Counters", min_value=1, max_value=10, value=DEFAULT_COUNTERS["Lost CNIC"])

st.sidebar.markdown("---")
st.sidebar.markdown("###  Random Seed")
use_seed = st.sidebar.checkbox("Fixed Seed (Reproducibility)", value=True)
seed_value = st.sidebar.number_input("Seed Value", min_value=0, max_value=999999, value=42) if use_seed else None

# Run Simulation Button
run_button = st.sidebar.button(" Run Simulation", type="primary", use_container_width=True)

# Trigger simulation ONLY when user clicks the button
if run_button:
    with st.spinner("Running Discrete-Event Simulation..."):
        df_ledger, sys_summary, df_service, df_counter, rn_tables = run_simulation(
            working_hours=working_hours,
            days=sim_days,
            counter_counts=counters,
            seed=seed_value
        )
        st.session_state["sim_results"] = {
            "df_ledger": df_ledger,
            "sys_summary": sys_summary,
            "df_service": df_service,
            "df_counter": df_counter,
            "rn_tables": rn_tables
        }

# Pre-build theoretical RN tables for initial display
rn_iat = build_rn_table(INTER_ARRIVAL_DIST)[["Value", "Probability", "Cumulative Probability", "Random-Digit Assignment"]]
rn_iat.columns = ["Inter-Arrival (min)", "Probability", "Cum. Prob", "RN Assignment"]

rn_svc = build_rn_table(SERVICE_TYPE_DIST)[["Value", "Probability", "Cumulative Probability", "Random-Digit Assignment"]]
rn_svc.columns = ["Service Type", "Probability", "Cum. Prob", "RN Assignment"]

rn_durations = {
    svc: build_rn_table(dist)[["Value", "Probability", "Cumulative Probability", "Random-Digit Assignment"]]
    for svc, dist in SERVICE_TIME_DISTS.items()
}
for svc in rn_durations:
    rn_durations[svc].columns = ["Service Time (min)", "Probability", "Cum. Prob", "RN Range"]

# ----------------- MAIN VIEW -----------------

# Case 1: Initial View (BEFORE running simulation) -> SHOW ALL 7 THEORETICAL TABLES
if "sim_results" not in st.session_state:
    st.info("👈 Set your counter counts in the blue sidebar on the left and click **'🚀 Run Simulation'** to generate the simulation ledger and performance analysis.")
    
    st.markdown("<h3 style='color:#0F172A; margin: 20px 0 6px 0;'>Theoretical Probability & Random-Digit Tables</h3>", unsafe_allow_html=True)
    st.caption("All 7 classroom random number distribution intervals (01–99, 00) mapped to cumulative probabilities.")
    
    # 1. Inter-arrival & Service Type Demand
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(render_html_table(rn_iat, "1. Inter-Arrival Time Distribution"), unsafe_allow_html=True)
    with col_b:
        st.markdown(render_html_table(rn_svc, "2. Service Category Demand Distribution"), unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#1E3A8A; font-weight:700; margin-bottom: 8px;'>3. Service Duration Distributions by Category</h4>", unsafe_allow_html=True)

    # 2. All 5 Service Duration Tables
    col_dur1, col_dur2, col_dur3 = st.columns(3)

    with col_dur1:
        st.markdown(render_html_table(rn_durations["New CNIC"], "New CNIC Duration"), unsafe_allow_html=True)
        st.markdown(render_html_table(rn_durations["Modification"], "Modification Duration"), unsafe_allow_html=True)

    with col_dur2:
        st.markdown(render_html_table(rn_durations["CNIC Renewal"], "CNIC Renewal Duration"), unsafe_allow_html=True)
        st.markdown(render_html_table(rn_durations["Lost CNIC"], "Lost CNIC Duration"), unsafe_allow_html=True)

    with col_dur3:
        st.markdown(render_html_table(rn_durations["B-Form / CRC"], "B-Form / CRC Duration"), unsafe_allow_html=True)


# Case 2: Simulation has been executed -> SHOW METRICS & RESULTS
else:
    res = st.session_state["sim_results"]
    df_ledger = res["df_ledger"]
    sys_summary = res["sys_summary"]
    df_service = res["df_service"]
    df_counter = res["df_counter"]
    rn_tables = res["rn_tables"]

    # 1. High-Contrast Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Citizens Served</div>
            <div class="metric-value">{sys_summary['Total Citizens Served']}</div>
            <div class="metric-sub">Total completed</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Wait Time</div>
            <div class="metric-value">{sys_summary['Average Waiting Time (min)']} <span style="font-size:14px; font-weight:500;">min</span></div>
            <div class="metric-sub">Queue average</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Service</div>
            <div class="metric-value">{sys_summary['Total Service Time (min)']} <span style="font-size:14px; font-weight:500;">min</span></div>
            <div class="metric-sub">Avg: {sys_summary['Average Service Time (min)']} min</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg System Time</div>
            <div class="metric-value">{sys_summary['Average Time in System (min)']} <span style="font-size:14px; font-weight:500;">min</span></div>
            <div class="metric-sub">Wait + Service</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Delayed Citizens</div>
            <div class="metric-value">{sys_summary['Probability of Waiting (%)']}%</div>
            <div class="metric-sub">Had to wait in line</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Overtime</div>
            <div class="metric-value">{sys_summary['Total Overtime (min)']} <span style="font-size:14px; font-weight:500;">min</span></div>
            <div class="metric-sub">Past closing time</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Main Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Simulation Ledger Table",
        "📊 Service & Counter Summary",
        "🎲 Random-Digit Tables"
    ])

    # TAB 1: Ledger Table (Jerry Banks Table 2.14 / 2.21)
    with tab1:
        st.markdown("<h4 style='color:#0F172A; margin: 10px 0 4px 0;'>Citizen-by-Citizen Simulation Ledger</h4>", unsafe_allow_html=True)
        st.caption("Citizen-by-citizen simulation ledger showing queue waiting times and server schedules.")

        f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 2.5, 1.8])
        with f_col1:
            service_filter = st.selectbox("Filter by Service Type:", ["All Services"] + list(counters.keys()))
        with f_col2:
            if sim_days > 1:
                day_filter = st.selectbox("Filter by Day:", ["All Days"] + [f"Day {d}" for d in range(1, sim_days + 1)])
            else:
                day_filter = "All Days"
        with f_col3:
            table_format = st.radio(
                "Table Format:",
                ["Separated Columns", "Single Column"],
                horizontal=True
            )
        with f_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

        # Apply filters
        display_df = df_ledger.copy()
        if service_filter != "All Services":
            display_df = display_df[display_df["Service Type"] == service_filter]
        if day_filter != "All Days":
            day_num = int(day_filter.split(" ")[1])
            display_df = display_df[display_df["Day"] == day_num]

        # Choose table display format
        all_cnt_names = df_counter['Counter Name'].tolist()
        if table_format.startswith("Separated"):
            display_table = build_split_ledger(
                display_df,
                selected_service=service_filter,
                all_counters=all_cnt_names
            )
        else:
            display_table = display_df

        # Download button uses the current view format
        csv_data = display_table.to_csv(index=False).encode('utf-8')
        f_col4.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="nadra_simulation_ledger.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Render ledger as a static HTML table (no column menus, no editing)
        ledger_html = render_html_table(display_table)
        st.markdown(
            f"<div style='max-height: 420px; overflow-y: auto; border: 1px solid #CBD5E1; border-radius: 8px;'>{ledger_html}</div>",
            unsafe_allow_html=True
        )

        # Column Totals & Classroom Averages
        tot_citizens = len(display_df)
        tot_serv = display_df['Service Time (min)'].sum()
        tot_wait = display_df['Wait Time (min)'].sum()
        tot_sys = display_df['Time in System (min)'].sum()

        avg_serv = round(tot_serv / tot_citizens, 2) if tot_citizens > 0 else 0.0
        avg_wait = round(tot_wait / tot_citizens, 2) if tot_citizens > 0 else 0.0
        avg_sys = round(tot_sys / tot_citizens, 2) if tot_citizens > 0 else 0.0

        # Calculate individual counter sums for Table 2.14 format
        counter_sums_html = ""
        if service_filter != "All Services":
            svc_counters = [c for c in all_cnt_names if c.startswith(service_filter)]
            if len(svc_counters) > 1:
                cnt_parts = []
                for c in svc_counters:
                    c_lbl = c.replace(f"{service_filter} ", "")
                    c_sum = display_df[display_df["Assigned Counter"] == c]["Service Time (min)"].sum()
                    cnt_parts.append(f"<div><span style='color:#64748B; font-weight:600;'>∑ [{c_lbl}] Service:</span> <strong style='color:#0F172A; font-size:15px;'>{c_sum:,} min</strong></div>")
                counter_sums_html = "".join(cnt_parts)

        st.markdown(f"""
        <div class="totals-box">
            <div style="font-size: 13px; font-weight: 700; color: #1E3A8A; text-transform: uppercase; margin-bottom: 10px;">
                Simulation Ledger Column Totals & Averages
            </div>
            <!-- Row 1: Column Totals -->
            <div style="display: flex; gap: 28px; flex-wrap: wrap; margin-bottom: 8px;">
                <div><span style="color:#64748B; font-weight:600;">Total Service Time (∑ Service):</span> <strong style="color:#0F172A; font-size:15px;">{tot_serv:,} min</strong></div>
                {counter_sums_html}
                <div><span style="color:#64748B; font-weight:600;">Total Waiting Time (∑ Wait):</span> <strong style="color:#0F172A; font-size:15px;">{tot_wait:,} min</strong></div>
                <div><span style="color:#64748B; font-weight:600;">Total Time in System (∑ System):</span> <strong style="color:#0F172A; font-size:15px;">{tot_sys:,} min</strong></div>
            </div>
            <!-- Divider -->
            <div style="border-top: 1px dashed #CBD5E1; margin: 8px 0 10px 0;"></div>
            <!-- Row 2: Classroom Averages -->
            <div style="display: flex; gap: 28px; flex-wrap: wrap;">
                <div><span style="color:#64748B; font-weight:600;">Avg Service Time:</span> <strong style="color:#0F172A; font-size:15px;">{avg_serv} min</strong></div>
                <div><span style="color:#64748B; font-weight:600;">Avg Waiting Time:</span> <strong style="color:#0F172A; font-size:15px;">{avg_wait} min</strong></div>
                <div><span style="color:#64748B; font-weight:600;">Avg Citizen Time in System:</span> <strong style="color:#0F172A; font-size:15px;">{avg_sys} min</strong></div>
                <div><span style="color:#64748B; font-weight:600;">Filtered Citizens:</span> <strong style="color:#0F172A; font-size:15px;">{tot_citizens:,}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: Service & Counter Summary
    with tab2:
        st.markdown("<h4 style='color:#0F172A; margin: 10px 0 4px 0;'>Service Type Demand & Performance</h4>", unsafe_allow_html=True)
        st.caption("Inspect which service category received the highest demand and which caused the longest queue delays.")
        st.markdown(render_html_table(df_service), unsafe_allow_html=True)

        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)

        st.markdown("<h4 style='color:#0F172A; margin: 10px 0 4px 0;'>Counter Performance & Utilization</h4>", unsafe_allow_html=True)
        st.caption("Citizens completed, busy time, and utilization percentage for each counter.")
        st.markdown(render_html_table(df_counter), unsafe_allow_html=True)

    # TAB 3: Random-Digit Tables
    with tab3:
        st.markdown("<h4 style='color:#0F172A; margin: 10px 0 4px 0;'>Theoretical Random-Digit Assignment Ranges (01–99, 00)</h4>", unsafe_allow_html=True)
        st.caption("Classroom random number intervals mapped to cumulative probabilities.")

        col_rn1, col_rn2 = st.columns(2)
        with col_rn1:
            st.markdown(render_html_table(rn_iat, "1. Inter-Arrival Time Mapping"), unsafe_allow_html=True)
        with col_rn2:
            st.markdown(render_html_table(rn_svc, "2. Service Category Demand Mapping"), unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#1E3A8A; font-weight:700; margin-bottom: 8px;'>3. Service Duration Mapping by Category</h4>", unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(render_html_table(rn_durations["New CNIC"], "New CNIC"), unsafe_allow_html=True)
            st.markdown(render_html_table(rn_durations["Modification"], "Modification"), unsafe_allow_html=True)
        with sc2:
            st.markdown(render_html_table(rn_durations["CNIC Renewal"], "CNIC Renewal"), unsafe_allow_html=True)
            st.markdown(render_html_table(rn_durations["Lost CNIC"], "Lost CNIC"), unsafe_allow_html=True)
        with sc3:
            st.markdown(render_html_table(rn_durations["B-Form / CRC"], "B-Form / CRC"), unsafe_allow_html=True)
