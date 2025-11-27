import time
import csv
import serial
import os


porta = serial.Serial("COM8", 115200)
NOME_ARQUIVO = "dados/dados.csv"
arquivo_existe = os.path.exists(NOME_ARQUIVO) and os.path.getsize(NOME_ARQUIVO) > 0
arquivo = open(NOME_ARQUIVO, "a", newline='')
writer = csv.writer(arquivo)
header = ["sensor_1R", "sensor_2R", "sensor_3R", "sensor_4R", "sensor_5R",
       "sensor_1L", "sensor_3L", "sensor_4L", "sensor_5L","acel1",
         "giro1","acel2","giro2","gesto"]

if not arquivo_existe:
   writer.writerow(header)
   print(f"Cabeçalho escrito em '{NOME_ARQUIVO}'.")



gesto_atual = input("Gestor atual: ")
inicio = time.time()

try:
    while True:
        #Lê uma linha da serial
        linha = porta.readline().decode().strip()

        if not(linha):
            continue
        # Divide a string recebida em lista de números
        dados = list(map(float, linha.split(',')))

        # Se a leitura veio incompleta, ignora
        if len(dados) < 13:  # 12 sensores no total (6L + 6R)
            continue

        # Calcula o tempo desde o início (em ms)
        tempo_ms = int((time.time() - inicio) * 1000)



       # Monta a linha completa com os sensores + nome do gesto
        linha_csv = dados + [gesto_atual]

        # Escreve no arquivo
        writer.writerow(linha_csv)

#        # Mostra no terminal (opcional)
        print(linha_csv)


except KeyboardInterrupt:
    print("\nColeta finalizada.")
    porta.close()
    arquivo.close()

