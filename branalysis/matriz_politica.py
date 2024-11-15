from .db.model import Parlamentar, Votacao, Voto
from .db.utils import get_parlamentar_id
from .plenario import Plenario
from collections import defaultdict
from typing import Callable, Iterable
import numpy as np, functools, statistics

def transformador_sim_nao(matriz_politica, voto):
   if voto.voto == 'SIM':
      return 1

   elif voto.voto == 'NÃO':
      return -1

def imputador_zero(matriz_politica, votos):
   return defaultdict(int)

def imputador_vota_com_partido(matriz_politica, votos):
   transformador = matriz_politica.transformador_voto()
   direcao_partidaria = {}

   for voto in votos:
      value = transformador(matriz_politica, voto)

      direcao_partidaria.setdefault(voto.partido, [])

      if value is not None:
         direcao_partidaria[voto.partido].append(value)

   return { k: statistics.mean(v) if len(v) > 0 else 0 for k, v in direcao_partidaria.items() }

TransformadorVoto = Callable[[Plenario, Voto], float]
Imputador = Callable[[Plenario, list[Voto], TransformadorVoto], dict[str, float]]

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
         votos = votacao.votos
         imputacao_votos = self._imputador(self, votos)

         matrix.append([0] * parlamentares_len)

         for voto in votos:
            parlamentar_id = get_parlamentar_id(voto)

            if parlamentar_id in parlamentares_index:
               value = self._transformador_voto(self, voto)
               matrix[-1][parlamentares_index[parlamentar_id]] = (
                  value if value is not None else imputacao_votos[voto.partido])

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