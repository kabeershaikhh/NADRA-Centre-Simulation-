"""
Core Discrete-Event Simulation Engine for NADRA Service Center.
Strictly follows textbook simulation modeling principles (Jerry Banks style).
Generates classic classroom simulation tables with 2-digit random numbers (01-00).
"""

import random
import pandas as pd
from config import (
    DEFAULT_WORKING_HOURS,
    DEFAULT_DAYS,
    DEFAULT_COUNTERS,
    INTER_ARRIVAL_DIST,
    SERVICE_TYPE_DIST,
    SERVICE_TIME_DISTS
)


def build_rn_table(dist_list):
    """
    Builds a textbook random-digit assignment table from a discrete probability distribution.
    Maps cumulative probabilities to two-digit classroom intervals (01-99, 00).
    """
    table = []
    cum_prob = 0.0
    prev_high = 0

    for item in dist_list:
        val = item["value"]
        prob = round(item["prob"], 4)
        cum_prob = round(cum_prob + prob, 4)

        low = prev_high + 1
        high = int(round(cum_prob * 100))

        # Format 2-digit representation (100 is written as '00')
        low_str = f"{low:02d}"
        high_str = "00" if high == 100 else f"{high:02d}"
        rn_range_str = f"{low_str} – {high_str}"

        table.append({
            "Value": val,
            "Probability": prob,
            "Cumulative Probability": min(cum_prob, 1.0),
            "Random-Digit Assignment": rn_range_str,
            "_low": low,
            "_high": high
        })
        prev_high = high

    return pd.DataFrame(table)


def sample_from_rn_table(df_rn_table, rng=None):
    """
    Generates a 2-digit random number (1-100) and maps it to the corresponding distribution value.
    Returns: (rn_int, rn_str, sampled_value)
    """
    rn = rng.randint(1, 100) if rng else random.randint(1, 100)
    rn_str = "00" if rn == 100 else f"{rn:02d}"

    for _, row in df_rn_table.iterrows():
        if row["_low"] <= rn <= row["_high"]:
            return rn, rn_str, row["Value"]

    # Fallback to last row if rounding edge case occurs
    last_row = df_rn_table.iloc[-1]
    return rn, rn_str, last_row["Value"]


