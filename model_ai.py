# model_ai.py - Aici va lucra TUDOR
import pandas as pd

def run_anomaly_detection(file_path):
    # Tudor va citi datele generate de Niki
    df = pd.read_csv(file_path)
    
    # Aici va fi creierul AI
    # Momentan returnam un status "Fake" ca sa poata lucra Iustin
    print(f"Analizand {len(df)} linii de date...")
    
    return "SAFE" # Sau "ATTACK_DETECTED"