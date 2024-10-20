from .model import *
from .utils import *
from peewee import *

def fetch(id):
   return get_json(f'{CAMARA_API}/proposicoes/{id}')

def convert(proposicao):
   proposicao = proposicao['dados']

   return Camara_Proposicao(
      id=proposicao['id'],
      tipo=proposicao['siglaTipo'],
      numero=proposicao['numero'],
      ano=proposicao['ano']
   )

def has_record(id):
   return Camara_Proposicao.select().where(Camara_Proposicao.id == id).exists()

def cache(id):
   justified_id = id.ljust(7)

   if has_record(id):
      print(f'Câmara | Proposição {justified_id} | Já cacheada. Pulando.')
      return

   proposicao = fetch(id)
   camara_proposicao = convert(proposicao)

   print(f'Câmara | Proposição {justified_id} | Cacheando.')

   camara_proposicao.save(force_insert=True)