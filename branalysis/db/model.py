
from datetime import date
from peewee import *
from typing import TYPE_CHECKING
import functools

if TYPE_CHECKING:
   from plenario import Plenario

DB = SqliteDatabase('branalysis.db')
SENADO_API = 'https://legis.senado.leg.br/dadosabertos'
CAMARA_API = 'https://dadosabertos.camara.leg.br/api/v2'
CAMARA_FILES_API = 'https://dadosabertos.camara.leg.br/arquivos'

def search_by_date(info, data):
   for x, inicio, fim in info:
      if inicio <= data <= fim:
         return x

class BaseModel(Model):
   class Meta:
      database = DB

class Parlamentar(BaseModel):
   id = TextField(primary_key=True)
   nome = TextField()
   sexo = TextField()
   data_nascimento = DateField(null=True)

   def set_plenario(self, plenario: 'Plenario'):
      self._plenario = plenario

      return self

   @functools.cache
   def partido(self, data: date) -> str:
      """
      Retorna o partido do parlamentar na data especificada.
      """
      return search_by_date(self.partidos(com_data=True), data)

   def partidos(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      """
      Retorna os partidos do parlamentar no período do Plenario associado. Como
      parlamentares podem pertencer a mais de um partido durante o período
      escolhido, seus partidos são representados como uma tupla, organizados em
      ordem cronológica. Isto é, um parlamentar com a tupla
      `("PT", "PSDB", "PT")` significa que ele se candidatou pelo PT, depois
      pelo PSDB e depois voltou para o PT.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("PT", date(2022, 5, 2), date(2022, 6, 3)), ("PSDB", date(2022, 6, 4), date(2022, 7, 5)), ("PT", date(2022, 7, 6), date(2022, 8, 7))`

      """
      return self._plenario.partidos_por_parlamentar(com_data)[self.id]

   @functools.cache
   def uf(self, data: date) -> str:
      """
      Retorna a UF do parlamentar na data especificada.
      """
      return search_by_date(self.ufs(com_data=True), data)

   def ufs(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      """
      Retorna as UFs do parlamentar no período do Plenario associado. Como
      parlamentares podem pertencer a mais de uma UF durante o período escolhido,
      suas UFs são representadas como uma tupla, organizados em ordem
      cronológica. Isto é, um parlamentar com a tupla `("SC", "RS", "SC")`
      significa que ele se candidatou em Santa Catarina, depois no Rio Grande do
      Sul e depois voltou para Santa Catarina.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("SC", date(2022, 5, 2), date(2022, 6, 3)), ("RS", date(2022, 6, 4), date(2022, 7, 5)), ("SC", date(2022, 7, 6), date(2022, 8, 7)))`
      """
      return self._plenario.ufs_por_parlamentar(com_data)[self.id]

   @functools.cache
   def macroregiao(self, data: date) -> str:
      """
      Retorna a macroregião do parlamentar na data especificada.
      """
      return search_by_date(self.macroregioes(com_data=True), data)

   def macroregioes(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      """
      Retorna as macroregiões do parlamentar no período do Plenario associado.
      Como parlamentares podem pertencer a mais de uma macroregião durante o
      período escolhido, suas macroregiões são representadas como uma tupla,
      organizados em ordem cronológica. Isto é, um parlamentar com a
      tupla `("SUL", "SUDESTE", "SUL")` significa que ele se candidatou no Sul,
      depois no Sudeste e depois voltou para o Sul.

      Também é possível passar o argumento `com_data=True` para obter a data de
      início e fim associadas:

      `(("SUL", date(2022, 5, 2), date(2022, 6, 3)), ("SUDESTE", date(2022, 6, 4), date(2022, 7, 5)), ("SUL", date(2022, 7, 6), date(2022, 8, 7))`
      """
      return self._plenario.macroregioes_por_parlamentar(com_data)[self.id]

   def presenca(self) -> float:
      """
      Retorna a presença do parlamentar no período do Plenario associado. Não é 100% fiel.
      """
      return self._plenario.presenca_por_parlamentar()[self.id]

class Voto(BaseModel):
   votacao: ForeignKeyField
   parlamentar: ForeignKeyField

   partido = TextField()
   uf = TextField()
   voto = TextField()

class Votacao(BaseModel):
   id = TextField(primary_key=True)
   data = DateField()
   tipo = TextField()
   numero = IntegerField()
   ano = IntegerField()

class Camara_Votacao(Votacao):
   pass

class Camara_Parlamentar(Parlamentar):
   pass

class Camara_Voto(Voto):
   votacao = ForeignKeyField(Camara_Votacao, backref='votos')
   parlamentar = ForeignKeyField(Camara_Parlamentar, backref='votos')

# Used only a facilitator cache, fields are duplicated to Camara_Votacao
class Camara_Proposicao(BaseModel):
   id = TextField(primary_key=True)
   tipo = TextField()
   numero = IntegerField()
   ano = IntegerField()

class Senado_Votacao(Votacao):
   pass

class Senado_Parlamentar(Parlamentar):
   pass

class Senado_Voto(Voto):
   votacao = ForeignKeyField(Senado_Votacao, backref='votos')
   parlamentar = ForeignKeyField(Senado_Parlamentar, backref='votos')

DB.connect()
DB.create_tables([
   Camara_Votacao, Camara_Parlamentar, Camara_Voto, Camara_Proposicao,
   Senado_Votacao, Senado_Parlamentar, Senado_Voto
])