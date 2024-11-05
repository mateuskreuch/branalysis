from .db import camara, senado
from .db.model import *
from .db.utils import get_parlamentar_id
from collections import defaultdict
from datetime import date
from types import MappingProxyType
from typing import Iterable
import functools

MACROREGIOES = ('NORTE', 'NORDESTE', 'CENTRO-OESTE', 'SUDESTE', 'SUL')
MACROREGIOES_POR_UF = ({ uf : MACROREGIOES[0] for uf in ('AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO') }
                    |  { uf : MACROREGIOES[1] for uf in ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') }
                    |  { uf : MACROREGIOES[2] for uf in ('DF', 'GO', 'MS', 'MT') }
                    |  { uf : MACROREGIOES[3] for uf in ('ES', 'MG', 'RJ', 'SP') }
                    |  { uf : MACROREGIOES[4] for uf in ('PR', 'RS', 'SC') })

def cast_periodo(periodo, end=False):
   if isinstance(periodo, date):
      return periodo.strftime('%Y-%m-%d')

   periodo = str(periodo)

   if len(periodo) == 4:
      periodo += '-01-01' if not end else '-12-31'

   return periodo

class Plenario:
   _PARLAMENTAR_CLS: BaseParlamentar
   _VOTACAO_CLS: BaseVotacao
   _VOTO_CLS: BaseVoto

   def __init__(self, periodo_comeco, periodo_fim = None):
      periodo_fim = periodo_fim or periodo_comeco

      periodo_comeco = cast_periodo(periodo_comeco, end=False)
      periodo_fim = cast_periodo(periodo_fim, end=True)

      self._periodo = (periodo_comeco, periodo_fim)

   def parlamentares(self, *fields) -> list[BaseParlamentar]:
      return list(p.set_plenario(self) for p in self._PARLAMENTAR_CLS
                                                   .select(*fields)
                                                   .join(self._VOTO_CLS)
                                                   .join(self._VOTACAO_CLS)
                                                   .where(self._VOTACAO_CLS.data.between(*self._periodo))
                                                   .group_by(self._PARLAMENTAR_CLS)
                                                   .order_by(self._PARLAMENTAR_CLS.nome))

   @functools.cache
   def partidos(self) -> tuple[str]:
      return tuple(v.partido for v in self.votos(self._VOTO_CLS.partido)
                                             .order_by(self._VOTO_CLS.partido)
                                             .distinct())

   @functools.cache
   def ufs(self) -> tuple[str]:
      return tuple(v.uf for v in self.votos(self._VOTO_CLS.uf)
                                             .order_by(self._VOTO_CLS.uf)
                                             .distinct())

   def macroregioes(self) -> tuple[str]:
      return MACROREGIOES

   def parlamentares_por_partido(self) -> dict[str, list[BaseParlamentar]]:
      votos = (self.votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.partido)
                  .order_by(self._VOTO_CLS.partido)
                  .distinct()
                  .iterator())

      result = {}

      for voto in votos:
         result.setdefault(voto.partido, []).append(voto.parlamentar.set_plenario(self))

      return result

   def parlamentares_por_uf(self) -> dict[str, list[BaseParlamentar]]:
      votos = (self.votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.uf)
                  .order_by(self._VOTO_CLS.uf)
                  .distinct()
                  .iterator())

      result = {}

      for voto in votos:
         result.setdefault(voto.uf, []).append(voto.parlamentar.set_plenario(self))

      return result

   @functools.cache
   def presenca_por_parlamentar(self) -> dict[str, float]:
      result = defaultdict(int)
      total_votacoes = self.votacoes().count()
      votos = self.votos(self._VOTO_CLS.parlamentar).iterator()

      for voto in votos:
         result[get_parlamentar_id(voto)] += 1

      return MappingProxyType({k: v / total_votacoes for k, v in result.items()})

   @functools.cache
   def ufs_por_parlamentar(self) -> dict[str, tuple[str]]:
      result = {}
      votos = (self.votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.uf)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      for voto in votos:
         parlamentar_id = get_parlamentar_id(voto)

         if parlamentar_id not in result:
            result[parlamentar_id] = [voto.uf]

         elif result[parlamentar_id][-1] != voto.uf:
            result[parlamentar_id].append(voto.uf)

      return MappingProxyType({k: tuple(v) for k, v in result.items()})

   @functools.cache
   def macroregioes_por_parlamentar(self) -> dict[str, tuple[str]]:
      result = {}
      votos = (self.votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.uf)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      for voto in votos:
         parlamentar_id = get_parlamentar_id(voto)
         macrorregiao = MACROREGIOES_POR_UF[voto.uf]

         if parlamentar_id not in result:
            result[parlamentar_id] = [macrorregiao]

         elif result[parlamentar_id][-1] != macrorregiao:
            result[parlamentar_id].append(macrorregiao)

      return MappingProxyType({k: tuple(v) for k, v in result.items()})

   @functools.cache
   def partidos_por_parlamentar(self) -> dict[str, tuple[str]]:
      result = {}
      votos = (self.votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.partido)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      for voto in votos:
         parlamentar_id = get_parlamentar_id(voto)

         if parlamentar_id not in result:
            result[parlamentar_id] = [voto.partido]

         elif result[parlamentar_id][-1] != voto.partido:
            result[parlamentar_id].append(voto.partido)

      return MappingProxyType({k: tuple(v) for k, v in result.items()})

   def votacoes(self, *fields) -> Iterable[BaseVotacao]:
      return (self._VOTACAO_CLS
                  .select(*fields)
                  .where(self._VOTACAO_CLS.data.between(*self._periodo))
                  .order_by(self._VOTACAO_CLS.id))

   def votos(self, *fields) -> Iterable[BaseVoto]:
      return (self._VOTO_CLS
               .select(*fields)
               .join(self._VOTACAO_CLS)
               .where(self._VOTACAO_CLS.data.between(*self._periodo))
               .order_by(self._VOTO_CLS.votacao))

   def periodo(self) -> tuple[int]:
      return self._periodo

class Camara(Plenario):
   _PARLAMENTAR_CLS = Camara_Parlamentar
   _VOTACAO_CLS = Camara_Votacao
   _VOTO_CLS = Camara_Voto

   def __init__(self, periodo_comeco, periodo_fim = None):
      super().__init__(periodo_comeco, periodo_fim)

      data_comeco, data_fim = self.periodo()
      ano_comeco = int(data_comeco[:4])
      ano_fim = int(data_fim[:4])

      for ano in range(ano_comeco, ano_fim + 1):
         camara.cache(ano)

class Senado(Plenario):
   _PARLAMENTAR_CLS = Senado_Parlamentar
   _VOTACAO_CLS = Senado_Votacao
   _VOTO_CLS = Senado_Voto

   def __init__(self, periodo_comeco, periodo_fim = None):
      super().__init__(periodo_comeco, periodo_fim)

      data_comeco, data_fim = self.periodo()
      ano_comeco = int(data_comeco[:4])
      ano_fim = int(data_fim[:4])

      for ano in range(ano_comeco, ano_fim + 1):
         senado.cache(ano)