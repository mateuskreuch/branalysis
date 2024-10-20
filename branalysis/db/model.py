from peewee import *

DB = SqliteDatabase('branalysis.db')
SENADO_API = 'https://legis.senado.leg.br/dadosabertos'
CAMARA_API = 'https://dadosabertos.camara.leg.br/api/v2'
CAMARA_FILES_API = 'https://dadosabertos.camara.leg.br/arquivos'

class BaseModel(Model):
   class Meta:
      database = DB

class BaseParlamentar(BaseModel):
   id = TextField(primary_key=True)
   nome = TextField()
   sexo = TextField()
   data_nascimento = DateField(null=True)

   def set_plenario(self, plenario):
      self._plenario = plenario

      return self

   def partidos(self) -> tuple[str]:
      return self._plenario.partidos_por_parlamentar()[self.id]

   def ufs(self) -> tuple[str]:
      return self._plenario.ufs_por_parlamentar()[self.id]

   def macroregioes(self) -> tuple[str]:
      return self._plenario.macroregioes_por_parlamentar()[self.id]

   def presenca(self) -> float:
      return self._plenario.presenca_por_parlamentar()[self.id]

class BaseVoto(BaseModel):
   votacao: ForeignKeyField
   parlamentar: ForeignKeyField

   partido = TextField()
   uf = TextField()
   voto = TextField()

class BaseVotacao(BaseModel):
   id = TextField(primary_key=True)
   data = DateField()
   tipo = TextField()
   numero = IntegerField()
   ano = IntegerField()

class Camara_Votacao(BaseVotacao):
   pass

class Camara_Parlamentar(BaseParlamentar):
   pass

class Camara_Voto(BaseVoto):
   votacao = ForeignKeyField(Camara_Votacao, backref='votos')
   parlamentar = ForeignKeyField(Camara_Parlamentar, backref='votos')

# Used only a facilitator cache, fields are duplicated to Camara_Votacao
class Camara_Proposicao(BaseModel):
   id = TextField(primary_key=True)
   tipo = TextField()
   numero = IntegerField()
   ano = IntegerField()

class Senado_Votacao(BaseVotacao):
   pass

class Senado_Parlamentar(BaseParlamentar):
   pass

class Senado_Voto(BaseVoto):
   votacao = ForeignKeyField(Senado_Votacao, backref='votos')
   parlamentar = ForeignKeyField(Senado_Parlamentar, backref='votos')

DB.connect()
DB.create_tables([
   Camara_Votacao, Camara_Parlamentar, Camara_Voto, Camara_Proposicao,
   Senado_Votacao, Senado_Parlamentar, Senado_Voto
])