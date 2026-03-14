import pandas as pd
import numpy as np
import random
try:
    from config import STATIONS
except ImportError:
    from src.config import STATIONS

# --- 0. DICȚIONARE DE TRADUCERE ---
weather_map = {"Senin": 0, "Noros": 1, "Furtuna": 2, "Tornada": 3, "Inundatie": 4}
status_map = {"ON": 1, "OFF": 0}

# --- 1. LOGICA DE GENERARE SENZORI (Semnături Clare) ---
def get_raw_sensors(sev, t):
    status, weather = "ON", "Senin"
    
    if sev == 0:
        freq, volt = random.uniform(49.99, 50.01), random.uniform(399.0, 401.0)
        weather = "Senin"
    elif sev == 1:
        freq, volt = random.uniform(49.94, 49.97), random.uniform(394.0, 397.0)
        weather = "Noros"
    elif sev == 2:
        freq, volt = random.uniform(49.80, 49.90), random.uniform(375.0, 385.0)
        weather = "Furtuna"
    elif sev == 3:
        freq = 50.0 + 0.15 * np.sin(t * 0.4)
        volt = 400.0 + 5.0 * np.cos(t * 0.4)
        weather = "Senin"
    elif sev == 4:
        freq, volt = random.uniform(48.5, 49.3), random.uniform(300.0, 340.0)
        weather = "Tornada"
    else: # sev == 5
        status, freq, volt = "OFF", 0.0, 0.0
        weather = "Inundatie"

    # Calcul fluxuri
    base_flow = 500 if status == "ON" else 0
    intrare = base_flow + np.random.randint(-15, 15) if status == "ON" else 0
    efficiency = 0.96 if volt > 380 else 0.75 if volt > 0 else 0
    iesire = (intrare * efficiency) + np.random.randint(-5, 5) if status == "ON" else 0

    return {
        "status": status_map[status],
        "weather": weather_map[weather],
        "frecventa_hz": round(freq, 4),
        "tensiune_kv": round(volt, 2),
        "flux_intrare_mw": round(intrare, 2),
        "flux_iesire_mw": round(iesire, 2)
    }

# --- 2. GENERARE DATE ANTRENAMENT (Evolutiv & Secvențial) ---
def generate_training_file(total_rows=100000):
    print(f"🏗️ Generăm {total_rows} rânduri evolutive pentru antrenament...")
    data = []
    
    # Generăm datele în "blocuri" de timp pentru fiecare stație
    rows_per_station = total_rows // len(STATIONS)
    
    for s_id in STATIONS.keys():
        current_sev = 0
        for t in range(rows_per_station):
            # Logica de evoluție: Severitatea nu sare haotic
            # Există o șansă mică să crească sau să scadă nivelul
            rand = random.random()
            if rand < 0.02: # 2% șansă să se schimbe starea
                if current_sev < 5: current_sev += 1
            elif rand < 0.04: # 2% șansă să se repare
                if current_sev > 0: current_sev -= 1
            
            # --- ADAUGĂM ERORI DE SENZOR (Zgomot) ---
            # Din când în când, forțăm o valoare de "5", dar etichetăm cu severitatea reală
            if random.random() < 0.005: # 0.5% șansă de senzor defect
                row = get_raw_sensors(5, t) # Valori de blackout
                actual_label = current_sev  # Dar AI-ul trebuie să învețe că e tot starea curentă
            else:
                row = get_raw_sensors(current_sev, t)
                actual_label = current_sev

            row["station_id"] = s_id
            row["timestamp"] = t
            row["nivel_severitate"] = actual_label
            data.append(row)

    df = pd.DataFrame(data)
    # Important: Nu amestecăm rândurile (Shuffle), Tudor are nevoie de ele în ordine!
    df.to_csv("data/training_data.csv", index=False)
    print("✅ training_data.csv generat cu succes!")

# --- 3. GENERARE STREAM LIVE (Evoluție Rapidă pentru Demo) ---
def generate_telemetry_stream(duration=300):
    print("🌐 Generăm stream live evolutiv...")
    all_rows = []
    target = random.choice(list(STATIONS.keys()))
    
    for t in range(duration):
        for s_id in STATIONS.keys():
            sev = 0
            if s_id == target:
                if 20 < t <= 50: sev = 1
                elif 50 < t <= 100: sev = 3 # Atac Cyber
                elif t > 100: sev = 5 # Blackout
            
            row = get_raw_sensors(sev, t)
            row["timestamp"] = t
            row["station_id"] = s_id
            row["nivel_severitate"] = sev
            all_rows.append(row)
            
    pd.DataFrame(all_rows).to_csv("data/telemetry_stream.csv", index=False)
    print("✅ telemetry_stream.csv gata!")

if __name__ == "__main__":
    generate_training_file()
    generate_telemetry_stream()