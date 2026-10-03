"""
Configuration file for NADRA Service Center Discrete-Event Simulation.
Defines baseline probability distributions, service types, and default counter counts.
All probability tables sum to 1.00 and map to 2-digit random numbers 01-99, 00.
"""

# Default Simulation Schedule
DEFAULT_WORKING_HOURS = 8      # 8 hours = 480 minutes per day
DEFAULT_DAYS = 1               # Default 1 day for clean classroom verification

# Default Counter Allocation per Service Category
DEFAULT_COUNTERS = {
    "New CNIC": 1,
    "CNIC Renewal": 1,
    "B-Form / CRC": 1,
    "Modification": 1,
    "Lost CNIC": 1
}

# 1. Inter-Arrival Time Distribution (minutes between citizen arrivals)
INTER_ARRIVAL_DIST = [
    {"value": 1, "prob": 0.15},
    {"value": 2, "prob": 0.25},
    {"value": 3, "prob": 0.30},
    {"value": 4, "prob": 0.20},
    {"value": 5, "prob": 0.10}
]

# 2. Service-Type Demand Distribution (which service arriving citizen requires)
SERVICE_TYPE_DIST = [
    {"value": "New CNIC", "prob": 0.30},
    {"value": "CNIC Renewal", "prob": 0.25},
    {"value": "B-Form / CRC", "prob": 0.20},
    {"value": "Modification", "prob": 0.15},
    {"value": "Lost CNIC", "prob": 0.10}
]

# 3. Service Time Distributions per Service Category (in whole minutes)
SERVICE_TIME_DISTS = {
    "New CNIC": [
        {"value": 8, "prob": 0.15},
        {"value": 10, "prob": 0.35},
        {"value": 12, "prob": 0.30},
        {"value": 15, "prob": 0.20}
    ],
    "CNIC Renewal": [
        {"value": 4, "prob": 0.20},
        {"value": 6, "prob": 0.40},
        {"value": 8, "prob": 0.25},
        {"value": 10, "prob": 0.15}
    ],
    "B-Form / CRC": [
        {"value": 5, "prob": 0.25},
        {"value": 7, "prob": 0.40},
        {"value": 9, "prob": 0.25},
        {"value": 12, "prob": 0.10}
    ],
    "Modification": [
        {"value": 6, "prob": 0.20},
        {"value": 8, "prob": 0.35},
        {"value": 10, "prob": 0.30},
        {"value": 12, "prob": 0.15}
    ],
    "Lost CNIC": [
        {"value": 5, "prob": 0.30},
        {"value": 7, "prob": 0.40},
        {"value": 9, "prob": 0.20},
        {"value": 11, "prob": 0.10}
    ]
}
