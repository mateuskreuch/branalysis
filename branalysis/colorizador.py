from .plenario import Plenario

CORES = [(0         , 0         , 0         , 1),
         (0.12156863, 0.46666667, 0.70588235, 1),
         (0.68235294, 0.78039216, 0.90980392, 1),
         (1         , 0.49803922, 0.05490196, 1),
         (1         , 0.73333333, 0.47058824, 1),
         (0.17254902, 0.62745098, 0.17254902, 1),
         (0.59607843, 0.8745098 , 0.54117647, 1),
         (0.83921569, 0.15294118, 0.15686275, 1),
         (1         , 0.59607843, 0.58823529, 1),
         (0.58039216, 0.40392157, 0.74117647, 1),
         (0.77254902, 0.69019608, 0.83529412, 1),
         (0.54901961, 0.3372549 , 0.29411765, 1),
         (0.76862745, 0.61176471, 0.58039216, 1),
         (0.89019608, 0.46666667, 0.76078431, 1),
         (0.96862745, 0.71372549, 0.82352941, 1),
         (0.49803922, 0.49803922, 0.49803922, 1),
         (0.78039216, 0.78039216, 0.78039216, 1),
         (0.7372549 , 0.74117647, 0.13333333, 1),
         (0.85882353, 0.85882353, 0.55294118, 1),
         (0.09019608, 0.74509804, 0.81176471, 1),
         (0.61960784, 0.85490196, 0.89803922, 1),
         (0.36746226, 0.57657207, 0.99569878, 1),
         (0.34374094, 0.99982132, 0.74416974, 1),
         (0.93693770, 0.35445788, 0.41093034, 1),
         (0.33537410, 0.98556435, 0.34436210, 1),
         (0.41227477, 0.69779199, 0.69629407, 1),
         (0.40796869, 0.71298256, 0.36128163, 1),
         (0.34350654, 0.33919606, 0.92732104, 1),
         (0.74948717, 0.35481691, 0.98683299, 1),
         (0.96067351, 0.99845293, 0.33948472, 1),
         (0.34555829, 0.82555298, 0.98921235, 1),
         (0.72532787, 0.48748777, 0.35086953, 1),
         (0.79460877, 0.99795462, 0.80524173, 1),
         (0.65089013, 0.54692150, 0.99562189, 1),
         (0.69060265, 0.99990261, 0.33661118, 1),
         (0.33850281, 0.34870083, 0.64869003, 1),
         (0.99635084, 0.34399350, 0.97769131, 1),
         (0.34568734, 0.85420426, 0.52686518, 1),
         (0.97384107, 0.55338914, 0.99604514, 1),
         (0.68163970, 0.33507463, 0.52441538, 1)]

class CorDict(dict):
   def textos_e_cores(self, key=None, reverse=False) -> tuple[list[str], list[int]]:
      if key is not None:
         key = lambda x: key(x[0])

      return zip(*sorted(self.items(), key=key, reverse=reverse))

class Colorizador(CorDict):
   def __init__(self, fallback='DESCONHECIDO'):
      super().__init__()

      self._fallback = fallback
      self._last_color = 0

   def __getitem__(self, key):
      if type(key) != tuple:
         return super().__getitem__(self._increase_color(key))

      elif len(key) != 1:
         self[self._fallback] = 0

         return 0

      return super().__getitem__(self._increase_color(key[0]))

   def _increase_color(self, key):
      if key not in self:
         self._last_color += 1

         self[key] = self._last_color

      return key

class SexoColorizador(CorDict):
   def __init__(self, homem_texto='HOMEM', mulher_texto='MULHER', outro_texto='OUTRO'):
      super().__init__()

      self._homem_texto = homem_texto
      self._mulher_texto = mulher_texto
      self._outro_texto = outro_texto

   def __getitem__(self, key):
      key = key.upper()

      if key == 'M' or key == 'MASCULINO' or key == 'HOMEM':
         self[self._homem_texto] = 0
         return super().__getitem__(self._homem_texto)

      elif key == 'F' or key == 'FEMININO' or key == 'MULHER':
         self[self._homem_texto] = 2
         return super().__getitem__(self._homem_texto)

      else:
         self[self._outro_texto] = 1
         return super().__getitem__(self._outro_texto)

class TempoColorizador(CorDict):
   def __init__(self, plenario: Plenario, intervalo=10):
      super().__init__()

      _, ano_final = plenario.periodo()
      self._intervalo = intervalo
      self._ano_final = self._get_closest(ano_final)

   def __getitem__(self, key):
      ano = self._get_closest(key.year)

      if ano not in self:
         self[ano] = (ano - self._ano_final) // self._intervalo

      return super().__getitem__(ano)

   def _get_closest(self, ano):
      return ano // self._intervalo * self._intervalo