def run_simulation(working_hours=DEFAULT_WORKING_HOURS, 
                   days=DEFAULT_DAYS, 
                   counter_counts=None, 
                   seed=None):
    """
    Runs discrete-event simulation for the specified days and operating hours.
    Returns:
      1. df_ledger: The detailed citizen-by-citizen simulation ledger (Table 2.21 style)
      2. system_summary: Overall metrics dictionary (Averages & Totals)
      3. df_service_summary: Breakdown table by Service Type (Demand & Times)
      4. df_counter_summary: Utilization & busy time table for each counter
      5. rn_tables_dict: The underlying theoretical RN assignment tables (Table 2.19 style)
    """
    if counter_counts is None:
        counter_counts = DEFAULT_COUNTERS.copy()

    # Initialize random number generator with seed if provided
    rng = random.Random(seed) if seed is not None else random.Random()

    # 1. Build theoretical RN assignment tables
    rn_tables = {
        "Inter-Arrival": build_rn_table(INTER_ARRIVAL_DIST),
        "Service-Type": build_rn_table(SERVICE_TYPE_DIST),
        "Services": {svc: build_rn_table(dist) for svc, dist in SERVICE_TIME_DISTS.items()}
    }

    # 2. Setup counters
    counters = []
    c_num = 1
    for svc, count in counter_counts.items():
        for i in range(count):
            counters.append({
                "counter_num": c_num,
                "counter_name": f"{svc} Counter {i+1}",
                "service": svc,
                "next_available": 0,
                "total_busy_time": 0,
                "citizens_served": 0
            })
            c_num += 1

    ledger_rows = []
    global_citizen_id = 0
    total_overtime_minutes = 0
    total_operating_minutes = days * working_hours * 60

    # 3. Simulate Day by Day
    for day in range(1, days + 1):
        day_limit = working_hours * 60  # minutes in a day
        current_clock = 0

        # Reset counter daily schedules for the new day
        for c in counters:
            c["next_available"] = 0

        day_citizen_count = 0
        while True:
            day_citizen_count += 1
            if day_citizen_count == 1:
                # First customer arrives at minute 0 with no inter-arrival time and no RN
                rn_arr_str = "-"
                iat = "-"
                arrival_time = 0
            else:
                # Subsequent customers have random inter-arrival time
                rn_arr, rn_arr_str, iat = sample_from_rn_table(rn_tables["Inter-Arrival"], rng)
                arrival_time = current_clock + iat

            # Arrivals stop at closing time
            if arrival_time > day_limit:
                break

            current_clock = arrival_time
            global_citizen_id += 1

            # Generate Service Type
            rn_svc, rn_svc_str, svc_type = sample_from_rn_table(rn_tables["Service-Type"], rng)

            # Generate Service Time for the selected service category
            rn_dur, rn_dur_str, serv_time = sample_from_rn_table(rn_tables["Services"][svc_type], rng)

            # Find compatible counters for this service
            valid_counters = [c for c in counters if c["service"] == svc_type]

            # Counter assignment: Earliest available counter (Tie-break: Lowest counter number)
            best_counter = min(
                valid_counters,
                key=lambda c: (max(c["next_available"], arrival_time), c["counter_num"])
            )

            service_start = max(best_counter["next_available"], arrival_time)
            waiting_time = service_start - arrival_time
            service_end = service_start + serv_time
            time_in_system = waiting_time + serv_time

            # Update assigned counter state
            best_counter["next_available"] = service_end
            best_counter["total_busy_time"] += serv_time
            best_counter["citizens_served"] += 1

            ledger_rows.append({
                "Citizen #": global_citizen_id,
                "Day": day,
                "RN Arrival": rn_arr_str,
                "Inter-Arrival (min)": iat,
                "Arrival Time": arrival_time,
                "RN Service Type": rn_svc_str,
                "Service Type": svc_type,
                "RN Duration": rn_dur_str,
                "Service Time (min)": serv_time,
                "Assigned Counter": best_counter["counter_name"],
                "Service Begins": service_start,
                "Wait Time (min)": waiting_time,
                "Service Ends": service_end,
                "Time in System (min)": time_in_system
            })

        # Calculate overtime for the day (any counter running past day_limit)
        day_max_finish = max([c["next_available"] for c in counters], default=day_limit)
        if day_max_finish > day_limit:
            total_overtime_minutes += (day_max_finish - day_limit)

    df_ledger = pd.DataFrame(ledger_rows)

    # 4. Compute Performance Summaries
    if not df_ledger.empty:
        total_citizens = len(df_ledger)
        total_waiting_time = int(df_ledger["Wait Time (min)"].sum())
        total_service_time = int(df_ledger["Service Time (min)"].sum())
        total_system_time = int(df_ledger["Time in System (min)"].sum())
        citizens_who_waited = int((df_ledger["Wait Time (min)"] > 0).sum())

        avg_wait = round(total_waiting_time / total_citizens, 2)
        avg_service = round(total_service_time / total_citizens, 2)
        avg_system = round(total_system_time / total_citizens, 2)
        prob_wait = round((citizens_who_waited / total_citizens) * 100, 2)
        numeric_iat = pd.to_numeric(df_ledger["Inter-Arrival (min)"], errors='coerce')
        avg_inter_arrival = round(numeric_iat.mean(), 2) if not numeric_iat.dropna().empty else 0.0
    else:
        total_citizens = total_waiting_time = total_service_time = total_system_time = citizens_who_waited = 0
        avg_wait = avg_service = avg_system = prob_wait = avg_inter_arrival = 0.0

    system_summary = {
        "Total Citizens Served": total_citizens,
        "Total Operating Time (min)": total_operating_minutes,
        "Average Inter-Arrival Time (min)": avg_inter_arrival,
        "Total Service Time (min)": total_service_time,
        "Average Service Time (min)": avg_service,
        "Total Waiting Time (min)": total_waiting_time,
        "Average Waiting Time (min)": avg_wait,
        "Average Time in System (min)": avg_system,
        "Probability of Waiting (%)": prob_wait,
        "Total Overtime (min)": total_overtime_minutes
    }

    # 5. Service Type Summary Table
    svc_summary_list = []
    for svc in counter_counts.keys():
        svc_df = df_ledger[df_ledger["Service Type"] == svc] if not df_ledger.empty else pd.DataFrame()
        count = len(svc_df)
        pct_demand = round((count / total_citizens * 100), 2) if total_citizens > 0 else 0.0
        tot_serv = int(svc_df["Service Time (min)"].sum()) if count > 0 else 0
        avg_serv = round(svc_df["Service Time (min)"].mean(), 2) if count > 0 else 0.0
        tot_wait = int(svc_df["Wait Time (min)"].sum()) if count > 0 else 0
        avg_wait_svc = round(svc_df["Wait Time (min)"].mean(), 2) if count > 0 else 0.0

        svc_summary_list.append({
            "Service Type": svc,
            "Citizens Arrived (Demand)": count,
            "% Share of Demand": f"{pct_demand}%",
            "Counters Assigned": counter_counts[svc],
            "Total Service Time (min)": tot_serv,
            "Avg Service Time (min)": avg_serv,
            "Total Waiting Time (min)": tot_wait,
            "Avg Waiting Time (min)": avg_wait_svc
        })

    df_service_summary = pd.DataFrame(svc_summary_list)

    # 6. Counter Performance Table
    counter_summary_list = []
    for c in counters:
        busy = c["total_busy_time"]
        util = round((busy / total_operating_minutes) * 100, 2) if total_operating_minutes > 0 else 0.0
        avg_c_serv = round(busy / c["citizens_served"], 2) if c["citizens_served"] > 0 else 0.0

        counter_summary_list.append({
            "Counter Name": c["counter_name"],
            "Service Category": c["service"],
            "Citizens Served": c["citizens_served"],
            "Total Busy Time (min)": busy,
            "Avg Service Time (min)": avg_c_serv,
            "Utilization (%)": f"{util}%"
        })

    df_counter_summary = pd.DataFrame(counter_summary_list)

    return df_ledger, system_summary, df_service_summary, df_counter_summary, rn_tables


