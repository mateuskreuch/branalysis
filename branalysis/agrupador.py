from collections import defaultdict
from typing import Any
import numpy as np

def agrupar_posicoes(modelo: np.ndarray, caracteristicas: list[Any | tuple[Any]]) -> dict[Any | tuple[Any], np.ndarray]:
   """
   Agrupa as posições de um modelo baseando-se em suas características. Exemplo:

   ```python
   modelo = PCA().fit_transform(matrix)
   clusters = HDBSCAN().fit_predict(modelo)
   caracteristicas = zip(clusters, (p.partidos() for p in parlamentares))

   for subcaracteristicas, submodelo in agrupar_posicoes(modelo, caracteristicas).items():
      cluster, partido = subcaracteristicas

      ax.scatter(submodelo[:, 0], submodelo[:, 1], color=cor[partido], marker=marcador[cluster])
   ```
   """
   grupos = defaultdict(list)

   for i, caracteristica in enumerate(caracteristicas):
      grupos[caracteristica].append(modelo[i, :])

   return {k: np.array(v) for k, v in grupos.items()}