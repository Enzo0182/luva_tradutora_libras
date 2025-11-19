import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from normalizacaoDados import Normalizar
from tensorflow.keras import models, layers, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

dados = pd.read_csv('dados/dados.csv')

colunas_usadas = [
          "sensor_1L", "sensor_2L", "sensor_3L", "sensor_4L","sensor_5L",
          "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R","acel1","giro1","acel2","giro2"
]

x = dados[colunas_usadas].values
y = dados['gesto'].values
l = LabelEncoder()
y = l.fit_transform(y)

np.save('dados/gestos', l.classes_)
print(dados.info())

x_treino_raw, x_teste_raw, y_treino_raw, y_teste_raw = train_test_split(x, y, test_size=0.2, shuffle=False)

norm = Normalizar()
x_treino_norm = norm.fit_transform(x_treino_raw)
x_teste_norm = norm.transform(x_teste_raw)

print(f"DEBUG: Shape do x_treino_norm (antes de janelar): {x_treino_norm.shape}")

x_treino, y_treino = norm.criar_janelas(x_treino_norm, y_treino_raw)
x_teste, y_teste = norm.criar_janelas(x_teste_norm, y_teste_raw)

print(f"Formato X_treino final (janelas): {x_treino.shape}")
print(f"Formato Y_treino final (janelas): {y_treino.shape}")

num_classes = len(np.unique(y_treino))
shape_entrada = (x_treino.shape[1], x_treino.shape[2])

y_treino_ohe = to_categorical(y_treino, num_classes=num_classes)
y_teste_ohe = to_categorical(y_teste, num_classes=num_classes)

modelo = models.Sequential([
    Input(shape=shape_entrada),
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.5),
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.5),
    layers.LSTM(64),
    layers.Dropout(0.5),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax'),
])

modelo.summary()
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
modelo.fit(x_treino, y_treino_ohe,validation_data=(x_teste, y_teste_ohe), epochs=50, batch_size=16, callbacks=[early_stop])

modelo.save('libras.h5')
print("salvo")

