import pandas as pd
import numpy as np
import random

# --- CONFIGURARE ---
def get_raw_sensors(sev, t):
    """Generează cifrele brute în funcție de severitate (0-5)"""
    freq = 50.0
    volt_kv = 400.0
    status = "ON"
    weather = "Senin"
    
    if sev == 1: freq += np.random.uniform(-0.02, 0.02)
    elif sev == 2: 
        freq += np.random.uniform(-0.08, 0.08)
        weather = "Furtuna"
    elif sev == 3: 
        freq += 0.15 * np.sin(t * 0.2) # Atac cibernetic
        volt_kv -= 10
        weather = "Viscol"
    elif sev == 4: 
        freq += np.random.uniform(-0.5, 0.5)
        volt_kv -= 50
        weather = "Tornada"
    elif sev == 5: 
        status = "OFF"; freq, volt_kv = 0, 0
        weather = "Inundatie"

    intrare = 500 + np.random.randint(-20, 20) if status == "ON" else 0
    iesire = 480 + np.random.randint(-30, 30) if status == "ON" else 0
    
    return {
        "status": status,
        "weather": weather,
        "frecventa_hz": round(freq, 4),
        "tensiune_kv": round(volt_kv, 2),
        "flux_intrare_mw": intrare,
        "flux_iesire_mw": iesire
    }

# --- 1. GENERARE DATE ANTRENAMENT (Pentru Tudor) ---
def generate_training_file(rows=5000):
    data = []
    for t in range(rows):
        sev = random.choices([0,1,2,3,4,5], weights=[60,15,10,7,5,3])[0]
        row = get_raw_sensors(sev, t)
        row["nivel_severitate"] = sev # Aici lăsăm eticheta pentru AI
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv("training_data.csv", index=False)
    print("✅ training_data.csv a fost creat pentru Tudor.")

# --- 2. FUNCȚIE PENTRU LIVE DEMO (Pentru main.py) ---
def get_live_data():
    """Simulează un senzor care trimite date acum"""
    # Alegem o severitate la întâmplare pentru demo
    real_sev = random.choices([0,1,2,3,4,5], weights=[70,10,5,10,3,2])[0]
    t_fake = random.randint(0, 1000)
    
    sensors = get_raw_sensors(real_sev, t_fake)
    # ATENȚIE: Returnăm senzorii ȘI severitatea separat, 
    # ca să putem verifica dacă AI-ul a ghicit corect.
    return sensors, real_sev

if __name__ == "__main__":
    generate_training_file()