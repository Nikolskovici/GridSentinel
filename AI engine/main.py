import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

def build_autoencoder(input_dimensions):
    # Poarta de intrare: aici intră datele senzorilor noștri (ex: frecvență, voltaj, putere)
    input_layer = Input(shape=(input_dimensions,))

    # Partea de compresie (Encoder): rețeaua "strânge" informația esențială
    encoded = Dense(16, activation='relu')(input_layer)
    encoded = Dense(8, activation='relu')(encoded)

    # Partea de reconstrucție (Decoder): rețeaua încearcă să refacă datele inițiale din memorie
    decoded = Dense(16, activation='relu')(encoded)
    output_layer = Dense(input_dimensions, activation='linear')(decoded)

    # Asamblăm creierul complet
    autoencoder = Model(inputs=input_layer, outputs=output_layer)

    # Folosim 'mse' (Eroarea Pătratică Medie) pentru a măsura exact cât de mult "a ieșit de pe contur" la desenare
    autoencoder.compile(optimizer='adam', loss='mse')

    return autoencoder

# Exemplu de inițializare pentru 5 senzori fictivi pe care îi vom monitoriza
model_anomalii = build_autoencoder(input_dimensions=5)

# Această funcție îți va printa în consolă arhitectura, e bună de pus și în prezentare
model_anomalii.summary()