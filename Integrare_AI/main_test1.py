import time
import random
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path

# 1. BLINDĂM TERMINALUL
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from tensorflow.keras.models import load_model
from AI_INTEGRATION import CyberGridOptimizer


class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def gaseste_fisier_csv(root_dir):
    posibile = [
        root_dir / "data" / "telemetry_stream.csv",
        root_dir / "data" / "telemetry_live.csv",
        root_dir / "telemetry_stream.csv",
        root_dir / "telemetry_live.csv",
    ]

    for cale in posibile:
        if cale.exists():
            return cale

    raise FileNotFoundError(
        "Nu am găsit niciun fișier CSV de telemetrie. "
        "Am căutat în: " + ", ".join(str(c) for c in posibile)
    )


def ruleaza_integrarea_finala():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C.HEADER}{C.BOLD}=== INITIALIZARE SISTEM SMART GRID SENTINEL ==={C.END}")

    # Căi calculate corect față de locația fișierului curent
    BASE_DIR = Path(__file__).resolve().parent
    ROOT_DIR = BASE_DIR.parent
    AI_DIR = ROOT_DIR / "AI engine"

    MODEL_PATH = AI_DIR / "model_gridsentinel.keras"
    SCALER_PATH = AI_DIR / "scaler_gridsentinel.pkl"

    # Încărcare AI și Scaler
    try:
        print(f"{C.BLUE}[+] Incarcare model Keras...{C.END}")
        print(f"{C.BLUE}    {MODEL_PATH}{C.END}")
        model_ai = load_model(MODEL_PATH)

        print(f"{C.BLUE}[+] Incarcare Scaler...{C.END}")
        print(f"{C.BLUE}    {SCALER_PATH}{C.END}")
        scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        print(f"{C.RED}[-]{C.BOLD} EROARE la incarcarea fisierelor AI: {e}{C.END}")
        return

    optimizer = CyberGridOptimizer()
    orase = ["CLJ", "BRZ", "BUC", "PFR", "VID", "BCN"]

    # Încărcare date CSV
    try:
        telemetry_path = gaseste_fisier_csv(ROOT_DIR)
        print(f"{C.BLUE}[+] Incarcare date CSV...{C.END}")
        print(f"{C.BLUE}    {telemetry_path}{C.END}")
        telemetry_data = pd.read_csv(telemetry_path)
        print(f"{C.GREEN}[+] S-au incarcat {len(telemetry_data)} inregistrari de la senzori.{C.END}")
    except Exception as e:
        print(f"{C.RED}[-] Nu gasesc fisierul CSV de telemetrie. Eroare: {e}{C.END}")
        return

    time.sleep(1)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{C.BOLD}>>> MONITORIZARE LIVE SMART GRID SENTINEL <<<{C.END}")
        print(f"Ultima actualizare: {time.strftime('%H:%M:%S')}\n")

        rand_senzor = telemetry_data.sample(1)

        # Curățare date
        rand_senzor_clean = rand_senzor.replace({
            'ON': 1, 'OFF': 0,
            'On': 1, 'Off': 0,
            'on': 1, 'off': 0
        })
        rand_senzor_clean = rand_senzor_clean.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Filtrare coloane inutile
        coloane_inutile = ['timestamp', 'nivel_severitate', 'curent_a', 'is_attack', 'label', 'station_id']
        date_pentru_ai = rand_senzor_clean.drop(
            columns=[c for c in coloane_inutile if c in rand_senzor_clean.columns]
        )

        try:
            date_scalate = scaler.transform(date_pentru_ai)
            predictie = model_ai.predict(date_scalate, verbose=0)
            prob_cyber = float(predictie[0][0])
        except Exception as e:
            print(f"{C.RED}[-] Eroare preprocesare: {e}{C.END}")
            time.sleep(2)
            continue

        # Extragere deficit
        deficit = float(rand_senzor["deficit_mw"].values[0]) if "deficit_mw" in rand_senzor.columns else random.randint(0, 500)
        nod = random.choice(orase)

        # Logica de apărare
        raport = optimizer.evalueaza_stare_retea(
            deficit_mw=deficit,
            probabilitate_cyber=prob_cyber,
            nod_suspect=nod
        )

        # Afișare stilizată
        nivel = raport['nivel_severitate']
        culoare_status = C.RED if nivel >= 4 else (C.YELLOW if nivel >= 2 else C.GREEN)

        print(f"{C.BOLD}{'=' * 60}{C.END}")
        print(f"STATUS GENERAL: {culoare_status}{C.BOLD}{raport['status_general']}{C.END}")
        print(f"NIVEL ALERTĂ:   {culoare_status}{nivel}{C.END}")

        bara_len = 25
        umplut = int(prob_cyber * bara_len)
        bara = "█" * umplut + "-" * (bara_len - umplut)
        print(f"RISC CYBER:     [{culoare_status}{bara}{C.END}] {prob_cyber * 100:.1f}%")
        print(f"DEFICIT MW:     {C.BOLD}{deficit} MW{C.END}")

        print(f"\n{C.BOLD}RECOMANDARE AI:{C.END}")
        if nivel > 0:
            print(f"{C.YELLOW}>>> {raport['recomandare_ai']}{C.END}")
            if raport['nod_afectat']:
                print(f"NOD SUSPECT:    {C.YELLOW}{raport['nod_afectat']}{C.END}")
            if raport['muchii_de_taiat']:
                print(f"{C.RED}{C.BOLD}IZOLARE ACTIVĂ: {', '.join(raport['muchii_de_taiat'])}{C.END}")
        else:
            print(f"{C.GREEN}Sistem stabil. Toți parametrii sunt în limite nominale.{C.END}")

        print(f"\n{C.BOLD}{'=' * 60}{C.END}")
        time.sleep(1.5)


if __name__ == "__main__":
    ruleaza_integrarea_finala()
