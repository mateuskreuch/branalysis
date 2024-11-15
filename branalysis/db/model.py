
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
      return search_by_date(self.partidos(com_data=True), data)

   def partidos(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      return self._plenario.partidos_por_parlamentar(com_data)[self.id]

   @functools.cache
   def uf(self, data: date) -> str:
      return search_by_date(self.ufs(com_data=True), data)

   def ufs(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      return self._plenario.ufs_por_parlamentar(com_data)[self.id]

   @functools.cache
   def macroregiao(self, data: date) -> str:
      return search_by_date(self.macroregioes(com_data=True), data)

   def macroregioes(self, com_data=False) -> tuple[str] | tuple[tuple[str, date, date]]:
      return self._plenario.macroregioes_por_parlamentar(com_data)[self.id]

   def presenca(self) -> float:
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