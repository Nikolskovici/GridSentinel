import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# 1. Pregătim arhitectura (Autoencoder-ul nostru)
def build_autoencoder(input_dimensions):
    input_layer = Input(shape=(input_dimensions,))
    encoded = Dense(16, activation='relu')(input_layer)
    encoded = Dense(8, activation='relu')(encoded)
    decoded = Dense(16, activation='relu')(encoded)
    output_layer = Dense(input_dimensions, activation='linear')(decoded)
    autoencoder = Model(inputs=input_layer, outputs=output_layer)
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder

# 2. Încărcăm ziua normală și facem tăierea riguroasă
dataset_normal = pd.read_csv('date_normale_transelectrica.csv')
date_fizice = dataset_normal[['Frecventa_Hz', 'Tensiune_kV', 'Flux_Intrare_MW', 'Flux_Iesire_MW']]

normalizator = MinMaxScaler()
date_scalate = normalizator.fit_transform(date_fizice)

# Aici facem ce ai sugerat: tăiem datele normale 80% pentru învățare, 20% pentru validare
date_antrenament, date_validare = train_test_split(date_scalate, test_size=0.2, random_state=42)

model_anomalii = build_autoencoder(input_dimensions=4)

# Antrenăm modelul pe cei 80% și îl punem să se autoevalueze pe restul de 20%
model_anomalii.fit(
    x=date_antrenament, y=date_antrenament,
    validation_data=(date_validare, date_validare),
    epochs=50, batch_size=32, verbose=1
)

# 3. SETUL DE TEST REAL: Aducem fișierul cu atacul cibernetic pentru Demo
dataset_atac = pd.read_csv('date_atac_demo.csv')
date_atac_fizice = dataset_atac[['Frecventa_Hz', 'Tensiune_kV', 'Flux_Intrare_MW', 'Flux_Iesire_MW']]

# Trebuie să normalizăm datele de atac exact cu aceeași riglă folosită la antrenament
date_atac_scalate = normalizator.transform(date_atac_fizice)

# 4. Punem AI-ul să reconstruiască datele atacate
predictii = model_anomalii.predict(date_atac_scalate)

# 5. Calculăm eroarea pentru fiecare secundă din setul de test
erori_reconstructie = np.mean(np.power(date_atac_scalate - predictii, 2), axis=1)

# 6. Legăm eroarea matematică de nivelurile voastre de alertă
# Definim o limită de eroare (un prag). Orice trece de acest prag declanșează alerta.
prag_baza = 0.05 

for i, eroare in enumerate(erori_reconstructie):
    if eroare < prag_baza:
        stare = "Nivel 0: Caz initial, reteaua functioneaza in parametrii normali"
        
    elif eroare < prag_baza * 2:
        stare = "Nivel 1: Mici deviatii de la normalitate, notificarea echipei de ingineri."
        
    elif eroare < prag_baza * 4:
        stare = "Nivel 2: Anomalie descoperita, inginerul principal este notificat si trebuie sa ia o decizie."
        
    elif eroare < prag_baza * 7:
        stare = "Nivel 3: Multiple anomalii detectate, pericol grav de avarie a retelei. Echipa de ingineri trebuie sa ia o decizie."
        
    elif eroare < prag_baza * 10:
        stare = "Nivel 4: Pericol iminent de avarie si intrerupere a serviciilor de curent electric. Alarma activata si fiecare inginer in functie anuntat."
        
    else:
        # Orice eroare uriașă care trece de prag_baza * 10 intră aici
        stare = "Nivel 5: Catastrofa. Fiecare inginer este anuntat indiferent daca este in tura sau nu."
        
    # Testăm logica în consolă
    print(f"Secunda {i} | Eroare calculata: {eroare:.4f} | Status: {stare}")