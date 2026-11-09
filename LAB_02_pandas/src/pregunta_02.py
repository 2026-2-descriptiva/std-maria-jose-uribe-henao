import pandas as pd
from pathlib import Path

def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "tbl0.tsv"
    df = pd.read_csv(ruta, sep="\t")
    return len(df.columns)

pregunta_02()