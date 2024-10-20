from .model import *
from .utils import *
from peewee import *

def fetch(id):
   return get_json(f'{SENADO_API}/senador/{id}.json')

def get_parlamentares_sem_data_nascimento():
   return Senado_Parlamentar.select(Senado_Parlamentar.id).where(Senado_Parlamentar.data_nascimento.is_null())

def cache():
   parlamentares = get_parlamentares_sem_data_nascimento()

   if len(parlamentares) == 0:
      return

   with DB.atomic():
      for parlamentar in parlamentares:
         data = fetch(parlamentar.id)

         print(f'Senado | Data de nascimento {parlamentar.id} | Cacheando.')

         parlamentar.data_nascimento = data['DetalheParlamentar']['Parlamentar']['DadosBasicosParlamentar']['DataNascimento']
         parlamentar.save()