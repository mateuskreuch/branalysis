from .db import camara, senado
from .db.model import *
from .db.utils import get_parlamentar_id
from collections import defaultdict
from datetime import date, timedelta
from types import MappingProxyType
from typing import Iterable
import functools

ONE_DAY = timedelta(days=1)
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
   _PARLAMENTAR_CLS: Parlamentar
   _VOTACAO_CLS: Votacao
   _VOTO_CLS: Voto

   def __init__(self, periodo_comeco, periodo_fim = None):
      periodo_fim = periodo_fim or periodo_comeco

      periodo_comeco = cast_periodo(periodo_comeco, end=False)
      periodo_fim = cast_periodo(periodo_fim, end=True)

      self._periodo = (periodo_comeco, periodo_fim)

   def parlamentares(self) -> list[Parlamentar]:
      return list(p.set_plenario(self) for p in self._PARLAMENTAR_CLS
                                                   .select()
                                                   .join(self._VOTO_CLS)
                                                   .join(self._VOTACAO_CLS)
                                                   .where(self._VOTACAO_CLS.data.between(*self._periodo))
                                                   .group_by(self._PARLAMENTAR_CLS)
                                                   .order_by(self._PARLAMENTAR_CLS.nome))

   @functools.cache
   def tipos_voto(self) -> tuple[str]:
      return tuple(v.voto for v in self._votos(self._VOTO_CLS.voto)
                                       .order_by(self._VOTO_CLS.voto)
                                       .distinct())

   @functools.cache
   def tipos_votacao(self) -> tuple[str]:
      return tuple(v.tipo for v in self._votacoes(self._VOTACAO_CLS.tipo)
                                       .order_by(self._VOTACAO_CLS.tipo)
                                       .distinct())

   @functools.cache
   def partidos(self) -> tuple[str]:
      return tuple(v.partido for v in self._votos(self._VOTO_CLS.partido)
                                          .order_by(self._VOTO_CLS.partido)
                                          .distinct())

   @functools.cache
   def ufs(self) -> tuple[str]:
      return tuple(v.uf for v in self._votos(self._VOTO_CLS.uf)
                                    .order_by(self._VOTO_CLS.uf)
                                    .distinct())

   def macroregioes(self) -> tuple[str]:
      return MACROREGIOES

   def parlamentares_por_partido(self) -> dict[str, list[Parlamentar]]:
      """
      Retorna os parlamentares agrupados por partido. Parlamentares podem
      estar associados a mais de um partido, devido a mudanças partidárias
      durante o período escolhido.
      """
      votos = (self._votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.partido)
                  .order_by(self._VOTO_CLS.partido)
                  .distinct()
                  .iterator())

      result = {}

      for voto in votos:
         result.setdefault(voto.partido, []).append(voto.parlamentar.set_plenario(self))

      return result

   def parlamentares_por_uf(self) -> dict[str, list[Parlamentar]]:
      """
      Retorna os parlamentares agrupados por UF. Parlamentares podem
      estar associados a mais de uma UF, devido a mudanças de domicílio
      durante o período escolhido.
      """
      votos = (self._votos(self._VOTO_CLS.parlamentar, self._VOTO_CLS.uf)
                  .order_by(self._VOTO_CLS.uf)
                  .distinct()
                  .iterator())

      result = {}

      for voto in votos:
         result.setdefault(voto.uf, []).append(voto.parlamentar.set_plenario(self))

      return result

   @functools.cache
   def presenca_por_parlamentar(self) -> dict[str, float]:
      """
      Retorna a presença de cada parlamentar no período escolhido. Não é 100% fiel.
      """
      result = defaultdict(int)
      total_votacoes = self._votacoes().count()
      votos = self._votos(self._VOTO_CLS.parlamentar).iterator()

      for voto in votos:
         result[get_parlamentar_id(voto)] += 1

      return MappingProxyType({k: v / total_votacoes for k, v in result.items()})

   @functools.cache
   def ufs_por_parlamentar(self, com_data=False) -> dict[str, tuple[str]] | dict[str, tuple[tuple[str, date, date]]]:
      """
      Retorna as UFs de cada parlamentar no período escolhido. Como
      parlamentares podem pertencer a mais de uma UF durante o período escolhido,
      cada parlamentar tem suas UFs representadas como uma tupla, organizados em
      ordem cronológica. Isto é, um parlamentar com a tupla `("SC", "RS", "SC")`
      significa que ele se candidatou em Santa Catarina, depois no Rio Grande do
      Sul e depois voltou para Santa Catarina.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("SC", date(2022, 5, 2), date(2022, 6, 3)), ("RS", date(2022, 6, 4), date(2022, 7, 5)), ("SC", date(2022, 7, 6), date(2022, 8, 7)))`
      """
      votos = (self._votos(self._VOTO_CLS.parlamentar, self._VOTACAO_CLS.data, self._VOTO_CLS.uf)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      return self._aggregate_votos(com_data, votos, lambda voto: voto.uf)

   @functools.cache
   def macroregioes_por_parlamentar(self, com_data=False) -> dict[str, tuple[str]] | dict[str, tuple[tuple[str, date, date]]]:
      """
      Retorna as macrorregiões de cada parlamentar no período escolhido. Como
      parlamentares podem pertencer a mais de uma macrorregião durante o período
      escolhido, cada parlamentar tem suas macrorregiões representadas como uma
      tupla, organizados em ordem cronológica. Isto é, um parlamentar com a
      tupla `("SUL", "SUDESTE", "SUL")` significa que ele se candidatou no Sul,
      depois no Sudeste e depois voltou para o Sul.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("SUL", date(2022, 5, 2), date(2022, 6, 3)), ("SUDESTE", date(2022, 6, 4), date(2022, 7, 5)), ("SUL", date(2022, 7, 6), date(2022, 8, 7))`
      """
      votos = (self._votos(self._VOTO_CLS.parlamentar, self._VOTACAO_CLS.data, self._VOTO_CLS.uf)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      return self._aggregate_votos(com_data, votos, lambda voto: MACROREGIOES_POR_UF[voto.uf])

   @functools.cache
   def partidos_por_parlamentar(self, com_data=False) -> dict[str, tuple[str]] | dict[str, tuple[tuple[str, date, date]]]:
      """
      Retorna os partidos de cada parlamentar no período escolhido. Como
      parlamentares podem pertencer a mais de um partido durante o período
      escolhido, cada parlamentar tem seus partidos representados como uma tupla,
      organizados em ordem cronológica. Isto é, um parlamentar com a tupla
      `("PT", "PSDB", "PT")` significa que ele se candidatou pelo PT, depois
      pelo PSDB e depois voltou para o PT.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("PT", date(2022, 5, 2), date(2022, 6, 3)), ("PSDB", date(2022, 6, 4), date(2022, 7, 5)), ("PT", date(2022, 7, 6), date(2022, 8, 7))`
      """
      votos = (self._votos(self._VOTO_CLS.parlamentar, self._VOTACAO_CLS.data, self._VOTO_CLS.partido)
                  .order_by(self._VOTACAO_CLS.data)
                  .iterator())

      return self._aggregate_votos(com_data, votos, lambda voto: voto.partido)

   def votacoes(self) -> list[Votacao]:
      return list(self._votacoes())

   def votos(self) -> list[Voto]:
      return list(self._votos())

   def _votacoes(self, *fields) -> Iterable[Votacao]:
      return (self._VOTACAO_CLS
                  .select(*fields)
                  .where(self._VOTACAO_CLS.data.between(*self._periodo))
                  .order_by(self._VOTACAO_CLS.data))

   def _votos(self, *fields) -> Iterable[Voto]:
      return (self._VOTO_CLS
               .select(*fields)
               .join(self._VOTACAO_CLS)
               .where(self._VOTACAO_CLS.data.between(*self._periodo))
               .order_by(self._VOTO_CLS.id))

   def periodo(self) -> tuple[date]:
      return (date.fromisoformat(self._periodo[0]), date.fromisoformat(self._periodo[1]))

   def _aggregate_votos(self, com_data, votos: Iterable[Voto], key):
      if com_data:
         return self._aggregate_votos_com_data(votos, key)

      else:
         return self._aggregate_votos_sem_data(votos, key)

   def _aggregate_votos_sem_data(self, votos: Iterable[Voto], key):
      result = {}

      for voto in votos:
         parlamentar_id = get_parlamentar_id(voto)
         x = key(voto)

         if parlamentar_id not in result:
            result[parlamentar_id] = [x]

         elif result[parlamentar_id][-1] != x:
            result[parlamentar_id].append(x)

      return MappingProxyType({k: tuple(v) for k, v in result.items()})

   def _aggregate_votos_com_data(self, votos: Iterable[Voto], key):
      data_inicial, data_final = self.periodo()
      result = {}

      for voto in votos:
         parlamentar_id = get_parlamentar_id(voto)
         x = key(voto)

         if parlamentar_id not in result:
            result[parlamentar_id] = [[x, data_inicial, None]]

         elif result[parlamentar_id][-1][0] != x:
            result[parlamentar_id][-1][2] = voto.votacao.data - ONE_DAY
            result[parlamentar_id].append([x, voto.votacao.data, None])

      for parlamentar_id in result:
         result[parlamentar_id][-1][2] = data_final
         result[parlamentar_id] = tuple((x, inicio, fim) for x, inicio, fim in result[parlamentar_id])

      return MappingProxyType(result)

class Camara(Plenario):
   _PARLAMENTAR_CLS = Camara_Parlamentar
   _VOTACAO_CLS = Camara_Votacao
   _VOTO_CLS = Camara_Voto

   def __init__(self, periodo_comeco, periodo_fim = None):
      super().__init__(periodo_comeco, periodo_fim)

      data_inicial, data_final = self.periodo()

      for ano in range(data_inicial.year, data_final.year + 1):
         camara.cache(ano)

class Senado(Plenario):
   _PARLAMENTAR_CLS = Senado_Parlamentar
   _VOTACAO_CLS = Senado_Votacao
   _VOTO_CLS = Senado_Voto

   def __init__(self, periodo_comeco, periodo_fim = None):
      super().__init__(periodo_comeco, periodo_fim)

      data_inicial, data_final = self.periodo()

      for ano in range(data_inicial.year, data_final.year + 1):
         senado.cache(ano)