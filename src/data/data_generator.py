import pandas as pd
import numpy as np
import random

# Încercăm să importăm stațiile indiferent de cum e rulat scriptul
try:
    from src.Interfata.config import STATIONS
except ImportError:
    from Interfata.config import STATIONS

# --- 0. DICȚIONARE DE TRADUCERE (Pentru Tudor/AI) ---
weather_map = {"Senin": 0, "Noros": 1, "Furtuna": 2, "Tornada": 3, "Inundatie": 4}
status_map = {"ON": 1, "OFF": 0}

# --- 1. LOGICA DE GENERARE SENZORI (Semnături Unice & Extreme) ---
def get_raw_sensors(sev, t):
    """Generează date realiste, incluzând Blackout și Fatal Surges"""
    status, weather = "ON", "Senin"
    
    # --- Cazuri de Severitate ---
    if sev == 0:
        # NORMAL: Frecvență perfectă, tensiune nominală
        freq, volt = random.uniform(49.99, 50.01), random.uniform(399.0, 401.0)
    
    elif sev == 1:
        # ATENȚIE: Mică instabilitate
        freq, volt = random.uniform(49.94, 49.97), random.uniform(394.0, 397.0)
        weather = "Noros"
        
    elif sev == 2:
        # ALERTĂ TEHNICĂ: Cădere de tensiune (Under-voltage)
        freq, volt = random.uniform(49.80, 49.90), random.uniform(370.0, 385.0)
        weather = "Furtuna"
        
    elif sev == 3:
        # CYBER ATTACK: Pattern sinusoidal (Semnătură matematică non-fizică)
        freq = 50.0 + 0.15 * np.sin(t * 0.4)
        volt = 400.0 + 5.0 * np.cos(t * 0.4)
        weather = "Senin"
        
    elif sev == 4:
        # CRITIC: Instabilitate severă pre-colaps
        freq, volt = random.uniform(48.5, 49.3), random.uniform(300.0, 340.0)
        weather = "Tornada"
        
    elif sev == 5: 
        # CATASTROFĂ: Tratăm Blackout vs. Fatal Surge (Over-voltage)
        if random.random() < 0.7:
            # Scenariul A: BLACKOUT (Sistem oprit)
            status, freq, volt = "OFF", 0.0, 0.0
            weather = "Inundatie"
        else:
            # Scenariul B: FATAL SURGE (Supra-sarcină masivă / Trăsnet / Atac pe transformator)
            status = "ON" 
            freq = random.uniform(52.5, 55.0) # Frecvență care distruge turbinele
            volt = random.uniform(485.0, 560.0) # Tensiune care topește izolatorii
            weather = "Tornada"

    # --- CALCUL FLUXURI (MW) ---
    base_flow = 500 if status == "ON" else 0
    # Eficiența scade dramatic în afara limitelor de siguranță (380V - 420V)
    if 380 <= volt <= 420:
        efficiency = 0.96
    elif status == "OFF":
        efficiency = 0.0
    else:
        efficiency = 0.40 # Pierderi masive prin căldură sau declanșări de protecție

    intrare = base_flow + np.random.randint(-15, 15) if status == "ON" else 0
    iesire = (intrare * efficiency) + np.random.randint(-5, 5) if status == "ON" else 0

    return {
        "status": status_map[status],
        "weather": weather_map[weather],
        "frecventa_hz": round(freq, 4),
        "tensiune_kv": round(volt, 2),
        "flux_intrare_mw": round(intrare, 2),
        "flux_iesire_mw": round(iesire, 2)
    }

# --- 2. GENERARE DATE ANTRENAMENT (Evolutiv & Station-Agnostic) ---
def generate_training_file(total_rows=100000):
    print(f"🏗️ Generăm {total_rows} rânduri evolutive (FĂRĂ STATION_ID pentru Generalizare)...")
    data = []
    rows_per_station = total_rows // len(STATIONS)
    
    for s_id in STATIONS.keys():
        current_sev = 0
        for t in range(rows_per_station):
            # Logica de evoluție temporală
            rand = random.random()
            if rand < 0.02 and current_sev < 5: current_sev += 1
            elif rand < 0.04 and current_sev > 0: current_sev -= 1
            
            # Injectăm erori de senzor (0.5% șansă)
            if random.random() < 0.005:
                row = get_raw_sensors(5, t) # Arată ca o catastrofă
                actual_label = current_sev  # Dar etichetăm cu starea reală (AI-ul învață să ignore spike-ul)
            else:
                row = get_raw_sensors(current_sev, t)
                actual_label = current_sev

            # NU includem station_id aici pentru a ajuta AI-ul să învețe fizica rețelei
            row["timestamp"] = t
            row["nivel_severitate"] = actual_label
            data.append(row)

    df = pd.DataFrame(data)
    df.to_csv("data/training_data.csv", index=False)
    print("✅ training_data.csv generat (100% Numeric & Evolutiv)!")

# --- 3. GENERARE STREAM LIVE (Pentru Demo-ul lui Alex) ---
def generate_telemetry_stream(duration=300):
    print(f"🌐 Generăm stream live evolutiv pentru {duration} secunde...")
    all_rows = []
    target = random.choice(list(STATIONS.keys()))
    
    for t in range(duration):
        for s_id in STATIONS.keys():
            sev = 0
            if s_id == target:
                if 20 < t <= 50: sev = 1
                elif 50 < t <= 100: sev = 3 # Atac Cyber
                elif 100 < t <= 150: sev = 4
                elif t > 150: sev = 5 # Fatal Surge / Blackout
            
            row = get_raw_sensors(sev, t)
            row["timestamp"] = t
            row["station_id"] = s_id # Aici lăsăm ID-ul pentru hartă
            row["nivel_severitate"] = sev
            all_rows.append(row)
            
    pd.DataFrame(all_rows).to_csv("data/telemetry_stream.csv", index=False)
    print("✅ telemetry_stream.csv actualizat!")

def get_live_data():
    """Simulează citirea live a datelor (pentru demo)"""
    # Într-un scenariu real, aici am citi de la senzori sau API-uri
    # Pentru demo, vom citi rând cu rând din telemetry_stream.csv
    df = pd.read_csv("data/telemetry_stream.csv")
    for _, row in df.iterrows():
        senzori = {
            "status": row["status"],
            "weather": row["weather"],
            "frecventa_hz": row["frecventa_hz"],
            "tensiune_kv": row["tensiune_kv"],
            "flux_intrare_mw": row["flux_intrare_mw"],
            "flux_iesire_mw": row["flux_iesire_mw"]
        }
        severitate_reala = row["nivel_severitate"]
        yield senzori, severitate_reala

if __name__ == "__main__":
    generate_training_file()
    generate_telemetry_stream()