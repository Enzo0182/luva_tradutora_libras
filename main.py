from normalizacaoDados import Normalizar
import tensorflow as tf
import numpy as np
from collections import deque
import serial as srl
import pyttsx3
import threading


try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
except:
    print(f"Aviso: pyttsx3 não pode ser inicializado (verifique drivers de áudio).")
    engine = None

def falar(texto):
    try:
        engine.say(texto)
        engine.runAndWait()
    except RuntimeError:
        pass

modelo = tf.keras.models.load_model('libras.h5')
gestos = np.load('dados/gestos.npy', allow_pickle=True)
norm = Normalizar()
ultimo_gesto_valido = None

WINDOW_SIZE = 10
buffer = deque(maxlen=WINDOW_SIZE)
historico_previsoes = deque(maxlen= 5)

porta = srl.Serial('COM8', 115200)
colunas_usadas = [
        "sensor_1R","sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R",
        "sensor_1L", "sensor_3L", "sensor_4L","sensor_5L",
        "acel1","giro1", "acel2","giro2"
]
todas_colunas =  [
    'sensor_1R', 'sensor_2R', 'sensor_3R', 'sensor_4R','sensor_5R',
    'sensor_1L', 'sensor_2L', 'sensor_3L', 'sensor_4L', 'sensor_5L','acel1','giro1','acel2','giro2'
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
            janela_normalizada = janela

            previsao = modelo.predict(np.expand_dims(janela_normalizada, axis=0))[0]

            indice_gesto = np.argmax(previsao)
            gesto_previsto = gestos[indice_gesto]
            confianca = np.max(previsao)
            print(f'confianca: {confianca}\n {gesto_previsto}')
            if confianca > 0.70:
                historico_previsoes.append(gesto_previsto)
            else:
                historico_previsoes.append("Incerteza")

            if len(historico_previsoes) == historico_previsoes.maxlen:
                gesto_estavel = max(set(historico_previsoes), key=historico_previsoes.count)
                if (gesto_estavel != "Repouso" and
                    gesto_estavel != "Incerteza" and
                    gesto_estavel != ultimo_gesto_valido):

                    print(f"GESTO DETECTADO: {gesto_estavel} (Confiança: {confianca:.2f})")

                    t = threading.Thread(target=falar, args=(gesto_estavel,))
                    t.start()
                    ultimo_gesto_valido = gesto_estavel
                elif gesto_estavel == "Repouso":
                    ultimo_gesto_valido = None
                    print("...", end='\r')


    except KeyboardInterrupt:
        print(f"\nPrograma encerrado pelo usuário.")
        break

    except Exception as e:
        print(f"Erro: {e}")

