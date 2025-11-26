# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from normalizacaoDados import Normalizar
# from tensorflow.keras import models, layers, Input
# from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
#
# dados = pd.read_csv('dados/dados.csv')
#
# colunas_usadas = [
#           "sensor_1L", "sensor_3L", "sensor_4L","sensor_5L",
#           "sensor_1R", "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R","acel1","giro1","acel2","giro2"
# ]
#
# x = dados[colunas_usadas].values
# y = dados['gesto'].values
# l = LabelEncoder()
# y = l.fit_transform(y)
#
# np.save('dados/gestos', l.classes_)
# print(dados.info())
#
# x_treino_raw, x_teste_raw, y_treino_raw, y_teste_raw = train_test_split(x, y, test_size=0.2, shuffle=True, stratify=y)
#
# norm = Normalizar()
# x_treino_norm = norm.fit_transform(x_treino_raw)
# x_teste_norm = norm.transform(x_teste_raw)
#
# print(f"DEBUG: Shape do x_treino_norm (antes de janelar): {x_treino_norm.shape}")
#
# x_treino, y_treino = norm.criar_janelas(x_treino_norm, y_treino_raw)
# x_teste, y_teste = norm.criar_janelas(x_teste_norm, y_teste_raw)
#
# print(f"Formato X_treino final (janelas): {x_treino.shape}")
# print(f"Formato Y_treino final (janelas): {y_treino.shape}")
#
# num_classes = len(np.unique(y_treino))
# shape_entrada = (x_treino.shape[1], x_treino.shape[2])
#
# y_treino_ohe = to_categorical(y_treino, num_classes=num_classes)
# y_teste_ohe = to_categorical(y_teste, num_classes=num_classes)
#
# modelo = models.Sequential([
#     Input(shape=shape_entrada),
#     layers.LSTM(64, return_sequences=True),
#     layers.Dropout(0.5),
#     layers.LSTM(64 , return_sequences=True),
#     layers.Dropout(0.5),
#     layers.LSTM(64),
#     layers.Dropout(0.5),
#     layers.Dense(64, activation='relu'),
#     layers.Dropout(0.5),
#     layers.Dense(num_classes, activation='softmax'),
# ])
#
# modelo.summary()
# early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
# checkpoint = ModelCheckpoint('libras.h5', monitor='val_loss', save_best_only=True)
# modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# modelo.fit(x_treino, y_treino_ohe,validation_data=(x_teste, y_teste_ohe), epochs=70, batch_size=16, callbacks=[checkpoint,early_stop])
#
# print("salvo")


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from normalizacaoDados import Normalizar
from tensorflow.keras import models, layers, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from scipy.signal import butter, filtfilt

# --- 1. FUNÇÃO DE FILTRO ---
def aplicar_filtro_butterworth(data, cutoff=3, fs=20, order=4):
    """
    data: array numpy ou coluna do pandas
    cutoff: frequência de corte (3Hz é bom para gestos humanos)
    fs: frequência de amostragem (quantas leituras seu ESP32 faz por segundo)
    order: ordem do filtro (suavidade)
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # Cria o filtro passa-baixa (low-pass)
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    # Aplica o filtro (filtfilt aplica frente e trás para não ter atraso de fase)
    y = filtfilt(b, a, data, axis=0)
    return y

# --- CARREGAR DADOS ---
dados = pd.read_csv('dados/dados.csv')

colunas_usadas = [
          "sensor_1L", "sensor_3L", "sensor_4L","sensor_5L",
          "sensor_1R", "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R",
          "acel1","giro1","acel2","giro2"
]

# --- 2. APLICAR O FILTRO ANTES DE TUDO ---
# Importante: Ajuste 'fs' para a frequência real do seu ESP32 (ex: 100ms delay = 10Hz, 20ms = 50Hz)
fs_estimado = 5
print("Aplicando filtro Butterworth nos dados brutos...")
for col in colunas_usadas:
    dados[col] = aplicar_filtro_butterworth(dados[col], cutoff=2, fs=fs_estimado)

x = dados[colunas_usadas].values
y = dados['gesto'].values

# Codificar Labels
l = LabelEncoder()
y_encoded = l.fit_transform(y)
np.save('dados/gestos', l.classes_)

# Normalizar (Ainda com os dados contínuos)
norm = Normalizar()
x_norm = norm.fit_transform(x)

# --- 3. CRIAR JANELAS (CORREÇÃO CRÍTICA) ---
# As janelas devem ser criadas ANTES de separar Treino/Teste e ANTES de embaralhar
print("Criando janelas temporais...")
# Nota: Assumindo que norm.criar_janelas aceita (X, y) e retorna (X_janelado, y_janelado)
# Se sua função criar_janelas não lida com a transição de gestos (ex: misturar final de 'Oi' com começo de 'Repouso'),
# o ideal é janelar agrupando pelo label ou garantindo continuidade.
x_janelas, y_janelas = norm.criar_janelas(x_norm, y_encoded)

print(f"Shape após janelamento: {x_janelas.shape}")

# --- 4. SPLIT (AGORA PODEMOS EMBARALHAR AS JANELAS) ---
x_treino, x_teste, y_treino, y_teste = train_test_split(
    x_janelas, y_janelas,
    test_size=0.2,
    shuffle=True,  # Agora sim pode dar shuffle, pois as janelas já estão formadas
    stratify=y_janelas
)

num_classes = len(np.unique(y_janelas))
shape_entrada = (x_treino.shape[1], x_treino.shape[2])

y_treino_ohe = to_categorical(y_treino, num_classes=num_classes)
y_teste_ohe = to_categorical(y_teste, num_classes=num_classes)

# --- MODELO ---
modelo = models.Sequential([
    Input(shape=shape_entrada),
    # Aumentei um pouco a complexidade ou ajustei dropout se necessário
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.3),
    layers.LSTM(64, return_sequences=False), # Última LSTM não precisa de return_sequences se for para Dense direto
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(num_classes, activation='softmax'),
])

modelo.summary()

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
checkpoint = ModelCheckpoint('libras.h5', monitor='val_loss', save_best_only=True)

modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = modelo.fit(
    x_treino, y_treino_ohe,
    validation_data=(x_teste, y_teste_ohe),
    epochs=70,
    batch_size=32, # Batch size 32 costuma ser mais estável que 16
    callbacks=[checkpoint, early_stop]
)
