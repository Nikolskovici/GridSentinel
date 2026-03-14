# config.py - Configurația Master GridSentinel

# 1. Stațiile fizice (Harta)
STATIONS = {
    "Constanta_Sud": {"priority": 1, "lat": 44.17, "lon": 28.63},
    "Bucuresti_Vest": {"priority": 2, "lat": 44.43, "lon": 26.10},
    "Cluj_Est": {"priority": 3, "lat": 46.77, "lon": 23.59},
    "Portile_de_Fier": {"priority": 1, "lat": 44.67, "lon": 22.62}
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