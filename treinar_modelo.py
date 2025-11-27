import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras import models, layers, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from scipy.signal import butter, filtfilt
from sklearn.utils import class_weight

# --- CONFIGURAÇÃO ---
DELAY_NO_ARDUINO = 30  # Ajustado conforme seu log (33Hz)
FS_REAL = 1000 / DELAY_NO_ARDUINO
CUTOFF_FILTRO = 3.0

def aplicar_filtro_butterworth(data, cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    if normal_cutoff >= 1: normal_cutoff = 0.99
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

# --- CARREGAR DADOS ---
dados = pd.read_csv('dados/dados.csv')

# Feature Engineering
dados['acel_total'] = np.sqrt(dados['acel1']**2 + dados['giro1']**2 + dados['acel2']**2 + dados['giro2']**2)

colunas_usadas = [
    "sensor_1L", "sensor_3L", "sensor_4L","sensor_5L",
    "sensor_1R", "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R",
    "acel1","giro1","acel2","giro2",
    "acel_total"
]

print("Filtrando...")
for col in colunas_usadas:
    dados[col] = aplicar_filtro_butterworth(dados[col].values, cutoff=CUTOFF_FILTRO, fs=FS_REAL)

x = dados[colunas_usadas].values
y = dados['gesto'].values

# Labels
l = LabelEncoder()
y_encoded = l.fit_transform(y)
np.save('dados/gestos.npy', l.classes_) # Salva nomes das classes

# --- NORMALIZAÇÃO CORRETA (SALVANDO O SCALER) ---
scaler = MinMaxScaler(feature_range=(0, 1))
x_norm = scaler.fit_transform(x)

# SALVAR O SCALER PARA O MAIN.PY
joblib.dump(scaler, 'dados/scaler.pkl')
print("Scaler salvo em dados/scaler.pkl")

# --- JANELAMENTO ---
# (Mantendo sua lógica simples de reshape para LSTM,
# mas idealmente use uma função de sliding window aqui)
# Se sua função 'norm.criar_janelas' apenas faz o reshape, ok.
# Vou simular um reshape simples caso você não tenha a lib externa:
WINDOW_SIZE = 10
step = 1
segments = []
labels = []

for i in range(0, len(x_norm) - WINDOW_SIZE, step):
    xs = x_norm[i: i + WINDOW_SIZE]
    ys = y_encoded[i + WINDOW_SIZE - 1] # Label do final da janela
    segments.append(xs)
    labels.append(ys)

x_janelas = np.array(segments)
y_janelas = np.array(labels)

print(f"Shape: {x_janelas.shape}")

x_treino, x_teste, y_treino, y_teste = train_test_split(
    x_janelas, y_janelas, test_size=0.2, shuffle=True, stratify=y_janelas
)

num_classes = len(np.unique(y_janelas))
y_treino_ohe = to_categorical(y_treino, num_classes=num_classes)
y_teste_ohe = to_categorical(y_teste, num_classes=num_classes)

# Pesos
pesos = class_weight.compute_class_weight(
    class_weight='balanced', classes=np.unique(y_treino), y=y_treino
)
pesos_dict = dict(enumerate(pesos))

# Modelo
modelo = models.Sequential([
    Input(shape=(x_treino.shape[1], x_treino.shape[2])),
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.4),
    layers.LSTM(32, return_sequences=False),
    layers.Dropout(0.4),
    layers.Dense(32, activation='relu'),
    layers.Dense(num_classes, activation='softmax'),
])

modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

checkpoint = ModelCheckpoint('libras.h5', monitor='val_loss', save_best_only=True)
modelo.fit(x_treino, y_treino_ohe, validation_data=(x_teste, y_teste_ohe),
           epochs=120, batch_size=32, callbacks=[checkpoint], class_weight=pesos_dict)