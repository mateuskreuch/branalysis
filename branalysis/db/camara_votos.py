from . import camara_parlamentares
from .model import *
from .utils import *
from peewee import *

def fetch(year):
   return get_json(f'{CAMARA_FILES_API}/votacoesVotos/json/votacoesVotos-{year}.json')

def convert(votos):
   for voto in votos['dados']:
      yield Camara_Voto(
         votacao=voto['idVotacao'],
         parlamentar=voto['deputado_']['id'],
         partido=voto['deputado_']['siglaPartido'],
         uf=voto['deputado_']['siglaUf'],
         voto=voto['voto']
      )

def cache(year):
   camara_parlamentares.cache()

   votos = fetch(year)

   print(f'Câmara | Votos {year} | Cacheando.')

   with DB.atomic():
      for camara_voto in convert(votos):
         camara_voto.save(force_insert=True)