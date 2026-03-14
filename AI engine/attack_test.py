import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Încărcăm sistemul
creier_ai = load_model('model_gridsentinel.keras')
normalizator = joblib.load('scaler_gridsentinel.pkl')

# Citim datele de test
dataset_test = pd.read_csv('telemetry_stream.csv')

# Traducem textul în numere
dataset_test['status'] = dataset_test['status'].map({'ON': 1, 'OFF': 0})
dictionar_vreme = {'Senin': 0, 'Furtuna': 1, 'Viscol': 2, 'Tornada': 3, 'Inundatie': 4}
dataset_test['weather'] = dataset_test['weather'].map(dictionar_vreme)

coloane_fizice = ['status', 'weather', 'frecventa_hz', 'tensiune_kv', 'flux_intrare_mw', 'flux_iesire_mw']
date_test_brute = dataset_test[coloane_fizice]

# Trecem datele prin model
date_test_scalate = normalizator.transform(date_test_brute)
predictii = creier_ai.predict(date_test_scalate)
erori_reconstructie = np.mean(np.power(date_test_scalate - predictii, 2), axis=1)

realitate = (dataset_test['nivel_severitate'] > 0).astype(int)

erori_pe_timp_de_pace = erori_reconstructie[realitate == 0]
erori_pe_timp_de_atac = erori_reconstructie[realitate == 1]

# Afișăm valorile reale în consolă pentru a nu mai ghici pragul
print(f"Media erorii cand reteaua e in siguranta: {np.mean(erori_pe_timp_de_pace):.6f}")
print(f"Media erorii cand reteaua e atacata: {np.mean(erori_pe_timp_de_atac):.6f}")
print(f"Cea mai MARE eroare gasita vreodata de AI: {np.max(erori_reconstructie):.6f}")

# Definim când dă AI-ul alarma. Folosim nivelul 2 de alertă ca punct de decizie.
prag_baza = 0.0000001
predictii_ai = (erori_reconstructie > prag_baza * 2).astype(int)

# Definim realitatea de pe teren: în fișierul vostru, orice nivel de severitate peste 0 înseamnă că e criză.
realitate = (dataset_test['nivel_severitate'] > 0).astype(int)

# Calculăm și desenăm vizual Matricea de Confuzie
matrice = confusion_matrix(realitate, predictii_ai)

plt.figure(figsize=(6, 4))
sns.heatmap(matrice, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal (Prezis)', 'Criză (Prezis)'], 
            yticklabels=['Normal (Real)', 'Criză (Real)'])
plt.title('Matricea de Confuzie - Evaluare GridSentinel')
plt.ylabel('Adevărul de pe Teren')
plt.xlabel('Decizia Inteligenței Artificiale')
plt.show()