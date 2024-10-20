from .plenario import Plenario
from collections import defaultdict
from datetime import date

CORES_DISTINTAS = [
   (0.3741306655295645, 0.349072765803321, 0.8348162335795388),
   (0.37573218148346815, 0.9489808336424043, 0.35106838436470095),
   (0.9992874799291896, 0.5295060093894586, 0.43013774174932773),
   (0.4093264984609415, 0.838729391108588, 0.9720942907986453),
   (0.8693973129787654, 0.4507760620335093, 0.993024353656399),
   (0.9239305343659042, 0.9614299996643482, 0.390135300556744),
   (0.4345792058717807, 0.5235702767220346, 0.3660494211237391),
   (0.6971785813763859, 0.7354099643004269, 0.6466176705917978),
   (0.7139677586013414, 0.3637320236752671, 0.6115289834379194),
   (0.35429960371281694, 0.6230902686833699, 0.7184899126936536),
   (0.9916659268432223, 0.6980223061092491, 0.8728823216319341),
   (0.6374566827866718, 0.9951768430434402, 0.8004025218725901),
   (0.6898124243884464, 0.6959353066476482, 0.997045602095707),
   (0.6226246771977914, 0.72081505773362, 0.3387673209955004),
   (0.36906918773203085, 0.8770337546576821, 0.6805627570877588),
   (0.33629254658782703, 0.35216085011564985, 0.5258696828442972),
   (0.9989249044071654, 0.3791868821654613, 0.686133612980559),
   (0.8917798812737324, 0.9036185122075772, 0.7300064790594751),
   (0.8511742134275163, 0.3338694895542629, 0.33681720801937054),
   (0.6329917679277868, 0.9884539275838238, 0.47637215253988896),
   (0.5955632337967515, 0.5027765084985402, 0.8201118480666277),
   (0.958139921779197, 0.7472086046167075, 0.5005064982232911),
   (0.35769901938135656, 0.5705777246820448, 0.9909414929728961),
   (0.8330285436329641, 0.5519612522013638, 0.669448660442525),
   (0.35932085067435454, 0.7252140688382851, 0.4414649438364519),
   (0.755402539167403, 0.5434283418027509, 0.4079013840005223),
   (0.6177594332880162, 0.33674577829595337, 0.9663646396508407),
   (0.7856249092622184, 0.8957148206621811, 0.9926999859641633),
   (0.5880867227839424, 0.5220738113342045, 0.574574341417137),
   (0.6069852493815256, 0.3652163882829195, 0.3761321077667719),
   (0.3394344048333136, 0.9977788662022778, 0.8804844613107417),
   (0.5640104895122536, 0.9778434314175751, 0.9995558358021173),
   (0.5252132249363133, 0.7159184530335653, 0.8310271742580797),
   (0.753009228080983, 0.8552708048283252, 0.4035680217800455),
   (0.7808647670207721, 0.358026968499378, 0.822234450081072),
   (0.5119582191369273, 0.8543336891071012, 0.5160679738898921),
   (0.3731485179618135, 0.4579809504638303, 0.6792496932657075),
   (0.5008296072809643, 0.6953919288896518, 0.5874723902878948),
   (0.8423151713740625, 0.605479379886042, 0.9534534090932217),
   (0.8119280542005836, 0.9935599529025767, 0.5722437823174334)
]

COR_PRETO = (0, 0, 0)
COR_MASCULINO = (31/255, 119/255, 180/255)
COR_FEMININO = (255/255, 83/255, 152/255)
CORES_SEXO = defaultdict(lambda: COR_PRETO, {'M': COR_MASCULINO, 'F': COR_FEMININO})

def gradiente(x):
   r = 0.8*x + 0.2
   g = 2*max(0, x - 0.5)

   return (r, g, 0)

class TupleDict(dict):
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

      return DatetimeDict(intervalo, {ano: gradiente((ano - ano_base) / ESCALA) for ano in range(ano_base, ate_ano, intervalo)})

   def por_sexo(self) -> dict[str, tuple[float]]:
      return CORES_SEXO

   def por_partido(self) -> dict[str | tuple[str], tuple[float]]:
      partidos = self._plenario.partidos()
      cores = TupleDict({partido: CORES_DISTINTAS[i % len(CORES_DISTINTAS)] for i, partido in enumerate(partidos)})

      return cores

   def por_macroregiao(self) -> dict[str, tuple[float]]:
      macroregioes = self._plenario.macroregioes()
      cores = TupleDict({macroregiao: CORES_DISTINTAS[i % len(CORES_DISTINTAS)] for i, macroregiao in enumerate(macroregioes)})

      return cores

   def por_uf(self) -> dict[str | tuple[str], tuple[float]]:
      ufs = self._plenario.ufs()
      cores = TupleDict({uf: CORES_DISTINTAS[i % len(CORES_DISTINTAS)] for i, uf in enumerate(ufs)})

      return cores