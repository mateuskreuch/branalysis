import requests

NO_PARTY = 'SEM PARTIDO'
NO_ENTRY = 'SEM REGISTRO'
NO_DATE = '0000-00-00'

def strip_dict_values(data):
   if isinstance(data, dict):
      keys_to_del = []

      for key, value in data.items():
         new_value = strip_dict_values(value)

         if new_value is not None:
            data[key] = new_value
         else:
            keys_to_del.append(key)

      for key in keys_to_del:
         del data[key]

   elif isinstance(data, list):
      for index in range(len(data)):
         data[index] = strip_dict_values(data[index])

   elif isinstance(data, str):
      x = data.strip().upper()

      return x if x else None

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