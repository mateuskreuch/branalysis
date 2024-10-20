from .db.model import BaseVoto
from .db.utils import get_parlamentar_id
from .plenario import Plenario
from collections import defaultdict
from typing import Callable
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

TransformadorVoto = Callable[[Plenario, BaseVoto], float]
Imputador = Callable[[Plenario, list[BaseVoto], TransformadorVoto], dict[str, float]]

class MatrizPolitica:
   def __init__(
      self,
      plenario: Plenario,
      imputador: Imputador = imputador_vota_com_partido,
      transformador_voto: TransformadorVoto = transformador_sim_nao
   ):
      self._plenario = plenario
      self._transformador_voto = transformador_voto
      self._imputador = imputador
      self._parlamentares = self._plenario.parlamentares()

   def de_parlamentares(self):
      return self.de_votacoes().T

   def de_votacoes(self):
      parlamentares_index = self._parlamentares_to_index()
      parlamentares_len = len(self._parlamentares)
      matrix = []

      for votacao in self._plenario.votacoes().iterator():
         votos = votacao.votos
         imputacao_votos = self._imputador(self, votos)

         matrix.append([0] * parlamentares_len)

         for voto in votos:
            parlamentar_id = get_parlamentar_id(voto)
            value = self._transformador_voto(self, voto)
            matrix[-1][parlamentares_index[parlamentar_id]] = (
               value if value is not None else imputacao_votos[voto.partido])

      return np.array(matrix)

   def plenario(self):
      return self._plenario

   def imputador(self):
      return self._imputador

   def transformador_voto(self):
      return self._transformador_voto

   @functools.cache
   def _parlamentares_to_index(self):
      return { x.id: i for i, x in enumerate(self._parlamentares) }