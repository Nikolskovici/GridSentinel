import time
import random
import pandas as pd
import numpy as np
import joblib
import os

# Dezactivam log-urile inutile de la TF
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from tensorflow.keras.models import load_model
from ai_integration import CyberGridOptimizer

# Culori ANSI pentru terminal
class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def genereaza_bara_risc(prob):
    lungime = 20
    umplut = int(prob * lungime)
    bara = "█" * umplut + "-" * (lungime - umplut)
    culoare = C.OKGREEN if prob < 0.3 else (C.WARNING if prob < 0.7 else C.FAIL)
    return f"[{culoare}{bara}{C.ENDC}] {prob*100:.1f}%"

def ruleaza_integrarea_finala():
    print(f"{C.HEADER}{C.BOLD}=== SISTEM SMART GRID SENTINEL - INITIALIZARE ==={C.ENDC}")
    
    try:
        model_ai = load_model("model_gridsentinel.keras")
        scaler = joblib.load("scaler_gridsentinel.pkl")
        print(f"{C.OKGREEN}[+] Nucleu AI incarcat cu succes.{C.ENDC}")
    except Exception as e:
        print(f"{C.FAIL}[-] EROARE CRITICA: {e}{C.ENDC}")
        return

    optimizer = CyberGridOptimizer()
    orase = ["CLJ", "BRZ", "BUC", "PFR", "VID", "BCN"]
    
    try:
        telemetry_data = pd.read_csv("telemetry_stream.csv")
        print(f"{C.OKGREEN}[+] Senzori online. Flux de date detectat.{C.ENDC}")
    except Exception as e:
        print(f"{C.FAIL}[-] Lipsa date telemetrie.{C.ENDC}")
        return

    print(f"\n{C.OKBLUE}{C.BOLD}>>> MONITORIZARE ACTIVA - ANALIZA IN TIMP REAL <<<{C.ENDC}\n")
    
    while True:
        rand_senzor = telemetry_data.sample(1)
        
        # Curatare date (HACK pentru 'Senin', 'ON', etc.)
        rand_senzor_clean = rand_senzor.replace({'ON': 1, 'OFF': 0, 'On': 1, 'Off': 0})
        rand_senzor_clean = rand_senzor_clean.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Predictie
        date_scalate = scaler.transform(rand_senzor_clean.values)
        predictie = model_ai.predict(date_scalate, verbose=0)
        prob_cyber = float(predictie[0][0])

        # Logica Deficit
        try:
            deficit = float(rand_senzor_clean["deficit_mw"].values[0])
        except:
            deficit = random.choices([0, 50, 180, 450], weights=[70, 15, 10, 5])[0]
            
        nod = random.choice(orase)
        raport = optimizer.evalueaza_stare_retea(deficit, prob_cyber, nod)
        
        # --- AFISARE REFACTORIZATA ---
        nivel = raport['nivel_severitate']
        prefix = C.FAIL if nivel >= 4 else (C.WARNING if nivel >= 2 else C.OKGREEN)
        
        print(f"{C.BOLD}{'='*60}{C.ENDC}")
        print(f"STARE SISTEM: {prefix}{C.BOLD}{raport['status_general']}{C.ENDC} (Nivel {nivel})")
        print(f"CYBER RISK:  {genereaza_bara_risc(prob_cyber)}")
        print(f"DEFICIT:     {C.BOLD}{deficit} MW{C.ENDC}")
        
        if nivel > 0:
            print(f"\n{C.WARNING}{C.BOLD}RECOMANDARE AI:{C.ENDC}")
            print(f" > {raport['recomandare_ai']}")
            
            if raport['nod_afectat']:
                print(f" > LOCATIE VULNERABILA: {C.FAIL}{raport['nod_afectat']}{C.ENDC}")
            
            if raport['muchii_de_taiat']:
                print(f" > {C.FAIL}{C.BOLD}IZOLARE URGENTA:{C.ENDC} Se taie conexiunile: {C.BOLD}{', '.join(raport['muchii_de_taiat'])}{C.ENDC}")
        else:
            print(f"\n{C.OKGREEN}Sistemul opereaza in parametri optimi. Nicio amenintare detectata.{C.ENDC}")
            
        time.sleep(3)

if __name__ == "__main__":
    ruleaza_integrarea_finala()