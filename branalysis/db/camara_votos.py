from . import camara_parlamentares
from .model import *
from .utils import *
from peewee import *

def fetch(year):
   return get_json(f'{CAMARA_FILES_API}/votacoesVotos/json/votacoesVotos-{year}.json')

def convert_partido(partido):
   return NO_PARTY if partido == 'S.PART.' else partido

def convert(votos):
   for voto in votos['dados']:
      if 'idVotacao' in voto and 'id' in voto['deputado_']:
         yield Camara_Voto(
            votacao=voto['idVotacao'],
            parlamentar=voto['deputado_']['id'],
            partido=convert_partido(voto['deputado_'].get('siglaPartido', NO_ENTRY)),
            uf=voto['deputado_'].get('siglaUf', NO_ENTRY),
            voto=voto.get('voto', NO_ENTRY)
         )

def cache(year):
   camara_parlamentares.cache()

   votos = fetch(year)

   print(f'Câmara | Votos {year} | Cacheando.')

   with DB.atomic():
      for camara_voto in convert(votos):
         camara_voto.save(force_insert=True)