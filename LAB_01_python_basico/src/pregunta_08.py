import pandas as pd
from pathlib import Path

def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    valores = df.groupby(1)[0].agg(lambda letras: sorted(set(letras))) 
    resultado = list(valores.items())

    return resultado

pregunta_08()