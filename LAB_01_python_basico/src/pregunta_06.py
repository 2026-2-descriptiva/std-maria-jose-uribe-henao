import pandas as pd
from pathlib import Path

def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    metricas = df[4].str.split(',').explode()
    metricas  = metricas.str.split(':', expand=True)
    metricas[1] = metricas[1].astype(int)
    valores = metricas.groupby(0)[1].agg(['min', 'max'])
    resultado = list(valores.itertuples(index=True, name=None))

    return resultado

pregunta_06()