# config.py - Configurația Master GridSentinel

# 1. Stațiile fizice (Harta)
# src/config.py

STATIONS = {
    "BUC": {"id": 0, "type": "city", "demand": 1850},
    "CLJ": {"id": 1, "type": "city", "demand": 420},
    "SUC": {"id": 2, "type": "city", "demand": 180},
    "CST": {"id": 3, "type": "city", "demand": 380},
    "TMS": {"id": 4, "type": "city", "demand": 390},
    "PLO": {"id": 5, "type": "city", "demand": 320},
    "CRV": {"id": 6, "type": "city", "demand": 210},
    "BRL": {"id": 7, "type": "city", "demand": 190},
    "BIS": {"id": 8, "type": "city", "demand": 120},
    "ORD": {"id": 9, "type": "city", "demand": 200},
    "PIT": {"id": 10, "type": "city", "demand": 240},
    "BCU": {"id": 11, "type": "city", "demand": 230},
    "SLT": {"id": 12, "type": "city", "demand": 110},
    "DRO": {"id": 13, "type": "city", "demand": 160},
    "CAL": {"id": 14, "type": "city", "demand": 90},
    "GAL": {"id": 15, "type": "city", "demand": 220},
    "SBU": {"id": 16, "type": "city", "demand": 170},
    "TGM": {"id": 17, "type": "city", "demand": 200},
    "CRN": {"id": 18, "type": "nuclear", "demand": -1400},
    "PFR": {"id": 19, "type": "hydro", "demand": -800},
    "VID": {"id": 20, "type": "hydro", "demand": -300},
    "BCN": {"id": 21, "type": "hydro", "demand": -200},
    "BRZ": {"id": 22, "type": "thermo", "demand": -600},
    "ISN": {"id": 23, "type": "thermo", "demand": -500},
    "TRC": {"id": 24, "type": "thermo", "demand": -400},
    "ARD": {"id": 25, "type": "city", "demand": 210},
    "IAS": {"id": 26, "type": "city", "demand": 340},
    "BMR": {"id": 27, "type": "city", "demand": 140},
    "ALB": {"id": 28, "type": "city", "demand": 150},
    "TLC": {"id": 29, "type": "city", "demand": 120},
    "TGJ": {"id": 30, "type": "city", "demand": 170}
}
# 2. Scara de Severitate (Definită de tine în imagine)
SEVERITY_LEVELS = {
    0: "Normal - Funcționare în parametri.",
    1: "Atenție - Mici deviații detectate.",
    2: "Alertă - Anomalie descoperită. Inginer notificat.",
    3: "Risc Ridicat - Posibil atac cibernetic. Activare Cyber-Defense.",
    4: "Critic - Pericol iminent de avarie. Alarmă activată.",
    5: "Catastrofă - Stație OFF. Procedură de Urgență."
}

# 3. Tipurile de vreme
WEATHER_TYPES = ["Senin", "Furtuna", "Viscol", "Tornada", "Inundatie"]
# 4. Definirea coloanelor pentru consistență (Contractul de Date)
FEATURES = [
    "frecventa_hz", 
    "tensiune_kv", 
    "curent_a", 
    "flux_intrare_mw", 
    "flux_iesire_mw"
]
TARGET = "nivel_severitate"
# 5. Culori pentru Dashboard (Alex)
SEVERITY_COLORS = {
    0: "#28a745", # Verde (Succes)
    1: "#94d3a2", # Verde deschis
    2: "#ffc107", # Galben (Atenție)
    3: "#fd7e14", # Portocaliu (Risc)
    4: "#dc3545", # Roșu (Critic)
    5: "#000000"  # Negru (Catastrofă)
}
# 6. Limite Tehnice
LIMITS = {
    "frecventa_min": 49.0,
    "frecventa_max": 51.0,
    "tensiune_min": 350.0 # kV
}