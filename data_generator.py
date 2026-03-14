import pandas as pd
import numpy as np
import time

def generate_grid_data(duration_seconds=1000):
    print(f"Generăm {duration_seconds} secunde de date de telemetrie...")
    
    data = []
    for t in range(duration_seconds):
        # 1. Simulam frecventa de baza (50 Hz)
        frequency = 50.0 + np.random.uniform(-0.01, 0.01)
        
        # 2. Injectam ATACUL (intre secundele 800 si 1000)
        is_attack = 0
        if t > 800:
            is_attack = 1
            # Micro-fluctuatie ritmica (sine wave) pe care o vede AI-ul
            frequency += 0.05 * np.sin(t * 0.5) 
            
        data.append({
            "timestamp": t,
            "frequency_hz": round(frequency, 4),
            "voltage_kv": round(400 + np.random.uniform(-0.5, 0.5), 2),
            "is_attack_label": is_attack  # Aceasta e "cheia" pentru Tudor (AI)
        })
        
    df = pd.DataFrame(data)
    df.to_csv("telemetry_live.csv", index=False)
    print("Succes! Fișierul 'telemetry_live.csv' a fost generat.")

if __name__ == "__main__":
    generate_grid_data()