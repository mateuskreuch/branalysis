from . import senado_parlamentares
from .model import *
from .utils import *
from peewee import *

def fetch(year):
   return get_json(f'{SENADO_API}/plenario/votacao/nominal/{year}.json')

def is_nominal(votacao):
   return votacao['Secreta'] == 'N' and 'Votos' in votacao

def filter_nominais(votacoes):
   filtered = []

   for votacao in votacoes['ListaVotacoes']['Votacoes']['Votacao']:
      if votacao['SiglaCasa'] == 'SF' and is_nominal(votacao):
         filtered.append(votacao)

   return filtered

def get_votacao_id(votacao):
   codigo_sessao = votacao['CodigoSessao']
   sequencial_sessao = votacao['CodigoSessaoVotacao']

   return f'{codigo_sessao}-{sequencial_sessao}'

def convert_votacao(votacao):
   return Senado_Votacao(
      id=get_votacao_id(votacao),
      data=votacao['DataSessao'],
      tipo=votacao['SiglaMateria'],
      numero=votacao['NumeroMateria'],
      ano=votacao['AnoMateria']
   )

def convert_voto(votacao, voto: dict):
   return Senado_Voto(
      votacao=get_votacao_id(votacao),
      parlamentar=voto['CodigoParlamentar'],
      partido=voto.get('SiglaPartido', 'SEM REGISTRO'),
      uf=voto['SiglaUF'],
      voto=voto['Voto']
   )

def convert_parlamentar(voto):
   return Senado_Parlamentar(
      id=voto['CodigoParlamentar'],
      nome=voto['NomeParlamentar'],
      sexo=voto['SexoParlamentar']
   )

def has_parlamentar(id):
   return Senado_Parlamentar.select().where(Senado_Parlamentar.id == id).exists()

def has_records(year):
   return Senado_Votacao.select().where(Senado_Votacao.data.year == year).exists()

def cache(year):
   senado_parlamentares.cache()

   if has_records(year):
      print(f'Senado | Votações, votos e senadores de {year} | Já cacheadas. Pulando.')
      return

   votacoes = fetch(year)
   votacoes = filter_nominais(votacoes)

   print(f'Senado | Votações, votos e senadores de {year} | Cacheando.')

   with DB.atomic():
      for votacao in votacoes:
         for voto in votacao['Votos']['VotoParlamentar']:
            senado_parlamentar = convert_parlamentar(voto)

            if not has_parlamentar(senado_parlamentar.id):
               senado_parlamentar.save(force_insert=True)

            senado_voto = convert_voto(votacao, voto)
            senado_voto.save(force_insert=True)

         senado_votacao = convert_votacao(votacao)
         senado_votacao.save(force_insert=True)

   senado_parlamentares.cache()