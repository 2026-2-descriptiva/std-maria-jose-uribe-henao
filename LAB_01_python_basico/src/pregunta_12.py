import pandas as pd
from pathlib import Path

def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """

    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    datos = df[[0,4]].copy()
    datos[4] = datos[4].str.split(',')
    datos = datos.explode(4)
    datos[4] = datos[4].str.split(':').str[1]
    datos[4] = datos[4].astype(int)
    resultado = datos.groupby(0, sort=True)[4].agg('sum')
    respuesta = resultado.to_dict()
    print(respuesta)
    return respuesta


pregunta_12()
