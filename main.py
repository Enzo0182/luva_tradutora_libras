import tensorflow as tf
import numpy as np
import joblib
from collections import deque
import serial as srl
import pyttsx3
import threading
from scipy.signal import butter, filtfilt

# --- CONFIGURAÇÃO IGUAL AO TREINO ---
DELAY_NO_ARDUINO = 30
FS_REAL = 1000 / DELAY_NO_ARDUINO
CUTOFF_FILTRO = 3.0


def aplicar_filtro_janela(data):
    try:
        nyq = 0.5 * FS_REAL
        normal_cutoff = CUTOFF_FILTRO / nyq
        if normal_cutoff >= 1: normal_cutoff = 0.99
        b, a = butter(4, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data, axis=0)
        return y
    except:
        return data


def falar(texto):
    """
    Cria uma nova instância do motor de voz para cada fala.
    Isso evita o travamento do pyttsx3 em threads.
    """
    try:
        # Inicializa um NOVO motor apenas para essa fala
        engine_local = pyttsx3.init()

        # Configurações (pode ajustar a velocidade se quiser)
        engine_local.setProperty('rate', 150)

        # Fala
        engine_local.say(texto)
        engine_local.runAndWait()

        # Importante: Para o loop do motor
        engine_local.stop()
        del engine_local  # Limpa da memória

    except Exception as e:
        print(f"Erro ao tentar falar: {e}")


# --- CARREGAR MODELO E SCALER ---
print("Carregando modelo e normalizador...")
modelo = tf.keras.models.load_model('libras.h5')
gestos = np.load('dados/gestos.npy', allow_pickle=True)
scaler = joblib.load('dados/scaler.pkl')  # <--- O SEGREDO ESTÁ AQUI

ultimo_gesto_valido = None
WINDOW_SIZE = 10
buffer = deque(maxlen=WINDOW_SIZE)
historico_previsoes = deque(maxlen=15)

try:
    porta = srl.Serial('COM8', 115200)
except:
    print("Erro COM8")

# Mesma ordem do treino!
colunas_modelo = [
    "sensor_1L", "sensor_3L", "sensor_4L", "sensor_5L",
    "sensor_1R", "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R",
    "acel1", "giro1", "acel2", "giro2",
    "acel_total"
]

# Mapeamento Arduino -> Colunas
todas_colunas_arduino = [
    'sensor_1R', 'sensor_2R', 'sensor_3R', 'sensor_4R', 'sensor_5R',
    'sensor_1L', 'sensor_3L', 'sensor_4L', 'sensor_5L',
    'acel1', 'giro1', 'acel2', 'giro2'
]

print("Iniciando...")

while True:
    try:
        if not porta.is_open: break
        linha = porta.readline().decode().strip()
        if not linha: continue
        try:
            dados_brutos = list(map(float, linha.split(',')))
        except:
            continue

        if len(dados_brutos) < 13: continue

        # Dicionário para organizar
        d = dict(zip(todas_colunas_arduino, dados_brutos))

        # Calcular Magnitude
        acel_total = np.sqrt(d['acel1'] ** 2 + d['giro1'] ** 2 + d['acel2'] ** 2 + d['giro2'] ** 2)
        d['acel_total'] = acel_total

        # Organizar na ordem certa
        linha_processada = [d[c] for c in colunas_modelo]
        buffer.append(linha_processada)

        if len(buffer) == WINDOW_SIZE:
            janela_raw = np.array(buffer)

            # 1. Filtro
            janela_filtrada = aplicar_filtro_janela(janela_raw)

            # 2. DETECÇÃO DE MOVIMENTO (Threshold)
            # Se o desvio padrão dos sensores for muito baixo, a mão está parada.
            # Calculamos a variação na coluna de Aceleração Total
            variacao = np.std(janela_filtrada[:, -1])  # Coluna acel_total

            # Se variar menos que 0.5, força Repouso (Ajuste esse 0.5 conforme necessidade)
            if variacao < 0.3:
                gesto_previsto = "Repouso"
                confianca = 1.0
                print(f"Estável (Var: {variacao:.2f}) -> Repouso Forçado")
            else:
                # 3. Normalizar (CRUCIAL: Usar o scaler carregado)
                janela_norm = scaler.transform(janela_filtrada)

                # 4. Prever
                previsao = modelo.predict(np.expand_dims(janela_norm, axis=0), verbose=0)[0]
                indice = np.argmax(previsao)
                gesto_previsto = gestos[indice]
                confianca = np.max(previsao)
                #print(f"Gesto: {gesto_previsto} | Conf: {confianca:.2f} | Var: {variacao:.2f}")

            # Lógica de Falar
            if confianca > 0.85:
                historico_previsoes.append(gesto_previsto)
            else:
                historico_previsoes.append("Incerteza")

            import time  # <--- Adicione no topo

            # ... (resto das variáveis)
            ultimo_tempo_fala = 0
            COOLDOWN_SEGUNDOS = 1.0  # Tempo que ele espera para ouvir o próximo gesto

            # ... (dentro do loop while) ...

            if len(historico_previsoes) == historico_previsoes.maxlen:
                estavel = max(set(historico_previsoes), key=historico_previsoes.count)

                # Verifica o tempo atual
                tempo_atual = time.time()

                if (estavel != "Repouso" and
                        estavel != "Incerteza" and
                        estavel != ultimo_gesto_valido):

                    # SÓ FALA SE PASSOU O TEMPO DE COOLDOWN
                    if (tempo_atual - ultimo_tempo_fala) > COOLDOWN_SEGUNDOS:
                        print(f">>> FALANDO: {estavel}")
                        t = threading.Thread(target=falar, args=(estavel,))
                        t.start()

                        ultimo_gesto_valido = estavel
                        ultimo_tempo_fala = tempo_atual  # Reseta o cronômetro

                        # Limpa o histórico para não misturar com o próximo gesto
                        historico_previsoes.clear()
                    else:
                        print(f"Ignorando {estavel} (Cooldown...)")

                elif estavel == "Repouso":
                    ultimo_gesto_valido = None

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Erro: {e}")