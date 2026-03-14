import pandas as pd
import numpy as np
import random
from config import STATIONS

# --- 1. LOGICA DE GENERARE SENZORI (Semnături Unice) ---
def get_raw_sensors(sev, t):
    """Generează cifre brute cu amprente digitale unice pentru fiecare nivel de severitate"""
    freq = 50.0
    volt_kv = 400.0
    status = "ON"
    weather = "Senin"

    if sev == 0:
        # NIVEL 0: Perfect stabil
        freq += random.uniform(-0.002, 0.002)
        volt_kv += random.uniform(-0.5, 0.5)

    elif sev == 1:
        # NIVEL 1: Mică instabilitate
        freq += random.uniform(-0.015, 0.015)
        volt_kv += random.uniform(-2.0, 2.0)
        weather = "Noros"

    elif sev == 2: 
        # NIVEL 2: Alertă Tehnică (Salt de frecvență + Cădere de tensiune)
        freq += random.uniform(0.05, 0.12) * random.choice([-1, 1]) 
        volt_kv -= random.uniform(10.0, 20.0) 
        weather = "Furtuna"

    elif sev == 3: 
        # NIVEL 3: Atac Cibernetic (Pattern sinusoidal - imposibil de ratat de AI)
        freq += 0.25 * np.sin(t * 0.3) 
        volt_kv += 7.0 * np.cos(t * 0.3)
        weather = "Senin" # Atacurile cibernetice apar des pe vreme bună

    elif sev == 4: 
        # NIVEL 4: Critic (Instabilitate extremă, aproape de colaps)
        freq += np.random.uniform(-0.8, 0.8)
        volt_kv -= random.uniform(70.0, 120.0) 
        weather = "Tornada"

    elif sev == 5: 
        # NIVEL 5: Catastrofă (Blackout / Stație oprită)
        status = "OFF"
        freq, volt_kv = 0.0, 0.0
        weather = "Inundatie"

    # Calcul fluxuri (MW) corelate cu starea sistemului
    base_flow = 500 if status == "ON" else 0
    intrare = base_flow + np.random.randint(-15, 15) if status == "ON" else 0
    # Eficiența scade dramatic dacă tensiunea e mică (Nivel 4)
    efficiency = 0.96 if volt_kv > 380 else 0.75 if volt_kv > 0 else 0
    iesire = (intrare * efficiency) + np.random.randint(-5, 5) if status == "ON" else 0
    
    return {
        "status": status,
        "weather": weather,
        "frecventa_hz": round(freq, 4),
        "tensiune_kv": round(volt_kv, 2),
        "flux_intrare_mw": round(intrare, 2),
        "flux_iesire_mw": round(iesire, 2)
    }

# --- 2. GENERARE DATE ANTRENAMENT (100.000 Rânduri) ---
def generate_training_file(rows=100000):
    """Creează setul de date echilibrat pentru antrenarea AI-ului"""
    data = []
    # Ponderi echilibrate pentru ca AI-ul să învețe toate clasele la fel de bine
    # 0:Normal, 1:Atenție, 2:Alertă, 3:Cyber, 4:Critic, 5:Catastrofă
    weights = [20, 15, 20, 15, 15, 15] 
    
    print(f"🏗️ Generăm {rows} rânduri pentru antrenament...")
    
    for t in range(rows):
        sev = random.choices([0, 1, 2, 3, 4, 5], weights=weights)[0]
        row = get_raw_sensors(sev, t)
        row["nivel_severitate"] = sev
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv("data/training_data.csv", index=False)
    
    print("\n✅ training_data.csv generat!")
    print("📊 Distribuția claselor:")
    print(df["nivel_severitate"].value_counts().sort_index())

# --- 3. GENERARE STREAM LIVE (Pentru Alex & Demo) ---
def generate_telemetry_stream(duration_seconds=300):
    """Generează date multi-stație pentru simularea în timp real"""
    all_rows = []
    # Alegem o singură stație victimă pentru a demonstra detecția selectivă
    target_station = random.choice(list(STATIONS.keys()))
    
    print(f"🌐 Generăm stream live pentru {len(STATIONS)} stații...")
    print(f"🎯 Stația vizată de anomalie: {target_station}")

    for t in range(duration_seconds):
        for s_id in STATIONS.keys():
            sev = 0
            # Aplicăm anomalie progresivă doar stației țintă
            if s_id == target_station and t > 30:
                if t < 60: sev = 2
                elif t < 100: sev = 3
                else: sev = 4
            
            row = get_raw_sensors(sev, t)
            row["timestamp"] = t
            row["station_id"] = s_id
            row["nivel_severitate"] = sev
            all_rows.append(row)
            
    df = pd.DataFrame(all_rows)
    df.to_csv("data/telemetry_stream.csv", index=False)
    print("✅ telemetry_stream.csv actualizat pentru demo!")

# --- 4. FUNCȚIE HELPER PENTRU MAIN.PY ---
def get_live_data():
    """Simulează citirea instantanee a unui senzor"""
    real_sev = random.choices([0, 1, 2, 3, 4, 5], weights=[70, 10, 5, 8, 4, 3])[0]
    t_fake = random.randint(0, 1000)
    sensors = get_raw_sensors(real_sev, t_fake)
    return sensors, real_sev

if __name__ == "__main__":
    # Rulăm ambele generări la pornirea scriptului
    generate_training_file(rows=100000)
    generate_telemetry_stream(duration_seconds=200)