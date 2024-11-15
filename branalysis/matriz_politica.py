from .db.model import Parlamentar, Votacao, Voto
from .db.utils import get_parlamentar_id
from collections import defaultdict
from statistics import mean
from typing import Callable, Iterable
import numpy as np, functools

def transformador_sim_nao(matriz_politica: 'MatrizPolitica', voto: Voto) -> float:
   match voto.voto:
      case 'SIM': return 1
      case 'NÃO': return -1
      case 'ABSTENÇÃO', 'OBSTRUÇÃO', 'P-NRV': return 0

def imputador_zero(matriz_politica: 'MatrizPolitica', votacao: Votacao, votos: list[Voto], votos_numericos: list[float]):
   return [x if x is not None else 0 for x in votos_numericos]

def imputador_vota_com_partido(matriz_politica: 'MatrizPolitica', votacao: Votacao, votos: list[Voto], votos_numericos: list[float]):
   data = votacao.data
   direcao_partidaria = defaultdict(int)

   for i, voto in enumerate(votos):
      if votos_numericos[i] is not None:
         direcao_partidaria.setdefault(voto.partido, []).append(votos_numericos[i])

   for k in direcao_partidaria:
      direcao_partidaria[k] = mean(direcao_partidaria[k])

   for i, parlamentar in enumerate(matriz_politica.parlamentares()):
      if votos_numericos[i] is None:
         votos_numericos[i] = direcao_partidaria[parlamentar.partido(data)]

   return votos_numericos

TransformadorVoto = Callable[['MatrizPolitica', Voto], float]
Imputador = Callable[['MatrizPolitica', Votacao, list[Voto], list[float]], list[float]]

class MatrizPolitica:
   def __init__(
      self,
      parlamentares: list[Parlamentar],
      votacoes: Iterable[Votacao],
      imputador: Imputador = imputador_vota_com_partido,
      transformador_voto: TransformadorVoto = transformador_sim_nao
   ):
      self._votacoes = votacoes
      self._parlamentares = parlamentares
      self._transformador_voto = transformador_voto
      self._imputador = imputador

   def de_parlamentares(self):
      return self.de_votacoes().T

   def de_votacoes(self):
      parlamentares_index = self._parlamentares_to_index()
      parlamentares_len = len(self._parlamentares)
      matrix = []

      for votacao in self._votacoes:
         votos = [None] * parlamentares_len
         matrix.append([None] * parlamentares_len)

         for voto in votacao.votos:
            parlamentar_id = get_parlamentar_id(voto)

            if parlamentar_id in parlamentares_index:
               votos[parlamentares_index[parlamentar_id]] = voto
               matrix[-1][parlamentares_index[parlamentar_id]] = self._transformador_voto(self, voto)

         matrix[-1] = self._imputador(self, votacao, votos, matrix[-1])

      return np.array(matrix)

   def de_similaridade(self, epsilon=0.01):
      return 1 - self.de_dissimilaridade(epsilon)

   def de_dissimilaridade(self, epsilon=0.01):
      votos = self.de_parlamentares()
      matrix = np.zeros((votos.shape[0], votos.shape[0]))

      for pa in range(votos.shape[0]):
         for pb in range(pa + 1, votos.shape[0]):
            dissimilaridade = 0

            for i in range(votos.shape[1]):
               if abs(votos[pa, i] - votos[pb, i]) > epsilon:
                  dissimilaridade += 1

            dissimilaridade /= votos.shape[1]

            matrix[pa, pb] = dissimilaridade
            matrix[pb, pa] = dissimilaridade

      return matrix

   def votacoes(self):
      return self._votacoes

   def parlamentares(self):
      return self._parlamentares

   def imputador(self):
      return self._imputador

   def transformador_voto(self):
      return self._transformador_voto

   @functools.cache
   def _parlamentares_to_index(self):
      return { x.id: i for i, x in enumerate(self._parlamentares) }