import time
import data_generator
from config import STATIONS, SEVERITY_LEVELS

# Aici vor aparea importurile colegilor cand sunt gata:
# import model_ai  <-- Tudor (AI)
# import iustin_logic <-- Iustin (Decizii/Actiuni)

def run_grid_sentinel():
    print("="*50)
    print("SISTEMUL GRID SENTINEL - TRANSELECTRICA DSS")
    print("STATUS: ACTIV - MONITORIZARE LIVE")
    print("="*50)

    try:
        while True:
            # 1. COLECTARE DATE (Munca ta, Niki)
            # Luam datele live "brute" si severitatea reala (pentru verificare)
            senzori, severitate_reala = data_generator.get_live_data()
            
            print(f"\n[SENZORI] Frecv: {senzori['frecventa_hz']}Hz | Tensiune: {senzori['tensiune_kv']}kV | Flux: {senzori['flux_intrare_mw']}MW")

            # 2. ANALIZA AI (Munca lui Tudor)
            # Tudor va face o functie care primeste 'senzori' si returneaza un numar 0-5
            # momentan simulam ca AI-ul returneaza ceva:
            nivel_detectat_ai = 3 # Aici va fi model_ai.predict(senzori)
            
            status_text = SEVERITY_LEVELS[nivel_detectat_ai]
            print(f"[AI ALERT] Nivel Detectat: {nivel_detectat_ai} ({status_text})")

            # 3. DECIZIE SI ACTIUNE (Munca lui Iustin)
            # Iustin va face o functie care spune ce sa facem pe baza nivelului
            # recomandare = iustin_logic.get_recommendation(nivel_detectat_ai)
            print(f"[ACTION] Recomandare: Verificare protocol Securitate Cibernetica.")

            # 4. VERIFICARE (Barem de corectare)
            if nivel_detectat_ai == severitate_reala:
                print("✅ VALIDARE: AI a identificat corect starea retelei.")
            else:
                print(f"⚠️ CALIBRARE: AI a estimat {nivel_detectat_ai}, dar realitatea este {severitate_reala}")

            print("-" * 30)
            
            # Asteptam 2 secunde pana la urmatoarea citire (pentru demo)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSistem oprit de utilizator.")

if __name__ == "__main__":
    run_grid_sentinel()