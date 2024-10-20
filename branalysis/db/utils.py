import requests

def strip_dict_values(data):
   if isinstance(data, dict):
      for key, value in data.items():
         data[key] = strip_dict_values(value)

   elif isinstance(data, list):
      for index in range(len(data)):
         data[index] = strip_dict_values(data[index])

   elif isinstance(data, str):
      return data.strip().upper()

   return data

def get_json(url):
   while True:
      response = requests.get(url, headers={'Accept': 'application/json'})

      if response.status_code == 200:
         return strip_dict_values(response.json())

      else:
         print(f'Erro de código {response.status_code} ao tentar buscar "{url}", tentando novamente...')

def get_parlamentar_id(voto):
   return voto.__data__['parlamentar']

def get_votacao_id(voto):
   return voto.__data__['votacao']