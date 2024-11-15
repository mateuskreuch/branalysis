# Branalysis

Biblioteca Python para coletar e analisar votações nominais do Congresso Nacional.

```python
from branalysis.plenario import Camara
from datetime import date
from matplotlib import pyplot as plt
from statistics import mean

ANO = 2023

def calcula_idade(parlamentar):
   return (date(ANO, 12, 31) - parlamentar.data_nascimento).days / 365

plenario = Camara(ANO)

# Organiza os partidos por idade média, criando tuplas (partido, idade média)
partido_idade_media = [
   (partido, mean(calcula_idade(p) for p in parlamentares))
   for partido, parlamentares in plenario.parlamentares_por_partido().items()
]

# Ordena por idade média crescente
partido_idade_media.sort(key=lambda x: x[1])

# Plota o gráfico de barras
barras = plt.bar(*zip(*partido_idade_media))

plt.bar_label(barras, fmt=lambda x: f'{x:.1f}', label_type='edge')
plt.ylabel('Idade média')
plt.xticks(rotation=-45, ha='left')
plt.show()
```

```python
from branalysis import Camara, MatrizPolitica, Colorizador, CORES
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

plenario = Camara(2023)
parlamentares = plenario.parlamentares()

# Cria a matriz de votos dos parlamentares
matriz = MatrizPolitica(parlamentares, plenario.votacoes()).de_parlamentares()

# Aplica a redução de dimensionalidade
modelo = PCA(n_components=2).fit_transform(matriz)

# Cria um colorizador, que mapeia cores para cada partido
colorizador = Colorizador(fallback='MAIS DE UM')
cor_por_parlamentar = [colorizador[p.partidos()] for p in parlamentares]

# Plota o mapa ideológico
grafico = plt.scatter(modelo[:, 0], modelo[:, 1], cmap=ListedColormap(CORES), c=cor_por_parlamentar)
texto_legenda, cores = colorizador.textos_e_cores()
cores_legenda = grafico.legend_elements(num=cores)[0]

plt.legend(cores_legenda, texto_legenda)
plt.show()
```