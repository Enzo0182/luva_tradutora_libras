from normalizacaoDados import Normalizar
import tensorflow as tf
import numpy as np
from collections import deque
import serial as srl

modelo = tf.keras.models.load_model('libras.h5')
gestos = np.load('gestos.npy', allow_pickle=True)
norm = Normalizar('dados/dados.csv')

WINDOW_SIZE = 100
buffer = deque(maxlen=WINDOW_SIZE)

porta = srl.Serial('COM3', 115200)

while True:
    linha = porta.readline().decode().strip()
    dados = list(map(float,linha.split(',')))
    buffer.append(dados)
    if len(buffer) == WINDOW_SIZE:
        janela = np.array(buffer)
        janela_normalizada = norm.pre_processar(janela)
        previsao = modelo.predict(np.expand_dims(janela_normalizada, axis=0))[0]
        gesto_previsto = gestos[np.argmax(previsao)]
        confianca = float(np.max(gesto_previsto))
        print(f"Gesto detectado: {gesto_previsto} (confiança: {confianca:.2f})")
