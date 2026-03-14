import pandas as pd
import numpy as np
import random

def generate_telemetry_stream(duration_seconds=1000):
    all_data = []
    
    for t in range(duration_seconds):
        sev = random.choices([0, 1, 2, 3, 4, 5], weights=[60, 15, 10, 7, 5, 3])[0]
        
        # Parametri de bază
        freq = 50.0
        volt_kv = 400.0 # Tensiunea direct in Kilovolti
        status = "ON"
        weather = "Senin"
        
        # Logica de severitate
        if sev == 1:
            freq += np.random.uniform(-0.02, 0.02)
        elif sev == 2:
            freq += np.random.uniform(-0.08, 0.08)
            weather = "Furtuna"
        elif sev == 3:
            freq += 0.15 * np.sin(t * 0.2) # Micro-fluctuații (Atac)
            volt_kv -= 10
            weather = "Viscol"
        elif sev == 4:
            freq += np.random.uniform(-0.5, 0.5)
            volt_kv -= 50
            weather = "Tornada"
        elif sev == 5:
            status = "OFF"
            freq, volt_kv = 0, 0
            weather = "Inundatie"

        # Fluxuri de Energie
        # Flux intrare = cat primeste statia din retea/centrale
        # Flux iesire = cat pleaca spre oras
        flux_intrare = 500 + np.random.randint(-20, 20) if status == "ON" else 0
        flux_iesire = 480 + np.random.randint(-30, 30) if status == "ON" else 0
        
        # Curent (A) = (MW * 10^6) / (kV * 10^3 * sqrt(3)) -> simplificat pt demo:
        ampere = (flux_intrare * 1000) / (volt_kv if volt_kv > 0 else 1)

        all_data.append({
            "timestamp": t,
            "status": status,
            "weather": weather,
            "frecventa_hz": round(freq, 4),
            "tensiune_kv": round(volt_kv, 2),
            "curent_a": round(ampere, 2),
            "flux_intrare_mw": flux_intrare,
            "flux_iesire_mw": flux_iesire,
            "nivel_severitate": sev
        })

    df = pd.DataFrame(all_data)
    df.to_csv("telemetry_stream.csv", index=False)
    print("Succes! Stream-ul a fost actualizat: telemetry_stream.csv")

if __name__ == "__main__":
    generate_telemetry_stream()