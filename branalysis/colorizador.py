from .plenario import Plenario
from collections import defaultdict
from datetime import date

CORES_DISTINTAS = [
   (0.374130, 0.349072, 0.834816), (0.375732, 0.948980, 0.351068),
   (0.999287, 0.529506, 0.430137), (0.409326, 0.838729, 0.972094),
   (0.869397, 0.450776, 0.993024), (0.923930, 0.961429, 0.390135),
   (0.434579, 0.523570, 0.366049), (0.697178, 0.735409, 0.646617),
   (0.713967, 0.363732, 0.611528), (0.354299, 0.623090, 0.718489),
   (0.991665, 0.698022, 0.872882), (0.637456, 0.995176, 0.800402),
   (0.689812, 0.695935, 0.997045), (0.622624, 0.720815, 0.338767),
   (0.369069, 0.877033, 0.680562), (0.336292, 0.352160, 0.525869),
   (0.998924, 0.379186, 0.686133), (0.891779, 0.903618, 0.730006),
   (0.851174, 0.333869, 0.336817), (0.632991, 0.988453, 0.476372),
   (0.595563, 0.502776, 0.820111), (0.958139, 0.747208, 0.500506),
   (0.357699, 0.570577, 0.990941), (0.833028, 0.551961, 0.669448),
   (0.359320, 0.725214, 0.441464), (0.755402, 0.543428, 0.407901),
   (0.617759, 0.336745, 0.966364), (0.785624, 0.895714, 0.992699),
   (0.588086, 0.522073, 0.574574), (0.606985, 0.365216, 0.376132),
   (0.339434, 0.997778, 0.880484), (0.564010, 0.977843, 0.999555),
   (0.525213, 0.715918, 0.831027), (0.753009, 0.855270, 0.403568),
   (0.780864, 0.358026, 0.822234), (0.511958, 0.854333, 0.516067),
   (0.373148, 0.457980, 0.679249), (0.500829, 0.695391, 0.587472),
   (0.842315, 0.605479, 0.953453), (0.811928, 0.993559, 0.572243)
]
CORES_DISTINTAS_LEN = len(CORES_DISTINTAS)

COR_PRETO = (0, 0, 0)
COR_MASCULINO = (31/255, 119/255, 180/255)
COR_FEMININO = (255/255, 83/255, 152/255)
CORES_POR_SEXO = defaultdict(lambda: COR_PRETO, {'M': COR_MASCULINO, 'F': COR_FEMININO})

def gradiente(x):
   r = 0.8*x + 0.2
   g = 2*max(0, x - 0.5)

   return (r, g, 0)

class TupleDict(dict):
   def __init__(self, itens):
      super().__init__({ k: CORES_DISTINTAS[i % CORES_DISTINTAS_LEN] for i, k in enumerate(itens) })

   def __getitem__(self, key):
      if type(key) == tuple:
         return super().__getitem__(key[0]) if len(key) == 1 else COR_PRETO
      else:
         return super().__getitem__(key)

class DatetimeDict(dict):
   def __init__(self, intervalo, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self._intervalo = intervalo

   def __getitem__(self, key):
      return super().__getitem__(key.year // self._intervalo * self._intervalo)

class Colorizador:
   def __init__(self, plenario: Plenario):
      self._plenario = plenario

   def por_ano(self, intervalo=10) -> dict[date, tuple[float]]:
      ESCALA = 100

      _, ate_ano = self._plenario.periodo()
      ano_base = ate_ano - ESCALA
      ano_base = ano_base // intervalo * intervalo

      return DatetimeDict(intervalo, {ano: gradiente((ano - ano_base) / ESCALA) for ano in range(ano_base, ate_ano + 1, intervalo)})

   def por_sexo(self) -> dict[str, tuple[float]]:
      return CORES_POR_SEXO

   def por_partido(self) -> dict[str | tuple[str], tuple[float]]:
      return TupleDict(self._plenario.partidos())

   def por_macroregiao(self) -> dict[str, tuple[float]]:
      return TupleDict(self._plenario.macroregioes())

   def por_uf(self) -> dict[str | tuple[str], tuple[float]]:
      return TupleDict(self._plenario.ufs())