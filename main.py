from normalizacaoDados import Normalizar
import tensorflow as tf
import numpy as np
from collections import deque
import serial as srl
import pyttsx3

modelo = tf.keras.models.load_model('libras.h5')
gestos = np.load('dados/gestos.npy', allow_pickle=True)
norm = Normalizar()

WINDOW_SIZE = 10
buffer = deque(maxlen=WINDOW_SIZE)
historico_previsoes = deque(maxlen= 5)

porta = srl.Serial('COM8', 115200)
colunas_usadas = [
    "sensor_1L", "sensor_2L", "sensor_3L", "sensor_4L","sensor_5L",
        "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R","acel1","giro1","acel2","giro2"
]
todas_colunas =  [
    'sensor_1L', 'sensor_2L', 'sensor_3L', 'sensor_4L', 'sensor_5L',
    'sensor_1R', 'sensor_2R', 'sensor_3R', 'sensor_4R','sensor_5R','acel1','giro1','acel2','giro2'
]

while True:
    try:
        linha = porta.readline().decode().strip()
        print(linha)
        dados = list(map(float,linha.split(',')))
        print(dados)
        if len(dados) < 14:
            continue
        dados_filtrados = []
        dados_dicionario = dict(zip(todas_colunas, dados))
        for coluna in colunas_usadas:
            dados_filtrados.append(dados_dicionario[coluna])
        buffer.append(dados_filtrados)
        print(dados_filtrados)
        if len(buffer) == WINDOW_SIZE:
            janela = np.array(buffer)
            janela_normalizada = norm.transform(janela)

            previsao = modelo.predict(np.expand_dims(janela_normalizada, axis=0))[0]

            indice_gesto = np.argmax(previsao)
            gesto_previsto = gestos[indice_gesto]
            historico_previsoes.append(gesto_previsto)
            gestos_final = max(set(historico_previsoes), key=historico_previsoes.count)
            print(f'{gestos_final}')


    except KeyboardInterrupt:
        print(f"\nPrograma encerrado pelo usuário.")
        break

    except Exception as e:
        print(f"Erro: {e}")
