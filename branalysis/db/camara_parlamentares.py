from .model import *
from .utils import *
from peewee import *

def fetch():
   return get_json(f'{CAMARA_FILES_API}/deputados/json/deputados.json')

def convert(deputados):
   for deputado in deputados['dados']:
      yield Camara_Parlamentar(
         id=deputado['uri'].split('/')[-1],
         nome=deputado['nome'],
         sexo=deputado['siglaSexo'],
         data_nascimento=deputado['dataNascimento']
      )

def has_records():
   return Camara_Parlamentar.select().exists()

def cache():
   if has_records():
      print(f'Câmara | Deputados | Já cacheados. Pulando.')
      return

   deputados = fetch()

   print(f'Câmara | Deputados | Cacheando.')

   with DB.atomic():
      for camara_deputado in convert(deputados):
         camara_deputado.save(force_insert=True)