def build_split_ledger(df_input, selected_service="All Services", all_counters=None):
    """
    Transforms the simulation ledger into the textbook Table 2.14 multi-server split format (Jerry Banks style).
    Each server/counter gets dedicated 'Service Begins', 'Service Time', and 'Service Ends' columns.
    When a citizen is served by Counter A, Counter B's columns are displayed as '-'.
    """
    if df_input.empty or not all_counters:
        return df_input.copy()

    # Determine which counters to display
    if selected_service != "All Services":
        active_counters = [c for c in all_counters if c.startswith(selected_service)]
        counter_labels = {c: c.replace(f"{selected_service} ", "") for c in active_counters}
    else:
        active_counters = all_counters
        counter_labels = {
            c: c.replace(" Counter ", " C").replace(" / ", "/").replace("New CNIC", "CNIC")
            for c in active_counters
        }

    split_rows = []
    for _, row in df_input.iterrows():
        r = {
            "Citizen #": row["Citizen #"],
            "Day": row["Day"],
            "RN Arrival": row["RN Arrival"],
            "Inter-Arrival (min)": row["Inter-Arrival (min)"],
            "Arrival Time": row["Arrival Time"],
        }
        if selected_service == "All Services":
            r["Service Type"] = row["Service Type"]

        r["RN Duration"] = row["RN Duration"]

        # Dedicated columns per counter (Table 2.14 Able & Baker style)
        for c in active_counters:
            lbl = counter_labels[c]
            if row["Assigned Counter"] == c:
                r[f"[{lbl}] Begins"] = row["Service Begins"]
                r[f"[{lbl}] Time"] = row["Service Time (min)"]
                r[f"[{lbl}] Ends"] = row["Service Ends"]
            else:
                r[f"[{lbl}] Begins"] = "-"
                r[f"[{lbl}] Time"] = "-"
                r[f"[{lbl}] Ends"] = "-"

        r["Wait Time (min)"] = row["Wait Time (min)"]
        r["Time in System (min)"] = row["Time in System (min)"]
        split_rows.append(r)

    return pd.DataFrame(split_rows)

