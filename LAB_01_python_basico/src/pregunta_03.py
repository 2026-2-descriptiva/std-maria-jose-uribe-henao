import pandas as pd
from pathlib import Path

def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """

    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    suma = df.groupby(0)[1].sum()
    resultado = [(letra, cantidad) for letra, cantidad in suma.items()]

    return resultado

pregunta_03()
