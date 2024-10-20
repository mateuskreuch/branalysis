from . import camara_proposicoes, camara_votos
from .model import *
from .utils import *
from peewee import *

def fetch(year):
   return get_json(f'{CAMARA_FILES_API}/votacoes/json/votacoes-{year}.json')

def is_nominal(votacao):
   return votacao['votosSim'] + votacao['votosNao'] + votacao['votosOutros'] > 0

def filter_nominais(votacoes):
   filtered = []

   for votacao in votacoes['dados']:
      if votacao['siglaOrgao'] == 'PLEN' and is_nominal(votacao):
         filtered.append(votacao)

   return filtered

def get_proposicao_id(votacao):
   return votacao['id'].split('-')[0]

def get_proposicao(votacao):
   proposicao_id = get_proposicao_id(votacao)

   return Camara_Proposicao.select().where(Camara_Proposicao.id == proposicao_id).get()

def convert(votacoes):
   for votacao in votacoes:
      proposicao = get_proposicao(votacao)

      yield Camara_Votacao(
         id=votacao['id'],
         data=votacao['data'],
         tipo=proposicao.tipo,
         numero=proposicao.numero,
         ano=proposicao.ano
      )

def has_records(year):
   return Camara_Votacao.select().where(Camara_Votacao.data.year == year).exists()

def cache(year):
   if has_records(year):
      print(f'Câmara | Votações {year} | Já cacheadas. Pulando.')
      return

   votacoes = fetch(year)
   votacoes = filter_nominais(votacoes)

   with DB.atomic():
      for votacao in votacoes:
         proposicao_id = get_proposicao_id(votacao)

         camara_proposicoes.cache(proposicao_id)

   camara_votos.cache(year)

   print(f'Câmara | Votações {year} | Cacheando.')

   with DB.atomic():
      for camara_votacao in convert(votacoes):
         camara_votacao.save(force_insert=True)