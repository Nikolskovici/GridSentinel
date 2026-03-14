import time
import random
import numpy as np
from AI_INTEGRATION import CyberDefenseAI, GridOptimizer

# Inițializăm creierele AI
creier_cyber = CyberDefenseAI()
creier_grid = GridOptimizer()

# Definim contextul MACRO (Capacitatea totală a țării în MW)
CAPACITATE_TOTALA_NATIONALA = 7500 

def generare_context_dynamic():
    tipuri = ['spital', 'industrial', 'comercial', 'rezidential', 'militar']
    return [{
        "nume": f"Nod_{i}",
        "tip": random.choice(tipuri),
        "mw": random.randint(30, 100),
        "smart": random.choice([True, False])
    } for i in range(5)]

print("🛡️ GridSentinel v6.0 - Impact Național & Human-in-the-Loop")

for t in range(7):
    print(f"\n--- [T+{t}s] Monitorizare Sistem ---")
    
    # --- CYBER CHECK (Micro) ---
    frecventa = 50.0 + random.uniform(-0.02, 0.02)
    if t == 4: frecventa = 47.5 # Simulăm atacul la secunda 4
    
    alerta_cyber = creier_cyber.analizeaza_flux_date(np.array([[frecventa]]))
    if alerta_cyber:
        print(f"🔴 {alerta_cyber} (Frecvență: {frecventa} Hz)")

    # --- GRID CHECK (Macro) ---
    date_teren = generare_context_dynamic()
    deficit = 150 if t == 2 else 0 # Simulăm deficitul la secunda 2
    
    if deficit > 0:
        # Calculăm procentul pierdut din rețeaua națională
        procentaj_pierdut = (deficit / CAPACITATE_TOTALA_NATIONALA) * 100
        
        print(f"🚨 ALERTĂ MAJORĂ: Deficit de {deficit} MW detectat!")
        print(f"📉 IMPACT NAȚIONAL: S-a pierdut **{procentaj_pierdut:.2f}%** din producția totală a țării ({CAPACITATE_TOTALA_NATIONALA} MW).")
        
        propuneri = creier_grid.genereaza_plan_dinamic(date_teren, deficit)
        
        print("\n📋 PLAN DE URGENȚĂ GENERAT DE AI (Așteaptă Aprobare):")
        for p in propuneri:
            print(f"  📍 [{p['locatie']}] - {p['tip']}")
            print(f"     Măsură: {p['actiune']} ({p['mw_salvati']} MW)")
            print(f"     Tehnic: {p['detalii']}")
            print(f"     Motiv: {p['motivatie']}")
            print("-" * 30)

        # CEREM APROBARE
        raspuns = input("\n👨‍🔬 INGINER DE TURĂ: Aprobați execuția planului? (y/n): ")
        
        if raspuns.lower() == 'y':
            print("✅ EXECUTAT. Releele au fost acționate conform planului.")
        else:
            print("🛑 ABORTAT. Inginerul a respins măsurile automate.")
            
    else:
        if not alerta_cyber:
            print(f"✅ Sistem stabil. Frecvență: {frecventa:.2f} Hz")
    
    time.sleep(1)