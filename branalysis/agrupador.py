from collections import defaultdict
from typing import Any
import numpy as np

def agrupar_posicoes(fit: np.ndarray, caracteristicas: list[Any | tuple[Any]]) -> dict[Any | tuple[Any], np.ndarray]:
   grupos = defaultdict(list)

   for i, caracteristica in enumerate(caracteristicas):
      grupos[caracteristica].append(fit[i, :])

   return {k: np.array(v) for k, v in grupos.items()}