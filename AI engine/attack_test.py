import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# 1. Aducem studentul la muncă și îi dăm rigla din facultate
creier_ai = load_model('model_gridsentinel.keras')
normalizator = joblib.load('scaler_gridsentinel.pkl')
print("Modelul și rigla au fost încărcate cu succes!")

# 2. Citim fișierul nou, cel pregătit pentru Demo (care conține atacul)
# Să presupunem că l-ați numit 'date_demo_juriu.csv'
dataset_test = pd.read_csv('telemetry_stream.csv')

# 3. Traducem cuvintele în matematică, exact cum am făcut la antrenament
dataset_test['status'] = dataset_test['status'].map({'ON': 1, 'OFF': 0})

dictionar_vreme = {'Senin': 0, 'Furtuna': 1, 'Viscol': 2, 'Tornada': 3, 'Inundatie': 4}
dataset_test['weather'] = dataset_test['weather'].map(dictionar_vreme)

# Extragem doar coloanele fizice. ATENȚIE: Nu mai filtrăm nivelul de severitate! 
# Acum lăsăm AI-ul să ghicească singur dacă e criză sau nu.
coloane_fizice = ['status', 'weather', 'frecventa_hz', 'tensiune_kv', 'flux_intrare_mw', 'flux_iesire_mw']
date_test_brute = dataset_test[coloane_fizice]

# 4. Folosim rigla veche pe datele noi (observă că folosim doar 'transform', nu 'fit_transform')
date_test_scalate = normalizator.transform(date_test_brute)

# 5. Punem AI-ul să reconstruiască datele și calculăm cât de mult a "ieșit de pe contur"
predictii = creier_ai.predict(date_test_scalate)
erori_reconstructie = np.mean(np.power(date_test_scalate - predictii, 2), axis=1)

# 6. Trecem erorile prin radarul vostru de viteză (Scara 0-5)
prag_baza = 0.02 # Acest număr îl vei ajusta tu la hackathon până arată perfect pe datele voastre

print("\n--- INIȚIERE MONITORIZARE TRANSELECTRICA ---")
for secunda, eroare in enumerate(erori_reconstructie):
    if eroare < prag_baza:
        stare = "Nivel 0: Reteaua functioneaza in parametrii normali"
    elif eroare < prag_baza * 2:
        stare = "Nivel 1: Mici deviatii detectate. Notificare ingineri."
    elif eroare < prag_baza * 4:
        stare = "Nivel 2: Anomalie confirmata. Necesita decizie umana."
    elif eroare < prag_baza * 7:
        stare = "Nivel 3: Pericol grav. Multiple anomalii in sistem."
    elif eroare < prag_baza * 10:
        stare = "Nivel 4: ATAC CIBERNETIC! Astept confirmare izolare retea IT."
    else:
        stare = "Nivel 5: CATASTROFA. Activare protocol de urgenta."
        
    print(f"Secunda {secunda} | Eroare AI: {eroare:.4f} | {stare}")