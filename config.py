"""Configuration data for the EV Charging Station Planner.
Covers major Punjab cities connected via GT Road (N-5), Motorways (M2, M4)
and other primary highways. Distances are real road-distance approximations."""

CITY_EDGES = [
    ('RAWALPINDI', 'ISLAMABAD', 13),
    ('ISLAMABAD', 'HARIPUR', 33),
    ('RAWALPINDI', 'JHELUM', 111),
    ('JHELUM', 'GUJRAT', 62),
    ('JHELUM', 'SARGODHA', 95),
    ('GUJRAT', 'GUJRANWALA', 49),
    ('GUJRAT', 'SARGODHA', 110),
    ('GUJRANWALA', 'SIALKOT', 50),
    ('GUJRANWALA', 'SHEIKHUPURA', 50),
    ('SHEIKHUPURA', 'LAHORE', 35),
    ('SHEIKHUPURA', 'FAISALABAD', 95),
    ('FAISALABAD', 'SARGODHA', 93),
    ('FAISALABAD', 'JHANG', 80),
    ('JHANG', 'SHORKOT', 50),
    ('FAISALABAD', 'TOBATEKSINGH', 50),
    ('TOBATEKSINGH', 'MULTAN', 130),
    ('LAHORE', 'OKARA', 129),
    ('OKARA', 'SAHIWAL', 40),
    ('SAHIWAL', 'KHANEWAL', 50),
    ('KHANEWAL', 'MULTAN', 50),
    ('SAHIWAL', 'MULTAN', 110),
    ('MULTAN', 'BAHAWALPUR', 95),
]

CHARGING_STATIONS = [
    'JHELUM', 'GUJRAT', 'GUJRANWALA', 'SHEIKHUPURA', 'LAHORE', 'FAISALABAD',
    'SARGODHA', 'OKARA', 'SAHIWAL', 'TOBATEKSINGH', 'MULTAN'
]

BATTERY_CAPACITY_KM = 150
KWH_PER_KM = 0.2
CHARGING_COST_PER_KWH = 30  # PKR
LOW_BATTERY_THRESHOLD_PCT = 20