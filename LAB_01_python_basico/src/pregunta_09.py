import pandas as pd
from pathlib import Path

def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """

    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    metricas = df[4].str.split(',').explode()
    claves  = metricas.str.split(':').str[0]
    claves = claves.value_counts().sort_index()
    diccionario = claves.to_dict()

    return diccionario


pregunta_09()