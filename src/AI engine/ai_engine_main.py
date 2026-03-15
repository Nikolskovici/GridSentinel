import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# Încărcăm fișierul generat de colegul tău
dataset_complet = pd.read_csv('data/training_data.csv', encoding='utf-8-sig')
print(f"START: Avem {len(dataset_complet)} rânduri în tabelul original.")

# Filtrăm tensiunea
dataset_complet = dataset_complet[dataset_complet['tensiune_kv'] > 0]
print(f"PUNCT CONTROL 1: Au rămas {len(dataset_complet)} rânduri după filtrarea tensiunii.")

# 1. Traducem cuvintele în numere (matematică pentru AI)
# Forțăm textul să fie curat (fără spații ascunse, totul cu majuscule) pentru a evita erorile de tipar
dataset_complet['status'] = dataset_complet['status'].astype(str).str.strip().str.upper()
dataset_complet['status'] = dataset_complet['status'].map({'ON': 1, 'OFF': 0})

# Dacă maparea nu a găsit cuvântul exact, va pune NaN. Noi umplem golurile cu 1 (ON) ca să nu pierdem date la hackathon
dataset_complet['status'] = dataset_complet['status'].fillna(1)
print(f"PUNCT CONTROL 2: Au rămas {len(dataset_complet)} rânduri după procesarea Status-ului.")

# Transformăm starea vremii direct în coduri numerice (0, 1, 2 etc) fără dicționar strict
dataset_complet['weather'] = dataset_complet['weather'].astype('category').cat.codes

# Ștergem ce e absolut stricat
dataset_complet = dataset_complet.dropna()
print(f"PUNCT CONTROL 3: Au rămas {len(dataset_complet)} rânduri după evacuarea erorilor finale (dropna).")

# Afișăm exact ce valori secrete ascunde coloana nivel_severitate
valori_severitate = dataset_complet['nivel_severitate'].unique()
print(f"INVESTIGAȚIE: În coloana nivel_severitate avem fix aceste valori: {valori_severitate}")

# 2. Filtrăm strict normalitatea (Aici presupunem că zero este normalitatea, dar dacă investigația de mai sus arată altceva, modifici aici)
date_normale = dataset_complet[dataset_complet['nivel_severitate'] == 0].copy()
print(f"FINAL: Antrenăm AI-ul pe {len(date_normale)} rânduri perfect normale.")
# 3. Alegem coloanele pe care le va analiza rețeaua neuronală
# Observă că avem 6 coloane de intrare acum, deci AI-ul trebuie ajustat
coloane_fizice = ['status', 'weather', 'frecventa_hz', 'tensiune_kv', 'flux_intrare_mw', 'flux_iesire_mw']
date_antrenament = date_normale[coloane_fizice]

# 4. Normalizarea (aducem toate valorile pe o scară de la 0 la 1)
normalizator = MinMaxScaler()
date_scalate = normalizator.fit_transform(date_antrenament)

# 5. Construim Autoencoder-ul adaptat la cele 6 coloane ale voastre
def build_autoencoder(input_dimensions):
    intrare = Input(shape=(input_dimensions,))
    compresie = Dense(16, activation='relu')(intrare)
    compresie = Dense(8, activation='relu')(compresie)
    reconstructie = Dense(16, activation='relu')(compresie)
    iesire = Dense(input_dimensions, activation='linear')(reconstructie)
    model = Model(inputs=intrare, outputs=iesire)
    model.compile(optimizer='adam', loss='mse')
    return model
# Am pus input_dimensions=6 pentru că avem 6 coloane fizice
creier_ai = build_autoencoder(input_dimensions=6)

# 6. Începem antrenamentul!
print("Începem memorarea parametrilor normali...")
creier_ai.fit(
    x=date_scalate, 
    y=date_scalate, 
    epochs=50, 
    batch_size=256, 
    verbose=1
)
print("Sistemul este antrenat și pregătit să apere Transelectrica!")

creier_ai.save('AI engine/model_gridsentinel.keras')
print("Creierul AI a fost salvat cu succes pe disk!")

# 2. Salvăm rigla de măsurat (Normalizatorul)
# Extensia .pkl (pickle) îngheață rigla matematică exact în starea ei curentă
joblib.dump(normalizator, 'AI engine/scaler_gridsentinel.pkl')
print("Rigla de normalizare a fost salvată!")
# Acum avem tot ce ne trebuie pentru a construi un sistem de detecție a anomaliilor în rețeaua Transelectrica!