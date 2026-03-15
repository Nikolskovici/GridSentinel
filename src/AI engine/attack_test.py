import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Încărcăm datele de test
# Dacă fișierul cu atacuri se numește altfel, modifică numele aici
dataset_test = pd.read_csv('data/training_data.csv', encoding='utf-8-sig')

# 2. Curățăm datele EXACT ca la antrenament pentru a evita erorile "NaN"
dataset_test = dataset_test[dataset_test['tensiune_kv'] > 0]
dataset_test['status'] = dataset_test['status'].astype(str).str.strip().str.upper()
dataset_test['status'] = dataset_test['status'].map({'ON': 1, 'OFF': 0}).fillna(1)
dataset_test['weather'] = dataset_test['weather'].astype('category').cat.codes
dataset_test = dataset_test.dropna()

# 3. Definim adevărul de teren (ce s-a întâmplat de fapt pe teren)
# 0 = Normal, 1 = Criză (orice nivel de severitate mai mare ca 0)
adevar_de_teren = (dataset_test['nivel_severitate'] > 0).astype(int)

# 4. Pregătim strict coloanele fizice pe care le recunoaște AI-ul
coloane_fizice = ['status', 'weather', 'frecventa_hz', 'tensiune_kv', 'flux_intrare_mw', 'flux_iesire_mw']
date_test_pentru_ai = dataset_test[coloane_fizice]

# 5. Încărcăm Creierul AI și Rigla de Normalizare de pe disk
print("Încărcăm modelul AI GridSentinel și sistemul de scalare...")
creier_ai = load_model('AI engine/model_gridsentinel.keras')
normalizator = joblib.load('AI engine/scaler_gridsentinel.pkl')

# 6. Scalăm datele de test pentru a vorbi aceeași limbă cu AI-ul
date_test_scalate = normalizator.transform(date_test_pentru_ai)

# 7. AI-ul încearcă să reconstruiască fluxul energetic
print("AI-ul analizează rețeaua și caută anomalii...")
reconstructie = creier_ai.predict(date_test_scalate)

# 8. Calculăm eroarea de reconstrucție pentru fiecare secundă de funcționare
erori_reconstructie = np.mean(np.square(date_test_scalate - reconstructie), axis=1)

# Afișăm mediile pe ecran ca să confirmăm că am scăpat definitiv de "NaN"
print(f"Media erorii generale: {np.mean(erori_reconstructie):.6f}")

# 9. Setăm limita de alarmă (Threshold) pentru operatorul uman
# Aici este cheia! Orice eroare peste acest număr declanșează alerta cibernetică
limita_alarma = 0.00000055

# 10. Decizia finală a inteligenței artificiale
decizie_ai = (erori_reconstructie > limita_alarma).astype(int)

# 11. Desenăm Matricea de Confuzie
matrice = confusion_matrix(adevar_de_teren, decizie_ai)

plt.figure(figsize=(8, 6))
sns.heatmap(matrice, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal (Prezis)', 'Atac Cibernetic (Prezis)'],
            yticklabels=['Normal (Real)', 'Atac Cibernetic (Real)'])
plt.title('Matricea de Confuzie - Evaluare AI GridSentinel')
plt.ylabel('Situația Reală din Teren')
plt.xlabel('Ce a detectat AI-ul nostru')
plt.show()