import pandas as pd
from normalizacaoDados import Normalizar
from tensorflow.keras import layers, models
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

dados = pd.read_csv('dados/dados.csv')
x = dados.drop(columns=['tempo_ms', 'gestos']).values
y = dados['gestos'].values

encoder = LabelEncoder()
y = encoder.fit_transform(y)

norm = Normalizar("dados/dados.csv")

x_norm = norm.pre_processar(x)

x_janelas, y_janelas = norm.criar_janelas(x_norm, y)

x_treino, x_teste, y_treino, y_teste = train_test_split(x_janelas, y_janelas, test_size=0.2)

modelo = models.Sequential(
    layers.LSTM(64, inputshape=(x_treino.shape[1], x_treino.shape[2])),
    layers.Dense(64, activation='relu'),
    layers.Dense(len(np.unique(y)), activation='softmax'),
)

modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
modelo.fit(x_treino, y_treino, validation_data= (x_teste, y_teste),epochs=30, batch_size=32)

modelo.save("melhor.modelo.h5")
np.save("classe_gestos", encoder.classes_)

