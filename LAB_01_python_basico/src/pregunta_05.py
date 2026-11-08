import pandas as pd
from pathlib import Path

def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    valor_maximo = df[1].groupby(df[0]).max()
    valor_minimo = df[1].groupby(df[0]).min()
    resultado = []
    for letra, maximo in valor_maximo.items():
            resultado.append((letra,maximo, valor_minimo[letra]))

    return resultado

pregunta_05()