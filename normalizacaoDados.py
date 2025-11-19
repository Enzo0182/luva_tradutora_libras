import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

class Normalizar:
    def __init__(self):
        self.means = None
        self.stds = None

    def fit(self, dados_treino):
        self.means = np.mean(dados_treino, axis=0)
        self.stds = np.std(dados_treino, axis=0)
        np.save('dados/means.npy', self.means)
        np.save('dados/stds.npy', self.stds)

    def transform(self, dados):
        if self.means is None or self.stds is None:
            try:
                self.means = np.load('dados/means.npy')
                self.stds = np.load('dados/stds.npy')
            except FileNotFoundError:
                print("Arquivo não encontrado")
        d = (dados - self.means) / (self.stds + 1e-8)
        return d.astype(np.float32)

    def fit_transform(self, dados):
        self.fit(dados)
        return self.transform(dados)

    @staticmethod
    def criar_janelas(dados, labels, window_size=10, passo=1):#label é igual aos gestos
        x, y = [], []
        for i in range(0, len(dados) - window_size, passo):
            x.append(dados[i:i + window_size])
            y.append(labels[i + window_size - 1])
        return np.array(x), np.array(y)